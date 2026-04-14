# memstats
A very simple Docker scrape target for Prometheus exporting free/total RAM and free/total storage on the root partition.

Usage:


```
git clone https://github.com/zaphod1988-2/memstats
docker compose up --build -d
curl http://localhost:9500/metrics

```
