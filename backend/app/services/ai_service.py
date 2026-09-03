import os
import json
import re
import time
from typing import Dict, List, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod
import logging
from pydantic import BaseModel
import aiohttp
from dotenv import load_dotenv

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Enumeration of supported AI providers"""

    OPENAI = "openai"
    NVIDIA_NIM = "nvidia_nim"
    LOCAL_LLM = "local_llm"
    AUTO = "auto"  # Automatically select the best provider


class AIModelConfig(BaseModel):
    """Configuration for a specific AI model"""

    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30
    enabled: bool = True

    class Config:
        use_enum_values = True


class AIResult(BaseModel):
    """Result from an AI analysis"""

    success: bool
    analysis: Dict[str, Any]
    provider: AIProvider
    model: str
    response_time: float
    tokens_used: Optional[int] = None
    error: Optional[str] = None


class AIAnalyzer(ABC):
    """Abstract base class for AI analyzers"""

    # Subclasses override these
    DEFAULT_BASE_URL = ""
    PROVIDER_LABEL = ""

    def __init__(self, config: AIModelConfig):
        self.config = config
        self.provider = config.provider
        self.model_name = config.model_name
        self.api_key = config.api_key
        self.api_url = config.api_url or self.DEFAULT_BASE_URL
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.timeout = config.timeout
        self.headers = {
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
        }

    def _analysis_prompt(self) -> str:
        return (
            "You are a senior penetration tester and security expert. Analyze the following attack "
            "logs from a cybersecurity training platform and generate a comprehensive security report.\n\n"
            "ANALYSIS REQUIREMENTS:\n"
            "1. Identify the vulnerability type (SQL Injection, XSS, IDOR, etc.)\n"
            "2. Provide a detailed technical explanation\n"
            "3. Give an example of exploitation\n"
            "4. Suggest prevention techniques\n"
            "5. Provide a secure code recommendation\n"
            "6. Determine risk level (critical, high, medium, low)\n"
            "7. Provide recommendations for fixing the vulnerability\n\n"
            "OUTPUT FORMAT:\n"
            "{\n"
            '  "vulnerability_type": "string",\n'
            '  "technical_explanation": "string",\n'
            '  "example_exploitation": "string",\n'
            '  "prevention": "string",\n'
            '  "secure_code_recommendation": "string",\n'
            '  "risk_level": "critical|high|medium|low",\n'
            '  "ai_recommendations": ["string"],\n'
            '  "ongoing_recommendations": ["string"]\n'
            "}\n\n"
            "Respond ONLY with the JSON object, no additional text."
        )

    def build_prompt(
        self, attack_logs: List[Dict[str, Any]], scan_details: Dict[str, Any]
    ) -> str:
        """Build the prompt for the AI provider"""
        context = f"""CONTEXT:
        - Target application: {scan_details['lab_name']}
        - Attack type: {scan_details['attack_type']}
        - Total attempts: {len(attack_logs)}

        ATTACK LOGS:
        {self._format_attack_logs(attack_logs)}
        """
        return context + self._analysis_prompt()

    def _format_attack_logs(self, attack_logs: List[Dict[str, Any]]) -> str:
        """Format attack logs for the prompt"""
        if not attack_logs:
            return "No attack logs available"

        formatted_logs = []
        for i, log in enumerate(attack_logs, 1):
            formatted_log = f"""Log {i}:
- Timestamp: {log.get('timestamp', 'N/A')}
- Payload: {log.get('payload', 'N/A')}
- Request: {log.get('request', 'N/A')}
- Response: {log.get('response', 'N/A')}
- Result: {log.get('result', 'N/A')}
- Severity: {log.get('severity', 'N/A')}
"""
            formatted_logs.append(formatted_log)

        return "\n\n".join(formatted_logs)

    @abstractmethod
    async def analyze(
        self, attack_logs: List[Dict[str, Any]], scan_details: Dict[str, Any]
    ) -> AIResult:
        """Analyze attack logs using the AI provider"""
        pass


class ChatCompletionsAnalyzer(AIAnalyzer):
    """Shared implementation for OpenAI-compatible chat completion APIs"""

    def _error(self, message: str, start_time: float) -> AIResult:
        logger.error(f"{self.PROVIDER_LABEL} analysis failed: {message}")
        return AIResult(
            success=False,
            analysis={},
            provider=self.provider,
            model=self.model_name,
            response_time=time.time() - start_time,
            error=message,
        )

    def _parse_json(self, content: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    return None
            return None

    async def analyze(
        self, attack_logs: List[Dict[str, Any]], scan_details: Dict[str, Any]
    ) -> AIResult:
        """Analyze attack logs using an OpenAI-compatible API"""
        start_time = time.time()

        try:
            prompt = self.build_prompt(attack_logs, scan_details)

            data = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a senior penetration tester and security expert.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "response_format": {"type": "json_object"},
            }

            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=timeout,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return self._error(
                            f"{self.PROVIDER_LABEL} API returned {response.status}: {error_text}",
                            start_time,
                        )

                    result = await response.json()

                    content = result["choices"][0]["message"]["content"]
                    analysis = self._parse_json(content)
                    if analysis is None:
                        return self._error(
                            "Could not extract valid JSON response from provider",
                            start_time,
                        )

                    tokens_used = result.get("usage", {}).get("total_tokens", None)

                    return AIResult(
                        success=True,
                        analysis=analysis,
                        provider=self.provider,
                        model=self.model_name,
                        response_time=time.time() - start_time,
                        tokens_used=tokens_used,
                    )

        except Exception as e:
            return self._error(str(e), start_time)


class OpenAIAnalyzer(ChatCompletionsAnalyzer):
    """Analyzer for OpenAI API"""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    PROVIDER_LABEL = "OpenAI"


class NVIDIA_NIM_Analyzer(ChatCompletionsAnalyzer):
    """Analyzer for NVIDIA NIM API"""

    DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
    PROVIDER_LABEL = "NVIDIA NIM"


class LocalLLMAnalyzer(ChatCompletionsAnalyzer):
    """Analyzer for local LLM (Ollama format)"""

    DEFAULT_BASE_URL = "http://localhost:11434/api"
    PROVIDER_LABEL = "Local LLM"

    async def analyze(
        self, attack_logs: List[Dict[str, Any]], scan_details: Dict[str, Any]
    ) -> AIResult:
        """Analyze attack logs using local LLM (Ollama format)"""
        start_time = time.time()

        try:
            prompt = self.build_prompt(attack_logs, scan_details)

            data = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False,
                "format": "json",
            }

            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/generate",
                    headers=self.headers,
                    json=data,
                    timeout=timeout,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return self._error(
                            f"Local LLM API returned {response.status}: {error_text}",
                            start_time,
                        )

                    result = await response.json()

                    content = result.get("response", "")
                    analysis = self._parse_json(content)
                    if analysis is None:
                        return self._error(
                            "Could not extract valid JSON response from local LLM",
                            start_time,
                        )

                    # For local LLMs, token usage may not be available;
                    # total_duration is in nanoseconds, not an exact token count
                    tokens_used = result.get("eval_count", None)

                    return AIResult(
                        success=True,
                        analysis=analysis,
                        provider=self.provider,
                        model=self.model_name,
                        response_time=time.time() - start_time,
                        tokens_used=tokens_used,
                    )

        except Exception as e:
            return self._error(str(e), start_time)


class AIManager:
    """Manages multiple AI providers and handles failover"""

    def __init__(self):
        self.analyzers: Dict[AIProvider, AIAnalyzer] = {}
        self.load_config()

    def load_config(self):
        """Load AI configuration from environment variables"""
        default_configs = [
            # OpenAI configuration
            {
                "provider": AIProvider.OPENAI,
                "model_name": "gpt-4o",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "api_url": os.getenv("OPENAI_API_URL"),
                "temperature": 0.7,
                "max_tokens": 1000,
                "enabled": os.getenv("OPENAI_ENABLED", "true").lower() == "true",
            },
            # NVIDIA NIM configuration
            {
                "provider": AIProvider.NVIDIA_NIM,
                "model_name": "nvidia/llama-3.1-nemotron-70b-instruct",
                "api_key": os.getenv("NVIDIA_API_KEY"),
                "api_url": os.getenv("NVIDIA_API_URL"),
                "temperature": 0.7,
                "max_tokens": 1000,
                "enabled": os.getenv("NVIDIA_ENABLED", "true").lower() == "true",
            },
            # Local LLM configuration
            {
                "provider": AIProvider.LOCAL_LLM,
                "model_name": "llama3.1:8b",
                "api_url": os.getenv("LOCAL_LLM_API_URL"),
                "temperature": 0.7,
                "max_tokens": 1000,
                "enabled": os.getenv("LOCAL_LLM_ENABLED", "true").lower() == "true",
            },
        ]

        for config_data in default_configs:
            model_config = AIModelConfig(**config_data)
            if model_config.enabled:
                analyzer = self._create_analyzer(model_config)
                if analyzer:
                    provider = (
                        model_config.provider
                        if isinstance(model_config.provider, AIProvider)
                        else AIProvider(model_config.provider)
                    )
                    self.analyzers[provider] = analyzer

        logger.info(
            f"Loaded {len(self.analyzers)} AI providers: {[p.value for p in self.analyzers.keys()]}"
        )

    def _create_analyzer(self, config: AIModelConfig) -> Optional[AIAnalyzer]:
        """Create an analyzer instance based on provider"""
        try:
            # use_enum_values stores provider as a string on the config model
            provider = (
                config.provider
                if isinstance(config.provider, AIProvider)
                else AIProvider(config.provider)
            )
            if provider == AIProvider.OPENAI:
                if not config.api_key:
                    logger.warning(
                        "OpenAI API key not configured, skipping OpenAI analyzer"
                    )
                    return None
                return OpenAIAnalyzer(config)
            elif provider == AIProvider.NVIDIA_NIM:
                if not config.api_key:
                    logger.warning(
                        "NVIDIA NIM API key not configured, skipping NVIDIA NIM analyzer"
                    )
                    return None
                return NVIDIA_NIM_Analyzer(config)
            elif provider == AIProvider.LOCAL_LLM:
                return LocalLLMAnalyzer(config)
            else:
                logger.warning(f"Unsupported AI provider: {provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to create analyzer for {config.provider}: {str(e)}")
            return None

    def _no_providers_result(self) -> AIResult:
        return AIResult(
            success=False,
            analysis={},
            provider=AIProvider.AUTO,
            model="",
            response_time=0,
            error="No AI providers are configured or enabled",
        )

    async def analyze_with_fallback(
        self, attack_logs: List[Dict[str, Any]], scan_details: Dict[str, Any]
    ) -> AIResult:
        """Analyze with fallback to other providers if one fails"""
        result = self._no_providers_result()

        # Try all enabled providers in order, return first success or last error
        for provider, analyzer in self.analyzers.items():
            result = await analyzer.analyze(attack_logs, scan_details)
            if result.success:
                return result

        return result

    async def analyze_with_provider(
        self,
        attack_logs: List[Dict[str, Any]],
        scan_details: Dict[str, Any],
        provider: AIProvider,
    ) -> AIResult:
        """Analyze using a specific provider"""
        if provider not in self.analyzers:
            return AIResult(
                success=False,
                analysis={},
                provider=provider,
                model="",
                response_time=0,
                error=f"Provider {provider.value} is not configured or disabled",
            )

        analyzer = self.analyzers[provider]
        return await analyzer.analyze(attack_logs, scan_details)

    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available providers"""
        return list(self.analyzers.keys())

    def check_provider_health(self, provider: AIProvider) -> Dict[str, Any]:
        """Check if a provider is available"""
        if provider not in self.analyzers:
            return {
                "available": False,
                "error": f"Provider {provider.value} is not configured or disabled",
            }

        return {
            "available": True,
            "provider": provider.value,
            "model": self.analyzers[provider].model_name,
        }


# Initialize AI Manager
ai_manager = AIManager()


# Global function to analyze with fallback
async def analyze_attacks_with_ai(
    attack_logs: List[Dict[str, Any]], scan_details: Dict[str, Any]
) -> AIResult:
    """Global function for AI analysis with fallback"""
    return await ai_manager.analyze_with_fallback(attack_logs, scan_details)


# Global function for specific provider analysis
async def analyze_attacks_with_provider(
    attack_logs: List[Dict[str, Any]],
    scan_details: Dict[str, Any],
    provider: AIProvider,
) -> AIResult:
    """Global function for AI analysis with specific provider"""
    return await ai_manager.analyze_with_provider(attack_logs, scan_details, provider)


# Global function to get available providers
def get_available_ai_providers() -> List[AIProvider]:
    """Get list of available AI providers"""
    return ai_manager.get_available_providers()


# Global function to check provider health
def check_ai_provider_health(provider: AIProvider) -> Dict[str, Any]:
    """Check if a provider is available"""
    return ai_manager.check_provider_health(provider)
