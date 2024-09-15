# Mininet Guide

### Run Wireshark
```bash
$ sudo wireshark
```

### Create Sample Topology
```bash
$ sudo mn
```

### Commands for information
```bash
mininet> nodes
mininet> net
mininet> dump
```

### Connectivity between hosts
```bash
mininet> h1 ping -c 1 h2
miniinet> pingall
```

### Run Web Server
```bash
mininet> h1 python3 -m http.server 80 &
mininet> h2 wget -O - h1
...
mininet> h1 kill %python3
```

### Clean up
```bash
mininet> exit
$ sudo mn -c
```
