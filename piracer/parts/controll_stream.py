import time
import zmq
import threading

class ControllStream():
    def __init__(self, host, port, frequency=10):
        self.host = host
        self.port = port

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{self.host}:{self.port}")

        self.frame_delta_time = 1.0 / frequency
        self.terminate = False
        self.thread = None

        self.state = {
            "throttle": 0,
            "steering": 50,
        }
        self.commands = {
            "throttle": 0,
            "steering": 0,
        }
        self.state_lock = threading.Lock()
        self.commands_lock = threading.Lock()

    def __del__(self):
        self.stop()

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.terminate = True
        self.socket.close()

    def _communicate(self):
            '''Send the state to the server and receive the commands'''
            state = self.state.copy()
            try:
                with self.state_lock:
                    state = self.state.copy()

                self.socket.send_json(state)
                response = self.socket.recv_json()
                print(response)

                with self.commands_lock:
                    self.commands = response

                return True
            except:
                return False

    def get_commands(self):
        with self.commands_lock:
            return self.commands

    def run(self):
        while not self.terminate:
            self._communicate()
            time.sleep(self.frame_delta_time)


if __name__ == '__main__':
    controll_stream = ControllStream('10.0.0.21', 5002, frequency=10)
    controll_stream.start()

    try:
        while True:
            time.sleep(0.01)
            print(controll_stream.get_commands())
    except KeyboardInterrupt:
        controll_stream.stop()


    

