from mininet.topo import Topo

class MyTopology(Topo):
    def build(self):
        # Create Network architecture
        bw = 20
        delay = '1ms'

        host = [self.addHost(f'h{i}') for i in range(1, 4 + 1)]
        switches = [self.addSwitch(f's{i}') for i in range(1, 4 + 1)]


        self.addLink(switches[0], switches[1], bw=bw, delay=delay)
        self.addLink(switches[0], switches[3], bw=bw, delay=delay)
        self.addLink(switches[2], switches[1], bw=bw, delay=delay)
        self.addLink(switches[2], switches[3], bw=bw, delay=delay)
        self.addLink(switches[1], host[0], bw=bw, delay=delay)
        self.addLink(switches[1], host[1], bw=bw, delay=delay)
        self.addLink(switches[3], host[2], bw=bw, delay=delay)
        self.addLink(switches[3], host[3], bw=bw, delay=delay)

