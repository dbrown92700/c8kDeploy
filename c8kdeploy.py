#!/usr/bin/env python3

from includes import esxUser, esxPassword, configdir, sleeptime, sourceOva, mask, logdir
from includes import ovftoolthreads, ovftoolpath, interfacemap, VMname
from includes import vmanage, vmanageUser, vmanagePassword
from ios import ios
from ping3 import ping
import os
import subprocess
from time import sleep
import threading
from vmanage_api import rest_api_lib

# Definition of the phases of C8K deployment

Statuses = ['Not Started', 'OVA Deploying', 'OVA Deployed', 'Pingable', 'SSH Works', 'Config Copied', \
            'Awaiting Registration', 'Registered', 'Activate Command Sent', 'Certificate Installed']
storesCompleted = 0

# Write current statuses of each C8Kv deployment to status.csv

def write_status(statuses):
    with open(f'{configdir}status.temp', 'w') as statusFile:
        for hostname in statuses:
            statusFile.write(f'{hostname},{statuses[hostname]}\n')
    os.replace(f'{configdir}status.temp', f'{configdir}status.csv')


# Threading class for ovftool push of OVA to ESX server

class deployOVA (threading.Thread):

    def __init__(self, threadstore):
        threading.Thread.__init__(self)
        self.threadId = 'OVA:' + threadstore['hostname']
        self.stdout = None
        self.stderr = None
        self.Store = threadstore

    def run(self):
        interfaces = ''
        for interface in interfacemap:
            interfaces += f'--net:{interface}={interfacemap[interface]} '

        ovfcommand = f'--name={vmname}\
             --X:injectOvfEnv\
             --X:logFile={logdir}{self.Store["hostname"]}ovftool.log\
             --X:logLevel=trivia\
             --acceptAllEulas\
             -ds=datastore1\
             -dm=thin\
             --deploymentOption={self.Store["deploymentOption"]}\
             {interfaces}\
             --X:enableHiddenProperties\
             --noSSLVerify\
             --allowExtraConfig\
             --machineOutput\
             --prop:com.cisco.c8000v.hostname.1={self.Store["hostname"]}\
             --prop:com.cisco.c8000v.login-username.1={self.Store["login-username"]}\
             --prop:com.cisco.c8000v.login-password.1={self.Store["login-password"]}\
             --prop:com.cisco.c8000v.mgmt-interface.1={self.Store["mgmt-interface"]}\
             --prop:com.cisco.c8000v.mgmt-ipv4-addr.1={self.Store["mgmt-ipv4-addr"]}\
             --prop:com.cisco.c8000v.mgmt-ipv4-gateway.1={self.Store["mgmt-ipv4-gateway"]}\
             --prop:com.cisco.c8000v.mgmt-ipv4-network.1={self.Store["mgmt-ipv4-network"]}\
             --powerOn\
             {sourceOva}\
             vi://{esxUser}:{esxPassword}@{self.Store["esxServer"]}'
        stdoutFile = open(f'{logdir}{self.Store["hostname"]}console.log', 'w')
        stderrFile = open(f'{logdir}{self.Store["hostname"]}error.log', 'w')
        proc = subprocess.Popen([f'{ovftoolpath}ovftool']+ovfcommand.split(), shell=False, stdout=stdoutFile, stderr=stderrFile)
        result = proc.wait()
        print(f'***THREAD COMPLETE Status {result}*** {self.Store["hostname"]} OVA Deployment Complete ***')


# ################################ DATA COLLECTION PHASE ##########################
# Load status data stored from previous run

storeStatuses = {}
print('--------- Beginning Statuses --------------------------------------------------')
try:
    statusfile = open(f'{configdir}status.csv', 'r', encoding='utf-8-sig')
    noStatus = False
    for line in statusfile:
        data = line.strip('\n').split(',')
        storeStatuses[data[0]] = int(data[1])
        if Statuses[int(data[1])] == 'Certificate Updated':
            storesCompleted += 1
        print(f'   {data[0]}: {Statuses[int(data[1])]}')
except:
    noStatus = True
    print('   NONE')

# Load stores data from parameters.csv file

stores = []
parameters = open(f'{configdir}parameters.csv', 'r', encoding='utf-8-sig')
header = parameters.readline().strip('\n').split(',')
for line in parameters:
    data = line.strip('\n').split(',')
    values = {}
    index = 0
    for parameter in header:
        values[parameter] = data[index]
        index += 1
    if noStatus:
        storeStatuses[values['hostname']] = 0
    stores.append(values)

write_status(storeStatuses)

# Download all bootstrap files.  If hostname is in the parameters list, save as hostname.cfg

storeList = list(storeStatuses.keys())
print('---------Download all bootstrap configs for Cat8000v attached to templates ---------')
vmsess = rest_api_lib(vmanage, vmanageUser, vmanagePassword)
bootDevices = vmsess.get_request('system/device/vedges?state=bootstrapconfiggenerated')['data']
vmsess.logout()
for device in bootDevices:
    print(f'  {device["uuid"]}: {device["configOperationMode"]}')
    if device['configOperationMode'] == 'vmanage':
        vmsess = rest_api_lib(vmanage, vmanageUser, vmanagePassword)
        url = f'system/device/bootstrap/device/{device["uuid"]}?configtype=cloudinit&inclDefRootCert=false'
        bootConfig = vmsess.get_request(url)['bootstrapConfig']
        vmsess.logout()
        for line in bootConfig.split('\n'):
            if line.find('hostname') > -1:
                filename = f'{line.replace("hostname","").lstrip()}'
                if filename in storeList:
                    with open(f'{configdir}{filename}.cfg', 'w') as file:
                        file.write(bootConfig)
                    print(f'  Saved {filename}')
                else:
                    print(f'    hostname {filename} not found in list.  Config file not saved')
                break
    else:
        print('    Not in vManage mode.  Skipped')

# Parse configuration files for UUID, Token(OTP) & System-IP that apply to parameters list

filelist = os.popen(f'ls {configdir}').read().split('\n')
for store in stores:
    filename = f'{store["hostname"]}.cfg'
    if filename in filelist:
        print(f'  Parsing {filename}')
        file = open(f'{configdir}{filename}')
        for line in file.read().split('\n'):
            for param in ['- uuid', ' - otp', 'system-ip']:
                if line.find(param) > -1:
                    pvalue = f'{line.replace(param, "").lstrip(" :-")}'
                    store[param.lstrip('- ')] = pvalue
                    print(f'    - {param.lstrip("- ")}:{pvalue}')
        storeList.remove(store['hostname'])
    else:
        print(f'  !!! {store["hostname"]} config file missing')

# Check if all configs were found.  List missing configs or continue to deployment phase

if len(storeList) > 0:
    print('    The following stores bootstrap configs are missing.  Script will terminate.')
    for store in storeList:
        print(f'      {store}')
    exit()
else:
    print('--- SUCCESS: All required bootstrap configs found and downloaded ---\n')

# ################################ DEPLOYMENT PHASE ##########################


# This loop iterates through all the steps until every C8Kv in the parameters file is fully deployed

runNumber = 0
while storesCompleted < len(stores):

    print(f'------------------------- Run {runNumber} ----------------------------------------------------')
    runNumber += 1

    # OVA PUSH START: Scan Not Started stores and begin an OVF deployment

    print('Scanning stores with status - Not Started')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'Not Started':

            if threading.active_count() < (ovftoolthreads + 1):
                storedata = dict(store)
                store['ovaThread'] = deployOVA(storedata)
                store['ovaThread'].start()
                print(f'  {store["hostname"]}: OVA Deployment Started')
                sleep(2)
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)
            else:
                print(f'  {store["hostname"]}: Delayed. {ovftoolthreads} deployments already running.')

    # OVA PUSH COMPLETE: Scan OVA Deploying stores and see if thread is done

    print('Scanning stores with status - OVA Deploying')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'OVA Deploying':
            if store['ovaThread'].is_alive():

                percentComplete = '0'
                try:
                    file = open(f'{logdir}{store["hostname"]}console.log')
                    lines = file.read()
                    file.close()
                except FileNotFoundError:
                    lines = '0'
                for line in lines.split('\n'):
                    if line.lstrip() != '':
                        percentComplete = line
                print(f'  {store["hostname"]}: OVA Still Deploying - At: {percentComplete}%')


            else:
                print(f'  {store["hostname"]}: OVA Deployed')
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)

    # PING STATUS: Scan OVA Deployed stores and check if they're ping-able

    print('Scanning stores with status - OVA Deployed')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'OVA Deployed':
            response = ping(store['mgmt-ipv4-addr'].replace(mask,''))
            if (response is None) or (not response):
                print(f'  {store["hostname"]}: Not Pingable')
            else:
                print(f'  {store["hostname"]}: Pingable - Moving to next step')
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)

    # SSH STATUS: Scan Pingable stores and see if SSH works

    print('Scanning stores with status - Pingable')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'Pingable':
            storessh = ios(store['mgmt-ipv4-addr'].replace(mask,''), store['login-username'], store['login-password'])
            print(f'  {store["hostname"]}: {storessh.status}')
            if storessh.status == 'Connected':
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)
                storessh.disconnect()

    # SCP CONFIG: Scan SSH Works stores, enable SCP, copy sdwan config

    print('Scanning stores with status - SSH Works')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'SSH Works':
            storessh = ios(store['mgmt-ipv4-addr'].replace(mask,''), store['login-username'], store['login-password'])
            storessh.send_command(command='config terminal', expect='config')
            storessh.send_command(command='ip scp server enable', expect='config')
            storessh.send_command(command='exit', expect='#')
            storessh.send_file(f'{configdir}{store["hostname"]}.cfg', 'ciscosdwan_cloud_init.cfg')
            response = storessh.send_command('dir').split('\n')
            result = 'SDWAN config SCP Fail. Will re-attempt'
            for line in response:
                if line.find('ciscosdwan_cloud_init.cfg') > -1:
                    result = 'SDWAN config SCP Success'
                    storeStatuses[store['hostname']] += 1
                    write_status(storeStatuses)
            print(f'  {store["hostname"]}: {result}')
            storessh.disconnect()

    # CONTROLLER-MODE ENABLE: Scan Config Copied Stores and enable Controller Mode

    print('Scanning stores with status - Config Copied')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'Config Copied':
            storessh = ios(store['mgmt-ipv4-addr'].replace(mask,''), store['login-username'], store['login-password'])
            response = storessh.send_command('controller-mode enable', 'confirm').split('\n')
            try:
                response = storessh.send_command('\n', '#').split('\n')
            except:
                response = 'Not Reachable'
            result = 'Success'
            storeStatuses[store['hostname']] += 1
            write_status(storeStatuses)
            print(f'  {store["hostname"]}: {result}')

    # CHECK CONTROL CONNECTION: Scan Awaiting Registration stores and see if they're registered to vManage
    # Uses vManage API to check registration status of device by system-ip in parameters.csv

    print('Scanning stores with status - Awaiting Registration')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'Awaiting Registration':
            vmsess = rest_api_lib(vmanage, vmanageUser, vmanagePassword)
            try:
                sdwanStatus = vmsess.get_request(f'device?deviceId={store["system-ip"]}')['data'][0]['reachability']
            except:
                sdwanStatus = 'Unreachable'
            vmsess.logout()
            if sdwanStatus == 'reachable':
                print(f'  {store["hostname"]}:  Registered to vManage')
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)
            else:
                print(f'  {store["hostname"]}:  Unreachable')

    # VEDGE-CLOUD ACTIVATE: Scan Registered stores and and send vedge-cloud activate command

    print('Scanning stores with status - Registered')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'Registered':
            try:
                storessh = ios(store['mgmt-ipv4-addr'].replace(mask,''), store['login-username'], store['login-password'])
                command = f'request platform software sdwan vedge_cloud activate \
                    chassis-number {store["uuid"]} token {store["otp"]}'
                response = storessh.send_command(command)
                storessh.disconnect()
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)
                print(f'  {store["hostname"]}:  Activate Command Sent')
                pring(f'    {command}')
            except Exception as e:
                print(f'  {store["hostname"]}:  SSH Error\n{e}')

    # CERTIFICATE INSTALLED: Scan Activate Command Sent stores and check certificate status

    print('Scanning stores with status - Activate Command Sent')
    for store in stores:
        vmsess = rest_api_lib(vmanage, vmanageUser, vmanagePassword)
        sdwanStatus = vmsess.get_request(f'certificate/vedge/list?model=vedge-C8000V')['data']
        vmsess.logout()
        if Statuses[int(storeStatuses[store['hostname']])] == 'Activate Command Sent':
            certStatus = 'Unknown'
            for edge in sdwanStatus:
                try:
                    if edge['system-ip'] == store['system-ip']:
                        certStatus = edge['vedgeCertificateState']
                        break
                except:
                    certStatus = 'Unknown'
            print(f'  {store["hostname"]}:  Certificate Status - {certStatus}')
            if certStatus == 'certinstalled':
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)
                storesCompleted += 1

    # DEPLOYMENT STATUS REPORT: Print Current Status of stores

    print('\n------------ Current status of stores -----------------------------------------')
    for store in stores:
        print(f'  {store["hostname"]}: {Statuses[int(storeStatuses[store["hostname"]])]}')

    if storesCompleted < len(stores):
        for time in range(sleeptime, 0, -1):
            print(f'{time} seconds before next run.', end='\r')
            sleep(1)

    # COMPLETION: Finish when all stores are 'Certificate Installed' status, or continue iteration.
