import os
from argparse import ArgumentParser
import numpy as np
from mininet.net import Mininet
from mininet.link import TCLink
import time

# Local Libraries
import json_parse
import topology
import switch

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


def genDCTraffic(t_source=None, t_sink=None, t_type: int = None, t_intensity=10, t_time=None, net: Mininet = None):
    data = {}
    full_json = []

    #for intensity in range(1, int(t_intensity) + 1):
    #    times, lines = [], []
    #    print(f"About {(intensity - 1) * 10}% done")
    #    print(f"Generating traffic for intensity {intensity}")

    #    flow_size = generateFromECDF(sizes, probs, 1)[0]
    #    for repetition in range(10):
    #        sender, receiver = np.random.choice(np.arange(1, 17, dtype=np.int32), 2, replace=False)
    #        source = net.getNodeByName(f"h{sender}")
    #        target = net.getNodeByName(f"h{receiver}")

    #        cmd = f"iperf -c {target.IP()} -n {8 * flow_size} --burst-period {1 / intensity} -y c"
    #        line = experiment(source, target, cmd, times)
    #        lines.append(line)

    #    data[intensity] = times

    #    json_data = process_to_json(lines)

    #    for index, json_object in enumerate(json_data):
    #        additional_info = {
    #            'time': data[intensity][index],
    #            'flows_per_second': intensity
    #        }
    #        json_object.update(additional_info)

    #    full_json.append(json_data)

    print('success!')
    # Write json object to file


    os.system('sudo chmod 0755 iperf_results.json')

    #make_box_plot()


def generateFromECDF(x_ecdf, y_ecdf, size=1):
    u = np.random.uniform(0, 1, size)
    samples = np.interp(u, y_ecdf, x_ecdf)
    return samples


if __name__ == '__main__':
    #parser = ArgumentParser(prog="ProgramName", description="DVAD20 Assignment 1", usage='%(prog)s [options]')
    #parser.add_argument('-s', '--source', help="where packets are sent from", required=False)
    #parser.add_argument('-S', '--sink', help="where packets are sent to", required=False)
    #parser.add_argument('-t', '--type', help="type of traffic, 1 for web search, 2 for data mining", required=False)
    #parser.add_argument('-i', '--intensity', help="how many packets per second", required=False)
    #parser.add_argument('-T', '--time', help="for how long to run test for", required=False)

    #args = parser.parse_args()

    os.system('sudo mn -c')

    mytopo = topology.MyTopology()
    net = Mininet(topo=mytopo, link=TCLink)

    net.start()

    genDCTraffic(t_type=1, net=net)
    genDCTraffic(t_type=2, net=net)

    net.stop()
