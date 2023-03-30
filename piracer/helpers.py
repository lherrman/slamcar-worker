import logging
import time

from dataclasses import dataclass

from pathlib import Path
from piracer import config as cfg

from donkeycar import Vehicle
from donkeycar.parts import pins

logger = logging.getLogger(__name__)


@dataclass
class DATA_NAMES:
    camera_image = 'cam/image'
    rc_steering = 'user/angle'
    rc_throttle = 'user/throttle'
    tub_record_count = 'tub/num_records'
    recorder_count = 'recorder/num_records'
    user_mode = 'user/mode'
    recording = 'recording'
    selected_ai_model = 'pilot/model'
    # not used, but donkeycar has some use for these
    web_buttons = 'web/buttons'


def add_steering_trottle(v: Vehicle):
    from donkeycar.parts.actuator import (
        PWMSteering,
        PWMThrottle,
        PulseController,
    )

    steering_controller = PulseController(
        pwm_pin=pins.pwm_pin_by_id(cfg.PWM_STEERING_PIN),
        pwm_scale=cfg.PWM_STEERING_SCALE,
        pwm_inverted=cfg.PWM_STEERING_INVERTED,
    )

    steering = PWMSteering(
        controller=steering_controller,
        left_pulse=cfg.STEERING_LEFT_PWM,
        right_pulse=cfg.STEERING_RIGHT_PWM,
    )

    throttle_controller = PulseController(
        pwm_pin=pins.pwm_pin_by_id(cfg.PWM_THROTTLE_PIN),
        pwm_scale=cfg.PWM_THROTTLE_SCALE,
        pwm_inverted=cfg.PWM_THROTTLE_INVERTED,
    )
    
    throttle = PWMThrottle(
        controller=throttle_controller,
        max_pulse=cfg.THROTTLE_FORWARD_PWM,
        zero_pulse=cfg.THROTTLE_STOPPED_PWM,
        min_pulse=cfg.THROTTLE_REVERSE_PWM,
    )

    v.add(steering, inputs=[DATA_NAMES.rc_steering], threaded=True)
    v.add(throttle, inputs=[DATA_NAMES.rc_throttle], threaded=True)



def add_controller(v: Vehicle, logging: bool = False):
    from piracer.parts.receiver import RCReceiver
    ctr = RCReceiver(cfg, logging)
    v.add(
        ctr,
        inputs=[
            DATA_NAMES.user_mode,
            DATA_NAMES.recording,
        ],
        outputs=[
            DATA_NAMES.rc_steering,
            DATA_NAMES.rc_throttle,
            DATA_NAMES.user_mode,
            DATA_NAMES.recording,
        ],
        threaded=False,
    )

def add_server_controller(v: Vehicle, logging: bool = False):
    from piracer.parts.receiver import ServerReceiver
    ctr = ServerReceiver(cfg, logging)
    v.add(
        ctr,
        inputs=[
            DATA_NAMES.user_mode,
        ],
        outputs=[
            DATA_NAMES.rc_steering,
            DATA_NAMES.rc_throttle,
            DATA_NAMES.user_mode,
        ],
        threaded=False,
    )

class VehicleSingleUpdate(Vehicle):
    """
    This allows us to run our own loop in the main function,
    so switching between slef driving and recording is easier.
    """

    def _warmup(self, rate_hz=10):
        self.on = True

        # print a nice startup banner
        from pyfiglet import Figlet
        f = Figlet(font='big')
        print(f.renderText('SlamCar'))
        print("SlamCar Worker")

        for entry in self.parts:
            if entry.get('thread'):
                # start the update thread
                entry.get('thread').start()

        # wait until the parts warm up.
        logger.info('Starting vehicle at {} Hz'.format(rate_hz))

    def single_update(self, loop_count, rate_hz=10, verbose=False):
        """
        rate_hz : int
            The max frequency that the drive loop should run. The actual
            frequency may be less than this if there are many blocking parts.
        verbose: bool
            If debug output should be printed into shell
        """
        start_time = time.time()

        self.update_parts()

        # sleep_time = 1.0 / rate_hz - (time.time() - start_time)
        # if sleep_time > 0.0:
        #     time.sleep(sleep_time)
        # else:
        #     # print a message when could not maintain loop rate.
        #     if verbose:
        #         logger.info(
        #             'WARN::Vehicle: jitter violation in vehicle loop '
        #             'with {0:4.0f}ms'.format(abs(1000 * sleep_time))
        #         )

        if verbose and loop_count % 200 == 0:
            self.profiler.report()
