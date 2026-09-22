from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from backend.app.db.database import Base


class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True, index=True)
    airline_code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    market_share = Column(Float, default=0.0)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "airline_code": self.airline_code,
            "name": self.name,
            "market_share": self.market_share,
            "active": self.active,
        }
