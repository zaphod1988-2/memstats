import os
from flask import Flask,Response
import threading
import time
from cheroot import wsgi
import psutil

app = Flask(__name__)

class Storage:
    '''Exports statistics for root partition'''
    def __init__(self):
        try:
            stat = os.statvfs("/host")
        except Exception as e:
            print(f"Error updating metrics: {e}")
        self.__total = stat.f_frsize * stat.f_blocks
        self.__free = stat.f_frsize * stat.f_bfree

    def get_free(self):
        return self.__free
    
    def get_total(self):
        return self.__total

class RAM:
    '''Exports RAM statistics'''
    def __init__(self, meminfo_path="/host/proc/meminfo"):
        # try: 
        #     values = {}
        #     with open(meminfo_path, "r", encoding="utf-8") as f:
        #         for line in f:
        #             key, value = line.split(":", 1)
        #             values[key] = value.strip()

        #     self.__total_ram = int(values["MemTotal"].split()[0]) * 1024
        #     self.__free_ram = int(values["MemAvailable"].split()[0]) * 1024
        # except Exception as e:
        #     print(f"Error updating metrics: {e}")
        psutil.PROCFS_PATH = "/host/proc"
        ram_info = psutil.virtual_memory()
        self.__free_ram = ram_info.available
        self.__total_ram = ram_info.total


    def get_free(self):
        return self.__free_ram
    
    def get_total(self):
        return self.__total_ram
    
class Webserver:
    def __init__(self):
        self.update_once()

    def update_once(self):
        ram = RAM()
        storage = Storage()
        self.free_ram = ram.get_free()
        self.total_ram = ram.get_total()
        self.free_storage = storage.get_free()
        self.total_storage = storage.get_total()

    def update_loop(self):
        while True:
            self.update_once()
            time.sleep(1)

@app.route("/metrics")
def metrics_endpoint():
        data = (
        "# HELP custom_computer_free_ram_bytes Free RAM in bytes\n"
        "# TYPE custom_computer_free_ram_bytes gauge\n"
        f"custom_computer_free_ram_bytes {metrics.free_ram}\n"
        "# HELP custom_computer_total_ram_bytes Total RAM in bytes\n"
        "# TYPE custom_computer_total_ram_bytes gauge\n"
        f"custom_computer_total_ram_bytes {metrics.total_ram}\n"
        "# HELP custom_computer_free_storage_bytes Free disk in bytes\n"
        "# TYPE custom_computer_free_storage_bytes gauge\n"
        f"custom_computer_free_storage_bytes {metrics.free_storage}\n"
        "# HELP custom_computer_total_storage_bytes Total disk in bytes\n"
        "# TYPE custom_computer_total_storage_bytes gauge\n"
        f"custom_computer_total_storage_bytes {metrics.total_storage}\n"
    )
        return Response(data, content_type="text/plain; version=0.0.4; charset=utf-8")

if __name__ == "__main__":
    metrics = Webserver()
    # Debug:
    # threading.Thread(target=metrics.update_loop, daemon=True).start()
    # app.run(host="0.0.0.0", port=8000, debug=False)

    # Prod:
    threading.Thread(target=metrics.update_loop, daemon=True).start()
    wsgi_server = wsgi.Server(("0.0.0.0", 9500), app)
    print("Starting WSGI server on http://0.0.0.0:9500/metrics")
    try:
        wsgi_server.start()
    finally:
        wsgi_server.stop()
    