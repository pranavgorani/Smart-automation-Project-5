from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date
from datetime import datetime
from backend.app.db.database import Base


class AirfareQuote(Base):
    __tablename__ = "airfare_quotes"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # LIVE_API, PERMITTED_WEB, MOCK, CSV_IMPORT
    source_reference = Column(String(255), nullable=True)
    origin = Column(String(10), nullable=False, index=True)
    destination = Column(String(10), nullable=False, index=True)
    route = Column(String(20), nullable=False, index=True)
    airline = Column(String(100), nullable=False, index=True)
    flight_number = Column(String(50), nullable=True)
    departure_date = Column(Date, nullable=False, index=True)
    departure_time = Column(String(20), nullable=True)
    arrival_time = Column(String(20), nullable=True)
    search_timestamp = Column(DateTime, nullable=False, index=True)
    advance_purchase_days = Column(Integer, nullable=False, index=True)  # 1, 7, 15, 30, 45
    fare_class = Column(String(50), default="Economy")
    fare_family = Column(String(50), default="Standard")
    
    # Fare decomposition
    base_fare = Column(Float, nullable=False)
    taxes = Column(Float, default=0.0)
    user_development_fee = Column(Float, default=0.0)
    convenience_fee = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    total_fare = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    
    availability = Column(Integer, default=9)
    stops = Column(Integer, default=0)
    refundability = Column(String(50), default="Non-refundable")
    raw_hash = Column(String(64), unique=True, index=True, nullable=True)
    data_quality_score = Column(Float, default=100.0)
    is_outlier = Column(Boolean, default=False)
    outlier_method = Column(String(50), nullable=True)
    outlier_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "source_type": self.source_type,
            "source_reference": self.source_reference,
            "origin": self.origin,
            "destination": self.destination,
            "route": self.route,
            "airline": self.airline,
            "flight_number": self.flight_number,
            "departure_date": self.departure_date.isoformat() if self.departure_date else None,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "search_timestamp": self.search_timestamp.isoformat() if self.search_timestamp else None,
            "advance_purchase_days": self.advance_purchase_days,
            "fare_class": self.fare_class,
            "fare_family": self.fare_family,
            "base_fare": self.base_fare,
            "taxes": self.taxes,
            "user_development_fee": self.user_development_fee,
            "convenience_fee": self.convenience_fee,
            "other_charges": self.other_charges,
            "total_fare": self.total_fare,
            "currency": self.currency,
            "availability": self.availability,
            "stops": self.stops,
            "refundability": self.refundability,
            "data_quality_score": self.data_quality_score,
            "is_outlier": self.is_outlier,
            "outlier_method": self.outlier_method,
            "outlier_score": self.outlier_score,
        }
