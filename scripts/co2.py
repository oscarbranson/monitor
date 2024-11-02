import signal
from pathlib import Path
from time import sleep
from typing import Optional
from monitor import co2, logging

class CO2Monitor:
    def __init__(self, sample_rate: int = 30, log_dir: str = "~/data"):
        self.running = True
        self.sample_rate = sample_rate
        self.log_dir = Path(log_dir).expanduser()
        self.logger = logging.Logger(sensor='CO2', log_dir=self.log_dir)
        self.sensor = co2.Sensor()  # Assuming Sensor class exists
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum: Optional[int] = None, frame: Optional[object] = None):
        """Graceful shutdown handler"""
        self.logger.info("Shutting down CO2 monitor...")
        self.running = False
        self.sensor.close()  # Assuming close method exists

    def run(self):
        """Main monitoring loop"""
        self.logger.info(f"Starting CO2 monitor (measuring every {self.sample_rate}s)")
        
        with self.sensor:
            while self.running:
                try:
                    co2_value = self.sensor.read()
                    self.logger.data(f'{co2_value:.0f}')
                except co2.SensorError as e:  # Assuming specific exception exists
                    self.logger.error(f"Sensor error: {e}")
                    sleep(5)  # Short retry delay
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")
                    self.shutdown()
                    break
                
                sleep(self.sample_rate)

def main():
    monitor = CO2Monitor()
    monitor.run()

if __name__ == "__main__":
    main()