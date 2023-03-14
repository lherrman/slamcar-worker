import os
from pathlib import Path


HAVE_CONSOLE_LOGGING = True
LOGGING_LEVEL = 'INFO'                     # (Python logging level) 'NOTSET' / 'DEBUG' / 'INFO' / 'WARNING' / 'ERROR' / 'FATAL' / 'CRITICAL'
LOGGING_FORMAT = 'piracer :: %(message)s'  # (Python logging format - https://docs.python.org/3/library/logging.html#formatter-objects

# FOR PGPIO
PI_GPIO_HOST = 'localhost'
PI_GPIO_PORT = 8888

# For RCReceiver
STEERING_RC_GPIO = 26
THROTTLE_RC_GPIO = 19
GEAR_RC_GPIO = 13

# currently unused
DATA_WIPER_RC_GPIO = 20

PIGPIO_STEERING_MID = 1500
PIGPIO_MAX_FORWARD = 2000
PIGPIO_STOPPED_PWM = 1500
PIGPIO_MAX_REVERSE = 1000
AUTO_RECORD_ON_THROTTLE = False
PIGPIO_INVERT = False
PIGPIO_JITTER = 0.025

# for Vehicle
STEERING_OFFSET = 10
# write out the percentage in decimal. E.g. for a max throttle of 50%, set the value to 0.5.
THROTTLE_FACTOR = 0.01

# Temp replacement of shelved config
STEERING_PWM = 300
THROTTLE_PWM = 300

PWM_STEERING_PIN = 'PCA9685.1:40.0'   # PWM output pin for steering servo
PWM_STEERING_SCALE = 1.0   # used to compensate for PWM frequency differents from 60hz; NOT for adjusting steering range
PWM_STEERING_INVERTED = False   # True if hardware requires an inverted PWM pulse
PWM_THROTTLE_PIN = 'PCA9685.1:40.1'   # PWM output pin for ESC
PWM_THROTTLE_SCALE = 1.0   # used to compensate for PWM frequence differences from 60hz; NOT for increasing/limiting speed
PWM_THROTTLE_INVERTED = False   # True if hardware requires an inverted PWM pulse
STEERING_LEFT_PWM = 550     # pwm value for full left steering
STEERING_RIGHT_PWM = 200    # pwm value for full right steering
THROTTLE_FORWARD_PWM = 430  # pwm value for max forward throttle
THROTTLE_STOPPED_PWM = 400  # pwm value for no movement
THROTTLE_REVERSE_PWM  = 370 # pwm value for max reverse throttle



# for Camera Stream
CAMERA_ENABLE = True
CAMERA_RESOLUTION = (1640, 1232)
CAMERA_FRAMERATE = 20
CAMERA_PORT = 5001
CAMERA_HOST = '10.0.0.21'


# for AI UNUSED
RATE_HZ = 20
FPS_DEBUG_INTERVAL = 10

# unused settings, because we hard coded this!
CONTROLLER_TYPE = 'pigpio_rc'
