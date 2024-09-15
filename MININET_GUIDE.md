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

### Clean up
```bash
mininet> exit
$ sudo mn -c
```
