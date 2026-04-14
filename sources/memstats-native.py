import os
from flask import Flask,Response
import threading
import time

class Storage:
    '''Exports statistics for root partition'''
    def __init__(self):
        stat = os.statvfs("/")
        self.__total = stat.f_frsize * stat.f_blocks
        self.__free = stat.f_frsize * stat.f_bfree

    def get_free(self):
        return self.__free
    
    def get_total(self):
        return self.__total

class RAM:
    '''Exports RAM statistics'''
    def __init__(self):
        page_size = os.sysconf("SC_PAGE_SIZE")
        phys_pages = os.sysconf("SC_PHYS_PAGES")
        avail_pages = os.sysconf("SC_AVPHYS_PAGES")
        self.__total_ram = page_size * phys_pages
        self.__free_ram = page_size * avail_pages

    def get_free(self):
        return self.__free_ram
    
    def get_total(self):
        return self.__total_ram
    
class Webserver:
    def __init__(self):
        self.counter = 0
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
            self.counter += 1
            self.update_once()
            time.sleep(1)

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/metrics")
    def home():
        data = f"""         
# TYPE custom_computer_free_ram_bytes gauge
# HELP custom_computer_free_ram_bytes Number of bytes of free RAM on this machine
custom_computer_free_ram_bytes {server.free_ram}
# HELP custom_computer_total_ram_bytes Number of bytes of total RAM on this machine
# TYPE custom_computer_total_ram_bytes gauge
custom_computer_total_ram_bytes {server.total_ram}
# HELP custom_computer_free_storage_bytes Number of bytes of free storage on root partition
# TYPE custom_computer_free_storage_bytes gauge
custom_computer_free_storage_bytes {server.free_storage}
# HELP custom_computer_total_storage_bytes Number of bytes of total storage on root partition
# TYPE custom_computer_total_storage_bytes gauge
custom_computer_total_storage_bytes {server.total_storage}           
            """
        return Response(data, mimetype="text/plain; version=0.0.4; charset=utf-8")


    server = Webserver()
    threading.Thread(target=server.update_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=False)