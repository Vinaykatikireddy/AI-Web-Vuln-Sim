from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

# Initialize the Base class
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    scans = relationship("Scan", back_populates="user")
    reports = relationship("Report", back_populates="user")


class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="stopped")  # stopped, running, starting, stopping, deleted
    docker_image = Column(String(255), nullable=False)
    port = Column(Integer)
    external_url = Column(String(255))  # For external labs, if any
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    scans = relationship("Scan", back_populates="lab")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    attack_type = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="scans")
    lab = relationship("Lab", back_populates="scans")
    logs = relationship("Log", back_populates="scan")
    report = relationship("Report", uselist=False, back_populates="scan")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    request = Column(Text)
    response = Column(Text)
    payload = Column(Text)
    result = Column(String(50))  # success, failure, vulnerability_detected
    severity = Column(String(20))  # low, medium, high, critical
    extra_data = Column(Text)  # JSON string for additional data

    # Relationships
    scan = relationship("Scan", back_populates="logs")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text)
    format = Column(String(20), default="html")  # html, markdown, pdf
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="pending")  # pending, generated, error

    # Relationships
    scan = relationship("Scan", back_populates="report")
    user = relationship("User", back_populates="reports")


class Payload(Base):
    __tablename__ = "payloads"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # sqli, xss, idor, auth-bypass, dir-traversal, file-upload
    payload = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
