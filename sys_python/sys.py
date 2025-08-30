import os, psutil, cpuinfo, platform, time, threading, requests, datetime, socket

from flask import jsonify, Flask

def config():
    port = "5050"
    host = "0.0.0.0"
    return port, host

def config_get_ip():
    host_name = socket.gethostname()
    ip_local_address = socket.gethostbyname(host_name)

    ip_publice = os.system("hostname -I")

    return ip_local_address, ip_publice

def open_port():
    port, _ = config()
    os.system(f"sudo ufw status")
    os.system(f"sudo ufw allow {port}/tcp")

def system_info():
    name_os = platform.system()
    sersion_os = platform.version()
    host_name = socket.gethostname()

    boottime_second = psutil.boot_time()
    current_time_seconds = time.time()
    uptime_seconds = current_time_seconds - boottime_second

    boot_times = datetime.datetime.fromtimestamp(boottime_second)

    return host_name, name_os, sersion_os, int(uptime_seconds), boot_times

def cpu():
    core_cpu = psutil.cpu_count(logical=False)
    logic_core_cpu = os.cpu_count()

    info = cpuinfo.get_cpu_info()
    cpu_info = info['brand_raw']

    cpu_used = psutil.cpu_percent()

    # temperature_cpu = psutil.sensors_temperatures()

    return core_cpu, logic_core_cpu, cpu_info, cpu_used

def memory():
    ram = psutil.virtual_memory()
    ram_total = ram.total / (1024 ** 3)
    ram_used = ram.used / (1024 ** 3)
    ram_available = ram.available / (1024 ** 3)
    ram_percent = ram.percent

    return ram_used, ram_total, ram_available, ram_percent

def network():
    hostname = socket.gethostname()
    ip_loacl = socket.gethostbyname(host=hostname)


def gpu():
    pass

def chek_disk():
    return len(psutil.disk_partitions(all=True))

def get_disk_os():
    for get_mountpoint in psutil.disk_partitions(all=True):
        if get_mountpoint.mountpoint == "/":
            usage = psutil.disk_usage(get_mountpoint.mountpoint)
            return usage.used / (1024**3), usage.total / (1024**3), usage.percent
        return 0,0,0
    return None

def get_disk_sum():
    total_used, total_size = 0, 0
    for part in psutil.disk_partitions(all=True):
        if part.mountpoint == "/":  
            continue  # bỏ qua ổ chứa OS
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_size += usage.total
            total_used += usage.used
        except PermissionError:
            continue  # một số phân vùng hệ thống không cho truy cập
    percent = (total_used / total_size) * 100 if total_size > 0 else 0
    return total_used / (1024**3), total_size / (1024**3), percent

def get_a_disk():
    data = []
    for path_disk in psutil.disk_partitions():
        if path_disk.mountpoint == "/":
            continue
        try:
            if str(path_disk.mountpoint) not in data:
                usage = psutil.disk_usage(path_disk.mountpoint)

                io1 = psutil.disk_io_counters()
                time.sleep(1)
                io2 = psutil.disk_io_counters()

                data.append({
                    f"{path_disk.mountpoint}" : {
                        "used": round(usage.used / (1024 ** 3)),
                        "total": round(usage.total / (1024 ** 3)),
                        "percent": usage.percent,
                        "read_speed" : (io1.read_bytes - io2.read_bytes) / 1024 /1024,
                        "write_speed" : (io1.write_bytes - io2.write_bytes) / 1024 / 1024
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
        host_name, name_os, sersion_os, uptime_seconds, boot_time = system_info()
        # cpu
        core_cpu, logic_core_cpu, cpu_info, cpu_used = cpu()
        # Ram
        ram_used, ram_total, ram_available, ram_percent = memory()
        # number disk
        number_sdiskpart = chek_disk()
        # is disk os 
        disk_os_used, disk_os_total, disk_os_percent = get_disk_os()
        # disk sum
        disk_sum_used, disk_sum_total, disk_sum_percent = get_disk_sum()
        # db a disk
        db_disk = get_a_disk()
                        
        # db 
        data_db = {
           "system" : {
               "host_name" : str(host_name),
               "os_name" : str(name_os),
               "os_version" : str(sersion_os),
               "uptime_seconds" : f"{uptime_seconds}",
               "boot_time" : f"{boot_time}"
           },
            "cpu" : {
                "core_cpu" : int(core_cpu),
                "logic_core_cpu" : int(logic_core_cpu),
                "info_cpu" : str(cpu_info),
                "cpu_used" : int(cpu_used),
                # "temperature_cpu" : str(temperature_cpu)
            },
            "memory" : {
                "ram_used" : f"{ram_used:.1f}",
                "ram_total" : f"{ram_total:.1f}",
                "ram_available" : f"{ram_available:.1f}",
                "ram_percent" : int(ram_percent),
                # "type_ram" : str
            },
            "disk" : {
                "number_disk" : int(number_sdiskpart),
                "disk_os" : {
                    "disk_os_used" : round(int(disk_os_used)),
                    "disk_os_total" : round(disk_os_total),
                    "disk_os_percent" : round(int(disk_os_percent))
                },
                "disk_sum" : {
                    "disk_sum_used" : round(int(disk_sum_used)),
                    "disk_sum_total" : int(disk_sum_total),
                    "disk_sum_percent" : round(int(disk_sum_percent)),
                },
                "db_disk" : db_disk
            }
        }

PORT, HOST = config()
app = Flask(__name__)

@app.route("/")
def root():
    return jsonify(data_db)

if __name__ == "__main__":
    ip_local, ip_publice = config_get_ip()
    rq_check_port = requests.get(f"{ip_local}{PORT}")
    if rq_check_port.status_code == "200":
        times = threading.Thread(target=db, daemon=True)
        times.start()
        app.run(debug=True, host=HOST, port=PORT)
    else:
        open_port()
        times = threading.Thread(target=db, daemon=True)
        times.start()
        app.run(debug=True, host=HOST, port=PORT)