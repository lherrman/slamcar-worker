from copy import deepcopy
from enum import Enum, EnumMeta

from piracer.data_persistence import shelve_db


class ContainsEnumMeta(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True


class CalibrationType(str, Enum, metaclass=ContainsEnumMeta):
    # not in calibration mode, default
    off = 'off'
    steering_right = 'steering_right'
    steering_left = 'steering_left'
    throttle_forward = 'throttle_forward'
    throttle_stop = 'throttle_stop'
    throttle_reverse = 'throttle_reverse'


class ModeEnum(str, Enum, metaclass=ContainsEnumMeta):
    # not in calibration mode, default
    user = 'user'
    self_driving = 'self_driving'
    calibrating = 'calibrating'


class ShelvedConfig:
    """
    This is a helper to excahnge data akin to a database.
    It seems to be faster than using sqlite.
    """

    def __init__(self):
        self.shelve = shelve_db
        # this is just to initialize the file upon startup
        self.shelve.set('initialized', True)

    def reset(self):
        self.shelve.reset_db()

    @property
    def mode(self):
        """
        can be one of 'user', 'self-driving' or 'calibrating'
        """
        # set default value
        return self.shelve.get('mode', ModeEnum.user.value)

    @mode.setter
    def mode(self, value):
        print('mode change', value)
        assert value in ['user', 'self-driving', 'calibrating'], f"value (currently {value}) must be one of 'user', 'self-driving', 'calibrating'"
        return self.shelve.set('mode', value)

    @property
    def selected_ai_model(self):
        # set default value
        return self.shelve.get('selected_ai_model', '')

    @selected_ai_model.setter
    def selected_ai_model(self, value):
        return self.shelve.set('selected_ai_model', value)

    @property
    def is_recording(self):
        # set default value
        return self.shelve.get('is_recording', False)

    @is_recording.setter
    def is_recording(self, value):
        return self.shelve.set('is_recording', value)

    @property
    def steering_pwm(self):
        # set default value
        return self.shelve.get('steering_pwm', 300)

    @steering_pwm.setter
    def steering_pwm(self, value):
        return self.shelve.set('steering_pwm', value)

    @property
    def throttle_pwm(self):
        # set default value
        return self.shelve.get('throttle_pwm', 300)

    @throttle_pwm.setter
    def throttle_pwm(self, value):
        return self.shelve.set('throttle_pwm', value)

    @property
    def STEERING_LEFT_PWM(self):
        # set default value
        return self.shelve.get('STEERING_LEFT_PWM', 490)

    @STEERING_LEFT_PWM.setter
    def STEERING_LEFT_PWM(self, value):
        return self.shelve.set('STEERING_LEFT_PWM', value)

    @property
    def STEERING_RIGHT_PWM(self):
        # set default value
        return self.shelve.get('STEERING_RIGHT_PWM', 250)

    @STEERING_RIGHT_PWM.setter
    def STEERING_RIGHT_PWM(self, value):
        return self.shelve.set('STEERING_RIGHT_PWM', value)

    @property
    def THROTTLE_FORWARD_PWM(self):
        # set default value
        return self.shelve.get('THROTTLE_FORWARD_PWM', 500)

    @THROTTLE_FORWARD_PWM.setter
    def THROTTLE_FORWARD_PWM(self, value):
        return self.shelve.set('THROTTLE_FORWARD_PWM', value)

    @property
    def THROTTLE_STOPPED_PWM(self):
        # set default value
        return self.shelve.get('THROTTLE_STOPPED_PWM', 370)

    @THROTTLE_STOPPED_PWM.setter
    def THROTTLE_STOPPED_PWM(self, value):
        return self.shelve.set('THROTTLE_STOPPED_PWM', value)

    @property
    def THROTTLE_REVERSE_PWM(self):
        # set default value
        return self.shelve.get('THROTTLE_REVERSE_PWM', 220)

    @THROTTLE_REVERSE_PWM.setter
    def THROTTLE_REVERSE_PWM(self, value):
        return self.shelve.set('THROTTLE_REVERSE_PWM', value)

    @property
    def calibration_dict(self):
        return dict(
            mode=self.mode,
            calibration_type=self.calibration_type,
            steering_pwm=self.steering_pwm,
            throttle_pwm=self.throttle_pwm,
            STEERING_LEFT_PWM=self.STEERING_LEFT_PWM,
            STEERING_RIGHT_PWM=self.STEERING_RIGHT_PWM,
            THROTTLE_FORWARD_PWM=self.THROTTLE_FORWARD_PWM,
            THROTTLE_STOPPED_PWM=self.THROTTLE_STOPPED_PWM,
            THROTTLE_REVERSE_PWM=self.THROTTLE_REVERSE_PWM,
        )

    @property
    def calibration_type(self):
        return self.shelve.get('calibration_type', CalibrationType.off)

    @calibration_type.setter
    def calibration_type(self, value: CalibrationType):
        assert value in CalibrationType
        return self.shelve.set('calibration_type', value)


class HSVConfig:
    """
    HSV Selection Helper
    """

    def __init__(self):
        self.data_location = '/data/hsv_settings.sqlite3'
        self.store = shelve_db
        # this is just to initialize the file upon startup
        self.store.set('initialized', True, location=self.data_location)

    def get_value(self, key, default=None):
        return self.store.get(key, default, location=self.data_location)

    def set_value(self, key, value):
        return self.store.set(key, value, location=self.data_location)

    def reset_db(self):
        return self.store.reset_db(location=self.data_location)

    @property
    def default_hsv_limits(self):
        # don't transform!
        return None

    @property
    def default_blue_hsv_limits(self):
        return dict(
            h_lower=80,
            h_upper=130,
            s_lower=0,
            s_upper=255,
            v_lower=20,
            v_upper=255,
        )

    @property
    def default_green_hsv_limits(self):
        return dict(
            h_lower=45,
            h_upper=70,
            s_lower=125,
            s_upper=255,
            v_lower=40,
            v_upper=255,
        )

    @property
    def default_orange_hsv_limits(self):
        return dict(
            h_lower=10,
            h_upper=25,
            s_lower=0,
            s_upper=255,
            v_lower=20,
            v_upper=255,
        )

    @property
    def available_hsvs(self):
        hsvs = self.get_value('available_hsvs')
        if hsvs:
            return hsvs
        return self.options

    @property
    def options(self):
        options = {}
        options['blue'] = [self.default_blue_hsv_limits]
        options['green'] = [self.default_green_hsv_limits]
        options['orange'] = [self.default_orange_hsv_limits]
        options['blue-green'] = [
            self.default_blue_hsv_limits,
            self.default_green_hsv_limits,
        ]
        options['blue-orange'] = [
            self.default_blue_hsv_limits,
            self.default_orange_hsv_limits,
        ]
        options['green-orange'] = [
            self.default_green_hsv_limits,
            self.default_orange_hsv_limits,            
        ]
        options['blue-green-orange'] = [
            self.default_blue_hsv_limits,
            self.default_green_hsv_limits,
            self.default_orange_hsv_limits,
        ]
        return options

    @available_hsvs.setter
    def available_hsvs(self, options: dict):
        # special case: override preconfigured value.
        # this one is tried and tested for our blue tape :-)
        # is also impossible to delete like this ;-)
        if not options:
            options = self.options
        return self.set_value('available_hsvs', options)

    @property
    def selected_hsv(self):
        return self.get_value('selected_hsv')

    @selected_hsv.setter
    def selected_hsv(self, value: str):
        return self.set_value('selected_hsv', value)

    @property
    def hsv_limits(self):
        selected_hsv = deepcopy(self.selected_hsv)
        if selected_hsv:
            return deepcopy(self.available_hsvs[selected_hsv])


scfg = ShelvedConfig()
hsv_cfg = HSVConfig()
