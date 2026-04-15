# memstats
A very simple Docker scrape target for Prometheus exporting free/total RAM and free/total storage on the root partition.

Usage:

```
git clone https://github.com/zaphod1988-2/memstats
docker compose up --build -d
curl http://localhost:9500/metrics
```
Be sure to setup the correct host paths:
* For /filesystem, use a path to the partition you want to measure. In most cases, that's just /. In HAOS for example, you'll need /mnt/data/supervisor/share or similar.
* For /host/proc, use the folder where your meminfo file sits.

The docker container is exporting the following properties:
```
custom_computer_free_ram_bytes 
custom_computer_total_ram_bytes 
custom_computer_free_storage_bytes 
custom_computer_total_storage_bytes 
```

I use it to fill the Proxmox Prometheus Dashboard (https://grafana.com/grafana/dashboards/10347-proxmox-via-prometheus/)
with additional information for my QEMU VMs as Proxmox is exporting false data (or in case of disk usage no data at all.) and without the need of the full-grown node exporter.

You will have to map the Proxmox exporter and the memstats data accordingly. Most important thing there is the id mapping to be able to match PVE and memstats data.

prometheus.yml:

```
- job_name: "memstats"
    static_configs:
      - targets:
          - "127.0.0.1:9500"
        labels:
          hostname: "vm-name"
          id: "qemu/100"
```

The customized dashboard JSON is in the files as well.