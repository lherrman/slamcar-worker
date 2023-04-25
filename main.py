import time
import logging
import traceback

from piracer import config as cfg
from piracer.helpers import (
    add_controller,
    add_server_controller,
    add_steering_trottle,
    VehicleSingleUpdate,
)
from piracer.config import Config as dcfg
from piracer.parts.camera_stream import CameraStream
from piracer.parts.actuator import PWMThrottle


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


def create_vehicle() -> VehicleSingleUpdate:
    vehicle = VehicleSingleUpdate()
    #add_controller(vehicle, logging=False)       # RC Remote Control Receiver
    add_server_controller(vehicle, logging=dcfg.get("console_logging")) # Server Remote Control Receiver
    add_steering_trottle(vehicle)                 # Steering and Throttle Control
    return vehicle


def monitor_config_changes(vehicle, config):
    '''
    If the config changes, we need to restart the vehicle
    '''
    if config != dcfg.get("car_parameters"):
                    config = dcfg.get("car_parameters")
                    vehicle.stop()
                    del vehicle
                    vehicle = create_vehicle()
                    vehicle._warmup(rate_hz=cfg.RATE_HZ)

def main():
    
    if dcfg.get("console_logging"):
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)

    if cfg.CAMERA_ENABLE:
        camera_stream = CameraStream(cfg.CAMERA_HOST, 
                                     cfg.CAMERA_PORT, 
                                     frame_delta_time=0.01, 
                                     size=cfg.CAMERA_RESOLUTION)
        camera_stream.start()

    while True:
        vehicle = create_vehicle()

        vehicle._warmup(rate_hz=cfg.RATE_HZ)
        loop_count = 0

        config = dcfg.get("car_parameters")
        try:
            while True:
                vehicle.single_update(
                    loop_count=loop_count,
                    rate_hz=cfg.RATE_HZ,
                    verbose=False)
                loop_count += 1

                monitor_config_changes(vehicle, config)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
        finally:
            logging.info('stopping vehicle')
            vehicle.stop()
            if cfg.CAMERA_ENABLE:
                camera_stream.stop()
            

if __name__ == '__main__':
    main()
    
