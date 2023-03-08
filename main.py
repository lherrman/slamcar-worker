import time
import logging
import traceback

from piracer import config as cfg
from piracer.helpers import (
    add_api_controller,
    add_camera,
    add_controller,
    add_recorder,
    add_steering_trottle,
    add_model_driver,
    add_steering_trottle_calibration,
    VehicleSingleUpdate,
)
from piracer.data_persistence import scfg

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_training_vehicle() -> VehicleSingleUpdate:
    vehicle = VehicleSingleUpdate()
    # since one is the input of the other
    cam = add_camera(vehicle)

    # warmup camera
    while cam.run() is None:
        time.sleep(1)

    api_ctr = add_api_controller(vehicle)
    receiver = add_controller(vehicle)
    steering, throttle = add_steering_trottle(vehicle)
    recorder = add_recorder(vehicle)
    return vehicle


def create_calibration_vehicle() -> VehicleSingleUpdate:
    vehicle = VehicleSingleUpdate()
    api_ctr = add_api_controller(vehicle)
    steering, throttle = add_steering_trottle_calibration(vehicle)
    return vehicle


def create_self_driving_vehicle() -> VehicleSingleUpdate:
    vehicle = VehicleSingleUpdate()
    # order matters, since one is the input of the other
    cam = add_camera(vehicle)

    # warmup camera
    while cam.run() is None:
        time.sleep(1)

    model_driver = add_model_driver(vehicle)
    steering, throttle = add_steering_trottle(vehicle)
    return vehicle


if __name__ == '__main__':
    from piracer.data_persistence import shelve_db

    if cfg.HAVE_CONSOLE_LOGGING:
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)

    # always start in the user loop
    scfg.mode = 'user'
    while True:
        mode = scfg.mode
        if mode == 'user':
            vehicle = create_training_vehicle()
        elif mode == 'self-driving':
            vehicle = create_self_driving_vehicle()
        elif mode == 'calibrating':
            vehicle = create_calibration_vehicle()
        else:
            scfg.mode = 'user'
            continue

        vehicle._warmup(rate_hz=cfg.RATE_HZ)
        loop_count = 0
        try:
            while mode == scfg.mode:
                vehicle.single_update(
                    loop_count=loop_count,
                    rate_hz=cfg.RATE_HZ,
                )   # , verbose=True)
                loop_count += 1
                print(f'loop_count: {loop_count}')
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
        finally:
            logging.info('stopping vehicle')
            vehicle.stop()
