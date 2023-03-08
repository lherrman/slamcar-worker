import sys
import logging

import onnxruntime as ort

from pathlib import Path
from torchvision import transforms

from piracer.data_persistence import scfg
from donkeycar.utils import arr_to_img

convert_tensor = transforms.ToTensor()
logger = logging.getLogger(__name__)


def create_ort_session(model_path):
    ort_sess = ort.InferenceSession(model_path)
    return ort_sess


LAST_ACTIVE_MODEL = ''
ORT_SESSION = None
PREDICTION_FUNCTION = None


def predict_next_input(image):
    name = Path(LAST_ACTIVE_MODEL).stem
    model = Path(LAST_ACTIVE_MODEL) / f'{name}.onnx'
    global ORT_SESSION
    if ORT_SESSION is None:
        print(f'loading learner from {model}')
        ORT_SESSION = create_ort_session(f'{model}')
    tensor_img = convert_tensor(image).unsqueeze(0).numpy()
    # tensor_img = convert_tensor(image).numpy()
    result = ORT_SESSION.run(None, {'image': tensor_img})
    throttle_data, steering_data = result[0][0]
    return float(throttle_data), float(steering_data)


def predict_next_image(image):
    return predict_next_input(image)


def unload_prediction_function():
    global LAST_ACTIVE_MODEL, ORT_SESSION, PREDICTION_FUNCTION
    ORT_SESSION = None
    PREDICTION_FUNCTION = None

    try:
        del override_driving
    except Exception as e:
        logger.error(e)
    try:
        del sys.modules['override_driving']
    except Exception as e:
        logger.error(e)
    try:
        sys.path.remove(str(LAST_ACTIVE_MODEL))
    except Exception as e:
        logger.error(e)


def get_predictor_function():
    global LAST_ACTIVE_MODEL, ORT_SESSION, PREDICTION_FUNCTION

    current_selected_model = scfg.selected_ai_model

    if not current_selected_model:
        logger.error('No active model found')
        scfg.mode = 'user'

    selected_model_folder = Path(current_selected_model)

    # switch model, unset the poor mans "cache"
    if str(selected_model_folder) != str(LAST_ACTIVE_MODEL):
        unload_prediction_function()

    if PREDICTION_FUNCTION is not None:
        return PREDICTION_FUNCTION

    if selected_model_folder:
        if not selected_model_folder.exists():
            logger.error(
                'self_driving_path',
                f'Path to model {selected_model_folder} not found',
            )
            raise ValueError(
                f'Path to model {selected_model_folder} not found'
            )

        # import function from custom function, if it exists
        try:
            LAST_ACTIVE_MODEL = selected_model_folder
            sys.path.insert(1, str(selected_model_folder))
            import override_driving

            PREDICTION_FUNCTION = override_driving.predict_throttle_speed
        except ImportError:
            unload_prediction_function()
            PREDICTION_FUNCTION = predict_next_image
        return PREDICTION_FUNCTION


class DonkeyModelDriver:
    def __init__(self, inputs=[]):
        from piracer.helpers import DATA_NAMES

        self.inputs = inputs
        assert (
            DATA_NAMES.camera_image in self.inputs
        ), 'images is a required input'
        try:
            self.predictor_function = get_predictor_function()
        except Exception:
            scfg.mode = 'user'
            raise

    def run(self, *args):
        from piracer.helpers import DATA_NAMES

        assert (
            len(self.inputs) == 1
        ), f'Expected one input, an image, but got {len(self.inputs)}'
        assert len(self.inputs) == len(
            args
        ), f'Expected {len(self.inputs)} inputs but received {len(args)}'

        image_idx = self.inputs.index(DATA_NAMES.camera_image)
        img = arr_to_img(args[image_idx])
        throttle_data, steering_data = self.predictor_function(img)
        if scfg.mode == 'user':
            return 0.0, 0.0
        return throttle_data, steering_data

    def shutdown(self):
        pass
