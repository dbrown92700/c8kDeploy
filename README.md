# Cat8000v Mass Deployment to ESXi

## Overview

This python script can deploy Cisco Cat8000v routers to multiple VMWare ESXi servers in SDWAN mode.  Typical use case would be deploying multiple branch office sites with ESXi servers on Cisco SDWAN.

**Script Steps:**
- Uses a CSV list of sites with IP, username, hostname, etc. parameters
- Assumes that the user has previously attached templates to C8Kv's in vManage
- Downloads all bootstrap configs from vManage
- Pushes C8Kv's in autonomous mode to ESX with boot parameters from CSV file
- Identifies bootstrap files by hostname and SCP's config to each router
- Reboots routers into controller-mode
- Checks to make sure it registers to vManage
- Issues vedge_cloud activate command
- Checks for certificate installed status on vManage

**Features and Dependancies:**
- Requires VMWare ovftool to be installed and executable from cli without a path
- It's set up to run this for as many devices as you want at the same time
- Multi-threaded OVA push with a setting for number of simultaneous uploads
- Maps interfaces to VM Networks
- Limited to the number of interfaces in the OVA.  If more than the 3 default interfaces are needed, use cot to edit the OVA prior to running as documented in the C8000v installation docs

## Installation and Use:
1. Clone repository
2. Install requirements
> pip3 install -r requirements.txt
3. Create OVA, Config, and Log directories
4. Edit settings in includes.py.  See notes below in step 5
5. Add sites to parameters.csv and move to Config directory
  - Each site must have a c8000v attached to a template in vManage
  - credentials in this file are for the C8Kv.  Credentials for ESX are in includes.py
  - mgmt-ipv4-addr must be expressed in CIDR format (i.e. 10.1.1.1/24)
  - mask setting in includes.py should match mgmt-ipv4-addr.
  - mgmt-ipv4-addr must be reachable from script server via SSH / SCP both on initial deployment and in SDWAN mode
  - mgmt-ipv4-network is the network part of the route added to the initial config (i.e. 0.0.0.0/0 for default route)
  - hostname in parameters must match hostname attached to config in vManage
  - valid settings for deploymentOption (i.e. 1CPU-4GB-16GB) can be listed using "ovftool *cat8000v.ova*"
6. Place Cat8Kv OVA in OVA directory
7. In vManage, attach template to C8Kv(s)
8. In vManage, generate bootstrap config for C8Kv(s) with attached templates.  The script will take care of downloading the config.
9. Execute c8kdeploy.py

**Notes:**

Cat8Kv IP address, mgmt-ipv4-addr, must be reachable via SSH both during the initial deployment in autonomous mode and after the reboot into controller mode for script to complete.  There's no provision as written for this address to change.  In both modes, the address can be placed on any interface.  In controller mode, the address will normally have to be on the management interface or a service interface.  If the address is on the tunnel interface, "allow service sshd" must be configured on the tunnel to enable ssh.

Script creates status.csv file in config.dir.  The status.csv file format records which step each device is on at any moment.  It should allow the script to re-start successfully if it's interupted during the deployment.  If there are problems restarting an interrupted deployment it may be necessary to back a stuck site up a step by decrementing the value.  For example, if the script is interrupted, it will terminate any active threads pushing OVA's to ESX servers.  To reset that process you would need to move that site back to step 0 and possibly manually kill a stuck deploy process on the ESX server or delete the partially deployed VM on the ESX server.  The steps (0-9) correspond to the Statuses list in c8kdeploy.py:

0. 'Not Started'
1. 'OVA Deploying'
2. 'OVA Deployed'
3. 'Pingable'
4. 'SSH Works'
5. 'Config Copied'
6. 'Awaiting Registration'
7. 'Registered'
8. 'Activate Command Sent'
9. 'Certificate Installed'
