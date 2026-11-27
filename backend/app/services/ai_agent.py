import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from sqlalchemy.orm import Session

from database import SessionLocal
from models import base
from services.ai_service import ai_manager, ChatCompletionsAnalyzer
from services.recon_service import ReconService

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """You are an autonomous AI web application security analyst operating inside an authorized, isolated educational vulnerability lab.
Your goal is to inspect the target lab's discovered surface, test hypotheses methodically using scoped HTTP requests, and record verified findings with concrete proof-of-concept evidence.

Available actions (respond ONLY with a single JSON object):
1. Send a scoped HTTP request to test a hypothesis:
{
  "action": "send_request",
  "thought": "Why you are sending this request and what you expect to observe",
  "method": "GET" | "POST",
  "path": "/relative/path",
  "params": {"key": "value"},
  "data": {"key": "value"},
  "payload_label": "short label"
}

2. Record a verified finding tied to a specific log_id from a prior send_request observation:
{
  "action": "record_finding",
  "thought": "Why the observed response confirms a vulnerability",
  "title": "Short finding title",
  "category": "sql_injection | xss | idor | auth_bypass | dir_traversal | file_upload_abuse | misconfiguration",
  "severity": "critical | high | medium | low",
  "log_id": 123,
  "endpoint": "/path",
  "technical_explanation": "Detailed technical explanation of the flaw",
  "poc_summary": "Exact observable evidence from the HTTP request/response",
  "remediation": "Actionable remediation & secure coding fix"
}

3. Finish the analysis when you have tested the key endpoints or answered the user's request:
{
  "action": "finish",
  "thought": "Summary of what was tested and discovered",
  "summary": "Concise final assessment"
}

Rules:
- Stay strictly on relative paths of the target lab.
- Never invent a log_id; only reference a log_id returned by a previous send_request step.
- Respond ONLY with valid JSON."""


class AIAgentRunner:
    """Orchestrates autonomous and interactive LLM-driven security analysis for a lab scan."""

    def __init__(self):
        self.recon = ReconService()

    def _get_analyzer(self) -> Optional[ChatCompletionsAnalyzer]:
        for analyzer in ai_manager.analyzers.values():
            if isinstance(analyzer, ChatCompletionsAnalyzer):
                return analyzer
        return None

    async def _call_llm_json(
        self,
        analyzer: ChatCompletionsAnalyzer,
        messages: List[Dict[str, str]],
        max_tokens: int = 1200,
    ) -> Dict[str, Any]:
        data = {
            "model": analyzer.model_name,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        timeout = aiohttp.ClientTimeout(total=analyzer.timeout)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{analyzer.api_url}/chat/completions",
                headers=analyzer.headers,
                json=data,
                timeout=timeout,
            ) as response:
                if response.status != 200:
                    err = await response.text()
                    raise RuntimeError(f"LLM API {response.status}: {err}")
                payload = await response.json()
                content = payload["choices"][0]["message"]["content"]
                parsed = analyzer._parse_json(content)
                if parsed is None:
                    raise RuntimeError("LLM returned non-JSON content")
                return parsed

    def _next_step_number(self, db: Session, scan_id: int) -> int:
        last = (
            db.query(base.AgentStep)
            .filter(base.AgentStep.scan_id == scan_id)
            .order_by(base.AgentStep.step_number.desc())
            .first()
        )
        return (last.step_number + 1) if last else 1

    def _add_step(
        self,
        db: Session,
        scan_id: int,
        role: str,
        phase: str,
        thought: Optional[str] = None,
        action_name: Optional[str] = None,
        action_input: Optional[Dict[str, Any]] = None,
        observation: Optional[str] = None,
        log_id: Optional[int] = None,
    ) -> base.AgentStep:
        step = base.AgentStep(
            scan_id=scan_id,
            step_number=self._next_step_number(db, scan_id),
            role=role,
            phase=phase,
            thought=thought,
            action_name=action_name,
            action_input=json.dumps(action_input) if action_input is not None else None,
            observation=observation,
            log_id=log_id,
        )
        db.add(step)
        db.commit()
        db.refresh(step)
        return step

    def _build_history_context(self, db: Session, scan_id: int) -> str:
        steps = (
            db.query(base.AgentStep)
            .filter(base.AgentStep.scan_id == scan_id)
            .order_by(base.AgentStep.step_number.asc())
            .all()
        )
        lines = []
        for s in steps:
            lines.append(
                f"Step {s.step_number} [{s.role}/{s.phase}]: "
                f"thought={s.thought or ''} | action={s.action_name or ''} | "
                f"input={s.action_input or ''} | observation={s.observation or ''} | log_id={s.log_id}"
            )
        return "\n".join(lines)

    async def _run_steps_loop(
        self,
        db: Session,
        scan: base.Scan,
        lab: base.Lab,
        focus: Optional[str],
        max_steps: int,
    ) -> None:
        analyzer = self._get_analyzer()
        if not analyzer:
            self._add_step(
                db,
                scan.id,
                role="assistant",
                phase="complete",
                thought="No AI provider is configured (set OPENAI_API_KEY, NVIDIA_API_KEY, or LOCAL_LLM_API_URL in .env).",
                action_name="finish",
                observation="Autonomous LLM analysis skipped because no AI provider is configured. Surface recon completed.",
            )
            return

        for _ in range(max_steps):
            history_text = self._build_history_context(db, scan.id)
            user_prompt = (
                f"Target Lab: {lab.name}\n"
                f"Description: {lab.description or 'N/A'}\n"
                f"Base URL: {lab.external_url}\n"
                f"Analysis Focus: {focus or 'Autonomous full security assessment'}\n\n"
                f"History so far:\n{history_text}\n\n"
                "Choose your next single JSON action."
            )
            try:
                decision = await self._call_llm_json(
                    analyzer,
                    [
                        {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
            except Exception as exc:
                self._add_step(
                    db,
                    scan.id,
                    role="assistant",
                    phase="complete",
                    thought=f"AI step failed: {exc}",
                    action_name="finish",
                    observation=str(exc),
                )
                break

            action = decision.get("action", "finish")
            thought = decision.get("thought", "")

            if action == "send_request":
                method = decision.get("method", "GET")
                path = decision.get("path", "/")
                params = decision.get("params")
                data = decision.get("data")
                payload_label = decision.get("payload_label", "")
                result = self.recon.send_scoped_request(
                    db=db,
                    scan_id=scan.id,
                    base_url=lab.external_url,
                    method=method,
                    path=path,
                    params=params,
                    data=data,
                    payload_label=payload_label,
                )
                self._add_step(
                    db,
                    scan.id,
                    role="tool",
                    phase="test",
                    thought=thought,
                    action_name="send_request",
                    action_input={"method": method, "path": path, "params": params, "data": data},
                    observation=json.dumps(result),
                    log_id=result.get("log_id"),
                )

            elif action == "record_finding":
                log_id = decision.get("log_id")
                severity = decision.get("severity", "medium")
                if log_id:
                    log_row = db.query(base.Log).filter(
                        base.Log.id == log_id, base.Log.scan_id == scan.id
                    ).first()
                    if log_row:
                        log_row.result = "vulnerability_detected"
                        log_row.severity = severity
                        db.commit()

                self._add_step(
                    db,
                    scan.id,
                    role="finding",
                    phase="observe",
                    thought=thought,
                    action_name="record_finding",
                    action_input={
                        "title": decision.get("title", "Vulnerability Detected"),
                        "category": decision.get("category", "unknown"),
                        "severity": severity,
                        "endpoint": decision.get("endpoint", "/"),
                        "technical_explanation": decision.get("technical_explanation", ""),
                        "poc_summary": decision.get("poc_summary", ""),
                        "remediation": decision.get("remediation", ""),
                    },
                    observation=decision.get("poc_summary", ""),
                    log_id=log_id,
                )

            else:
                self._add_step(
                    db,
                    scan.id,
                    role="assistant",
                    phase="complete",
                    thought=thought,
                    action_name="finish",
                    observation=decision.get("summary", "Analysis complete."),
                )
                break

    def run_autonomous_scan_sync(self, scan_id: int, focus: Optional[str] = None) -> None:
        """Background entrypoint to run recon + autonomous LLM analysis for a scan."""
        db = SessionLocal()
        try:
            scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
            if not scan:
                return
            lab = db.query(base.Lab).filter(base.Lab.id == scan.lab_id).first()
            if not lab:
                scan.status = "failed"
                db.commit()
                return

            scan.status = "running"
            scan.started_at = datetime.now(timezone.utc)
            db.commit()

            surface = self.recon.map_surface(lab.external_url)
            self._add_step(
                db,
                scan.id,
                role="tool",
                phase="recon",
                thought=f"Mapped target attack surface for {lab.name} ({lab.external_url}).",
                action_name="map_surface",
                action_input={"base_url": lab.external_url},
                observation=json.dumps(surface),
            )

            asyncio.run(self._run_steps_loop(db, scan, lab, focus, max_steps=10))

            scan.status = "completed"
            scan.completed_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as exc:
            logger.exception(f"Autonomous scan {scan_id} failed: {exc}")
            scan = db.query(base.Scan).filter(base.Scan.id == scan_id).first()
            if scan:
                scan.status = "failed"
                db.commit()
        finally:
            db.close()

    async def interact(self, db: Session, scan: base.Scan, message: str) -> None:
        """Handle an interactive follow-up instruction or question from the user."""
        lab = db.query(base.Lab).filter(base.Lab.id == scan.lab_id).first()
        if not lab:
            raise ValueError("Lab not found")

        self._add_step(
            db,
            scan.id,
            role="user",
            phase="interact",
            thought=message,
            action_name="user_prompt",
            observation=message,
        )
        await self._run_steps_loop(db, scan, lab, focus=f"User follow-up: {message}", max_steps=4)

    async def generate_structured_report(self, db: Session, scan: base.Scan) -> base.Report:
        """Transform recorded findings and HTTP logs into a structured PoC report."""
        lab = db.query(base.Lab).filter(base.Lab.id == scan.lab_id).first()
        finding_steps = (
            db.query(base.AgentStep)
            .filter(base.AgentStep.scan_id == scan.id, base.AgentStep.role == "finding")
            .all()
        )
        logs_by_id = {
            log.id: log
            for log in db.query(base.Log).filter(base.Log.scan_id == scan.id).all()
        }

        structured_findings: List[Dict[str, Any]] = []
        severity_weights = {"critical": 95, "high": 75, "medium": 50, "low": 25}
        max_score = 0

        for step in finding_steps:
            data = json.loads(step.action_input) if step.action_input else {}
            severity = data.get("severity", "medium").lower()
            max_score = max(max_score, severity_weights.get(severity, 40))

            linked_log = logs_by_id.get(step.log_id) if step.log_id else None
            poc_evidence = {
                "log_id": step.log_id,
                "request": linked_log.request if linked_log else "N/A",
                "response_excerpt": (linked_log.response[:500] if linked_log and linked_log.response else "N/A"),
                "observation": data.get("poc_summary") or step.observation or "",
            }

            structured_findings.append(
                {
                    "title": data.get("title", "Security Finding"),
                    "vulnerability_type": data.get("category", "unknown").replace("_", " ").title(),
                    "endpoint": data.get("endpoint", "/"),
                    "risk_level": severity,
                    "technical_explanation": data.get("technical_explanation", step.thought or ""),
                    "example_exploitation": poc_evidence["observation"],
                    "poc_evidence": poc_evidence,
                    "prevention": data.get("remediation", ""),
                    "secure_code_recommendation": data.get("remediation", ""),
                }
            )

        executive_summary = (
            f"Autonomous AI security analysis of {lab.name if lab else 'the target lab'} "
            f"identified {len(structured_findings)} finding(s) across {len(logs_by_id)} recorded HTTP probe(s)."
        )

        report_payload = {
            "executive_summary": executive_summary,
            "risk_score": max_score if structured_findings else 0,
            "findings": structured_findings,
            "ai_recommendations": [
                f["prevention"] for f in structured_findings if f.get("prevention")
            ] or ["Continue periodic security testing and input validation reviews."],
        }

        existing = db.query(base.Report).filter(base.Report.scan_id == scan.id).first()
        if existing:
            existing.content = json.dumps(report_payload)
            existing.status = "generated"
            existing.generated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing

        report = base.Report(
            scan_id=scan.id,
            user_id=scan.user_id,
            content=json.dumps(report_payload),
            format="html",
            status="generated",
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
