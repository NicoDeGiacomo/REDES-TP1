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
##### Go to Folder
```bash
cd REDES-TP1/
```

##### Run Wireshark
```bash
sudo wireshark
```

##### Run Mininet
```bash
sudo mn --custom topology.py --topo custom
```

##### Launch XTerm
```bash
xterm h1
xterm h2
xterm h3
xterm h4
```

##### Launch Server in H1
```bash
python3.12 src/start_server.py -H 10.0.0.1 -p 12345
```

##### Launch Download Client in H2 (TCP+SACK)
```bash
python3.12 src/download.py -H 10.0.0.1 -p 12345 -n file.mp4
```

##### Launch Upload Client in H3 (TCP+SACK)
```bash
python3.12 src/upload.py -H 10.0.0.1 -p 12345 -n file.jpg
```

##### Launch Download Client in H4 (TCP+SACK)
```bash
python3.12 src/download.py -H 10.0.0.1 -p 12345 -n file.txt
```

To use S&W protocol, add the parameter -P1 to the client command.
