import logging

logger = logging.getLogger(__name__)

from piracer.data_persistence import scfg


class WebAPIValueGetter:
    def __init__(self):
        print('Starting Donkey Value Getter')
        self.mode = scfg.mode
        self.recording = scfg.is_recording
        self.selected_ai_model = scfg.selected_ai_model

    def update(self):
        """Start the API Server."""
        self.mode = scfg.mode
        self.recording = scfg.is_recording
        self.selected_ai_model = scfg.selected_ai_model
        return self.mode, self.recording, self.selected_ai_model

    def run_threaded(self):
        self.update()
        return self.mode, self.recording, self.selected_ai_model

    def run(self, *args, **kwargs):
        return self.run_threaded(*args, **kwargs)

    def shutdown(self):
        pass
