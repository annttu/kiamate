#!/usr/bin/env python3

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


def main():
    database.init_db()

    vm = VehicleManager(region=1, brand=1, username=credentials.email, password=credentials.password,
                        pin=credentials.pin)

    vm.check_and_refresh_token()

    vm.update_all_vehicles_with_cached_state()

    while True:
        start = time.time()
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
                logger.exception("Failed to store vehicle state")
                database.db_session.rollback()
            try:
                update_ev_battery(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle state")
                database.db_session.rollback()
            try:
                update_ev_range(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle state")
                database.db_session.rollback()
            try:
                update_daily_stats(car_id=car_id, vehicle=vehicle)
            except Exception:
                logger.exception("Failed to store vehicle state")
                database.db_session.rollback()

        time.sleep(int(start + 900 - time.time()))

        try:
            vm.check_and_force_update_vehicles(force_refresh_interval=60)
        except Exception:
            logger.exception("Failed to update vehicle states")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
