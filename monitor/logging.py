import logging
from datetime import datetime
from pathlib import Path

# Define custom level (between INFO=20 and WARNING=30)
DATA_LEVEL = 25
logging.addLevelName(DATA_LEVEL, 'DATA')
logging.DATA = DATA_LEVEL

class Logger:
    def __init__(self, sensor='CO2', log_dir="logs", log_level=logging.DATA):
        """Initialize logger with directory and level."""
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.sensor = sensor
        self._setup_logger()
        
    def _setup_logger(self):
        """Configure the logger with file and console handlers."""
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Generate filename with current date
        current_date = datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file = self.log_dir / f"{current_date}-{self.sensor}.log"
        
        # Create and configure logger
        self.logger = logging.getLogger(self.sensor)
        self.logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s,%(levelname)s,%(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Log info level message."""
        self.logger.info(message)
    
    def data(self, message):
        """Log data level message."""
        self.logger.log(DATA_LEVEL, message)
    
    def warning(self, message):
        """Log warning level message."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error level message."""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug level message."""
        self.logger.debug(message)