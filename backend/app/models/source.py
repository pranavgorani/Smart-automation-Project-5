from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from datetime import datetime
from backend.app.db.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(50), nullable=False)  # LIVE_API, PERMITTED_WEB, MOCK, CSV_IMPORT, DGCA_REFERENCE
    status = Column(String(50), default="ACTIVE")  # ACTIVE, DEGRADED, INACTIVE, ERROR
    last_success = Column(DateTime, nullable=True)
    last_failure = Column(DateTime, nullable=True)
    request_count = Column(Integer, default=0)
    success_rate = Column(Float, default=100.0)
    compliance_status = Column(String(50), default="COMPLIANT")
    robots_checked = Column(Boolean, default=True)
    rate_limit_seconds = Column(Integer, default=5)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "request_count": self.request_count,
            "success_rate": self.success_rate,
            "compliance_status": self.compliance_status,
            "robots_checked": self.robots_checked,
            "rate_limit_seconds": self.rate_limit_seconds,
        }


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)  # SUCCESS, PARTIAL, FAILED
    records_collected = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "run_timestamp": self.run_timestamp.isoformat() if self.run_timestamp else None,
            "source": self.source,
            "source_type": self.source_type,
            "status": self.status,
            "records_collected": self.records_collected,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
        }
