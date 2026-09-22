from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from backend.app.db.database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    route_code = Column(String(20), unique=True, nullable=False, index=True)
    city_pair = Column(String(100), nullable=False)
    passenger_weight = Column(Float, nullable=False, default=0.05)
    route_weight = Column(Float, nullable=False, default=0.05)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "route_code": self.route_code,
            "city_pair": self.city_pair,
            "passenger_weight": self.passenger_weight,
            "route_weight": self.route_weight,
            "active": self.active,
        }
