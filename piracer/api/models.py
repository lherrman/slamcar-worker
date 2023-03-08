from typing import Optional
from pydantic import BaseModel
from typing import Dict
from enum import Enum

from piracer.data_persistence import CalibrationType, ModeEnum


class DummyItem(BaseModel):
    title: str


class SystemStats(BaseModel):
    cpu_count: int
    cpu_count_threads: int
    cpu_usage: list
    cpu_usage_percent: list
    disk_total: float
    disk_used: float
    disk_percent_used: float
    ram_total: float
    ram_available: float
    ram_used_percent: float
    ram_free: float
    eth0: Optional[str]
    wlan0: Optional[str]


class StatusInfo(BaseModel):
    self_driving: Optional[bool]
    training_mode: Optional[bool]
    model: Optional[str]
    is_recording: Optional[bool]
    current_selected_model: str


class RecordingFolder(BaseModel):
    name: str
    path: str
    file_count: int
    download_link: str


class VehiclePWM(BaseModel):
    pwm: int


class VehicleCalibration(BaseModel):
    mode: str
    calibration_type: CalibrationType
    steering_pwm: int
    throttle_pwm: int
    STEERING_LEFT_PWM: int
    STEERING_RIGHT_PWM: int
    THROTTLE_FORWARD_PWM: int
    THROTTLE_STOPPED_PWM: int
    THROTTLE_REVERSE_PWM: int


class VehicleCalibrationType(BaseModel):
    calibration_type: CalibrationType = CalibrationType.off


class VehicleMode(BaseModel):
    mode: ModeEnum = ModeEnum.user


class ModelFolder(RecordingFolder):
    pass


class ContainerStatusEnum(str, Enum):
    running = 'running'
    created = 'created'
    restarting = 'restarting'
    removing = 'removing'
    paused = 'paused'
    exited = 'exited'
    dead = 'dead'
    unknown = 'unknown'


class ContainerInfo(BaseModel):
    id: str
    image: str
    labels: Dict[str, str]
    name: str
    short_id: str
    status: ContainerStatusEnum


class ContainerLog(BaseModel):
    logs: str
    since: float


class FakeUser(BaseModel):
    username: str


class UserInDB(FakeUser):
    hashed_password: str


class HSVBounds(BaseModel):
    h_lower: int
    h_upper: int
    s_lower: int
    s_upper: int
    v_lower: int
    v_upper: int


class HSVSettingName(BaseModel):
    name: str


class HSVSetting(HSVSettingName):
    hsv_bounds: HSVBounds
