# Modifying the original OVA
The original OVA file from Cisco Systems a number of different deployment options for various CPU core counts, Memory and Disk sizes.  The original OVA also includes only three network interface definitions.

It is likely that the OVA will need to be modified to include only one deployment option and also have additional network interface cards defined.

Those changes to the OVA can be made through the use of two tools.  The [Common OVF Tool (COT)](https://cot.readthedocs.io) can be used to remove all but the desired deployment option, as well as to add additional network interface definitions.

The resulting OVA file must then be modified by the VMware [ovftool](https://developer.vmware.com/web/tool/4.4.0/ovf) tool to create an OVA tool that can be used for deployment.  Please download the appropriate ```ovftool``` for your operating system and ensure it is in your PATH.


## COT Installation:
Install the ```cot``` tool by following the instructions provided at [this link](https://cot.readthedocs.io/en/latest/installation.html).

## OVA Deployment Option (profile) selection:
All but the desired deployment option, or profile, must be removed from the original OVA file:

```
> cot edit-hardware c8000v-universalk9.17.04.02.ova -o c8k-01.ova -p "4CPU-8GB-8GB" --delete-all-other-profiles
NOTICE  : Unrecognized product class 'com.cisco.c8000v'. Treating this as a generic platform.
Delete profile 1CPU-4GB-16GB? [y]
NOTICE  : Deleting configuration profile 1CPU-4GB-16GB
Delete profile 4CPU-4GB-8GB? [y]
NOTICE  : Deleting configuration profile 4CPU-4GB-8GB
Delete profile 1CPU-4GB-8GB? [y]
NOTICE  : Deleting configuration profile 1CPU-4GB-8GB
Delete profile 4CPU-8GB-16GB? [y]
NOTICE  : Deleting configuration profile 4CPU-8GB-16GB
Delete profile 4CPU-4GB-16GB? [y]
NOTICE  : Deleting configuration profile 4CPU-4GB-16GB
Delete profile 2CPU-4GB-8GB? [y]
NOTICE  : Deleting configuration profile 2CPU-4GB-8GB
Delete profile 2CPU-4GB-16GB? [y]
NOTICE  : Deleting configuration profile 2CPU-4GB-16GB
>
```

The resulting OVA file is not compatible with the ```ovftool``` and checking the OVA file against ```ovftool`` displays an error about an OVF file:

```
> ovftool c8k-01.ova
Error: Did not find an .ovf file at the beginning of the OVA package.
>
```

To rectify this, the OVA file must be extracted to its components to reveal the internal files of the OVA, including the OVF file:

```
> tar -xvf c8k-01.ova
c8k-01.ovf
c8k-01.mf
c8000v_harddisk_8G.vmdk
c8000v_harddisk_16G.vmdk
README-OVF.txt
c8000v-universalk9_vga.17.04.02.iso
>
```

To see where the errors are in the OVF file, run the ```ovftool``` against that ovf file:

```
> ovftool c8k-01.ovf
Error:
 - Line 58: Duplicate element 'InstanceID'.
 - Line 77: Duplicate element 'InstanceID'.
 - Line 108: Duplicate element 'InstanceID'.
>
```

These line numbers refer to ```<ovf:Item> </ovf:Item>``` sections in the OVF file where there are multiple entries for VCPUs, Memory, and Disk sizes.  Here is an example of where there are two VCPU sections around line 58:

```
      <ovf:Item>
        <rasd:AllocationUnits>hertz * 10^6</rasd:AllocationUnits>
        <rasd:Description>Number of Virtual CPUs</rasd:Description>
        <rasd:ElementName>1 virtual CPU(s)</rasd:ElementName>
        <rasd:InstanceID>1</rasd:InstanceID>
        <rasd:ResourceType>3</rasd:ResourceType>
        <rasd:VirtualQuantity>1</rasd:VirtualQuantity>
        <pasd:InstructionSet ovf:required="false">DMTF:x86:64</pasd:InstructionSet>
        <pasd:InstructionSetExtensionName ovf:required="false">DMTF:x86:SSE2 DMTF:x86:SSE3 DMTF:x86:SSSE3</pasd:InstructionSetExtensionName>
        <vmw:CoresPerSocket ovf:required="false">1</vmw:CoresPerSocket>
      </ovf:Item>
      <ovf:Item ovf:configuration="4CPU-8GB-8GB">
        <rasd:AllocationUnits>hertz * 10^6</rasd:AllocationUnits>
        <rasd:Description>Number of Virtual CPUs</rasd:Description>
        <rasd:ElementName>4 virtual CPU(s)</rasd:ElementName>
        <rasd:InstanceID>1</rasd:InstanceID>
        <rasd:ResourceType>3</rasd:ResourceType>
        <rasd:VirtualQuantity>4</rasd:VirtualQuantity>
        <pasd:InstructionSet ovf:required="false">DMTF:x86:64</pasd:InstructionSet>
        <pasd:InstructionSetExtensionName ovf:required="false">DMTF:x86:SSE2 DMTF:x86:SSE3 DMTF:x86:SSSE3</pasd:InstructionSetExtensionName>
        <vmw:CoresPerSocket ovf:required="false">1</vmw:CoresPerSocket>
      </ovf:Item>
```

The first ```<ovf:Item> </ovf:Item>``` should be removed, leaving the section that explictly calls out the desired deployment (profile) option.

Do this for VCPUs, Memory, and Disk sections as noted in the output from ```ovftool``` as referenced above.

Once complete, if you saved an original copy of the OVF file before editing, you should be able to see an output from ```diff` against the original and new file similar to the following:

```
> diff c8k-01.ovf__original c8k-01.ovf
47,57d46
<       <ovf:Item>
<         <rasd:AllocationUnits>hertz * 10^6</rasd:AllocationUnits>
<         <rasd:Description>Number of Virtual CPUs</rasd:Description>
<         <rasd:ElementName>1 virtual CPU(s)</rasd:ElementName>
<         <rasd:InstanceID>1</rasd:InstanceID>
<         <rasd:ResourceType>3</rasd:ResourceType>
<         <rasd:VirtualQuantity>1</rasd:VirtualQuantity>
<         <pasd:InstructionSet ovf:required="false">DMTF:x86:64</pasd:InstructionSet>
<         <pasd:InstructionSetExtensionName ovf:required="false">DMTF:x86:SSE2 DMTF:x86:SSE3 DMTF:x86:SSSE3</pasd:InstructionSetExtensionName>
<         <vmw:CoresPerSocket ovf:required="false">1</vmw:CoresPerSocket>
<       </ovf:Item>
69,76d57
<       <ovf:Item>
<         <rasd:AllocationUnits>byte * 2^20</rasd:AllocationUnits>
<         <rasd:Description>Memory Size</rasd:Description>
<         <rasd:ElementName>4096MB of memory</rasd:ElementName>
<         <rasd:InstanceID>2</rasd:InstanceID>
<         <rasd:ResourceType>4</rasd:ResourceType>
<         <rasd:VirtualQuantity>4096</rasd:VirtualQuantity>
<       </ovf:Item>
99,106d79
<       </ovf:Item>
<       <ovf:Item>
<         <rasd:AddressOnParent>0</rasd:AddressOnParent>
<         <rasd:ElementName>Hard Drive</rasd:ElementName>
<         <rasd:HostResource>ovf:/disk/vmdisk2</rasd:HostResource>
<         <rasd:InstanceID>5</rasd:InstanceID>
<         <rasd:Parent>3</rasd:Parent>
<         <rasd:ResourceType>17</rasd:ResourceType>
>
```

The manifest (```.mf```) file must be updated to have a correct SHA1 hash for the changed OVF file.

```
> sha1sum c8k-01.ovf
462ed3ad90690eb465f06724fe356c23248c78bd  c8k-01.ovf
> cp c8k-01.mf c8k-01.mf__original
> vim c8k-01.mf
>
> diff c8k-01.mf__original c8k-01.mf
1c1
< SHA1(c8k-01.ovf)= 20281039c3fa9736ad1cda8632e490d7d974e045
---
> SHA1(c8k-01.ovf)= 462ed3ad90690eb465f06724fe356c23248c78bd
>
>
```

The changed OVF file and other extracted files from the OVA can be re-packaged into a new OVA file using the ```ovftool```:

```
> ovftool c8k-01.ovf c8k-02.ova
Opening OVF source: c8k-01.ovf
The manifest validates
Opening OVA target: c8k-02.ova
Writing OVA package: c8k-02.ova
Transfer Completed
Completed successfully
>
```

The new OVA file can be checked against the ```ovftool``` and should complete successfully:

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

Download Size:  771.77 MB

Deployment Sizes:
  Flat disks:   8.75 GB
  Sparse disks: 1.03 GB

Networks:
  Name:        GigabitEthernet1
  Description: Data network 1

  Name:        GigabitEthernet2
  Description: Data network 2

  Name:        GigabitEthernet3
  Description: Data network 3

Virtual Machines:
  Name:               Cisco Catalyst 8000V Edge Router
  Operating System:   other3xlinux64guest
  Virtual Hardware:
    Families:         vmx-10 vmx-11 vmx-13
    Number of CPUs:   4
    Cores per socket: 1
    Memory:           8.00 GB

    Disks:
      Index:          0
      Instance ID:    5
      Capacity:       8.00 GB
      Disk Types:     SCSI-VirtualSCSI

    NICs:
      Adapter Type:   VMXNET3
      Connection:     GigabitEthernet1

      Adapter Type:   VMXNET3
      Connection:     GigabitEthernet2

      Adapter Type:   VMXNET3
      Connection:     GigabitEthernet3

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
  Id:          4CPU-8GB-8GB
  Label:       Large + DRAM Upgrade - 8GB Disk
  Description: Large hardware profile (requires purchase of DRAM upgrade SKU) -
               4 vCPUs, 8 GB RAM, 8 GB Disk

References:
  File:  c8k-02-disk1.vmdk
  File:  c8k-02-disk2.vmdk
  File:  c8k-02-file1.txt
  File:  c8k-02-file2.iso

>
```

## Adding interfaces to the OVA file:
Additional interfaces can be added to the OVA file if needed using the ```cot``` tool.

### COT parameters
* Use the ```-o output.ova``` paramter to specify the name of the new OVA
* Use the ```--nics X``` parameter to specify the number of interfaces.
* Use the ```--nic-name "GigabitEthernet{1}"``` parameter to specify the interface name pattern.
* Use the ```--nic-types "VMXNET3"``` parameter to specify the type of interface.
* Use the ```--nic-networks "PG name 1" "PG name 2" ...``` to map VMware port-group names to VM interfaces
* Use the ```--network-descriptions "PG name 1" "PG name 2" ...``` to provide interface descriptions

```
> cot edit-hardware ./c8k-02.ova -o c8k-03.ova \
    --nics 9 \
    --nic-names "GigabitEthernet{1}" \
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
ERROR   : The sha1 checksum for file 'c8k-02.ovf' is expected to be:
a1f7a70499c217a8403bcffa74e39a5140a43fee29b5ea1514589b06e7607d6d
but is actually:
8855a72dfcb4e5074bc669f033394fafe7871764
This file may have been tampered with!
ERROR   : The sha1 checksum for file 'c8k-02-disk1.vmdk' is expected to be:
40eebf457e23e714b57eb76cd6b7500d3310ff089dfde63185bb53a0417cc0e6
but is actually:
641eeee203e715f5a0cc4cd2317af25a15b584e3
This file may have been tampered with!
ERROR   : The sha1 checksum for file 'c8k-02-disk2.vmdk' is expected to be:
e5421b85c2095374c9c9127db99074497a22a0efbcf9e79c9902ba3ab5bf59a1
but is actually:
c9e2bead38ffbae7a14372bd8ee0b1bfa1c6140e
This file may have been tampered with!
ERROR   : The sha1 checksum for file 'c8k-02-file1.txt' is expected to be:
b0d6c9a56810bd6e55f047d14d2f4637e468b7e285cf0cdf6fffdebb2ea5a87f
but is actually:
c45e724987e297d83ea4816217bb2bd208a7d6b0
This file may have been tampered with!
ERROR   : The sha1 checksum for file 'c8k-02-file2.iso' is expected to be:
0366e7282cb90a966830d6dd377c4adb740fa5149f53717dc9fd7d3a9de95390
but is actually:
531d8d06288c0654d2a367e513588692483a83ae
This file may have been tampered with!
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

>
> cot info c8k-03.ova
NOTICE  : Unrecognized product class 'com.cisco.c8000v'. Treating this as a generic platform.
------------------------------------------------------------------------------------------------------------------------------
c8k-03.ova
------------------------------------------------------------------------------------------------------------------------------
Product:  Cisco C8000V
          http://www.cisco.com/en/US/products/ps12559/index.html
Vendor:   Cisco Systems, Inc.
          http://www.cisco.com
Version:  17.04.02
          Cisco IOS-XE Software, version 17.04.02

Files and Disks:     File Size  Capacity Device
                     --------- --------- --------------------
  c8k-02-disk1.vmdk    707 KiB     8 GiB
  c8k-02-disk2.vmdk  1.316 MiB    16 GiB
  c8k-02-file1.txt   8.535 KiB
  c8k-02-file2.iso   771.1 MiB           cdrom @ IDE 1:0

Hardware Variants:
  System types:             vmx-10 vmx-11 vmx-13
  SCSI device types:        VirtualSCSI
  Ethernet device types:    VMXNET3

Configuration Profiles:  CPUs    Memory NICs Serials Disks/Capacity
                         ---- --------- ---- ------- --------------
  4CPU-8GB-8GB (default)    4     8 GiB    9       0  1 /    24 GiB
    Label:          "Large + DRAM Upgrade - 8GB Disk"
    Description:    "Large hardware profile (requires purchase of DRAM upgrade SKU) - 4 vCPUs, 8 GB RAM, 8 GB Disk"

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
```

As before, the resulting OVA will not be useable by ```ovftool``` and must be un-packed and then repackaged by ```ovftool``` in order to rectify this:

```
> ovftool c8k-03.ova
Error: Did not find an .ovf file at the beginning of the OVA package.
> tar -xvf c8k-03.ova
c8k-03.ovf
c8k-03.mf
c8k-02-disk1.vmdk
c8k-02-disk2.vmdk
c8k-02-file1.txt
c8k-02-file2.iso
> ovftool c8k-03.ovf
OVF version:   1.0
VirtualApp:    false
Name:          Cisco C8000V
Version:       17.04.02
Full Version:  Cisco IOS-XE Software, version 17.04.02
Vendor:        Cisco Systems, Inc.
Product URL:   http://www.cisco.com/en/US/products/ps12559/index.html
Vendor URL:    http://www.cisco.com

Download Size:  771.77 MB

Deployment Sizes:
  Flat disks:   8.75 GB
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
    Number of CPUs:   4
    Cores per socket: 1
    Memory:           8.00 GB

    Disks:
      Index:          0
      Instance ID:    5
      Capacity:       8.00 GB
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
  Id:          4CPU-8GB-8GB
  Label:       Large + DRAM Upgrade - 8GB Disk
  Description: Large hardware profile (requires purchase of DRAM upgrade SKU) -
               4 vCPUs, 8 GB RAM, 8 GB Disk

References:
  File:  c8k-02-disk1.vmdk
  File:  c8k-02-disk2.vmdk
  File:  c8k-02-file1.txt
  File:  c8k-02-file2.iso

> ovftool c8k-03.ovf c8k-04.ova
Opening OVF source: c8k-03.ovf
The manifest validates
Opening OVA target: c8k-04.ova
Writing OVA package: c8k-04.ova
Transfer Completed
Completed successfully
>
>
> ovftool c8k-04.ova
OVF version:   1.0
VirtualApp:    false
Name:          Cisco C8000V
Version:       17.04.02
Full Version:  Cisco IOS-XE Software, version 17.04.02
Vendor:        Cisco Systems, Inc.
Product URL:   http://www.cisco.com/en/US/products/ps12559/index.html
Vendor URL:    http://www.cisco.com

Download Size:  771.77 MB

Deployment Sizes:
  Flat disks:   8.75 GB
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
    Number of CPUs:   4
    Cores per socket: 1
    Memory:           8.00 GB

    Disks:
      Index:          0
      Instance ID:    5
      Capacity:       8.00 GB
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
  Id:          4CPU-8GB-8GB
  Label:       Large + DRAM Upgrade - 8GB Disk
  Description: Large hardware profile (requires purchase of DRAM upgrade SKU) -
               4 vCPUs, 8 GB RAM, 8 GB Disk

References:
  File:  c8k-04-disk1.vmdk
  File:  c8k-04-disk2.vmdk
  File:  c8k-04-file1.txt
  File:  c8k-04-file2.iso

>
```
