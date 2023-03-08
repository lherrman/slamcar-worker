import cv2
from vidgear.gears import VideoGear
import imutils
from pathlib import Path
from piracer.data_persistence import hsv_cfg
import piracer.config as cfg


def reducer(frame=None, percentage=0, interpolation=cv2.INTER_LANCZOS4):
    if frame is None:
        raise ValueError('[Helper:ERROR] :: Input frame cannot be NoneType!')
    if not (percentage > 0 and percentage < 90):
        raise ValueError(
            '[Helper:ERROR] :: Given frame-size reduction percentage is invalid, Kindly refer docs.'
        )
    if not (isinstance(interpolation, int)):
        raise ValueError(
            '[Helper:ERROR] :: Given interpolation is invalid, Kindly refer docs.'
        )
    (height, width) = frame.shape[:2]
    reduction = ((100 - percentage) / 100) * width
    ratio = reduction / float(width)
    dimensions = (int(reduction), int(height * ratio))
    return cv2.resize(frame, dimensions, interpolation=interpolation)


def write_frame(frame, destination: Path):
    if not destination.exists():
        destination.mkdir(exist_ok=True, parents=True)
    overwrite_images_after = 20
    images = sorted(list(destination.glob('*.jpg')), key=lambda x: int(x.stem))
    if len(images) > overwrite_images_after:
        for im in images[:-overwrite_images_after]:
            im.unlink()
    next_im_name = 0
    if len(images):
        next_im_name = int(images[-1].stem) + 1
    # ready to reduce size later on
    # reducer frames size if you want more performance otherwise comment this line
    frame = reducer(
        frame, percentage=30, interpolation=cv2.INTER_AREA
    )  # reduce frame by 30%
    cv2.imwrite(str(destination / f'{next_im_name}.jpg'), frame)


class VidgearCam:
    def __init__(
        self,
        image_w=160,
        image_h=120,
        iCam=0,
        rate_hz=10,
        image_stream_location:Path = Path(cfg.IMAGE_STREAM_LOCATION),
    ):
        options= {
            'CAP_PROP_FRAME_WIDTH': 640,
            'CAP_PROP_FRAME_HEIGHT': 480,
            'CAP_PROP_FPS': rate_hz,
        }
        self.cap = VideoGear(source=iCam, **options).start()

        self.image_w = image_w
        self.image_h = image_h
        self.frame = None
        self.running = True
        self.image_stream_location = image_stream_location

    def poll(self):
        frame = self.cap.read()
        if frame is not None:
            frame = imutils.resize(frame, width=self.image_w, height=self.image_h)
            self.frame = self.transform_frame(frame=frame)
            if self.image_stream_location is not None:
                write_frame(self.frame, self.image_stream_location)

    def transform_frame(self, frame):
        hsv_limits = hsv_cfg.hsv_limits
        if not hsv_limits:
            return frame

        frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        result = None
        for idx, limit in enumerate(hsv_limits):
            try:
                low_H, low_S, low_V = limit['h_lower'], limit['s_lower'], limit['v_lower']
                high_H, high_S, high_V = limit['h_upper'], limit['s_upper'], limit['v_upper']
            except TypeError as e:
                print(e)
                return frame

            mask = cv2.inRange(frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))
            if idx > 0:
                result = cv2.bitwise_or(result, mask)
            else:
                result = mask

        return cv2.bitwise_and(frame, frame, mask=result)

    def update(self):
        """
        poll the camera for a frame
        """
        while self.running:
            self.poll()

    def run_threaded(self):
        return self.frame

    def run(self):
        self.poll()
        return self.frame

    def shutdown(self):
        self.running = False
        self.cap.stop()
