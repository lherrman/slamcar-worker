import json

import cv2

from datetime import datetime


class DonkeyRecorder:
    """
    A Donkey part, which can write records to the datastore.
    """

    def __init__(self, base_path, inputs=[], types=[]):
        from piracer.helpers import DATA_NAMES

        self.base_path = base_path

        self.inputs = inputs
        self.types = types
        assert (
            DATA_NAMES.recording in self.inputs
        ), 'recording status is a required input'
        assert (
            DATA_NAMES.camera_image in self.inputs
        ), 'images is a required input'
        assert (
            DATA_NAMES.rc_throttle in self.inputs
        ), 'throttle is a required input'
        assert (
            DATA_NAMES.rc_steering in self.inputs
        ), 'steering is a required input'
        self.recording_started = False
        self.record_count = 0

    def initialize_new_recording(self):
        now = datetime.now()
        self.out_path_base = self.base_path / str(now.isoformat())
        self.out_path_base.mkdir(parents=True, exist_ok=True)

    def run(self, *args):
        from piracer.helpers import DATA_NAMES

        assert (
            len(self.inputs) > 3
        ), f'Expected at least three inputs, but only got {len(self.inputs)}'
        assert len(self.inputs) == len(
            args
        ), f'Expected {len(self.tub.inputs)} inputs but received {len(args)}'

        recording_idx = self.inputs.index(DATA_NAMES.recording)
        is_recording = args[recording_idx]
        if is_recording:
            if not self.recording_started:
                self.initialize_new_recording()
                self.recording_started = True
            self._write_record(values=args)
        else:
            self.recording_started = False
        return

    def shutdown(self):
        pass

    def _write_record(self, values):
        from piracer.helpers import DATA_NAMES

        self.record_count += 1

        now = datetime.now()
        iso_date = str(now.isoformat())

        steering_idx = self.inputs.index(DATA_NAMES.rc_steering)
        throttle_idx = self.inputs.index(DATA_NAMES.rc_throttle)
        steering, throttle = values[steering_idx], values[throttle_idx]

        image_idx = self.inputs.index(DATA_NAMES.camera_image)
        image = values[image_idx]

        img_destination = self.out_path_base / f'{iso_date}.png'
        log_destination = self.out_path_base / f'{iso_date}.json'

        cv2.imwrite(str(img_destination), image)

        with open(log_destination, 'w', encoding='utf-8') as f:
            data = {
                'timestamp': str(now),
                'steering': steering,
                'throttle': throttle,
            }
            f.write(json.dumps(data))
