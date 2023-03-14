import time
import logging
import traceback

from piracer import config as cfg
from piracer.helpers import (
    add_controller,
    add_steering_trottle,
    VehicleSingleUpdate,
)
from piracer.parts.camera_stream import CameraStream
from piracer.parts.actuator import PWMThrottle

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


def add_pwm_throttle(v: VehicleSingleUpdate):
    throttle = PWMThrottle(
        controller=None,
        max_pulse=cfg.THROTTLE_FORWARD_PWM,
        zero_pulse=cfg.THROTTLE_STOPPED_PWM,
        min_pulse=cfg.THROTTLE_REVERSE_PWM,
    )
    v.add(throttle, outputs=['throttle'], threaded=True)

def create_vehicle() -> VehicleSingleUpdate:
    vehicle = VehicleSingleUpdate()
    add_controller(vehicle, logging=False)
    #add_pwm_throttle(vehicle)
    add_steering_trottle(vehicle)
    return vehicle


def main():
    
    if cfg.HAVE_CONSOLE_LOGGING:
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)

    if cfg.CAMERA_ENABLE:
        stream = CameraStream(cfg.CAMERA_HOST, cfg.CAMERA_PORT, frame_delta_time=0.05)
        stream.start()

    while True:
        vehicle = create_vehicle()

        vehicle._warmup(rate_hz=cfg.RATE_HZ)
        loop_count = 0
        try:
            while True:
                vehicle.single_update(
                    loop_count=loop_count,
                    rate_hz=cfg.RATE_HZ,
                )   # , verbose=True)
                loop_count += 1

        except KeyboardInterrupt:
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
        finally:
            logging.info('stopping vehicle')
            vehicle.stop()
            if cfg.CAMERA_ENABLE:
                stream.stop()

if __name__ == '__main__':
    main()
    
