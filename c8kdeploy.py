#!python

from ios import ios
from ping3 import ping

class Store:
    def __init__(self, id, ip, status):
        self.id = id
        self.ip = ip
        self.status = status

stores = [Store('store1234','192.168.100.111',0), Store('store8888','10.90.18.74',0)]
username = 'admin'
password = 'admin'
sleeptime = 120

Statuses = ['Not Started','Pingable','SSH Works','Config Copied','Reset','Registered']

print('Scanning stores with status - Not Started')
for store in stores:
    if Statuses[store.status] == 'Not Started':
        response = ping(store.ip)
        if response == None:
            print(f'  {store.id}: Not Pingable')
        else:
            print(f'  {store.id}: Pingable - Moving to next step')
            store.status += 1
print('Scanning stores with status - Pingable')
for store in stores:
    if Statuses[store.status] == 'Pingable':
        storessh = ios(store.ip, username, password, 10111)
        print(f'  {store.id}: {storessh.status}')
        if storessh.status == 'Connected':
            store.status += 1
        storessh.disconnect()
print('Scanning stores with status - SSH Works')
for store in stores:
    if Statuses[store.status] == 'SSH Works':
        storessh = ios(store.ip, username, password, 10111)
        storessh.send_file('ios.py', 'testfile.txt')
        response = storessh.send_command('dir').split('\n')
        result = 'Fail'
        for line in response:
            if line.find('testfile.txt') > -1:
                result = 'Success'
                store.status += 1
        print(f'  {store.id}: {result}')
print('Current status of stores')
for store in stores:
    print(f'  {store.id}: {Statuses[store.status]}')