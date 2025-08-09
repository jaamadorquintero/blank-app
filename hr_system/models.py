from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class RoleEnum(str, Enum):
    """Roles de usuario"""

    EMPLOYEE = "employee"
    HR = "hr"
    MANAGEMENT = "management"


class User(Base):
    """Usuario del sistema con control de roles."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(SqlEnum(RoleEnum), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"))

    worker = relationship("Worker", back_populates="user")


class Worker(Base):
    """Ficha individual del trabajador."""

    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    employee_number = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    curp = Column(String(18), unique=True, nullable=False)
    rfc = Column(String(13), unique=True, nullable=False)
    address = Column(String(200))
    phone = Column(String(20))
    hire_date = Column(Date, default=datetime.utcnow)
    position = Column(String(100))
    contract_type = Column(String(50))
    area_project = Column(String(100))
    daily_salary = Column(Float, default=0)
    photo_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("WorkerDocument", back_populates="worker")
    cardex_entries = relationship("WorkerCardex", back_populates="worker")
    user = relationship("User", uselist=False, back_populates="worker")


class DocumentType(str, Enum):
    CV = "cv"
    CERTIFICATE = "certificate"
    MEDICAL = "medical"
    INE = "ine"
    ADDRESS_PROOF = "address_proof"


class WorkerDocument(Base):
    """Documentos asociados al trabajador."""

    __tablename__ = "worker_documents"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    doc_type = Column(SqlEnum(DocumentType), nullable=False)
    file_path = Column(String(255), nullable=False)

    worker = relationship("Worker", back_populates="documents")


class WorkerCardex(Base):
    """Historial laboral del trabajador."""

    __tablename__ = "worker_cardex"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    description = Column(Text)
    event_date = Column(Date, default=datetime.utcnow)

    worker = relationship("Worker", back_populates="cardex_entries")


class IncidenceType(str, Enum):
    NONE = "none"
    ABSENCE = "absence"
    TARDINESS = "tardiness"
    EARLY_EXIT = "early_exit"


class AttendanceRecord(Base):
    """Registro de asistencia diaria."""

    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime)
    incidence = Column(SqlEnum(IncidenceType), default=IncidenceType.NONE)
    notes = Column(Text)

    worker = relationship("Worker")


class PermitStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PermitType(str, Enum):
    PERSONAL = "personal"
    MEDICAL = "medical"
    OTHER = "other"


class Permit(Base):
    """Solicitudes de permiso."""

    __tablename__ = "permits"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    permit_type = Column(SqlEnum(PermitType), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    justification = Column(Text)
    evidence_path = Column(String(255))
    status = Column(SqlEnum(PermitStatus), default=PermitStatus.PENDING)
    approved_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    worker = relationship("Worker")
    approver = relationship("User")


class IncidentStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class Incident(Base):
    """Incidencias relacionadas con el trabajador."""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    incident_type = Column(String(50), nullable=False)
    description = Column(Text)
    evidence_path = Column(String(255))
    status = Column(SqlEnum(IncidentStatus), default=IncidentStatus.OPEN)
    responsible_id = Column(Integer, ForeignKey("users.id"))
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    worker = relationship("Worker")
    responsible = relationship("User")


class Payroll(Base):
    """Cálculo de pago semanal."""

    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    base_salary = Column(Float, nullable=False)
    days_worked = Column(Integer, default=0)
    overtime_hours = Column(Float, default=0)
    overtime_rate = Column(Float, default=1.5)
    bonuses = Column(Float, default=0)
    deductions = Column(Float, default=0)
    permit_unpaid_hours = Column(Float, default=0)
    total_pay = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    worker = relationship("Worker")
