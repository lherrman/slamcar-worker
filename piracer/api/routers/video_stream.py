import time
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from piracer import config as cfg

router = APIRouter()


def frame_generator(path):
    last_name = ''
    while True:
        fname = sorted(list(path.glob('*.jpg')), key=lambda x: int(x.stem))
        if len(fname) > 2:
            file_name = fname[-2]
            if file_name == last_name:
                time.sleep(0.01)
                continue
            last_name = file_name
            # give the image a chance to be fully written to disk
            with open(file_name, 'rb') as im_file:
                im = im_file.read()
            yield b'--frame\r\nContent-Type:image/png\r\n\r\n' + im + b'\r\n'
        else:
            time.sleep(0.01)


@router.get('/video')
async def video():
    """
    Return a async video streaming response.
    """
    return StreamingResponse(
        frame_generator(Path(cfg.IMAGE_STREAM_LOCATION)),
        media_type='multipart/x-mixed-replace; boundary=frame',
    )
