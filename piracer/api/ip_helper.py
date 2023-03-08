import psutil


def get_ip_and_stats():
    """
    Return vehicle stats
    """
    (
        ram_total,
        ram_available,
        ram_used_percent,
        ram_free,
        *_,
    ) = psutil.virtual_memory()

    disk_total, disk_used, disk_percent_used, *_ = psutil.disk_usage('/')

    networks = psutil.net_if_addrs()

    cpu_count_threads = psutil.cpu_count()
    cpu_usage = psutil.getloadavg()
    cpu_usage_percent = []
    for load in cpu_usage:
        percent = (load / cpu_count_threads) * 100
        cpu_usage_percent.append(percent)

    system_stats = dict(
        cpu_count=psutil.cpu_count(logical=False),
        cpu_count_threads=cpu_count_threads,
        cpu_usage=cpu_usage,
        cpu_usage_percent=cpu_usage_percent,
        disk_total=disk_total,
        disk_used=disk_used,
        disk_percent_used=disk_percent_used,
        ram_total=ram_total / 1000000000,
        ram_available=ram_available / 1000000000,
        ram_used_percent=ram_used_percent,
        ram_free=ram_free / 1000000000,
        wlan0=None,
        eth0=None,
    )

    if networks.get('wlan0'):
        wlan0 = networks.get('wlan0')
        system_stats['wlan0'] = wlan0[0][1]

    if networks.get('eth0'):
        eth0 = networks.get('eth0')
        system_stats['eth0'] = eth0[0][1]

    return system_stats
