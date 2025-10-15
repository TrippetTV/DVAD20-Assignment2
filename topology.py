from mininet.topo import Topo

class MyTopology(Topo):
    def build(self):
        # Create Network architecture
        bw = 20
        bw_second = 80
        delay = '1ms'

        host = [self.addHost(f'h{i}') for i in range(1, 17)]
        switches = [self.addSwitch(f's{i}') for i in range(1, 14)]

        leaf_switches = switches[:8]
        middle_switches = switches[8:12]
        backbone_switch = switches[12]

        for i, host in enumerate(host):
            self.addLink(host, leaf_switches[i // 2], delay=delay, bw=bw)

        for i in range(0, 8, 2):
            self.addLink(leaf_switches[i], middle_switches[i // 2], delay=delay, bw=bw)
            self.addLink(leaf_switches[i + 1], middle_switches[i // 2], delay=delay, bw=bw)

        for middle_switches in middle_switches:
            self.addLink(middle_switches, backbone_switch, delay=delay, bw=bw)
