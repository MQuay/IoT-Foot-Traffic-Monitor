from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Device(Base):
    __tablename__ = "device"

    id = mapped_column(Integer, primary_key=True)
    device_name: Mapped[str]
    password = mapped_column(String, nullable=True)
    register_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_login: Mapped[datetime] = mapped_column(insert_default=func.now())
    
    def todict(self):
        dict = {
            "id": self.id,
            "device_name": self.device_name,
            "register_date": self.register_date,
            "last_login": self.last_login,
        }
        return dict

class Log(Base):
    __tablename__ = "log"
    
    id = mapped_column(Integer, primary_key=True)
    device_id = mapped_column(ForeignKey("device.id"))
    status: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(insert_default=func.now())

    def todict(self):
        dict = {
            "id": self.id,
            "device_id": self.device_id,
            "status": self.status,
            "timestamp": self.timestamp
        }
        return dict