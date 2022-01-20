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
- Requires VMWare ovftool to be installed
- It's set up to run this for as many devices as you want at the same time
- Multi-threaded OVA push with a setting for number of simultaneous uploads
- Maps interfaces to VM Networks.
- See Modify_OVA.md document for details on adding more than the 3 interfaces included in default OVA

## Installation and Use:
1. Clone repository
2. Install requirements
> pip3 install -r requirements.txt
3. Ensure VMWare ovftool is installed
> https://developer.vmware.com/web/tool/4.4.0/ovf
5. Create OVA, Config, and Log directories
6. Edit settings in includes.py.  See notes below in step 7
7. Add sites to parameters.csv and move to Config directory
  - each site must have a c8000v attached to a template in vManage
  - credentials in this file are for the C8Kv.  Credentials for ESX are in includes.py
  - mgmt-ipv4-addr must be expressed in CIDR format (i.e. 10.1.1.1/24)
  - mask setting in includes.py should match mgmt-ipv4-addr.
  - mgmt-ipv4-addr must be reachable from script server via SSH / SCP both on initial deployment and in SDWAN mode
  - mgmt-ipv4-network is the network part of the route added to the initial config (i.e. 0.0.0.0/0 for default route)
  - hostname in parameters must match hostname attached to config in vManage
  - valid settings for deploymentOption (i.e. 1CPU-4GB-16GB) can be listed using "ovftool *cat8000v.ova*"
8. Place Cat8Kv OVA in OVA directory
9. In vManage, attach template to C8Kv(s).  Hostname must match the parameters file.  The script will generate and download the bootstrap file.
10. Execute c8kdeploy.py

**Notes:**

Cat8Kv IP address, mgmt-ipv4-addr, must be reachable via SSH both during the initial deployment in autonomous mode and after the reboot into controller mode for script to complete.  There's no provision as written for this address to change.  In both modes, the address can be placed on any interface.  In controller mode, the address will normally have to be on the management interface or a service interface.  If the address is on the tunnel interface, "allow service sshd" must be configured on the tunnel to enable ssh.

Script creates status.csv file in config.dir.  The status.csv file format records which step each device is on at any moment.  It should allow the script to re-start successfully if it's interupted during the deployment.  If there are problems restarting an interrupted deployment it may be necessary to back a stuck site up a step by decrementing the value.  For example, if the script is interrupted, it will terminate any active threads pushing OVA's to ESX servers.  To reset that process you would need to move that site back to step 0 and possibly manually kill a stuck deploy process on the ESX server or delete the partially deployed VM on the ESX server.  The steps (0-10) correspond to the Statuses list in c8kdeploy.py.

## Script Steps and Statuses

### Data Phase:

- reads in data from parameters.csv
- reads in data from status.csv if this deployment was previously run and stopped
- scans vManage API for all C8Kv devices with templates attached (in vManage mode) and in "tokengenerated" (undeployed) status.  Generates and downloads bootstrap configs for all of these.  Saves configs with hostnames that match the parameters.csv file
- Checks that all sites have a config.  If any are missing, prints a list and terminates.

### Deployment Phase:

Iterates through all sites repeatedly moving them through the following steps until all sites are complete or failed.

0. **'Not Started'**:
- The deployment host has successfully generated and downloaded a bootstrap config for this site.
- Executes the ovftool command.
1. **'OVA Deploying'**:
- The OVA is uploading to the ESX server, and progress % will be printed on subsequent runs.
- A "Thread Complete" message will be printed when the command is done executing.  If status is not "0" (Success), the ovftool console messages will be printed for troubleshooting and the site status will be moved to "OVA Deployment Failed"
2. **'OVA Deployed'**:
- ovftool command has completed successfully.
- The deployment host attempts to ping the C8K IP for that site.
3. **'Pingable'**:
- Ping works
- The deployment host attempts to SSH into the C8K IP address.
4. **'SSH Works'**:
- SSH works
- Uses scp to copy the site config to the C8K bootflash://ciscosdwan_cloud_init.cfg.
5. **'Config Copied'**:
- SCP complete.
- Uses ssh to issue the "controller-mode enable" command.
6. **'Awaiting Registration'**:
- The C8K will be rebooting into SDWAN mode and loading the bootstrap config during this time.
- Uses vManage API to look for the C8K to connect to vManage,
7. **'Registered'**:
- The vManage API shows the C8K connected.
- The deployment host uses ssh to issue the "vedge-cloud activate" command.
8. **'Activate Command Sent'**:
- vedge-cloud activate command sent.
- The deployment host uses the vManage API to check the the C8K certificate status.
9. **'Certificate Installed'**:
- The certificate status is "certinstalled".
- The deployment is complete.
10. **'OVA Deployment Failed'**:
- The ovftool command returned an error.
- Remaining steps were skipped and no further action will be taken.

## Author

This project was written and is maintained by the following individuals:

* David Brown <davibrow@cisco.com>
