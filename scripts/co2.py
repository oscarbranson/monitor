import signal
from pathlib import Path
from time import sleep
from typing import Optional
from monitor import co2, logging

from monitor.monitor import Monitor

def main():
    monitor = Monitor(sensors={'CO2': co2.Sensor}, sample_rate_s=3, log_dir="~/data")
    monitor.run()

if __name__ == "__main__":
    main()