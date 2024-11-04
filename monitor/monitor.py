import signal
from pathlib import Path
from time import sleep
from typing import Optional
from monitor import co2, logging
from .errors import SensorError


class Monitor:
    def __init__(self, sensors: dict = {}, sample_rate_s: int = 3, log_dir: str = "~/data"):
        self.running = True
        self.name = '-'.join(sensors.keys())
        self.sensors = {k: sensor() for k, sensor in sensors.items()}  # assuming the items of sensor are class
        self.sample_rate = sample_rate_s
        self.log_dir = Path(log_dir).expanduser()
        self.logger = logging.Logger(sensor=self.name, log_dir=self.log_dir)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum: Optional[int] = None, frame: Optional[object] = None):
        """Graceful shutdown handler"""
        self.logger.info(f"Shutting down {self.name} monitor...")
        self.running = False
        [v.close() for v in self.sensors.values()]  # Assuming close method exists

    def run(self):
        """Main monitoring loop"""
        self.logger.info(f"Starting {self.name} monitor (measuring every {self.sample_rate}s)")
        
        with self.sensor:
            while self.running:
                try:
                    values = [sensor.read() for sensor in self.sensors.values()]
                    self.logger.data(','.join([f'{v:.0f}' for v in values]))
                except SensorError as e:  # Assuming specific exception exists
                    self.logger.error(f"Sensor error: {e}")
                    sleep(5)  # Short retry delay
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")
                    self.shutdown()
                    break
                
                sleep(self.sample_rate)