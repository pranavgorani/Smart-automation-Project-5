from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint
from datetime import datetime
from backend.app.db.database import Base


class IndexValue(Base):
    __tablename__ = "index_values"

    id = Column(Integer, primary_key=True, index=True)
    index_date = Column(Date, unique=True, nullable=False, index=True)
    index_value = Column(Float, nullable=False)
    daily_change = Column(Float, default=0.0)
    weekly_change = Column(Float, default=0.0)
    monthly_change = Column(Float, default=0.0)
    base_period = Column(String(20), default="2026-01-01")
    methodology_version = Column(String(20), default="1.0")
    route_count = Column(Integer, default=13)
    observation_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=95.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "index_date": self.index_date.isoformat() if self.index_date else None,
            "index_value": round(self.index_value, 2),
            "daily_change": round(self.daily_change, 2),
            "weekly_change": round(self.weekly_change, 2),
            "monthly_change": round(self.monthly_change, 2),
            "base_period": self.base_period,
            "methodology_version": self.methodology_version,
            "route_count": self.route_count,
            "observation_count": self.observation_count,
            "confidence_score": round(self.confidence_score, 1),
        }


class RouteIndex(Base):
    __tablename__ = "route_index"

    id = Column(Integer, primary_key=True, index=True)
    index_date = Column(Date, nullable=False, index=True)
    route = Column(String(20), nullable=False, index=True)
    index_value = Column(Float, nullable=False)
    median_fare = Column(Float, nullable=False)
    mean_fare = Column(Float, nullable=False)
    fare_change = Column(Float, default=0.0)
    weight = Column(Float, nullable=False)
    observation_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("index_date", "route", name="uq_route_index_date_route"),)

    def to_dict(self):
        return {
            "id": self.id,
            "index_date": self.index_date.isoformat() if self.index_date else None,
            "route": self.route,
            "index_value": round(self.index_value, 2),
            "median_fare": round(self.median_fare, 2),
            "mean_fare": round(self.mean_fare, 2),
            "fare_change": round(self.fare_change, 2),
            "weight": self.weight,
            "observation_count": self.observation_count,
        }


class DataQualityLog(Base):
    __tablename__ = "data_quality"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, nullable=True)
    source = Column(String(100), nullable=False)
    records_collected = Column(Integer, default=0)
    records_valid = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    duplicates = Column(Integer, default=0)
    missing_values = Column(Integer, default=0)
    outliers = Column(Integer, default=0)
    completeness_score = Column(Float, default=100.0)
    validity_score = Column(Float, default=100.0)
    timeliness_score = Column(Float, default=100.0)
    uniqueness_score = Column(Float, default=100.0)
    consistency_score = Column(Float, default=100.0)
    quality_score = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "source": self.source,
            "records_collected": self.records_collected,
            "records_valid": self.records_valid,
            "records_rejected": self.records_rejected,
            "duplicates": self.duplicates,
            "missing_values": self.missing_values,
            "outliers": self.outliers,
            "completeness_score": round(self.completeness_score, 1),
            "validity_score": round(self.validity_score, 1),
            "timeliness_score": round(self.timeliness_score, 1),
            "uniqueness_score": round(self.uniqueness_score, 1),
            "consistency_score": round(self.consistency_score, 1),
            "quality_score": round(self.quality_score, 1),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DGCAReferenceRecord(Base):
    __tablename__ = "dgca_reference_records"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(10), nullable=False, index=True)
    route = Column(String(20), nullable=False, index=True)
    airline = Column(String(100), nullable=False)
    passengers = Column(Integer, nullable=False)
    average_fare = Column(Float, nullable=False)
    fuel_surcharge = Column(Float, default=0.0)
    source = Column(String(100), default="DGCA_MONTHLY")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "month": self.month,
            "route": self.route,
            "airline": self.airline,
            "passengers": self.passengers,
            "average_fare": round(self.average_fare, 2),
            "fuel_surcharge": round(self.fuel_surcharge, 2),
            "source": self.source,
        }
