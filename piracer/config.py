import os
from pathlib import Path

# Configuration for static parameters
# Dynamic configuration is stored in the config.json file

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

# Temp replacement of shelved config
STEERING_PWM = 300
THROTTLE_PWM = 300

PWM_STEERING_PIN = 'PCA9685.1:40.0'   # PWM output pin for steering servo
PWM_STEERING_SCALE = 1.0   # used to compensate for PWM frequency differents from 60hz; NOT for adjusting steering range
PWM_STEERING_INVERTED = False   # True if hardware requires an inverted PWM pulse
PWM_THROTTLE_PIN = 'PCA9685.1:40.1'   # PWM output pin for ESC
PWM_THROTTLE_SCALE = 1.0   # used to compensate for PWM frequence differences from 60hz; NOT for increasing/limiting speed
PWM_THROTTLE_INVERTED = False   # True if hardware requires an inverted PWM pulse


# for Camera Stream
CAMERA_ENABLE = True
CAMERA_RESOLUTION = (864, 648)
CAMERA_FRAMERATE = 20
CAMERA_PORT = 5001
CAMERA_HOST = '192.168.59.126'


# for AI UNUSED
RATE_HZ = 60
FPS_DEBUG_INTERVAL = 10

# unused settings, because we hard coded this!
CONTROLLER_TYPE = 'pigpio_rc'


# for the dynamic config
import json
class Config:
    @staticmethod
    def get(key):
        config = json.load(open('config.json', 'r'))
        if key in config:
            return config[key]
        
        for _, conf  in config.items():
            if key in conf:
                return conf[key]
            
        raise KeyError(f'Key {key} not found in config')
        
    @staticmethod
    def set(key, value):
        set_value = value
        # Check if value is a string that can be converted to a number
        if type(value) == str:
            try:
                set_value = float(value)
                if set_value.is_integer():
                    set_value = int(set_value)
            except:
                pass
        config = json.load(open('config.json', 'r'))
        for _, conf  in config.items():
            if key in conf:
                conf[key] = set_value
                json.dump(config, open('config.json', 'w'), indent=2)
                return
            
        raise KeyError(f'Key {key} not found in config')

    @staticmethod
    def add(group, key, value):
        config = json.load(open('config.json', 'r'))
        if group in config:
            if key in config[group]:
                raise KeyError(f'Key {key} already exists in config')
            config[group][key] = value
            json.dump(config, open('config.json', 'w'), indent=2)
            return
        raise KeyError(f'Group {group} not found in config')

    @staticmethod
    def get_groups():
        config = json.load(open('config.json', 'r'))
        return list(config.keys())
    
    @staticmethod
    def get_keys(group):
        config = json.load(open('config.json', 'r'))
        if group in config:
            return list(config[group].keys())
        raise KeyError(f'Group {group} not found in config')
