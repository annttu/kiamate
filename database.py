from sqlalchemy import create_engine, Column, Integer, DateTime, \
     ForeignKey, Float, UniqueConstraint, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB

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


class Status(Model):
    __tablename__ = 'status'

    id = Column('id', postgresql.BIGINT, primary_key=True, nullable=False, unique=True)
    car_id = Column('car_id', Integer, ForeignKey('car.id'), nullable=False)
    odometer = Column('odo', Float, nullable=True)
    car_battery_percentage = Column('car_battery_percentage', Integer, nullable=True)  # 12V battery
    engine_is_running = Column('engine_is_running', Boolean, nullable=True)
    ev_charge_port_door_is_open = Column('ev_charge_port_door_is_open', Boolean, nullable=True)
    smart_key_battery_warning_is_on = Column('smart_key_battery_warning_is_on', Boolean, nullable=True)
    washer_fluid_warning_is_on = Column('washer_fluid_warning_is_on', Boolean, nullable=True)
    brake_fluid_warning_is_on = Column('brake_fluid_warning_is_on', Boolean, nullable=True)
    air_control_is_on = Column('air_control_is_on', Boolean, nullable=True)
    defrost_is_on = Column('defrost_is_on', Boolean, nullable=True)
    steering_wheel_heater_is_on = Column('steering_wheel_heater_is_on', Boolean, nullable=True)
    back_window_heater_is_on = Column('back_window_heater_is_on', Boolean, nullable=True)
    side_mirror_heater_is_on = Column('side_mirror_heater_is_on', Boolean, nullable=True)
    front_left_seat_status = Column('front_left_seat_status', Boolean, nullable=True)
    front_right_seat_status = Column('front_right_seat_status', Boolean, nullable=True)
    rear_left_seat_status = Column('rear_left_seat_status', Boolean, nullable=True)
    rear_right_seat_status = Column('rear_right_seat_status', Boolean, nullable=True)
    is_locked = Column('is_locked', Boolean, nullable=True)
    front_left_door_is_open = Column('front_left_door_is_open', Boolean, nullable=True)
    front_right_door_is_open = Column('front_right_door_is_open', Boolean, nullable=True)
    back_left_door_is_open = Column('back_left_door_is_open', Boolean, nullable=True)
    back_right_door_is_open = Column('back_right_door_is_open', Boolean, nullable=True)
    trunk_is_open = Column('trunk_is_open', Boolean, nullable=True)
    hood_is_open = Column('hood_is_open', Boolean, nullable=True)
    front_left_window_is_open = Column('front_left_window_is_open', Boolean, nullable=True)
    front_right_window_is_open = Column('front_right_window_is_open', Boolean, nullable=True)
    back_left_window_is_open = Column('back_left_window_is_open', Boolean, nullable=True)
    back_right_window_is_open = Column('back_right_window_is_open', Boolean, nullable=True)
    tire_pressure_all_warning_is_on = Column('tire_pressure_all_warning_is_on', Boolean, nullable=True)
    tire_pressure_rear_left_warning_is_on = Column('tire_pressure_rear_left_warning_is_on', Boolean, nullable=True)
    tire_pressure_front_left_warning_is_on = Column('tire_pressure_front_left_warning_is_on', Boolean, nullable=True)
    tire_pressure_front_right_warning_is_on = Column('tire_pressure_front_right_warning_is_on', Boolean, nullable=True)
    tire_pressure_rear_right_warning_is_on = Column('tire_pressure_rear_right_warning_is_on', Boolean, nullable=True)
    data = Column('data', JSONB, nullable=False)
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
