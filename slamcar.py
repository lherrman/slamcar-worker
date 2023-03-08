
import pigpio
import config as cfg
from parts.receiver import RCReceiver
import time

if __name__ == '__main__':
    rc = RCReceiver(cfg, debug=True)

    for i in range(10):
        print(rc.signals)
        time.sleep(0.1)