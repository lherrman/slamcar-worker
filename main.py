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

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

 
def create_vehicle() -> VehicleSingleUpdate:
    vehicle = VehicleSingleUpdate()
    add_controller(vehicle, logging=False)
    add_steering_trottle(vehicle)
    return vehicle

if __name__ == '__main__':

    if cfg.HAVE_CONSOLE_LOGGING:
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)

    stream = CameraStream("10.0.0.21", 5001, frame_delta_time=0.05)
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
            stream.stop()
