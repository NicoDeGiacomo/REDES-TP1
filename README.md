# REDES-TP1

### Setup Instructions
[Mac Setup Instructions](/MAC_INSTALL.md)

### Mininet Guide
[Mininet Guide](/MININET_GUIDE.md)

### Libraries & Tools
- [argparse](https://docs.python.org/3/library/argparse.html)
- [logging](https://docs.python.org/3/library/logging.html)
- [socket](https://docs.python.org/3/library/socket.html)
- [flake8](https://flake8.pycqa.org/en/latest/)

### Development Instructions
Run flake8 to check for style errors before committing.
```bash
$ flake8 src/
```

Run md5sum to check for the integrity of the transferred file.
```bash
$ md5sum src/file.txt > hashfile
$ md5sum -c hashfile
```

### Run Instructions
Run Server
```bash
$ python3 src/start-server.py
```

Run Client
```bash
$ python3 src/upload.py
```
