#!/usr/bin/env python3
from datetime import datetime

import schedule
from hyundai_kia_connect_api import *
import time
import pprint
import logging


import credentials
import database

logger = logging.getLogger("kia-mate")

pp = pprint.PrettyPrinter(indent=4, depth=4, width=80)


def add_or_update_car(vehicle):
    q = database.Car.query.filter(database.Car.api_id == vehicle.id)
    car_obj = q.first()
    if not car_obj:
        print("Creating new car")
        car_obj = database.Car(
            api_id=vehicle.id,
            name=vehicle.name,
            model=vehicle.model,
        )
        database.db_session.add(car_obj)
    if car_obj.name != vehicle.name:
        print("Updating car name")
        car_obj.name = vehicle.name
        database.db_session.add(car_obj)
    database.db_session.commit()
    return car_obj.id


def update_location(car_id, vehicle):
    q = database.Location.query.filter(
        database.Location.car_id == car_id,
        database.Location.time == vehicle.last_updated_at)
    location_obj = q.first()
    if location_obj:
        return
    location_obj = database.Location(
        car_id=car_id,
        lat=vehicle.location_latitude,
        lon=vehicle.location_longitude,
        speed=vehicle.data.get('vehicleLocation', {}).get('speed', {}).get('value', 0),
        heading=vehicle.data.get('vehicleLocation', {}).get('head', 0),
        odo=vehicle.odometer,
        # location_last_updated_at timestamp timezone and date don't match...
        # time=vehicle.location_last_updated_at
        time=vehicle.last_updated_at
    )
    database.db_session.add(location_obj)
    database.db_session.commit()


def update_ev_battery(car_id, vehicle):
    q = database.EVBattery.query.filter(
        database.EVBattery.car_id == car_id,
        database.EVBattery.time == vehicle.last_updated_at)
    db_obj = q.first()
    if db_obj:
        return
    db_obj = database.EVBattery(
        car_id=car_id,
        battery_charging=int(vehicle.ev_battery_is_charging),
        battery_percent=vehicle.ev_battery_percentage,
        time=vehicle.last_updated_at,
    )
    database.db_session.add(db_obj)
    database.db_session.commit()


def update_ev_range(car_id, vehicle):
    q = database.EVRange.query.filter(
        database.EVRange.car_id == car_id,
        database.EVRange.time == vehicle.last_updated_at)
    db_obj = q.first()
    if db_obj:
        return
    db_obj = database.EVRange(
        car_id=car_id,
        ev_range=int(vehicle.ev_driving_range),
        air_temperature=vehicle.air_temperature,
        time=vehicle.last_updated_at,
    )
    database.db_session.add(db_obj)
    database.db_session.commit()


def update_status(car_id, vehicle):
    q = database.Status.query.filter(
        database.Status.car_id == car_id,
        database.Status.time == vehicle.last_updated_at)
    db_obj = q.first()
    if db_obj:
        return
    db_obj = database.Status(
        car_id=car_id,
        odometer=vehicle.odometer,
        car_battery_percentage=vehicle.car_battery_percentage,
        engine_is_running=vehicle.engine_is_running,
        ev_charge_port_door_is_open=vehicle.ev_charge_port_door_is_open,
        smart_key_battery_warning_is_on=vehicle.smart_key_battery_warning_is_on,
        washer_fluid_warning_is_on=vehicle.washer_fluid_warning_is_on,
        brake_fluid_warning_is_on=vehicle.brake_fluid_warning_is_on,
        air_control_is_on=vehicle.air_control_is_on,
        defrost_is_on=vehicle.defrost_is_on,
        steering_wheel_heater_is_on=vehicle.steering_wheel_heater_is_on,
        back_window_heater_is_on=vehicle.back_window_heater_is_on,
        side_mirror_heater_is_on=vehicle.side_mirror_heater_is_on,
        front_left_seat_status=vehicle.front_left_seat_status,
        front_right_seat_status=vehicle.front_right_seat_status,
        rear_left_seat_status=vehicle.rear_left_seat_status,
        rear_right_seat_status=vehicle.rear_right_seat_status,
        is_locked=vehicle.is_locked,
        front_left_door_is_open=vehicle.front_left_door_is_open,
        front_right_door_is_open=vehicle.front_right_door_is_open,
        back_left_door_is_open=vehicle.back_left_door_is_open,
        back_right_door_is_open=vehicle.back_right_door_is_open,
        trunk_is_open=vehicle.trunk_is_open,
        hood_is_open=vehicle.hood_is_open,
        front_left_window_is_open=vehicle.front_left_window_is_open,
        front_right_window_is_open=vehicle.front_right_window_is_open,
        back_left_window_is_open=vehicle.back_left_window_is_open,
        back_right_window_is_open=vehicle.back_right_window_is_open,
        tire_pressure_all_warning_is_on=vehicle.tire_pressure_all_warning_is_on,
        tire_pressure_rear_left_warning_is_on=vehicle.tire_pressure_rear_left_warning_is_on,
        tire_pressure_front_left_warning_is_on=vehicle.tire_pressure_front_left_warning_is_on,
        tire_pressure_front_right_warning_is_on=vehicle.tire_pressure_front_right_warning_is_on,
        tire_pressure_rear_right_warning_is_on=vehicle.tire_pressure_rear_right_warning_is_on,
        time=vehicle.last_updated_at,
        data=vehicle.data,
    )
    database.db_session.add(db_obj)
    database.db_session.commit()


def update_daily_stats(car_id, vehicle):
    for stat in vehicle.daily_stats:
        update_daily_stat(car_id=car_id, stat=stat)
    database.db_session.commit()


def update_daily_stat(car_id, stat):
    q = database.DailyStats.query.filter(
        database.DailyStats.car_id == car_id,
        database.DailyStats.time == stat.date)
    db_obj = q.first()
    if not db_obj:

        db_obj = database.DailyStats(
            car_id=car_id,
            total_consumed=stat.total_consumed,
            engine_consumption=stat.engine_consumption,
            climate_consumption=stat.climate_consumption,
            onboard_electronics_consumption=stat.onboard_electronics_consumption,
            battery_care_consumption=stat.battery_care_consumption,
            regenerated_energy=stat.regenerated_energy,
            distance=stat.distance,
            time=stat.date,
        )
    else:
        db_obj.total_consumed = stat.total_consumed
        db_obj.engine_consumption = stat.engine_consumption
        db_obj.climate_consumption = stat.climate_consumption
        db_obj.onboard_electronics_consumption = stat.onboard_electronics_consumption
        db_obj.battery_care_consumption = stat.battery_care_consumption
        db_obj.regenerated_energy = stat.regenerated_energy
        db_obj.distance = stat.distance
    database.db_session.add(db_obj)


def update_daytrip_infos(vehicle_manager):
    for vehicle_id, vehicle in vehicle_manager.vehicles.items():
        try:
            car_id = add_or_update_car(vehicle=vehicle)
        except Exception:
            logger.exception("Failed to store vehicle state")
            continue
        now = datetime.now()
        start_of_day = datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0)
        for stat in vehicle.daily_stats:
            if stat.date < start_of_day:
                try:
                    update_daytrip_info(car_id, vehicle, vehicle_manager, stat.date)
                except Exception:
                    logger.exception("Failed to store daytrip info")
                    database.db_session.rollback()
                    break
        database.db_session.commit()


def update_daytrip_info(car_id, vehicle, vehicle_manager, day):
    q = database.Trip.query.filter(
        database.Trip.car_id == car_id,
        database.Trip.day == day)
    db_obj = q.first()
    if db_obj:
        return
    # Get stats
    vehicle_manager.update_day_trip_info(vehicle.id, day.strftime("%Y%m%d"))
    for trip in vehicle.day_trip_info.trip_list:
        timestamp = datetime.strptime(trip.hhmmss, "%H%M%S").replace(year=day.year, month=day.month, day=day.day)
        db_obj = database.Trip(
            car_id=car_id,
            drive_time=trip.drive_time,
            idle_time=trip.idle_time,
            distance=trip.distance,
            avg_speed=trip.avg_speed,
            max_speed=trip.max_speed,
            time=timestamp,
            day=day,
        )
        database.db_session.add(db_obj)


def main():
    database.init_db()

    vm = VehicleManager(region=1, brand=1, username=credentials.email, password=credentials.password,
                        pin=credentials.pin)

    # Update previous days trip info twice a day
    schedule.every().day.at("00:30").do(update_daytrip_infos, vm)
    schedule.every().day.at("12:30").do(update_daytrip_infos, vm)

    while True:
        start = time.time()

        try:
            vm.check_and_refresh_token()
            # Forcing update frequently might consume 12v battery.
            # vm.check_and_force_update_vehicles(force_refresh_interval=60)
            vm.update_all_vehicles_with_cached_state()
        except Exception:
            logger.exception("Failed to update vehicle states")

        for vehicle_id, vehicle in vm.vehicles.items():
            pprint.pprint(vehicle)
            print(vehicle.id, vehicle.name)
            try:
                car_id = add_or_update_car(vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle state")
                database.db_session.rollback()
                continue
            try:
                update_location(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle location")
                database.db_session.rollback()
            try:
                update_ev_battery(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle ev battery status")
                database.db_session.rollback()
            try:
                update_ev_range(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle ev range")
                database.db_session.rollback()
            try:
                update_status(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle status")
                database.db_session.rollback()
            try:
                update_daily_stats(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle daily stats")
                database.db_session.rollback()

        schedule.run_pending()

        time.sleep(int(start + 900 - time.time()))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
