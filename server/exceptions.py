class PortError(Exception):
    def __init__(self, port):
        self.port = port

    def __str__(self):
        return f"Creartion socket on port {self.port} is impossible"
