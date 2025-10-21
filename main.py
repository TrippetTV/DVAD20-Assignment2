import os
import sys
import time
import numpy as np
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController, OVSSwitch


# Local Libraries
import json_parse
import topology



def experiment(source, target, cmd: str, times):
    target.cmd("iperf -s &")
    time.sleep(1)
    start_time = time.time()
    line = source.cmd(cmd)
    end_time = time.time()
    target.cmd("pkill iperf")
    time.sleep(1)
    times.append(end_time - start_time)
    return line


def get_traffic_type(t_type: int):
    if t_type == 1:
        sizes = [0, 1e5, 2e5, 3e5, 5e5, 8e5, 1e6]
        probs = [0, 0.175, 0.3, 0.6, 0.9, 0.95, 1]
    elif t_type == 2:
        sizes = [180, 300, 460, 575, 590, 600, 645, 710, 820, 910]
        probs = [0.075, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    else:
        print("Incorrect type, exiting program")
        sys.exit()
    return sizes, probs


def genDCTraffic(t_source=None, t_sink=None, t_type: int = None, t_intensity=10, t_time=None, net: Mininet = None):
    sizes, probs = get_traffic_type(t_type)

    data = {}
    full_json = []

    for intensity in range(1, int(t_intensity) + 1):
        times, lines = [], []
        print(f"About {(intensity - 1) * 10}% done")
        print(f"Generating traffic for intensity {intensity}")

        flow_size = generateFromECDF(sizes, probs, 1)[0]
        for repetition in range(10):
            sender, receiver = np.random.choice(np.arange(1, 17, dtype=np.int32), 2, replace=False)
            source = net.getNodeByName(f"h{sender}")
            target = net.getNodeByName(f"h{receiver}")

            cmd = f"iperf -c {target.IP()} -n {8 * flow_size} --burst-period {1 / intensity} -y c"
            line = experiment(source, target, cmd, times)
            lines.append(line)

        data[intensity] = times

        json_data = json_parse.process_to_json(lines)

        for index, json_object in enumerate(json_data):
            additional_info = {
                'time': data[intensity][index],
                'flows_per_second': intensity
            }
            json_object.update(additional_info)

        full_json.append(json_data)

    print('success!')
    json_parse.json_write_file("iperf_results.json", full_json)

    os.system('sudo chmod 0755 iperf_results.json')

    # make_box_plot()


def generateFromECDF(x_ecdf, y_ecdf, size=1):
    u = np.random.uniform(0, 1, size)
    samples = np.interp(u, y_ecdf, x_ecdf)
    return samples


if __name__ == '__main__':
    #os.system('sudo mn -c')

    mytopo = topology.MyTopology()
    net = Mininet(topo=mytopo,
                  link=TCLink,
                  autoSetMacs=True,
                  autoStaticArp=True,
                  controller=RemoteController
                  )


    net.start()

    #genDCTraffic(t_type=1, net=net)
    #genDCTraffic(t_type=2, net=net)

    net.interact()
    net.stop()
