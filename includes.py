# VMWare information
# Username and password
# Final name of the Cat8000v VM on ESXi
# Interface map for C8Kv to VM Networks. Max of 3 interfaces unless you edit the OVA package to include more
# Python host path for ovftool
# Number of simultaneous uploads for deploying the VM to ESX servers
esxUser = 'root'
esxPassword = 'password'
VMname = 'c8000v_pyscript'
interfacemap = {
     'GigabitEthernet1': 'StoreMgmtNet',
     'GigabitEthernet2': 'StoreLAN',
     'GigabitEthernet3': 'SDW-IOT-VPN20'
}
ovftoolpath = '/Applications/VMware OVF Tool/'
ovftoolthreads = 2

# Directories for OVA, configs and logs
# Configs and logs will be generated automatically
# parameters.csv must be saved in the config directory
# A deployment status file will be generated in the config directory and is used in case the program is interrupted
sourceOva = '/Users/davibrow/Downloads/Cat8Kv/pythonscript/ovasource/c8000v.ova'
configdir = '/Users/davibrow/Downloads/Cat8Kv/pythonscript/configs/'
logdir = '/Users/davibrow/Downloads/Cat8Kv/pythonscript/logs/'

# vManage ip or hostname, username, & password
vmanage = 'vmanage.cisco.com'
vmanageUser = 'davibrow'
vmanagePassword = 'password'

# Mask for the management IP (i.e. '/24').  This will be stripped off the mgmt-ipv4-addr field and used for ssh
mask = '/24'

# Wait time in seconds between successive deployment scans and updates
sleeptime = 5
