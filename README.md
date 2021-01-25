# Build VMWare VMs and vSwitches

Manages Local vSwitches, Distributed vSwitches and VMs in vCentre or on the individual ESX hosts.
This has been tested on Ansible 2.8.4. At some point needs to be ported to 2.10 and changed to use collections

## Variables

All variables for the playbooks are in the vars folder, it doesn't use *host_vars* or *group_vars*.
It is easier to have all the variables in one place and then use jinja plugins to create the relevant Data Models from these.\
Another reason for this is that the output returned on screen from Ansible nested loops is confusing as it shows the whole loop rather than just the individual parameters for the  object that was created.

### base.yml

The vCentre or standalone ESX host plays are run against, default directory locations and default VM specifications.

If run against vCentre the individual ESX hosts that objects will be created on are defined with the *esx_host* variable in the in the *vms.yml* file. When deploying an OVF (*vm_from_ovf*) cant specify *esx_host* as *vmware_deploy_ovf* does not support it. The VM is built on the first ESX host in vCentre, I think need to use cluster have not added option to playbooks or tested yet.\
If the device is a standalone ESX host *esxi_host* is still required in the *vms.yml* variable file but ignored in the plays.

*dflt_vm* values apply if they are not specified in variable file when building VMs from templates (*vm_tmpl*) and ISOs (*vm_iso*). The only setting in *dflt_vm* used by OVFs (*vm_ovf*) is *prov_type*.

| Parent-dict  | Child-dict | Information |
|--------------|-----------|--------------|
| login | device | *vCentre or standalone ESX Host to run the play against* |
| login | user | *vCentre or standalone ESX host username* |
| login | pass | *vCentre or standalone ESX host password* |
| dir | tmpl | *Location where templates are stored (directory in inventory)* |
| dir | iso | *Location where ISO images are stored (in the DS)* |
| dir | ovf | *Location where OVFs are stored (cannot be the DS)* |
| dflt_vm | port_grp | *Default port-group used* |
| dflt_vm | hdd | *Default Hardrive size in GB* |
| dflt_vm | prov_type | *Default Hardrive provision type* |
| dflt_vm | 2048 | *Default memory in MB* |
| dflt_vm | hotadd_mem | *Whether memory is hot-swappable* |
| dflt_vm | 1 | *Default number of CPUs* |
| dflt_vm | hotadd_cpu | *Whether CPU is hot-swappable* |
| dflt_vm | scsi_ctrl | *Default SCSI adaptor/controller type* |

### port_grps.yml

*Object* defines whether this dictionary object can be used for creating local vSwitches, distributed vSwitches or both.

| Object  | Key | Mandatory | Information |
|---------|-----|-----------|-------------|
| lvs/dvs | name | Yes | *Name of the vSwitch* |
| dvs | dc | Yes | *DC DvS it is created on. Either one DC or a list of DCs* |
| dvs | num_uplinks | No | *Number of uplinks on the DvS. If not defined is 4* |
| lvs | esx_host | Yes | *ESX host LvS it is created on. Can either be one host or a list of hosts* |
| lvs/dvs | mtu | No | *MTU of the vS, if not defined is 1500* |
| dvs | discovery_ptcl | No | *discovery protocol of the vS, if not defined is CDP* |
| dvs | discovery_oper | No | *discovery operation of the vS, if not defined is listen* |
| lvs/dvs | state | Yes | *State of the vSwitch and possibly port-groups (global)* |
| lvs/dvs | port_grp | No | *List of port-groups. If defined sub-options also required* |
| lvs/dvs | port_grp.name | Yes | *Name of the port-group* |
| lvs/dvs | port_grp.vlan | Yes | *VLAN of the port-group* |
| lvs/dvs | port_grp.trunk | No | *Required if the the port-group is a trunk* |
| lvs/dvs | port_grp.state | No | *State of the port-group, if not defined uses the vSwitch state* |
| dvs | port_grp.num_ports | No | *Number of ports on the DvS, if not defined is 8* |

### vms.yml

*Object* defines whether this dictionary can be used when creating VMs from templates (*vm_tmpl*), VM shells with an ISO (*vm_iso*) or VMs from OVFs (*vm_ovf*).

If a Multi-point (*MP*) object is mandatory it must be defined in at least one location.\
Optional (*Mandatory No*) only need defining when changing the default value.

Multi-point (*MP*) means the object can be defined at multiple points within the variable file with the lowest point taking precedence. For example, defining the *state* under the *DC* applies to all VMs in that DC, if also defined under a *template* it would be overridden for those devices using that template and if defined under the *VM* both the DC and template setting would be overridden for that specific VM.\


| Object  | Key | Mandatory | Information |
|---------|-----|-----------|-------------|
| tmpl/iso/ovf | dc | Yes | *Name of the Data Centre to create the VM* |
| tmpl/iso | esx_host | MP Yes | *ESX host on which to create all the VMs* |
| tmpl/iso/ovf | ds | MP Yes | *The Datastore on which to create all the VMs* |
| tmpl/iso/ovf | state | MP Yes | *State for all VMs* |
| tmpl | domain | MP No | *The domain name for all VMs* |
| tmpl | dns_svrs | MP No | *List of DNS servers for all VMs* |
| tmpl | dns_suffix | MP No | *The DNS suffix for all VMs* |

The main difference between TMPL, ISO and OVF data models is the *type* dictionary. TMPL groups the parameters based on the template, ISO groups them based on the guest OS and OVF groups them based on the OVF template.\
Under this grouping the VM parameters can be applied for all VMs that would be created from this object (for example all VMs built from a specific template) and/or override this and define the VM parameters under each individual VM.

OVF does no allow any of the hardware parameters to be change except for HDD provisioning type (*prov_type*), *thin* or *thick*. It doesn't have the *port_grp* dictionary, instead *network* is a dictionary of dictionaries *{vnic_name: port-group}*.

| Object  | Key | Mandatory | Information |
|---------|-----|-----------|-------------|
| tmpl/iso/ovf | type | Yes | *List of templates or OS IDs which contain the VMs to be created* |
| tmpl | type.tmpl | Yes | *VM template used to build the VMs* |
| iso | type.os_id | Yes | *Operating system type used to build the VMs* |
| iso | type.image | MP No | *The ISO image loaded at VM startup* |
| ovf | type.ovf | Yes | *OVF to build the VM from* |
| tmpl/iso | type.esx_host | MP Yes | *Takes precedence over the DC esx_host dict* |
| tmpl/iso/ovf | type.ds | MP Yes | *Takes precedence over the DC datastore dict* |
| tmpl/iso/ovf | type.state | MP Yes | *Takes precedence over DC state dict* |
| tmpl | type.domain | MP No | *Takes precedence over the DC domain name dict* |
| tmpl | type.dns_svrs | MP No | *Takes precedence over the DC DNS servers dict* |
| tmpl | type.dns_suffix | MP No | *Takes precedence over DC DNS suffix dict* |
| tmpl | type.timezone | MP No | *Timezone for all VMs* |
| tmpl/iso/ovf | type.dir | MP No | *vCentre folder in which to build all the VMs* |
| tmpl/iso | type.port_grp | MP No | *Port-group the VMs are in* |
| tmpl/iso | type.hdd | MP No | *Hardrive size in GB* |
| tmpl/iso/ovf | type.prov_type | MP No | *The HDD provisioning type* |
| tmpl/iso | type.mem | MP No | *Memory size in GB* |
| tmpl/iso | type.hotadd_mem | MP No | *Memory is hot-swappable* |
| tmpl/iso | type.cpu | MP No | *Number of vCPUs* |
| tmpl/iso | type.hotadd_cpu | MP No | *vCPU is hot-swappable* |
| tmpl/iso | type.scsi_ctrl | MP No | *Set the iSCSI controller* |
| ovf | type.network | MP No | *Dictionaries of {vnic_name: port-group}* |

When deploying ISOs upto 4 NICs can be defined, although the the last 3 can only be done so under the VM.\
IP, mask and gateway can only be used if deploying a template.\
OVF properties (Key:value pair) can be injected in through VMware Tools (never tried). These parameters are specific to the ovf, need to open the ovf file in a text editor to determine what these values should be, you will. Alternatively deploy it and then look in vApp Options >> environment.

| Object  | Key | Mandatory | Information |
|---------|-----|-----------|-------------|
| tmpl/iso | type.vms | Yes | *List of VMs to be created* |
| tmpl/iso | type.vms.name | Yes | *Name of the VM* |
| tmpl | type.vms.ip | No | *VMs IP addressed. If defined the GW and mask must also be defined* |
| tmpl | type.vms.netmask | No | *VMs subnet mask. If defined the IP and GWk must also be defined* |
| tmpl | type.vms.gw | No | *VMs default gateway. If defined the IP and mask must also be defined* |
| tmpl | type.vms.mac | No | *MAC address of the VM* |
| iso | type.vms.port_grp2 | No | *Port-group for NIC2 on the the server is in* |
| iso | type.vms.port_grp3 | No | *Port-group for NIC3 on the the server is in* |
| iso | type.vms.port_grp4 | No | *Port-group for NIC4 on the the server is in* |
| tmpl/iso | type.vms.esx_host | MP Yes | *Takes precedence over DC and template setting* |
| tmpl/iso | type.vms.ds | MP Yes | *Takes precedence over DC and template setting* |
| tmpl/iso | type.vms.state | MP Yes | *Takes precedence over DC and template setting* |
| tmpl/iso | type.vms.dir | MP No | *Takes precedence over DC and template setting* |
| tmpl | type.vms.domain | MP Yes | *Takes precedence over DC and template setting* |
| tmpl | type.vms.dns_svrs | MP Yes | *Takes precedence over DC and template setting* |
| tmpl | type.vms.dns_suffix | MP Yes | *Takes precedence over DC and template setting* |
| tmpl | type.vms.timezone | MP Yes | *Takes precedence over DC and template setting* |
| iso | type.vms.image | MP No | *Takes precedence over DC and OS type setting* |
| tmpl/iso | type.vms.port_grp | MP No | *Takes precedence over DC and OS type setting* |
| tmpl/iso | type.vms.hdd | MP No | *Takes precedence over DC and OS type setting* |
| tmpl/iso | type.vms.prov_type | MP No | *Takes precedence over DC and OS type setting* |
| tmpl/iso | type.vms.mem | MP No | *Takes precedence over DC and OS type setting* |
| tmpl/iso | type.vms.cpu | MP No | *Takes precedence over DC and OS type setting* |
| tmpl/iso | type.vms.scsi_ctrl | MP No | *Takes precedence over DC and OS type setting* |
| ovf | type.vms.network| MP No | *Dictionaries of {vnic_name: port-group}* |
| ovf | type.vms.ovf_prop | No | *Dictionaries of OVF properties* |

## Roles

The tasks are split into roles which are further split dependant on the particular task.

### vs_portgrp

- lvs_portgrp: *Create the Local vSwitch and any port-groups on that LvS*
- dvs_portgrp: *Create the Distributed vSwitch and any port-groups on that DvS*

### vm

- vm_from_template: *Create a VM from a template or cloned VM*
- vm_with_iso: *Create an empty VM optionally with a ISO loaded*
- vm_from_ovf: *Create a VM from a OVF*

## Running the playbook

A prerequisite to running these Ansible VMware plays is to instal *PyVmomi* on the ansible host (*pip install PyVmomi*).

The playbook can be run with any of the following tags:

**--tag lvs:** Creates Local vSwitches as defined by the *lvs* dictionary in *port_grps.yml*.\
**--tag dvs:** Creates Distributed vSwitches as defined by the *dvs* dictionary in *port_grps.yml*.\
**--tag vm_tmpl:** Creates VMs from a template as defined by the *vm_tmpl* dictionary in *vms.yml*.\
**--tag vm_iso:** Creates VM shell (with optional image) as defined by the *vm_iso* dictionary in *vms.yml*.\
**--tag vm_ovf:** Creates VMs from an OVF as defined by the *vm_ovf* dictionary in *vms.yml*.

## Caveats


!!!!!! REWRITE CAVEATS, CHNAGE PASSWORD TO BE VAULT, ADD TO GITHUB !!!!!!!!


A few things couldnt get to work properly. Not essential in lab but would be good to fix at somepoint

Doesnt work on any:
mac: Deleted HWADDR and UUID from template but it still gets random AMC address
Timezone: Doesnt work, always uses the template setting
scsi_ctrl: Doesnt work, always uses the template setting
prov_type: Doesnt work, always uses the template setting

WIN10
customization: None of these work as need to run sysprep but if do that have to setup user each time:
ip, mask, gateway, hostname, domain, dns_servers, dns_suffix

## TODO

Upgrade Ansible to 2.10 and convert these playbooks to use collections.\
Add cluster option to all the roles and test deploying using cluster.\
Try injecting values using vApps in *vmware_guest >> vapp_properties* (not added to *vm_iso* role yet) and *vmware_deploy_ovf >> properties* (already in *vm_ovf* role).
