import socket
import cv2
import time
import zmq
from picamera2 import Picamera2
import threading
from PIL import Image

class CameraStream():
    def __init__(self, host, port, frame_delta_time = 0.1, size=(864, 648)):
        self.host = host
        self.port = port

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{self.host}:{self.port}")

        self.camera = Picamera2()
        self.frame_delta_time = frame_delta_time
        self.terminate = False
        self.thread = None

        # Configure the camera
        config = self.camera.create_still_configuration()
        config['main']['size'] = size
        self.camera.configure(config)
        self.camera.start()

    def __del__(self):
        self.stop()

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.terminate = True
        self.socket.close()
        self.camera.stop()

    def send_image(self, image):
            try:
                # Convert the image to bytes and prepend the size of the message
                _, buffer = cv2.imencode('.jpg', image)
                img_bytes = buffer.tobytes()
                message = len(img_bytes).to_bytes(4, byteorder='big') + img_bytes

                # Send the message to the server and wait for a response
                self.socket.send(message)
                response = self.socket.recv()
                return response == b'OK'
            except:
                return False

    def run(self):
        while not self.terminate:
            image = self.camera.capture_array()
            self.send_image(image)
            time.sleep(self.frame_delta_time)


# if __name__ == '__main__':
#     stream = CameraStream('10.0.0.21', 5001, frame_delta_time=0.5)
#     stream.start()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         stream.stop()


    

