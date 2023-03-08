import shutil
import pathlib
import tempfile

from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import Response

from piracer.api.zipper import (
    unzip_files,
    zip_files,
    get_folder_names,
    get_folder_from_name,
    get_folder_info,
)
from piracer.api.ip_helper import get_ip_and_stats
from piracer.api.docker_logs import (
    get_container_names,
    get_log_stream_for_container,
)
from piracer.api import models
from piracer.helpers import get_status_info
from piracer import config as cfg
from piracer.data_persistence import scfg, hsv_cfg, CalibrationType, ModeEnum


router = APIRouter()


@router.get('/system/stats', response_model=models.SystemStats)
async def vehicle_system_stats_response():
    """
    Return system stats
    """
    system_stats = get_ip_and_stats()
    return system_stats


@router.get('/stats', response_model=models.StatusInfo)
async def vehicle_local_stats_response():
    """
    Return vehicle status
    """
    info = get_status_info()
    return info


@router.post('/switch-driving-mode', response_model=models.StatusInfo)
async def switch_driving_mode_endpoint():
    """
    switch driving mode (self-driving vs manual)
    """
    if scfg.mode == 'user':
        # this is actually not important, it just needs to be something different
        # than user
        scfg.mode = 'self-driving'
    else:
        scfg.mode = 'user'
    info = get_status_info()
    return info


@router.post('/switch-recording', response_model=models.StatusInfo)
async def flip_recording_switch():
    """
    flip recording switch (on/off)
    """
    scfg.is_recording = not scfg.is_recording
    info = get_status_info()
    return info


@router.get('/calibration/state', response_model=models.VehicleCalibration)
async def calibration_state():
    """
    Return steering/throttle current values
    """
    return scfg.calibration_dict


@router.post(
    '/calibration/set-mode',
    response_model=models.VehicleCalibration,
)
async def set_mode_type(mode: models.VehicleMode):
    """
    set calibration type (steering right, left, throttle forward, stop and reverse)
    """
    if not mode.mode in ModeEnum:
        scfg.mode = 'user'
        return scfg.calibration_dict

    scfg.mode = mode.mode.value
    return scfg.calibration_dict


@router.post(
    '/calibration/set-calibration-type',
    response_model=models.VehicleCalibration,
)
async def set_calibration_type(calibration: models.VehicleCalibrationType):
    """
    set calibration type (steering right, left, throttle forward, stop and reverse)
    """
    if not calibration.calibration_type in [
        CalibrationType.steering_left,
        CalibrationType.steering_right,
        CalibrationType.throttle_forward,
        CalibrationType.throttle_reverse,
        CalibrationType.throttle_stop,
    ]:
        scfg.calibration_type = CalibrationType.off
        return scfg.calibration_dict

    scfg.calibration_type = calibration.calibration_type
    if scfg.calibration_type == CalibrationType.steering_left:
        scfg.steering_pwm = scfg.STEERING_LEFT_PWM
    elif scfg.calibration_type == CalibrationType.steering_right:
        scfg.steering_pwm = scfg.STEERING_RIGHT_PWM
    elif scfg.calibration_type == CalibrationType.throttle_forward:
        scfg.throttle_pwm = scfg.THROTTLE_FORWARD_PWM
    elif scfg.calibration_type == CalibrationType.throttle_reverse:
        scfg.throttle_pwm = scfg.THROTTLE_REVERSE_PWM
    elif scfg.calibration_type == CalibrationType.throttle_stop:
        scfg.throttle_pwm = scfg.THROTTLE_STOPPED_PWM
    return scfg.calibration_dict


@router.post(
    '/calibration/set-steering', response_model=models.VehicleCalibration
)
async def calibrate_steering(pwm: models.VehiclePWM):
    """
    set steering pwm
    """
    set_value = False
    # ignore all not steering related stuff
    if scfg.calibration_type == CalibrationType.steering_left:
        scfg.STEERING_LEFT_PWM = pwm.pwm
        set_value = True
    elif scfg.calibration_type == CalibrationType.steering_right:
        scfg.STEERING_RIGHT_PWM = pwm.pwm
        set_value = True
    if set_value:
        scfg.steering_pwm = pwm.pwm
    return scfg.calibration_dict


@router.post(
    '/calibration/set-throttle', response_model=models.VehicleCalibration
)
async def calibrate_throttle(pwm: models.VehiclePWM):
    """
    set throttle pwm
    """
    set_value = False
    # ignore all not throttle related settings
    if scfg.calibration_type == CalibrationType.throttle_forward:
        scfg.THROTTLE_FORWARD_PWM = pwm.pwm
        set_value = True
    elif scfg.calibration_type == CalibrationType.throttle_reverse:
        scfg.THROTTLE_REVERSE_PWM = pwm.pwm
        set_value = True
    elif scfg.calibration_type == CalibrationType.throttle_stop:
        scfg.THROTTLE_STOPPED_PWM = pwm.pwm
        set_value = True
    if set_value:
        scfg.throttle_pwm = pwm.pwm
    return scfg.calibration_dict


@router.get('/recordings/list', response_model=list[models.RecordingFolder])
async def list_recording_folders():
    """
    List of recording folders
    """
    return get_folder_names(exclude_names=['models'])


@router.get('/recordings/download/{path}')
async def download_records_folder(path: str):
    """
    return requested directory
    """
    folder = get_folder_info(
        get_folder_from_name(path),
        download_link_base='/api/recordings/download/',
    )
    out_zip_name = f"{folder['name']}.zip"
    zip_data = zip_files(pathlib.Path(folder['path']), folder['name'])
    headers = {'Content-Disposition': 'attachment; filename=%s' % out_zip_name}
    resp = Response(
        zip_data.getvalue(),
        media_type='application/x-zip-compressed',
        headers=headers,
    )
    return resp


@router.delete('/recordings/remove')
async def delete_records_folder(folder: models.RecordingFolder):
    """
    return requested directory
    """
    if str(cfg.UPLOADS_BASE_PATH) in str(folder.path):
        shutil.rmtree(folder.path)
        return {'ok': True}
    raise FileNotFoundError(f'{folder.path} is invalid')


@router.get('/models', response_model=list[models.ModelFolder])
async def models_list():
    """
    get list of available models.
    """
    return get_folder_names(
        cfg.UPLOADS_BASE_PATH / 'models',
        download_link_base='/api/models/download/',
    )


@router.post('/upload-model', response_model=models.StatusInfo)
async def upload_model(file: UploadFile):
    """
    upload model file / zip
    """

    def create_dir(file):
        folder_name = pathlib.Path(file.filename).stem
        upload_destination = pathlib.Path(cfg.MODEL_FOLDER_PATH) / folder_name
        upload_destination.mkdir(exist_ok=True, parents=True)
        return upload_destination

    await file.seek(0)

    if file.filename.endswith('.zip'):
        with tempfile.NamedTemporaryFile(suffix='.zip') as tmp_file:
            tmp_file.write(await file.read())
            tmp_file.flush()
            tmp_file.seek(0)
            try:
                upload_destination = create_dir(file)
                unzip_files(tmp_file.name, upload_destination)
            except FileNotFoundError as err:
                shutil.rmtree(upload_destination)
                raise HTTPException(status_code=404, detail=str(err))

    elif file.filename.endswith('.onnx'):
        upload_destination = create_dir(file)
        dest_file_path = upload_destination / file.filename
        file.seek(0)
        with open(dest_file_path, 'wb') as dest_file:
            dest_file.write(await file.read())
    else:
        HTTPException(status_code=404, detail='invalid file provided')

    info = get_status_info()
    return info


@router.get('/models/download/{path}')
async def download_model_folder(path: str):
    """
    return requested directory
    """
    absolute_path = cfg.MODEL_FOLDER_PATH
    folder = get_folder_info(
        absolute_path / path, download_link_base='/api/models/download/'
    )
    out_zip_name = f"{folder['name']}.zip"
    zip_data = zip_files(pathlib.Path(folder['path']), '.')
    headers = {'Content-Disposition': 'attachment; filename=%s' % out_zip_name}
    resp = Response(
        zip_data.getvalue(),
        media_type='application/x-zip-compressed',
        headers=headers,
    )
    return resp


@router.post('/models/activate', response_model=models.StatusInfo)
async def activate_model(folder: models.ModelFolder):
    """
    activate model for self driving
    """
    scfg.selected_ai_model = folder.path

    info = get_status_info()
    return info


@router.delete('/models/remove')
async def delete_model_folder(folder: models.ModelFolder):
    """ """
    if str(cfg.UPLOADS_BASE_PATH / 'models') in str(folder.path):
        shutil.rmtree(folder.path)
        return {'ok': True}
    raise FileNotFoundError(f'{folder.path} is invalid')


@router.get('/containers', response_model=list[models.ContainerInfo])
async def docker_containers():
    """
    Container list with statuses
    """
    return get_container_names()


@router.get(
    '/containers/{container_id}/{since_nano_seconds}',
    response_model=models.ContainerLog,
)
async def docker_container_log(
    container_id: str, since_nano_seconds: float = None
):
    """
    Container logs
    """
    if not since_nano_seconds or since_nano_seconds <= 10:
        logs, at_nano_second = get_log_stream_for_container(container_id)
    else:
        logs, at_nano_second = get_log_stream_for_container(
            container_id, since=float(since_nano_seconds)
        )
    return {
        'logs': logs,
        'since': at_nano_second,
    }


# HSV Camera settings
@router.get('/hsvs', response_model=list[models.HSVSettingName])
async def get_hsvs():
    available_hsvs = hsv_cfg.available_hsvs
    if not available_hsvs:
        return []
    return [{'name': i} for i in available_hsvs]


@router.post('/hsvs/select', response_model=models.HSVSettingName)
async def select_hsv(hsv: models.HSVSettingName):
    hsv_cfg.selected_hsv = hsv.name
    return hsv.dict()


@router.get('/hsvs/selected', response_model=models.HSVSettingName | None)
async def get_selected_hsv():
    if hsv_cfg.selected_hsv:
        return {'name': hsv_cfg.selected_hsv}


@router.post('/hsvs/reset', response_model=models.HSVSettingName | None)
async def reset_hsv():
    hsv_cfg.selected_hsv = hsv_cfg.default_hsv_limits
    return None
