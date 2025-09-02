import os, psutil, cpuinfo, platform, time, threading, datetime, socket
from flask import jsonify, Flask

def system_info():
    name_os = platform.system()
    version_os = platform.version()
    host_name = socket.gethostname()
    uptime_seconds = int(time.time() - psutil.boot_time())
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    return host_name, name_os, version_os, uptime_seconds, boot_time

def cpu():
    core_cpu = psutil.cpu_count(logical=False)
    logic_core_cpu = os.cpu_count()
    info = cpuinfo.get_cpu_info()
    cpu_info = info['brand_raw']
    cpu_used = psutil.cpu_percent(interval=1)  # nhanh hơn
    return core_cpu, logic_core_cpu, cpu_info, cpu_used

def memory():
    ram = psutil.virtual_memory()
    return (
        ram.used / (1024 ** 3),
        ram.total / (1024 ** 3),
        ram.available / (1024 ** 3),
        ram.percent
    )

def get_disk_os():
    for part in psutil.disk_partitions(all=True):
        if part.mountpoint == "/":
            usage = psutil.disk_usage(part.mountpoint)
            return usage.used / (1024**3), usage.total / (1024**3), usage.percent
    return 0, 0, 0

def get_disk_sum():
    total_used, total_size = 0, 0
    for part in psutil.disk_partitions(all=True):
        if part.mountpoint == "/":
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_size += usage.total
            total_used += usage.used
        except PermissionError:
            continue
    percent = (total_used / total_size) * 100 if total_size > 0 else 0
    return total_used / (1024**3), total_size / (1024**3), percent

# lưu IO counters để tính tốc độ disk mà không cần sleep
prev_io = psutil.disk_io_counters()

def get_a_disk():
    global prev_io
    new_io = psutil.disk_io_counters()
    read_speed = (new_io.read_bytes - prev_io.read_bytes) / 1024 / 1024
    write_speed = (new_io.write_bytes - prev_io.write_bytes) / 1024 / 1024
    prev_io = new_io

    data = []
    for part in psutil.disk_partitions():
        if part.mountpoint == "/":
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            data.append({
                part.mountpoint: {
                    "used": round(usage.used / (1024 ** 3)),
                    "total": round(usage.total / (1024 ** 3)),
                    "percent": usage.percent,
                    "read_speed": read_speed,
                    "write_speed": write_speed
                }
            })
        except PermissionError:
            continue
    return data

data_db = {}

def db():
    global data_db
    while True:
        # system info
        host_name, name_os, version_os, uptime_seconds, boot_time = system_info()
        # cpu
        core_cpu, logic_core_cpu, cpu_info, cpu_used = cpu()
        # memory
        ram_used, ram_total, ram_available, ram_percent = memory()
        # disk
        disk_os_used, disk_os_total, disk_os_percent = get_disk_os()
        disk_sum_used, disk_sum_total, disk_sum_percent = get_disk_sum()
        db_disk = get_a_disk()

        data_db = {
            "system": {
                "host_name": host_name,
                "os_name": name_os,
                "os_version": version_os,
                "uptime_seconds": uptime_seconds,
                "boot_time": str(boot_time)
            },
            "cpu": {
                "core_cpu": core_cpu,
                "logic_core_cpu": logic_core_cpu,
                "info_cpu": cpu_info,
                "cpu_used": f'{cpu_used:.0f}',
            },
            "memory": {
                "ram_used": f"{ram_used:.1f}",
                "ram_total": f"{ram_total:.1f}",
                "ram_available": f"{ram_available:.1f}",
                "ram_percent": int(ram_percent),
            },
            "disk": {
                "disk_os": {
                    "disk_os_used": round(disk_os_used),
                    "disk_os_total": round(disk_os_total),
                    "disk_os_percent": round(disk_os_percent)
                },
                "disk_sum": {
                    "disk_sum_used": round(disk_sum_used),
                    "disk_sum_total": round(disk_sum_total),
                    "disk_sum_percent": round(disk_sum_percent),
                },
                "db_disk": db_disk
            }
        }

        time.sleep(0.1)  # refresh mỗi 1 giây

PORT, HOST = "5050", "0.0.0.0"
app = Flask(__name__)

@app.route("/")
def root():
    return jsonify(data_db)

if __name__ == "__main__":
    threading.Thread(target=db, daemon=True).start()
    app.run(debug=True, host=HOST, port=PORT)
