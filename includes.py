# VMWare information
# username and password
# name of the Cat8000v VM
# Number of simultaneous threads for deploying the VM to ESX servers
esxUser = 'root'
esxPassword = 'password'
VMname = 'c8000v_pyscript'
interfacemap = '--net:"GigabitEthernet1"="StoreMgmtNet"\
             --net:"GigabitEthernet2"="StoreLAN"\
             --net:"GigabitEthernet3"="SDW-IOT-VPN20"'
ovftoolpath = '/Applications/VMware\ OVF\ Tool/'
ovftoolthreads = 5

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

# Wait time between successive deployment scans and updates
sleeptime = 5
