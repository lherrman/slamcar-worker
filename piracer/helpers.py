import logging
import time

from dataclasses import dataclass

from pathlib import Path
from piracer import config as cfg

from donkeycar import Vehicle
from donkeycar.parts import pins

from piracer.data_persistence import scfg

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

    dt = cfg.get_pwm_steeering_throttle()
    steering_controller = PulseController(
        pwm_pin=pins.pwm_pin_by_id(dt['PWM_STEERING_PIN']),
        pwm_scale=dt['PWM_STEERING_SCALE'],
        pwm_inverted=dt['PWM_STEERING_INVERTED'],
    )
    steering = PWMSteering(
        controller=steering_controller,
        left_pulse=dt['STEERING_LEFT_PWM'],
        right_pulse=dt['STEERING_RIGHT_PWM'],
    )

    throttle_controller = PulseController(
        pwm_pin=pins.pwm_pin_by_id(dt['PWM_THROTTLE_PIN']),
        pwm_scale=dt['PWM_THROTTLE_SCALE'],
        pwm_inverted=dt['PWM_THROTTLE_INVERTED'],
    )
    throttle = PWMThrottle(
        controller=throttle_controller,
        max_pulse=dt['THROTTLE_FORWARD_PWM'],
        zero_pulse=dt['THROTTLE_STOPPED_PWM'],
        min_pulse=dt['THROTTLE_REVERSE_PWM'],
    )

    v.add(steering, inputs=[DATA_NAMES.rc_steering], threaded=True)
    v.add(throttle, inputs=[DATA_NAMES.rc_throttle], threaded=True)
    return steering, throttle


def add_steering_trottle_calibration(v: Vehicle):
    from donkeycar.parts.actuator import (
        PulseController,
    )
    from piracer.parts.actuator import (
        PWMSteeringCalibrator,
        PWMThrottleCalibrator,
    )

    dt = cfg.get_pwm_steeering_throttle()
    steering_controller = PulseController(
        pwm_pin=pins.pwm_pin_by_id(dt['PWM_STEERING_PIN']),
        pwm_scale=dt['PWM_STEERING_SCALE'],
        pwm_inverted=dt['PWM_STEERING_INVERTED'],
    )
    steering = PWMSteeringCalibrator(
        controller=steering_controller,
    )

    # throttle_controller = PulseController(
    #     pwm_pin=pins.pwm_pin_by_id(dt['PWM_THROTTLE_PIN']),
    #     pwm_scale=dt['PWM_THROTTLE_SCALE'],
    #     pwm_inverted=dt['PWM_THROTTLE_INVERTED'],
    # )
    # throttle = PWMThrottleCalibrator(
    #     controller=throttle_controller,
    # )

    v.add(steering, inputs=[], threaded=True)
    # v.add(throttle, inputs=[], threaded=True)
    return steering, None


def add_api_controller(v: Vehicle):
    from piracer.parts.api_getter import WebAPIValueGetter

    ctr = WebAPIValueGetter()
    v.add(
        ctr,
        inputs=[],
        outputs=[
            DATA_NAMES.user_mode,
            DATA_NAMES.recording,
            DATA_NAMES.selected_ai_model,
        ],
        threaded=True,
    )
    return ctr


def add_controller(v: Vehicle):
    from piracer.parts.receiver import RCReceiver

    ctr = RCReceiver(cfg)
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
    return ctr


def add_camera(v: Vehicle):
    from piracer.parts.camera import VidgearCam

    cam = VidgearCam(
        image_w=cfg.IMAGE_W,
        image_h=cfg.IMAGE_H,
        rate_hz=cfg.RATE_HZ,
        image_stream_location=Path(cfg.IMAGE_STREAM_LOCATION),
    )
    v.add(cam, outputs=[DATA_NAMES.camera_image], threaded=True)
    return cam


def add_recorder(v: Vehicle):
    from piracer.parts.recorder import DonkeyRecorder

    # DATA_NAMES.recording needs to be the first entry!
    recorder = DonkeyRecorder(
        base_path=cfg.UPLOADS_BASE_PATH,
        inputs=[
            DATA_NAMES.recording,
            DATA_NAMES.camera_image,
            DATA_NAMES.rc_steering,
            DATA_NAMES.rc_throttle,
        ],
        types=['bool', 'image_array', 'float', 'float'],
    )

    v.add(
        recorder,
        inputs=[
            DATA_NAMES.recording,
            DATA_NAMES.camera_image,
            DATA_NAMES.rc_steering,
            DATA_NAMES.rc_throttle,
        ],
        # no return value
        outputs=[],
    )
    return recorder


def add_model_driver(v: Vehicle):
    from piracer.parts.self_drive.model_driver import DonkeyModelDriver

    # DATA_NAMES.recording needs to be the first entry!
    model_driver = DonkeyModelDriver(
        inputs=[
            DATA_NAMES.camera_image,
        ],
    )

    v.add(
        model_driver,
        inputs=[
            DATA_NAMES.camera_image,
        ],
        outputs=[
            DATA_NAMES.rc_throttle,
            DATA_NAMES.rc_steering,
        ],
        threaded=False,
    )
    return model_driver


def get_status_info():
    mode = scfg.mode
    selected_ai_model = scfg.selected_ai_model
    return {
        'self_driving': not mode == 'user',
        'training_mode': mode == 'user',
        'calibrating': mode == 'calibrating',
        'model': selected_ai_model,
        'is_recording': scfg.is_recording,
        'current_selected_model': selected_ai_model,
    }


class VehicleSingleUpdate(Vehicle):
    """
    This allows us to run our own loop in the main function,
    so switching between slef driving and recording is easier.
    """

    def _warmup(self, rate_hz=10):
        self.on = True

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

        sleep_time = 1.0 / rate_hz - (time.time() - start_time)
        if sleep_time > 0.0:
            time.sleep(sleep_time)
        else:
            # print a message when could not maintain loop rate.
            if verbose:
                logger.info(
                    'WARN::Vehicle: jitter violation in vehicle loop '
                    'with {0:4.0f}ms'.format(abs(1000 * sleep_time))
                )

        if verbose and loop_count % 200 == 0:
            self.profiler.report()
