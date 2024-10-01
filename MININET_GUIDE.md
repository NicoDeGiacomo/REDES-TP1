# Mininet Guide
Summary of commands and instructions for Mininet, taken from:\
https://mininet.org/sample-workflow/

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
mininet> links
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

### Run Regression Test
```bash
$ sudo mn --test pingpair
$ sudo mn --test pingall
$ sudo mn --test iperf
```

### Custom Topology
One switch and three hosts.
```bash
$ sudo mn --test pingall --topo single,3
```

Four switches and four hosts. Linear.
```bash
$ sudo mn --topo linear,4
```

Custom topology with a python script.\
https://mininet.org/walkthrough/#custom-topologies

### Link Customization
Packet Loss (10%)
```bash
$ sudo mn --link tc,loss=10
```

Bandwidth (10Mbps)
```bash
$ sudo mn --link tc,bw=10
```

Delay (10ms)
```bash
$ sudo mn --link tc,delay=10ms
```

Bring link down/up
```bash
mininet> link s1 h1 down
mininet> link s1 h1 up
```

### Run a python program inside a host
```bash
mininet> h1 python3 my_program.py
```

### Clean up
```bash
mininet> exit
$ sudo mn -c
```

### Run topology
Inside the file, change the packet loss parameter.
```bash
sudo mn --custom topology.py --topo custom
```
```bash
xterm h1 # server
python3 src/start_server.py
```
```bash
xterm h2 # velociraptor.jpg
python3 src/upload.py
```

```bash
xterm h3 # natural.jpg
python3 src/upload.py -n natural.jpg
```

