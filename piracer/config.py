import os
from os import environ
from pathlib import Path

from piracer.data_persistence import scfg


def get_value(env_var_name: str, default_value):
    return environ.get(env_var_name, default_value)


HAVE_CONSOLE_LOGGING = True
LOGGING_LEVEL = 'INFO'          # (Python logging level) 'NOTSET' / 'DEBUG' / 'INFO' / 'WARNING' / 'ERROR' / 'FATAL' / 'CRITICAL'
LOGGING_FORMAT = 'piracer :: %(message)s'  # (Python logging format - https://docs.python.org/3/library/logging.html#formatter-objects


# FOR PGPIO
PI_GPIO_HOST = str(get_value('PI_GPIO_HOST', 'localhost'))
PI_GPIO_PORT = int(get_value('PI_GPIO_PORT', 8888))

# For RCReceiver
STEERING_RC_GPIO = int(get_value('STEERING_RC_GPIO', 26))
THROTTLE_RC_GPIO = int(get_value('THROTTLE_RC_GPIO', 19))
GEAR_RC_GPIO = int(get_value('GEAR_RC_GPIO', 13))

# currently unused
DATA_WIPER_RC_GPIO = int(get_value('DATA_WIPER_RC_GPIO', 20))

PIGPIO_STEERING_MID = int(get_value('PIGPIO_STEERING_MID', 1500))
PIGPIO_MAX_FORWARD = int(get_value('PIGPIO_MAX_FORWARD', 2000))
PIGPIO_STOPPED_PWM = int(get_value('PIGPIO_STOPPED_PWM', 1500))
PIGPIO_MAX_REVERSE = int(get_value('PIGPIO_MAX_REVERSE', 1000))
AUTO_RECORD_ON_THROTTLE = False
PIGPIO_INVERT = bool(get_value('PIGPIO_INVERT', False))
PIGPIO_JITTER = float(get_value('PIGPIO_JITTER', 0.025))

# for Vehicle
STEERING_OFFSET = int(get_value('STEERING_OFFSET', 10))
# write out the percentage in decimal. E.g. for a max throttle of 50%, set the value to 0.5.
THROTTLE_FACTOR = float(get_value('THROTTLE_FACTOR', 1.0))

# for Software
UPLOADS_BASE_PATH = Path(get_value('UPLOADS_BASE_PATH', '/home/pi/uploads'))
SELF_DRIVING_MODEL_PATH = get_value('SELF_DRIVING_MODEL_PATH', None)
MODEL_FOLDER_PATH = UPLOADS_BASE_PATH / 'models'
IMAGE_STREAM_LOCATION = get_value(
    'IMAGE_STREAM_LOCATION', '/tmp/image-stream/'
)

# IMAGE_W = 320
# IMAGE_H = 240

#  this gives distorted images!
# IMAGE_W = 240
# IMAGE_H = 180

IMAGE_W = 160
IMAGE_H = 120

RATE_HZ = 20
FPS_DEBUG_INTERVAL = 10

def get_pwm_steeering_throttle():
    return {
        'PWM_STEERING_PIN': 'PCA9685.1:40.0',  # PWM output pin for steering servo
        'PWM_STEERING_SCALE': 1.0,  # used to compensate for PWM frequency differents from 60hz; NOT for adjusting steering range
        'PWM_STEERING_INVERTED': False,  # True if hardware requires an inverted PWM pulse
        'PWM_THROTTLE_PIN': 'PCA9685.1:40.1',  # PWM output pin for ESC
        'PWM_THROTTLE_SCALE': 1.0,  # used to compensate for PWM frequence differences from 60hz; NOT for increasing/limiting speed
        'PWM_THROTTLE_INVERTED': False,  # True if hardware requires an inverted PWM pulse
        'STEERING_LEFT_PWM': scfg.STEERING_LEFT_PWM,  # pwm value for full left steering
        'STEERING_RIGHT_PWM': scfg.STEERING_RIGHT_PWM,  # pwm value for full right steering
        # 'STEERING_LEFT_PWM': 550,  # pwm value for full left steering
        # 'STEERING_RIGHT_PWM': 200,  # pwm value for full right steering
        # disabled setting of throttle, since it almost broke a car :-)
        # 'THROTTLE_FORWARD_PWM': scfg.THROTTLE_FORWARD_PWM,  # pwm value for max forward throttle
        # 'THROTTLE_STOPPED_PWM': scfg.THROTTLE_STOPPED_PWM,  # pwm value for no movement
        # 'THROTTLE_REVERSE_PWM': scfg.THROTTLE_REVERSE_PWM,  # pwm value for max reverse throttle
        'THROTTLE_FORWARD_PWM': 500,  # pwm value for max forward throttle
        'THROTTLE_STOPPED_PWM': 370,  # pwm value for no movement
        'THROTTLE_REVERSE_PWM': 220,  # pwm value for max reverse throttle

    }

WEB_CONTROL_PORT = int(
    os.getenv('WEB_CONTROL_PORT', 8000)
)  # which port to listen on when making a web controller
WEB_INIT_MODE = 'user'              # which control mode to start in. one of user|local_angle|local. Setting local will start in ai mode.

# unused settings, because we hard coded this!
CONTROLLER_TYPE = 'pigpio_rc'
