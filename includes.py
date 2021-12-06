# VMWare information
# username and password
# name of the Cat8000v VM
# Number of simultaneous threads for deploying the VM to ESX servers
esxUser = 'root'
esxPassword = '10-9=One'
VMname = 'c8000v_ovftool5'
ovftoolthreads = 5

# Directories for OVA, configs and logs
# Configs and logs will be generated automatically
# parameters.csv must be saved in the config directory
# A deployment status file will be generated in the config directory and is used in case the program is interrupted
sourceOva = '/Users/davibrow/Downloads/Cat8Kv/pythonscript/ovasource/c8000v.ova'
configdir = '/Users/davibrow/Downloads/Cat8Kv/pythonscript/configs/'
logdir = '/Users/davibrow/Downloads/Cat8Kv/pythonscript/logs/'

# vManage ip or hostname, username, & password
vmanage = 'vmanage.secmob.com'
vmanageUser = 'davibrow'
vmanagePassword = '10-9=One'

# Mask for the management IP (i.e. '/24').  This will be stripped off the mgmt-ipv4-addr field and used for ssh
mask = '/24'

# Wait time between successive deployment scans and updates
sleeptime = 5
