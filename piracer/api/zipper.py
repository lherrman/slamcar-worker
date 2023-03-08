import shutil
import os
import zipfile
import io
from pathlib import Path
from piracer import config as cfg


def zip_files(folder: Path, zip_subdir):
    # Open StringIO to grab in-memory ZIP contents
    s = io.BytesIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, 'w')

    for fpath in folder.glob('*'):
        _, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()
    return s


def unzip_files(zip_file_path: Path, dest_folder: Path):
    # raises FileNotFound if required file isn't found
    check_zip_for_needed_files(zip_file_path)

    shutil.rmtree(dest_folder, ignore_errors=True)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)

    return dest_folder


def check_zip_for_needed_files(zip_file_path: Path):
    essential_file = 'override_driving.py'

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_names = list(zip_ref.namelist())

        # be lenient: allow zip with onnx as single file
        if len(zip_names) == 1:
            if zip_names[0].endswith('onnx'):
                return

        if essential_file not in zip_names:
            raise FileNotFoundError(
                f'the zip-file is missing {essential_file}.'
                'It must contain a prediction function, `def predict_throttle_speed()`'
                'or an onnx file.'
            )


def count_files_in_folder(p: Path):
    return len(list(p.glob('*')))


def get_folder_from_name(path_name):
    path = cfg.UPLOADS_BASE_PATH / path_name
    return path


def get_folder_info(p: Path, download_link_base):
    return {
        'name': p.name,
        'path': str(p),
        'type': 'folder',
        'file_count': count_files_in_folder(p),
        'download_link': f'{download_link_base}{p.name}',
    }


def get_folder_names(
    path: Path = None,
    exclude_names: list = None,
    download_link_base: str = '/api/recordings/download/',
):
    if path is None:
        path = cfg.UPLOADS_BASE_PATH
    filter = lambda p: p.is_dir()

    if exclude_names is not None:
        filter = lambda p: p.is_dir() and p.name not in exclude_names
    try:
        folder_list = sorted(
            [
                get_folder_info(p, download_link_base)
                for p in path.iterdir()
                if filter(p)
            ],
            key=lambda item: os.path.getmtime(item['path']),
            reverse=True,
        )
    except:
        folder_list = []
    return folder_list
