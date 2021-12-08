# Adding Interfaces to the OVA file
The original OVA from Cisco Systems only includes 3 interfaces.  If additional interfaces are needed they can be added through the use of the [Common OVF Tool (COT)](https://cot.readthedocs.io) and the ```ovftool``` command from VMware.\

## COT installation
Be sure to install the COT tool using the instructions at ]this page](https://cot.readthedocs.io/en/latest/installation.html).

## COT parameters
Use the ```-o output.ova``` paramter to specify the name of the new OVA
Use the ```--nics X``` parameter to specify the number of interfaces.\
Use the ```--nic-name "GigabitEthernet{1}"``` parameter to specify the interface name pattern.\
Use the ```--nic-types "VMXNET3"``` parameter to specify the type of interface.\
Use the ```--nic-networks "PG name 1" "PG name 2" ...``` to map VMware port-group names to VM interfaces\
Use the ```--network-descriptions "PG name 1" "PG name 2" ...``` to provide interface descriptions\

## COT example
Here is an example of adding additional interfaces to the original OVA file:
```
> cot edit-hardware ./c8000v-universalk9.17.04.02.ova -o c8k-01.ova \
    --nics 9 \
    --nic-name "GigabitEthernet{1}" \
    --nic-types "VMXNET3" \
    --nic-networks "StoreMgmtNet" \
                   "StoreLAN" \
                   "SDW-IOT-VPN20" \
                   "SDW-PUB-WIFI-VPN20" \
                   "WAN-MPLS-VS0" \
                   "WAN-LTE" \
                   "SDW-MIS-VPN0" \
                   "SDW-BB-VPN0" \
                   "WAN-MIS-VS0" \
    --network-descriptions "StoreMgmtNet" \
                           "StoreLAN" \
                           "SDW-IOT-VPN20" \
                           "SDW-PUB-WIFI-VPN20" \
                           "WAN-MPLS-VS0" \
                           "WAN-LTE" \
                           "SDW-MIS-VPN0" \
                           "SDW-BB-VPN0" \
                           "WAN-MIS-VS0"
NOTICE  : Unrecognized product class 'com.cisco.c8000v'. Treating this as a generic platform.
Network StoreMgmtNet is not currently defined. Create it? [y]
Network StoreLAN is not currently defined. Create it? [y]
Network SDW-IOT-VPN20 is not currently defined. Create it? [y]
Network SDW-PUB-WIFI-VPN20 is not currently defined. Create it? [y]
Network WAN-MPLS-VS0 is not currently defined. Create it? [y]
Network WAN-LTE is not currently defined. Create it? [y]
Network SDW-MIS-VPN0 is not currently defined. Create it? [y]
Network SDW-BB-VPN0 is not currently defined. Create it? [y]
Network WAN-MIS-VS0 is not currently defined. Create it? [y]
NOTICE  : Removing unused network GigabitEthernet1
NOTICE  : Removing unused network GigabitEthernet2
NOTICE  : Removing unused network GigabitEthernet3
>

>
> cot info c8k-01.ova
NOTICE  : Unrecognized product class 'com.cisco.c8000v'. Treating this as a generic platform.
-------------------------------------------------------------------------------------------------------------------------------------------
c8k-01.ova
-------------------------------------------------------------------------------------------------------------------------------------------
Product:  Cisco C8000V
          http://www.cisco.com/en/US/products/ps12559/index.html
Vendor:   Cisco Systems, Inc.
          http://www.cisco.com
Version:  17.04.02
          Cisco IOS-XE Software, version 17.04.02

Files and Disks:                      File Size  Capacity Device
                                      --------- --------- --------------------
  c8000v_harddisk_8G.vmdk               707 KiB     8 GiB
  c8000v_harddisk_16G.vmdk            1.316 MiB    16 GiB
  README-OVF.txt                      8.535 KiB
  c8000v-universalk9_vga.17.04.02.iso 771.1 MiB           cdrom @ IDE 1:0

Hardware Variants:
  System types:             vmx-10 vmx-11 vmx-13
  SCSI device types:        VirtualSCSI
  Ethernet device types:    VMXNET3

Configuration Profiles:   CPUs    Memory NICs Serials Disks/Capacity
                          ---- --------- ---- ------- --------------
  1CPU-4GB-16GB (default)    1     4 GiB    9       0  1 /    24 GiB
    Label:          "Small- 16GB Disk"
    Description:    "Minimal hardware profile - 1 vCPU, 4 GB RAM, 16 GB Disk"
  1CPU-4GB-8GB               1     4 GiB    9       0  1 /    24 GiB
    Label:          "Small - 8GB Disk"
    Description:    "Minimal hardware profile - 1 vCPU, 4 GB RAM, 8 GB Disk"
  2CPU-4GB-8GB               2     4 GiB    9       0  1 /    24 GiB
    Label:          "Medium - 8GB Disk"
    Description:    "Medium hardware profile - 2 vCPUs, 4 GB RAM, 8 GB Disk"
  4CPU-4GB-8GB               4     4 GiB    9       0  1 /    24 GiB
    Label:          "Large - 8GB Disk"
    Description:    "Large hardware profile - 4 vCPUs, 4 GB RAM, 8 GB Disk"
  4CPU-8GB-8GB               4     8 GiB    9       0  1 /    24 GiB
    Label:          "Large + DRAM Upgrade - 8GB Disk"
    Description:    "Large hardware profile (requires purchase of DRAM upgrade SKU) - 4 vCPUs, 8 GB RAM, 8 GB Disk"
  2CPU-4GB-16GB              2     4 GiB    9       0  1 /    24 GiB
    Label:          "Medium - 16GB Disk"
    Description:    "Medium hardware profile - 2 vCPUs, 4 GB RAM, 16 GB Disk"
  4CPU-4GB-16GB              4     4 GiB    9       0  1 /    24 GiB
    Label:          "Large - 16GB Disk"
    Description:    "Large hardware profile - 4 vCPUs, 4 GB RAM, 16 GB Disk"
  4CPU-8GB-16GB              4     8 GiB    9       0  1 /    24 GiB
    Label:          "Large + DRAM Upgrade - 16GB Disk"
    Description:    "Large hardware profile (requires purchase of DRAM upgrade SKU) - 4 vCPUs, 8 GB RAM, 16 GB Disk"

Networks:
  StoreMgmtNet        "StoreMgmtNet"
  StoreLAN            "StoreLAN"
  SDW-IOT-VPN20       "SDW-IOT-VPN20"
  SDW-PUB-WIFI-VPN20  "SDW-PUB-WIFI-VPN20"
  WAN-MPLS-VS0        "WAN-MPLS-VS0"
  WAN-LTE             "WAN-LTE"
  SDW-MIS-VPN0        "SDW-MIS-VPN0"
  SDW-BB-VPN0         "SDW-BB-VPN0"
  WAN-MIS-VS0         "WAN-MIS-VS0"

NICs and Associated Networks:
  GigabitEthernet1 : StoreMgmtNet
  GigabitEthernet2 : StoreLAN
  GigabitEthernet3 : SDW-IOT-VPN20
  GigabitEthernet4 : SDW-PUB-WIFI-VPN20
  GigabitEthernet5 : WAN-MPLS-VS0
  GigabitEthernet6 : WAN-LTE
  GigabitEthernet7 : SDW-MIS-VPN0
  GigabitEthernet8 : SDW-BB-VPN0
  GigabitEthernet9 : WAN-MIS-VS0

Environment:
  Transport types: iso

Properties:
  <config-version>                                                                  "1.0"
  <hostname>                Router Name                                             ""
  <login-username>          Login Username                                          ""
  <login-password>          Login Password                                          ""
  <domain-name>             Domain Name                                             ""
  <mgmt-interface>          Management Interface                                    "GigabitEthernet1"
  <mgmt-vlan>               Management VLAN                                         ""
  <mgmt-ipv4-addr>          Management Interface IPv4 Address/Mask                  ""
  <mgmt-ipv4-gateway>       Management IPv4 Gateway                                 ""
  <mgmt-ipv4-network>       Management IPv4 Network                                 ""
  <pnsc-ipv4-addr>          PNSC IPv4 Address                                       ""
  <pnsc-agent-local-port>   PNSC Agent Local Port                                   ""
  <pnsc-shared-secret-key>  PNSC Shared Secret Key                                  ""
  <remote-mgmt-ipv4-addr>   Remote Management IPv4 Address (optional, deprecated)   ""
  <enable-scp-server>       Enable SCP Server                                       "false"
  <enable-ssh-server>       Enable SSH Login and Disable Telnet Login               "false"
  <enable-sdwan>            Enable SDWAN Feature                                    "false"
  <privilege-password>      Enable Password                                         ""
  <license>                 License boot level                                      "ax"
  <resource-template>       Resource template                                       "default"
  <vbond-ipv4-addr>         vBond Server IPv4 Address                               ""
  <otp>                     OTP                                                     ""
  <uuid>                    UUID                                                    ""
  <org>                     Organization                                            ""
>
>

```

This new OVA file is not yet useable by the ```ovftool``` from VMware.  In order to rectify that issue, the new OVA file must be extracted using ```tar``` and then re-archived into an OVA file using the ```ovftool```.  Here is an example of that process:

```
> ovftool c8k-01.ova
Error: Did not find an .ovf file at the beginning of the OVA package.
>
>
> tar -xvf c8k-01.ova
c8k-01.ovf
c8k-01.mf
c8000v_harddisk_8G.vmdk
c8000v_harddisk_16G.vmdk
README-OVF.txt
c8000v-universalk9_vga.17.04.02.iso
>
> ovftool c8k-01.ovf c8k-02.ova
Opening OVF source: c8k-01.ovf
The manifest validates
Opening OVA target: c8k-02.ova
Writing OVA package: c8k-02.ova
Transfer Completed
Completed successfully
>

```


The new OVA file should be readable via ```ovftool``` without error:

```
> ovftool c8k-02.ova
OVF version:   1.0
VirtualApp:    false
Name:          Cisco C8000V
Version:       17.04.02
Full Version:  Cisco IOS-XE Software, version 17.04.02
Vendor:        Cisco Systems, Inc.
Product URL:   http://www.cisco.com/en/US/products/ps12559/index.html
Vendor URL:    http://www.cisco.com

Download Size:  772.39 MB

Deployment Sizes:
  Flat disks:   16.75 GB
  Sparse disks: 1.03 GB

Networks:
  Name:        StoreMgmtNet
  Description: StoreMgmtNet

  Name:        StoreLAN
  Description: StoreLAN

  Name:        SDW-IOT-VPN20
  Description: SDW-IOT-VPN20

  Name:        SDW-PUB-WIFI-VPN20
  Description: SDW-PUB-WIFI-VPN20

  Name:        WAN-MPLS-VS0
  Description: WAN-MPLS-VS0

  Name:        WAN-LTE
  Description: WAN-LTE

  Name:        SDW-MIS-VPN0
  Description: SDW-MIS-VPN0

  Name:        SDW-BB-VPN0
  Description: SDW-BB-VPN0

  Name:        WAN-MIS-VS0
  Description: WAN-MIS-VS0

Virtual Machines:
  Name:               Cisco Catalyst 8000V Edge Router
  Operating System:   other3xlinux64guest
  Virtual Hardware:
    Families:         vmx-10 vmx-11 vmx-13
    Number of CPUs:   1
    Cores per socket: 1
    Memory:           4.00 GB

    Disks:
      Index:          0
      Instance ID:    5
      Capacity:       16.00 GB
      Disk Types:     SCSI-VirtualSCSI

    NICs:
      Adapter Type:   VMXNET3
      Connection:     StoreMgmtNet

      Adapter Type:   VMXNET3
      Connection:     StoreLAN

      Adapter Type:   VMXNET3
      Connection:     SDW-IOT-VPN20

      Adapter Type:   VMXNET3
      Connection:     SDW-PUB-WIFI-VPN20

      Adapter Type:   VMXNET3
      Connection:     WAN-MPLS-VS0

      Adapter Type:   VMXNET3
      Connection:     WAN-LTE

      Adapter Type:   VMXNET3
      Connection:     SDW-MIS-VPN0

      Adapter Type:   VMXNET3
      Connection:     SDW-BB-VPN0

      Adapter Type:   VMXNET3
      Connection:     WAN-MIS-VS0

Properties:
  ClassId:     com.cisco.c8000v
  Key:         hostname
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Router Name
  Type:        string(..63)
  Description: Hostname of this router

  ClassId:     com.cisco.c8000v
  Key:         login-username
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Login Username
  Type:        string(..64)
  Description: Username for remote login

  ClassId:     com.cisco.c8000v
  Key:         login-password
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Login Password
  Type:        password(..25)
  Description: Password for remote login.
               WARNING: While this password will be stored securely within IOS,
               the plain-text password will be recoverable from the OVF
               descriptor file.

  ClassId:     com.cisco.c8000v
  Key:         domain-name
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Domain Name
  Type:        string(..238)
  Description: Network domain name (such as "cisco.com")

  ClassId:     com.cisco.c8000v
  Key:         mgmt-interface
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Management Interface
  Type:        string
  Description: Management interface (such as "GigabitEthernet1" or
               "GigabitEthernet1.100")
  Value:       GigabitEthernet1

  ClassId:     com.cisco.c8000v
  Key:         mgmt-vlan
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Management VLAN
  Type:        string(..5)
  Description: Management dot1Q VLAN (requires specifying a subinterface such
               as "GigabitEthernet1.100" for the Management Interface)

  ClassId:     com.cisco.c8000v
  Key:         mgmt-ipv4-addr
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Management Interface IPv4 Address/Mask
  Type:        string(..33)
  Description: IPv4 address and mask for management interface (such as
               "192.0.2.100/24" or "192.0.2.100 255.255.255.0"), or "dhcp" to
               configure via DHCP

  ClassId:     com.cisco.c8000v
  Key:         mgmt-ipv4-gateway
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Management IPv4 Gateway
  Type:        string(..16)
  Description: IPv4 gateway address (such as "192.0.2.1") for management
               interface, or "dhcp" to configure via DHCP

  ClassId:     com.cisco.c8000v
  Key:         mgmt-ipv4-network
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Management IPv4 Network
  Type:        string(..33)
  Description: IPv4 Network (such as "192.168.2.0/24" or "192.168.2.0
               255.255.255.0") that the management gateway should route to.

  ClassId:     com.cisco.c8000v
  Key:         pnsc-ipv4-addr
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       PNSC IPv4 Address
  Type:        string(..15)
  Description: IPv4 address without mask (such as "192.0.2.110") of PNSC
               service controller

  ClassId:     com.cisco.c8000v
  Key:         pnsc-agent-local-port
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       PNSC Agent Local Port
  Type:        string(..5)
  Description: PNSC service agent SSL port (on local C8000V) to receive
               policies from service manager.
               The port shall be in the range of [55001, 61000] if shared IP is
               used, i.e., Remote Management IPv4 Address is not configured.

  ClassId:     com.cisco.c8000v
  Key:         pnsc-shared-secret-key
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       PNSC Shared Secret Key
  Type:        password(..64)
  Description: PNSC service controller shared secret key (8-64 characters) for
               PNSC agent to get SSL certificate from the controller.
               WARNING: While this password will be stored securely within IOS,
               the plain-text password will be recoverable from the OVF
               descriptor file.

  ClassId:     com.cisco.c8000v
  Key:         remote-mgmt-ipv4-addr
  InstanceId   1
  Category:    1. Bootstrap Properties
  Label:       Remote Management IPv4 Address (optional, deprecated)
  Type:        string(..15)
  Description: Secondary IPv4 address without mask (such as "192.0.2.101") for
               access to remote management features (REST API, etc.). This
               should be in the same IP subnet as the Management Interface IPv4
               Address entered above.
               Warning: THIS IS A DEPRECATED OPTION IN THIS RELEASE.

  ClassId:     com.cisco.c8000v
  Key:         enable-scp-server
  InstanceId   1
  Category:    2. Features
  Label:       Enable SCP Server
  Type:        boolean
  Description: Enable IOS SCP server feature
  Value:       False

  ClassId:     com.cisco.c8000v
  Key:         enable-ssh-server
  InstanceId   1
  Category:    2. Features
  Label:       Enable SSH Login and Disable Telnet Login
  Type:        boolean
  Description: Enable remote login via SSH and disable remote login via telnet.
               Requires login-username and login-password to be set!
  Value:       False

  ClassId:     com.cisco.c8000v
  Key:         enable-sdwan
  InstanceId   1
  Category:    2. Features
  Label:       Enable SDWAN Feature
  Type:        boolean
  Description: Disabled: fill out section 3. Enabled: fill out section 4.
  Value:       False

  ClassId:     com.cisco.c8000v
  Key:         privilege-password
  InstanceId   1
  Category:    3. Non-SDWAN Configuration Properties
  Label:       Enable Password
  Type:        password(..25)
  Description: Password for privileged (enable) access.
               WARNING: While this password will be stored securely within IOS,
               the plain-text password will be recoverable from the OVF
               descriptor file.

  ClassId:     com.cisco.c8000v
  Key:         license
  InstanceId   1
  Category:    3. Non-SDWAN Configuration Properties
  Label:       License boot level
  Type:        string(..30)
  Description: Configure license boot level(such as ax, security, appx, ipbase,
               lite, vacs)
  Value:       ax

  ClassId:     com.cisco.c8000v
  Key:         resource-template
  InstanceId   1
  Category:    3. Non-SDWAN Configuration Properties
  Label:       Resource template
  Type:        string(..30)
  Description: Configure Resource template(service_plane_medium,
               service_plane_heavy or default)
  Value:       default

  ClassId:     com.cisco.c8000v
  Key:         vbond-ipv4-addr
  InstanceId   1
  Category:    4. SDWAN Configuration Properties
  Label:       vBond Server IPv4 Address
  Type:        string(..15)
  Description: Address of the vBond server

  ClassId:     com.cisco.c8000v
  Key:         otp
  InstanceId   1
  Category:    4. SDWAN Configuration Properties
  Label:       OTP
  Type:        string(..32)
  Description: One Time Password

  ClassId:     com.cisco.c8000v
  Key:         uuid
  InstanceId   1
  Category:    4. SDWAN Configuration Properties
  Label:       UUID
  Type:        string(..64)
  Description: Universally Unique Identifier

  ClassId:     com.cisco.c8000v
  Key:         org
  InstanceId   1
  Category:    4. SDWAN Configuration Properties
  Label:       Organization
  Type:        string(..32)
  Description: Organization Name

Deployment Options:
  Id:          1CPU-4GB-8GB
  Label:       Small - 8GB Disk
  Description: Minimal hardware profile - 1 vCPU, 4 GB RAM, 8 GB Disk

  Id:          2CPU-4GB-8GB
  Label:       Medium - 8GB Disk
  Description: Medium hardware profile - 2 vCPUs, 4 GB RAM, 8 GB Disk

  Id:          4CPU-4GB-8GB
  Label:       Large - 8GB Disk
  Description: Large hardware profile - 4 vCPUs, 4 GB RAM, 8 GB Disk

  Id:          4CPU-8GB-8GB
  Label:       Large + DRAM Upgrade - 8GB Disk
  Description: Large hardware profile (requires purchase of DRAM upgrade SKU) -
               4 vCPUs, 8 GB RAM, 8 GB Disk

  Id:          1CPU-4GB-16GB  (default)
  Label:       Small- 16GB Disk
  Description: Minimal hardware profile - 1 vCPU, 4 GB RAM, 16 GB Disk

  Id:          2CPU-4GB-16GB
  Label:       Medium - 16GB Disk
  Description: Medium hardware profile - 2 vCPUs, 4 GB RAM, 16 GB Disk

  Id:          4CPU-4GB-16GB
  Label:       Large - 16GB Disk
  Description: Large hardware profile - 4 vCPUs, 4 GB RAM, 16 GB Disk

  Id:          4CPU-8GB-16GB
  Label:       Large + DRAM Upgrade - 16GB Disk
  Description: Large hardware profile (requires purchase of DRAM upgrade SKU) -
               4 vCPUs, 8 GB RAM, 16 GB Disk

References:
  File:  c8k-02-disk1.vmdk
  File:  c8k-02-disk2.vmdk
  File:  c8k-02-file1.txt
  File:  c8k-02-file2.iso


```

