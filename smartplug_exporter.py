import pyHS100

plug = pyHS100.SmartPlug('192.168.1.20')
#asyncio.run(plug.update())
print('Hardware: {}'.format(plug.hw_info))
print('Full sysinfo: {}'.format(plug.get_sysinfo()))
print('Status: {}'.format(plug.state))
print('Alias: {}'.format(plug.alias))
print('Energy Readings: {}'.format(plug.get_emeter_realtime()))
