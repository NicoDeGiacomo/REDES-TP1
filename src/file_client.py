class FileClient:
    def __init__(self, file_path):
        self.eof = 0
        self.file_path = file_path
        self.file = None

    def open(self, mode):
        self.file = open(self.file_path, mode)

    def close(self):
        self.file.close()

    def read(self, buffer):
        if self.file and not self.eof:
            data = self.file.read(buffer)
            if not data:
                self.eof = 1
            return data

    def write(self, data):
        if self.file:
            self.file.write(data)
