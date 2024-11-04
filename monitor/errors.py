class SensorError(Exception):
    def __init__(self, message="Can't communicate with sensor"):
        self.mssage = message
        super().__init__(self.message)