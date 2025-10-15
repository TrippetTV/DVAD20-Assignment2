import json
import matplotlib.pyplot as plt


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


def json_write_file(name: str = "out.json", json_object: list[dict[str, str]] = None) -> None:
    with open(name, 'w', encoding='utf-8') as file:
        json.dump(json_object, file, sort_keys=True, ensure_ascii=False, indent=4)