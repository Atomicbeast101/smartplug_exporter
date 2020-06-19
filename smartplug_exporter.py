#!/usr/bin/env python3
# Imports
import prometheus_client
import traceback
import threading
import argparse
import pyHS100
import time

# Arguments
parser = argparse.ArgumentParser(description='Prometheus exporter where it reports speedtest statistics based on user\'s preference.')
parser.add_argument('--web.listen-address', action='store', dest='listen_addr', help='Specify host and port for Prometheus to use to display metrics for scraping.')
parser.add_argument('--targets', action='store', dest='targets', help='List of targets separated by comma to collect.')
parser.add_argument('--interval', action='store', dest='interval', help='How often in seconds the tests should be performed.')

# Attributes
metrics = {
    'smartplug_alive': prometheus_client.Gauge('smartplug_alive', 'Reports if smart plug is alive and responding. 0=Offline, 1=Online', ['target']),
    'smartplug_current': prometheus_client.Gauge('smartplug_current', 'Current current of the power (in amps).', ['target']),
    'smartplug_voltage': prometheus_client.Gauge('smartplug_voltage', 'Current voltage of the power draw.', ['target']),
    'smartplug_power': prometheus_client.Gauge('smartplug_power', 'Current watts of the power draw.', ['target'])
}

# Classes
class UpdateMetrics(threading.Thread):
    def __init__(self, _targets, _interval):
        threading.Thread.__init__(self)
        self.targets = _targets
        self.interval = _interval
    
    def run(self):
        while True:
            for target in self.targets:
                try:
                    print('INFO: Updating metrics...', flush=True)
                    # Get data
                    plug = pyHS100.SmartPlug(target)
                    data = plug.get_emeter_realtime()

                    # Update metrics
                    metrics['smartplug_alive'].labels(target=target).set(1)
                    metrics['smartplug_current'].labels(target=target).set(data['current'])
                    metrics['smartplug_voltage'].labels(target=target).set(data['voltage'])
                    metrics['smartplug_power'].labels(target=target).set(data['power'])
                    print('INFO: Metrics updated!', flush=True)
                except Exception:
                    # Set metrics to 0
                    metrics['smartplug_alive'].labels(target=target).set(0)
                    metrics['smartplug_current'].labels(target=target).set(0)
                    metrics['smartplug_voltage'].labels(target=target).set(0)
                    metrics['smartplug_power'].labels(target=target).set(0)
                    print('ERROR: Unable to update metrics for {} target!'.format(target))

            # Wait
            time.sleep(self.interval)

# Main
if __name__ == '__main__':
    print('INFO: Loading exporter...')
    options = parser.parse_args()
    host = '0.0.0.0'
    port = 9100
    targets = []
    interval = 5
    try:
        if options.listen_addr:
            host = options.listen_addr.split(':')[0]
            port = int(options.listen_addr.split(':')[-1])
        if options.targets:
            targets = options.targets.split(',')
        if options.interval:
            interval = int(options.interval)
    except Exception:
        print('ERROR: Invalid argument input! Reason:\n{}'.format(traceback.print_exc()))
    print('INFO: Exporter ready!')
    UpdateMetrics(_targets=targets, _interval=interval).start()
    prometheus_client.start_http_server(port, host)
