import time
import docker


def get_client():
    # client = docker.from_env()
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    return client


def get_container_names():
    c = get_client()
    infos = []
    for container in c.containers.list(all=True):
        infos.append(
            {
                'id': container.id,
                'image': container.image.id,
                'labels': container.labels,
                'name': container.name,
                'short_id': container.short_id,
                'status': container.status,
            }
        )
    return infos


def get_log_stream_for_container(container_id, since: int | None = None):
    c = get_client()
    container = c.containers.get(container_id)
    if since:
        return container.logs(since=since, timestamps=True), time.time()
    else:
        return container.logs(tail=100, timestamps=True), time.time()
