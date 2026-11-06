"""Logs Raspberry Pi system metrics (CPU temperature, load, memory) to CSV."""

import argparse
import csv
import datetime
import os
import pathlib
import time

LOG_FILE = pathlib.Path.home() / "data" / "system_log.csv"
FIELDS = ["timestamp", "cpu_temp_c", "load_1m", "mem_used_pct"]


def read_cpu_temp():
    """Returns the CPU temperature in degrees Celsius."""
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        return int(f.read()) / 1000.0


def read_mem_used_pct():
    """Returns the percentage of RAM currently in use."""
    info = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":")
            info[key] = int(value.split()[0])
    return 100.0 * (1 - info["MemAvailable"] / info["MemTotal"])


def log_sample(writer):
    """Reads all metrics once and writes them as one CSV row."""
    writer.writerow({
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "cpu_temp_c": read_cpu_temp(),
        "load_1m": os.getloadavg()[0],
        "mem_used_pct": round(read_mem_used_pct(), 1),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=float, default=0,
                        help="Seconds between samples (0 = single sample).")
    parser.add_argument("--count", type=int, default=1,
                        help="Number of samples to take.")
    parser.add_argument("--output", type=pathlib.Path, default=LOG_FILE)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    is_new = not args.output.exists()
    with open(args.output, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        for i in range(args.count):
            log_sample(writer)
            f.flush()
            if i < args.count - 1:
                time.sleep(args.interval)


if __name__ == "__main__":
    main()
