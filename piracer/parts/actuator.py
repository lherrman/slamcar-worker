import time
import logging

from piracer.data_persistence import scfg

logger = logging.getLogger(__name__)


class PWMSteeringCalibrator:
    """
    Wrapper over a PWM pulse controller to convert angles to PWM pulses.
    """

    def __init__(self, controller):

        if controller is None:
            raise ValueError(
                'PWMSteering requires a set_pulse controller to be passed'
            )
        set_pulse = getattr(controller, 'set_pulse', None)
        if set_pulse is None or not callable(set_pulse):
            raise ValueError('controller must have a set_pulse method')

        self.controller = controller
        self.pulse = scfg.steering_pwm
        self.running = True
        logger.info('PWM Steering created')

    def update(self):
        while self.running:
            self.controller.set_pulse(self.pulse)

    def run_threaded(self, *args):
        self.pulse = scfg.steering_pwm

    def run(self, *args):
        self.run_threaded()
        self.controller.set_pulse(self.pulse)

    def shutdown(self):
        # set steering straight
        self.pulse = 0
        time.sleep(0.3)
        self.running = False


class PWMThrottleCalibrator:
    """
    Wrapper over a PWM pulse controller
    """

    def __init__(self, controller):

        if controller is None:
            raise ValueError(
                'PWMThrottle requires a set_pulse controller to be passed'
            )
        set_pulse = getattr(controller, 'set_pulse', None)
        if set_pulse is None or not callable(set_pulse):
            raise ValueError('controller must have a set_pulse method')

        self.controller = controller
        self.pulse = scfg.THROTTLE_STOPPED_PWM

        # send zero pulse to calibrate ESC
        logger.info('Init ESC')
        self.controller.set_pulse(scfg.THROTTLE_FORWARD_PWM)
        time.sleep(0.01)
        self.controller.set_pulse(scfg.THROTTLE_REVERSE_PWM)
        time.sleep(0.01)
        self.controller.set_pulse(scfg.THROTTLE_STOPPED_PWM)
        time.sleep(1)
        self.running = True
        logger.info('PWM Throttle created')

    def update(self):
        while self.running:
            self.controller.set_pulse(self.pulse)

    def run_threaded(self):
        throttle = scfg.throttle_pwm
        self.pulse = throttle

    def run(self):
        self.run_threaded()
        self.controller.set_pulse(self.pulse)

    def shutdown(self):
        # stop vehicle
        self.run(0)
        self.running = False
