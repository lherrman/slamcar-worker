from piracer.api import models

from fastapi import FastAPI
from piracer.api.routers import vehicle, video_stream


# FIXME: Use password or similar to protect from maliciously updating/accessing
# somebody elses car

app = FastAPI(
    openapi_url='/api/openapi.json',
    docs_url='/api/docs',
    redoc_url=None,
    host='',
    servers=[{'url': '/'}],
    root_path_in_servers=False,
)

app.include_router(
    vehicle.router,
    prefix='/api',
    tags=['Vehicle'],
    # dependencies=[Depends(get_token_header)],
    # responses={418: {"description": "I'm a teapot"}},
)

app.include_router(
    video_stream.router,
    prefix='',
    tags=['Video'],
    # dependencies=[Depends(get_token_header)],
    # responses={418: {"description": "I'm a teapot"}},
)


@app.get('/', response_model=models.DummyItem)
async def read_root():
    return {'title': 'hello world, nothing to see here'}
