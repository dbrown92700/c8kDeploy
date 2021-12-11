#!/usr/bin/env python3

from includes import esxUser, esxPassword, configdir, sleeptime, sourceOva, mask, logdir
from includes import ovftoolthreads, ovftoolpath, interfacemap, VMname
from includes import vmanage, vmanageUser, vmanagePassword
from ios import ios
from ping3 import ping
import os, sys
import subprocess
from time import sleep
import threading
from vmanage_api import rest_api_lib
from datetime import datetime

# Definition of the phases of C8K deployment

Statuses = ['Not Started', 'OVA Deploying', 'OVA Deployed', 'Pingable', 'SSH Works', 'Config Copied', \
            'Awaiting Registration', 'Registered', 'Activate Command Sent', 'Certificate Installed', \
            'OVA Deployment Failed']
storesCompleted = 0

# Write current statuses of each C8Kv deployment to status.csv

def write_status(statuses):
    with open(f'{configdir}status.temp', 'w') as statusFile:
        for hostname in statuses:
            statusFile.write(f'{hostname},{statuses[hostname]}\n')
    os.replace(f'{configdir}status.temp', f'{configdir}status.csv')

def timestamp():
    t = datetime.now()
    return f'{t.day:02}/{t.month:02}/{t.year} {t.hour:02}:{t.minute:02}:{t.second:02}'


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

        ovfcommand = f'--name={self.Store["hostname"]}\
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
        stdoutFile.close()
        stderrFile.close()
        if result == 0:
            print(f'***THREAD COMPLETE Status {result}*** {self.Store["hostname"]} OVA Deployment Complete ***')
        else:
            with open(f'{logdir}{self.Store["hostname"]}console.log') as stdoutFile:
                print(f'\n\n{self.Store["hostname"]} OVA Deployment Finished with ERROR CONDITION ******************\n\n')
                for line in stdoutFile.readlines():
                    print(line, end='')
                print(f'{self.Store["hostname"]} OVA Deployment Finished with ERROR CONDITION ******************\n\n')
        return result



# Logger class is used to send console output to a file and console simultaneously

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout

    def open(self, logfile):
        self.log = open(logfile, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


    # ################################ BEGIN MAIN PROGRAM ##########################

# Mirror console stdout output to log file
sys.stdout = Logger()
sys.stdout.open(f'{logdir}console.log')

    # ################################ DATA COLLECTION PHASE ##########################
# Load status data stored from previous run

storeStatuses = {}
print(f'--------- Beginning Statuses --- {timestamp()} -----------------------------------------------')
try:
    statusfile = open(f'{configdir}status.csv', 'r', encoding='utf-8-sig')
    noStatus = False
    for line in statusfile:
        data = line.strip('\n').split(',')
        storeStatuses[data[0]] = int(data[1])
        if Statuses[int(data[1])] == 'Certificate Installed' or \
                Statuses[int(data[1])] == 'OVA Deployment Failed':
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
    values['activateTime'] = datetime.now()
    stores.append(values)

write_status(storeStatuses)

# Generate bootstrap files for all C8K in vManage mode in tokengenerated state
# Download all bootstrap files.  If hostname is in the parameters list, save as hostname.cfg

storeList = list(storeStatuses.keys())
print('---------Download all bootstrap configs for Cat8000v attached to templates ---------')
vmsess = rest_api_lib(vmanage, vmanageUser, vmanagePassword)
bootDevices = vmsess.get_request('system/device/vedges?model=vedge-C8000V&state=bootstrapconfiggenerated')['data']
tokenDevices = vmsess.get_request('system/device/vedges?model=vedge-C8000V&state=tokengenerated')['data']
bootDevices = tokenDevices + bootDevices
vmsess.logout()
for device in bootDevices:
    print(f'  {device["uuid"]}: {device["configOperationMode"]}')
    if device['configOperationMode'] == 'vmanage':
        if device['vedgeCertificateState'] == 'tokengenerated':
            print('    Bootstrap config not generated.  Generating now.')
        else:
            print('    Bootstrap already generated.')
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
                    print(f'    Saved {filename} config')
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

    t = datetime.now()
    print(f'------------------------- Run {runNumber} --- {timestamp()} ------------------------------------------')
    runNumber += 1

    # OVA PUSH START: Scan Not Started stores and begin an OVF deployment

    print('Scanning stores with status - Not Started')
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'Not Started':

            if threading.active_count() < (ovftoolthreads + 1):
                storedata = dict(store)
                store['ovaThread'] = deployOVA(storedata)
                store['ovaResult'] = store['ovaThread'].start()
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
                if store['ovaResult'] == 0:
                    print(f'  {store["hostname"]}: OVA Deployed')
                    storeStatuses[store['hostname']] += 1
                    write_status(storeStatuses)
                else:
                    print(f'  {store["hostname"]}: OVA Deployment Failed')
                    storeStatuses[store['hostname']] = Statuses.index('OVA Deployment Failed')
                    write_status(storeStatuses)
                    storesCompleted += 1

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
                print('    SSH Works - Moving to next step')

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
                    result = 'SDWAN config SCP Success. Moving to next step.'
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
            storeStatuses[store['hostname']] += 1
            write_status(storeStatuses)
            print(f'  {store["hostname"]}: controller-mode enable Command Sent. Moving to next step')

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
                print(f'  {store["hostname"]}:  Registered to vManage. Moving to next step')
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
                command = 'request platform software sdwan vedge_cloud activate '
                command += f'chassis-number {store["uuid"]} token {store["otp"]}'
                response = storessh.send_command(command)
                storessh.disconnect()
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)
                print(f'  {store["hostname"]}:  Activate Command Sent. Moving to next step')
                print(f'    {command}')
                store['activateTime'] = datetime.now()
            except Exception as e:
                print(f'  {store["hostname"]}:  SSH Error\n{e}')

    # CERTIFICATE INSTALLED: Scan Activate Command Sent stores and check certificate status

    print('Scanning stores with status - Activate Command Sent')
    sdwanStatus = ''
    for store in stores:
        if Statuses[int(storeStatuses[store['hostname']])] == 'Activate Command Sent':
            if sdwanStatus == '':
                vmsess = rest_api_lib(vmanage, vmanageUser, vmanagePassword)
                sdwanStatus = vmsess.get_request(f'certificate/vedge/list?model=vedge-C8000V')['data']
                vmsess.logout()
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
                print(f'    {store["hostname"]} Install Complete')
                storeStatuses[store['hostname']] += 1
                write_status(storeStatuses)
                storesCompleted += 1
            else:
                lapsed = (datetime.now() - store['activateTime']).seconds
                print(f'     {lapsed} seconds since last Activate command.')
                if lapsed > 300:
                    print('       Over 5 minutes. Moving back to Registered state to retry.')
                    storeStatuses[store['hostname']] -= 1
                    write_status(storeStatuses)

    # DEPLOYMENT STATUS REPORT: Print Current Status of stores

    print(f'\n------------ Current status of stores --- {timestamp()} --------------------------------')
    for x in range(9):
        stats = list(storeStatuses.values())
        print(f'{Statuses[x]}:{stats.count(x):<3}', end=' ')
    print(f'Completed:{storesCompleted:<3}\n')
    for store in stores:
        print(f'  {store["hostname"]}: {Statuses[int(storeStatuses[store["hostname"]])]}')

    if storesCompleted < len(stores):
        print(f'-----------------------{storesCompleted} sites are fully complete.--------------------------------\n\n')
        sys.stdout.flush()
        print(f'    seconds before next run.', end='\r')
        for time in range(sleeptime, 0, -1):
            print(f'{time:3}', end='\r')
            sleep(1)
    else:
        print(f'{timestamp()}: All Sites completed.')
    print('\n\n')

    # COMPLETION: Finish when all stores are 'Certificate Installed' status, or continue iteration.
