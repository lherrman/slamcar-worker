import socket
import cv2
import time

from picamera2 import Picamera2
import threading

class CameraStream():
    def __init__(self, host, port, frame_delta_time = 0.1, size=(864, 648)):
        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.camera = Picamera2()
        self.frame_delta_time = frame_delta_time
        self.terminate = False
        self.thread = None

        config = self.camera.create_still_configuration()
        config['main']['size'] = size
        self.camera.configure(config)

        print(f"Connecting Video to {self.host}:{self.port}")
        self.socket.connect((self.host, self.port))
        print("Video Connected.")
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

    def send(self, data):
        self.socket.send(data)

    def send_image(self, image):
        SEPARATOR = "<SEPARATOR>"
        BUFFER_SIZE = 4096

        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()

        filesize = len(image_bytes)

        # send filesize
        self.socket.send(f"{filesize}".encode())

        # send image bytes
        for i in range(0, len(image_bytes), BUFFER_SIZE):
            self.socket.send(image_bytes[i:i+BUFFER_SIZE])

        print(f"[+] Sent {filesize} bytes).")

    def run(self):
        while not self.terminate:
            image = self.camera.capture_array()
            self.send_image(image)
            time.sleep(self.frame_delta_time)


if __name__ == '__main__':
    stream = CameraStream('10.0.0.21', 5001, frame_delta_time=0.05)
    stream.start()

    while True:
        time.sleep(5)

    

