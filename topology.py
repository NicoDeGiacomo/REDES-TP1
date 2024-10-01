from mininet.topo import Topo
from mininet.link import TCLink


class CustomTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Crear hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Crear switch
        s1 = self.addSwitch('s1')

        # h1 --> s1, packet_loss=10%
        self.addLink(h1, s1, cls=TCLink, loss=10)

        # The rest of the links are normal
        self.addLink(h2, s1, cls=TCLink)
        self.addLink(h3, s1, cls=TCLink)
        self.addLink(h4, s1, cls=TCLink)


topos = {'custom': CustomTopo}
