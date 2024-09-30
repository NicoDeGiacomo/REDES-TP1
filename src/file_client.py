import os


class FileClient:
    def __init__(self, file_path):
        self.eof = 0
        self.file_path = file_path
        self.file = None

    def open(self, mode):
        self.file = open(self.file_path, mode)

    def close(self):
        self.file.close()

    def read(self, buffer_size):
        if self.file and not self.eof:
            data = self.file.read(buffer_size)
            if len(data) < buffer_size:  #
                self.eof = 1
            return data

    def write(self, data):
        if self.file:
            self.file.write(data)

    def delete(self):
        self.close()
        os.remove(self.file_path)
