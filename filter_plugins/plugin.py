import os

class FilterModule(object):
    def filters(self):
        return {
            'vs_dm': self.vs_dm,
            'vm_dm': self.vm_dm
        }

    # Adds dictionary key:value only if the variable has been defined
    def cond_dict(self, input_dict, temp_dict, dflt_val, obj):
        if input_dict.get(obj, dflt_val) != None:
            temp_dict[obj] = input_dict.get(obj, dflt_val)

    # Adds NIC parameters to the network dictionary
    def ntwk_dict(self, input_dict, temp_dict, obj):
        if input_dict.get(obj) != None:
            if 'port_grp' in obj:
                temp_dict['network'].append(dict(name=input_dict[obj]))
            else:
                temp_dict['network'][0][obj] = input_dict.get(obj)

    # Creates the Local vSwitch Data Models for all LvS and all port-groups
    def vs_dm(self, vs):
        all_vs, all_grp = ([] for i in range(2))
        for each_vs in vs:
            # Converts esx_host (LvS) or DC (DvS) to a list if is a string.
            if each_vs.get('esx_host') != None:
                esx_or_dc = each_vs['esx_host'].split(',') if isinstance(each_vs['esx_host'], str) else each_vs['esx_host']
            elif each_vs.get('dc') != None:
                esx_or_dc = each_vs['dc'].split(',') if isinstance(each_vs['dc'], str) else each_vs['dc']

            # Creates list of all LvS
            for each_esx_or_dc in esx_or_dc:
                tmp_vs = {}                  # temp dict reset at each LvS iteration
                tmp_vs['name'] = each_vs['name']
                tmp_vs['state'] = each_vs['state']
                tmp_vs['esx_host_or_dc'] = each_esx_or_dc
                self.cond_dict(each_vs, tmp_vs, None, 'mtu')                  # defaults to 1500
                self.cond_dict(each_vs, tmp_vs, None, 'discovery_ptcl')       # defaults to CDP
                self.cond_dict(each_vs, tmp_vs, None, 'discovery_oper')       # defaults to listen
                self.cond_dict(each_vs, tmp_vs, None, 'num_uplinks')          # defaults to 4
                all_vs.append(tmp_vs)
                # Creates list of all Port-Groups
                try:
                    for each_grp in each_vs['port_grp']:
                        tmp_grp = {}            # temp dict reset at each port-group iteration
                        tmp_grp['esx_host_or_dc'] = each_esx_or_dc
                        tmp_grp['vs_name'] = each_vs['name']
                        tmp_grp['grp_name'] = each_grp['name']
                        tmp_grp['vlan'] = each_grp['vlan']
                        self.cond_dict(each_grp, tmp_grp, None, 'trunk')              # If trunk is defined adds dict
                        tmp_grp['state'] = each_grp.get('state', each_vs['state'])
                        self.cond_dict(each_grp, tmp_grp, None, 'num_ports')          # Defaults to 8
                        if each_vs.get('dc') != None:                           # DC is not needed to create DvS port-groups
                            del tmp_grp['esx_host_or_dc']
                        all_grp.append(tmp_grp)
                except:
                    all_grp.append({})
        return dict(all_lvs=all_vs, all_grp=all_grp)


    def vm_dm(self, vm_tmpl, fldr, dflt_vm):
        all_vms = []
        for each_dc in vm_tmpl:

            # TOP_MULTi_PLACE: Create variable for top-level of parameters that can be set in multiple places
            dc_esx = each_dc.get('esx_host')
            dc_ds = each_dc.get('ds')
            dc_dmn = each_dc.get('domain')
            dc_dns_svr = each_dc.get('dns_svrs')
            dc_dns_sfx = each_dc.get('dns_suffix')
            dc_state = each_dc.get('state')

            # Variables to be used in next loop
            os_type = each_dc.pop('type')
            for each_type in os_type:
                # MID_MULTi_PLACE: Create variable for mid-level of parameters that can be set in multiple places
                type_esx = each_type.get('esx_host', dc_esx)
                type_ds = each_type.get('ds', dc_ds)
                type_dmn = each_type.get('domain', dc_dmn)
                type_dns_svr = each_type.get('dns_svrs', dc_dns_svr)
                type_dns_sfx = each_type.get('dns_suffix', dc_dns_sfx)
                type_state = each_type.get('state', dc_state)
                type_timezone = each_type.get('timezone')
                type_dir = each_type.get('dir')
                type_image = each_type.get('image')
                # MID_MULTi_PLACE: Network, hardware and disk parameters, again mid-level that can be set in multiple places
                type_port_grp = each_type.get('port_grp', dflt_vm['port_grp'])
                type_hdd = each_type.get('hdd', dflt_vm['hdd'])
                type_prov_type = each_type.get('prov_type', dflt_vm['prov_type'])
                type_mem = each_type.get('mem', dflt_vm['mem'])
                type_hotadd_mem = each_type.get('hotadd_mem', dflt_vm['hotadd_mem'])
                type_cpu = each_type.get('cpu', dflt_vm['cpu'])
                type_hotadd_cpu = each_type.get('hotadd_cpu', dflt_vm['hotadd_cpu'])
                type_scsi_ctrl = each_type.get('scsi_ctrl', dflt_vm['scsi_ctrl'])

                for each_vm in each_type['vms']:
                    tmp_vm = {}            # temp dict reset at each VM iteration
                    # BOT_MULTI-PLACE: Create dict element for bottom-level of parameters that can be set in multiple places
                    # vm_tmpl and vm_iso
                    tmp_vm['esx_host'] = each_vm.get('esx_host', type_esx)
                    tmp_vm['ds'] = each_vm.get('ds', type_ds)
                    tmp_vm['state'] = each_vm.get('state', type_state)
                    # Either adds base_dir to directory or if not specified uses the base_dir
                    if each_vm.get('dir', type_dir) != None:
                        tmp_vm['dir'] = os.path.join(each_dc['dc'], 'vm', each_vm.get('dir', type_dir))
                    else:
                        tmp_vm['dir'] = os.path.join(each_dc['dc'], 'vm')
                    # Not used in vm_tmpl
                    self.cond_dict(each_vm, tmp_vm, type_image, 'image')
                    if tmp_vm.get('image') != None:    # Adds ISO location to the image name
                        tmp_vm['image'] = str(fldr) + ' ' + str(tmp_vm['image'])
                    # Not used in vm_iso
                    self.cond_dict(each_vm, tmp_vm, type_timezone, 'timezone')
                    self.cond_dict(each_vm, tmp_vm, type_dmn, 'domain')
                    self.cond_dict(each_vm, tmp_vm, type_dns_svr, 'dns_svrs')
                    self.cond_dict(each_vm, tmp_vm, type_dns_sfx, 'dns_suffix')

                    # BOT_MULTi_PLACE: Creates a dicts for bottom-level of parameters that can be set in multiple places
                    if dflt_vm != None:       # Conditional as not needed for vm_ovf
                        tmp_vm['hardware'] = dict(memory_mb=each_vm.get('mem', type_mem), hotadd_mem=each_vm.get('hotadd_mem', type_hotadd_mem),
                                                 num_cpus=each_vm.get('cpu',type_cpu), hotadd_cpu=each_vm.get('hotadd_cpu', type_hotadd_cpu),
                                                 scsi=each_vm.get('scsi_ctrl', type_scsi_ctrl))
                        tmp_vm['disk'] = [dict(size_gb=each_vm.get('hdd', type_hdd), type=each_vm.get('prov_type', type_prov_type))]

                    # Creates Network dictionary holding list of NICs and their parameters
                    tmp_vm['network'] = [dict(name=each_vm.get('port_grp', type_port_grp))]
                    self.ntwk_dict(each_vm, tmp_vm, 'ip')
                    self.ntwk_dict(each_vm, tmp_vm, 'netmask')
                    self.ntwk_dict(each_vm, tmp_vm, 'gw')
                    self.ntwk_dict(each_vm, tmp_vm, 'mac')
                    self.ntwk_dict(each_vm, tmp_vm, 'port_grp2')
                    self.ntwk_dict(each_vm, tmp_vm, 'port_grp3')
                    self.ntwk_dict(each_vm, tmp_vm, 'port_grp4')

                    # BOT_SINGLE-PLACE: Create dict element for parameters only set in the one place
                    # vm_tmpl and vm_iso
                    tmp_vm['dc'] = each_dc['dc']
                    tmp_vm['name'] = each_vm['name']
                    # vm_tmpl only
                    self.cond_dict(each_type, tmp_vm, None, 'tmpl')
                    if tmp_vm.get('tmpl') != None:    # Adds template location to the template name
                        tmp_vm['tmpl'] = os.path.join(str(fldr), str(tmp_vm['tmpl']))
                    # vm_iso only
                    self.cond_dict(each_type, tmp_vm, None, 'os_id')

                    # vm_iso only - has lot less so strips lot out and replaces the network list with a dictionary
                    if each_type.get('ovf') != None:
                        tmp_vm['ovf'] = os.path.join(str(fldr), str(each_type['ovf']))
                        del tmp_vm['hardware']
                        tmp_vm['disk'] = tmp_vm['disk'][0]['type']
                        # Merges network dictionary from type and vms
                        tmp_vm['network'] = each_type.get('network', {})
                        tmp_vm['network'].update(each_vm.get('network', {}))
                        # If OVF properties are set adds inject dictionary
                        if each_vm.get('ovf_prop') != None:
                            tmp_vm['inj_prop'] = True
                            tmp_vm['ovf_prop'] = each_vm['ovf_prop']

                    all_vms.append(tmp_vm)

        return all_vms