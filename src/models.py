from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False) 

    bookings = relationship("Booking", back_populates="user")


class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    type = Column(String)  
    capacity = Column(Integer)
    price = Column(Integer)

    bookings = relationship("Booking", back_populates="resource")
    schedules = relationship("Schedule", back_populates="resource")


class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    resource_id = Column(Integer, ForeignKey('resources.id'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=False)
    is_confirmed = Column(Boolean, default=False)

    user = relationship("User", back_populates="bookings")
    resource = relationship("Resource", back_populates="bookings")


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey('resources.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_blocked = Column(Boolean, default=False)  # Флаг для блокировки ресурса на определенное время

    resource = relationship("Resource", back_populates="schedules")


