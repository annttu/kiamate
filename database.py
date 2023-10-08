from sqlalchemy import create_engine, Column, Integer, DateTime, \
     ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy.dialects import postgresql


import credentials

engine = create_engine(credentials.database_uri)
db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def init_db():
    Model.metadata.create_all(bind=engine)


Model = declarative_base(name='Model')
Model.query = db_session.query_property()


class Car(Model): 
    __tablename__ = 'car'
    id = Column('id', Integer, primary_key=True, nullable=False, unique=True)
    api_id = Column('api_id', postgresql.TEXT, nullable=False, unique=True)
    name = Column('name', postgresql.TEXT, nullable=False)
    model = Column('model', postgresql.TEXT, nullable=False)


class Location(Model):
    __tablename__ = 'location'

    id = Column('id', postgresql.BIGINT, primary_key=True, nullable=False, unique=True)
    car_id = Column('car_id', Integer, ForeignKey('car.id'), nullable=False)
    lat = Column('lat', Float, nullable=False)
    lon = Column('lon', Float, nullable=False)
    speed = Column('speed', Integer, nullable=False)
    heading = Column('heading', Integer, nullable=False)
    odo = Column('odo', Float, nullable=True)
    time = Column('time', DateTime(timezone=True), nullable=False)

    UniqueConstraint(car_id, time)


class EVBattery(Model):
    __tablename__ = 'ev_battery'

    id = Column('id', postgresql.BIGINT, primary_key=True, nullable=False, unique=True)
    car_id = Column('car_id', Integer, ForeignKey('car.id'), nullable=False)
    battery_charging = Column('battery_charging', Integer, nullable=False)
    battery_percent = Column('battery_percent', Integer, nullable=False)
    time = Column('time', DateTime(timezone=True), nullable=False)

    UniqueConstraint(car_id, time)


class EVRange(Model):
    __tablename__ = 'ev_range'

    id = Column('id', postgresql.BIGINT, primary_key=True, nullable=False, unique=True)
    car_id = Column('car_id', Integer, ForeignKey('car.id'), nullable=False)
    ev_range = Column('range', Integer, nullable=False)
    air_temperature = Column('air_temperature', Float, nullable=False)
    time = Column('time', DateTime(timezone=True), nullable=False)

    UniqueConstraint(car_id, time)


class DailyStats(Model):
    __tablename__ = 'daily_stats'

    id = Column('id', postgresql.BIGINT, primary_key=True, nullable=False, unique=True)
    car_id = Column('car_id', Integer, ForeignKey('car.id'), nullable=False)
    total_consumed = Column('total_consumed', Integer, nullable=False)
    engine_consumption = Column('engine_consumption', Integer, nullable=False)
    climate_consumption = Column('climate_consumption', Integer, nullable=False)
    onboard_electronics_consumption = Column('onboard_electronics_consumption', Integer, nullable=False)
    battery_care_consumption = Column('battery_care_consumption', Integer, nullable=False)
    regenerated_energy = Column('regenerated_energy', Integer, nullable=False)
    distance = Column('distance', Integer, nullable=False)

    time = Column('time', DateTime(timezone=True), nullable=False)

    UniqueConstraint(car_id, time)


class Trip(Model):
    __tablename__ = 'trip'
    id = Column('id', postgresql.BIGINT, primary_key=True, nullable=False, unique=True)
    car_id = Column('car_id', Integer, ForeignKey('car.id'), nullable=False)
    drive_time = Column('drive_time', Integer, nullable=False)
    idle_time = Column('idle_time', Integer, nullable=False)
    distance = Column('distance', Integer, nullable=False)
    avg_speed = Column('avg_speed', Integer, nullable=False)
    max_speed = Column('max_speed', Integer, nullable=False)
    time = Column('time', DateTime(timezone=True), nullable=False)
    day = Column('day', DateTime(timezone=True), nullable=False)

    UniqueConstraint(car_id, time)
