import json
import os
from argparse import ArgumentParser
import numpy as np
import sys
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
import matplotlib.pyplot as plt
import time


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


def make_box_plot():
    with open('iperf_results.json', 'r') as file:
        data = json.load(file)

    flow_rates = []
    times = []

    for intensity_group in data:
        if intensity_group:
            flow_rate = intensity_group[0]['flows_per_second']
            flow_rates.append(flow_rate)

            time_values = [entry['time'] for entry in intensity_group]
            times.append(time_values)

    plt.figure(figsize=(6, 6))
    box_plot = plt.boxplot(times,
                           labels=[f'{rate:.0f}' for rate in flow_rates],
                           patch_artist=True)

    for box in box_plot['boxes']:
        box.set(facecolor='lightblue', alpha=0.7)

    for median in box_plot['medians']:
        median.set(color='darkred', linewidth=2)

    for whisker in box_plot['whiskers']:
        whisker.set(color='gray', linestyle='--')

    for cap in box_plot['caps']:
        cap.set(color='gray')

    plt.xlabel('Flows per Second (s)')
    plt.ylabel('Flow Completion Time (s)')
    plt.title('Flow Completion Time vs Traffic Intensity')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig('flow_completion_time_boxplot.pdf', bbox_inches='tight', dpi=300,format='pdf')
    plt.show()


def process_line_to_json(line):
    parts = line.split(',')
    # if len(parts) < 8:
    # return None

    try:
        return {
            'timestamp': parts[0].strip(),
            'source_ip': parts[1].strip(),
            'source_port': parts[2].strip(),
            'dest_ip': parts[3].strip(),
            'dest_port': parts[4].strip(),
            'transfer_id': parts[5].strip(),
            'interval': parts[6].strip(),
            'transferred_bytes': int(float(parts[7].strip())),
            'bits_per_second': int(float(parts[8].strip()))
        }
    except (ValueError, IndexError):
        return None


def process_to_json(output: list[str], additional_info=None) -> list[dict[str, str]]:
    json_data = []

    for line in output:
        line = line.strip()
        parsed = process_line_to_json(line)
        if parsed:
            if additional_info:
                parsed.update(additional_info)
            json_data.append(parsed)
            json.dumps(parsed)

    return json_data


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

        json_data = process_to_json(lines)

        for index, json_object in enumerate(json_data):
            additional_info = {
                'time': data[intensity][index],
                'flows_per_second': intensity
            }
            json_object.update(additional_info)

        full_json.append(json_data)

    print('success!')
    # Write json object to file
    with open('iperf_results.json', 'w', encoding='utf-8') as file:
        json.dump(full_json, file, sort_keys=True, ensure_ascii=False, indent=4)

    os.system('sudo chmod 0755 iperf_results.json')

    make_box_plot()


def generateFromECDF(x_ecdf, y_ecdf, size=1):
    u = np.random.uniform(0, 1, size)
    samples = np.interp(u, y_ecdf, x_ecdf)
    return samples


if __name__ == '__main__':
    parser = ArgumentParser(prog="ProgramName", description="DVAD20 Assignment 1", usage='%(prog)s [options]')
    parser.add_argument('-s', '--source', help="where packets are sent from", required=False)
    parser.add_argument('-S', '--sink', help="where packets are sent to", required=False)
    parser.add_argument('-t', '--type', help="type of traffic, 1 for web search, 2 for data mining", required=False)
    parser.add_argument('-i', '--intensity', help="how many packets per second", required=False)
    parser.add_argument('-T', '--time', help="for how long to run test for", required=False)

    args = parser.parse_args()
    os.system('sudo mn -c')

    mytopo = MyTopology()
    net = Mininet(topo=mytopo, link=TCLink)

    net.start()

    genDCTraffic(t_type=1, net=net)
    genDCTraffic(t_type=2, net=net)

    net.stop()
