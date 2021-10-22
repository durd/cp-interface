#!/usr/bin/env python3

import phpypam
import urllib3
from cpapi import APIClient, APIClientArgs

# modules made for this project
from config import Config

# silence certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ipam_search_childsubnets(parentsubnet):
    parent = pi.get_entity('subnets', '/cidr/' + parentsubnet)
    #print(json.dumps(parent, indent=2))

    children = pi.get_entity('subnets', parent[0]['id'] + '/slaves/')
    #print(json.dumps(children, indent=2))

    childvlans = []
    for k in children:
        if k['vlanId'] != '0' and 'xxx' not in k['description'].lower():
            childvlans.append(k)
            #print(k)
    #print(json.dumps(childvlans, indent=2))

    subnets = []
    for k in childvlans:
        k['vlan-number'] = pi.get_entity('vlan', k['vlanId'])['number']
        subnets.append(k)
    #print(json.dumps(vlansubnets, indent=2))
    return subnets

def fwsections_build(subnets):
    fwsections = []
    for k in subnets:
        fwsections.append(k['vlan-number'] + '-' + k['subnet'] + '_' + k['mask'] + '-' + k['description'])
    #print(json.dumps(fwsections, indent=2))
    return fwsections

def mgmt_add_sections(secs, package):
    sections = list(secs)
    layer = package + ' Network'
    payload = {'layer': layer, 'position': 'bottom'}
    data = []
    for section in sections:
        payload['name'] = section
        api_res = client_mgmt.api_call('add-access-section', payload)
        if api_res.success:
            data.append(api_res.data)
            #print(json.dumps(data, indent=2))
    return data

def mgmt_get_target(policy):
    payload = {'name': policy}
    api_res = client_mgmt.api_call('show-package', payload)
    if api_res.success:
        data = api_res.data
        #print(json.dumps(data, indent=2))
    return data['installation-targets'][0]['name']

def mgmt_get_cluster(target):
    payload = {'name': target}
    api_res = client_mgmt.api_call('show-simple-cluster', payload)
    if api_res.success:
        data = api_res.data
        #print(json.dumps(data, indent=2))
    return data

def gaia_get_hastatus(ip, cpusername, cppassword):
    client_args_gaia = APIClientArgs(server=ip, unsafe=True, context='gaia_api')
    with APIClient(client_args_gaia) as client_gaia:
        # login to gaia api
        login_res = client_gaia.login(cpusername, cppassword)

        if login_res.success is False:
            print('Login failed: {}'.format(login_res.error_message))
            exit(1)
        else:
            print('GAiA login succeeded')

        api_res = client_gaia.api_call('show-cluster-state', {})
        if api_res.success:
            data = api_res.data
            #print(json.dumps(data, indent=2))
        else:
            data = api_res.data
        return data

def gaia_get_vlanifs(interface, ip, cpusername, cppassword):
    client_args_gaia = APIClientArgs(server=ip, unsafe=True, context='gaia_api')
    with APIClient(client_args_gaia) as client_gaia:
        # login to gaia api
        login_res = client_gaia.login(cpusername, cppassword)

        if login_res.success is False:
            print('Login failed: {}'.format(login_res.error_message))
            exit(1)
        else:
            print('GAiA login succeeded')

        payload = {'parent': interface}
        api_res = client_gaia.api_call('show-vlan-interfaces', payload)
        if api_res.success:
            data = api_res.data
            #print(json.dumps(data, indent=2))
        return data

def gaia_add_vlanifs(vlans, peerid, cpnodenr):
    payload = dict(vlans)
    x = payload['ipv4-address'].split('.')
    if cpnodenr == 1:
        x[3] = str(int(x[3])+peerid+1)
    elif cpnodenr == 2:
        x[3] = str(int(x[3])+peerid+2)
    bleh = ".".join(x)
    #print(payload, x)
    payload['ipv4-address'] = bleh
    #print(payload, peerid, x)
    api_res = client_gaia.api_call('add-vlan-interface', payload)
    if api_res.success:
        data = api_res.data
        #print(json.dumps(data, indent=2))
    return data

def mgmt_add_vlanifs(payload):
    api_res = client_mgmt.api_call('set-simple-cluster', payload)
    if api_res.success:
        data = api_res.data
        #print(json.dumps(data, indent=2))
    return data

def mgmt_show_task(taskid):
    payload = dict(taskid)
    api_res = client_mgmt.api_call('show-task', payload)
    if api_res.success:
        data = api_res.data
        #print(json.dumps(data, indent=2))
    return data

def mgmt_publish():
    api_res = client_mgmt.api_call('publish', {})
    if api_res.success:
        data = api_res.data
        #print(json.dumps(data, indent=2))
    return data

def create_cluster_vlans():
    clvlan = {'name': '', 'interfaces': {}, 'members': {'update': [{'name': '', 'interfaces': [{'name': '', 'ipv4-address': '', 'ipv4-mask-length': ''}]}]}}
    clvlan['interfaces']['add'] = []
    clvlan['members']['update'] = []
    clvlan['name'] = cluster['name']
    clvlanif = {'interface-type': 'cluster', 'topology': 'internal', 'anti-spoofing': 'true', 'topology-settings': {'interface-leads-to-dmz': 'false', 'ip-address-behind-this-interface': 'network defined by the interface ip and net mask'}}
    nodeifs = []

    do_something = False
    for i in childsubnets:
        if i['vlan-number'] in diffed:
            do_something = True
            y = i['subnet'].split('.')
            y[3] = str(int(y[3])+1)
            x = '.'.join(y)
            a = dict(clvlanif)
            a.update({'name': cpinterface + '.' + i['vlan-number'], 'ipv4-address': x, 'ipv4-mask-length': i['mask'], 'comments': i['description']})
            clvlan['interfaces']['add'].append(a)
    for node in active_vlans:
        if node == 'name':
            clvlan['members']['update'].append({'name': active_vlans[node]})
        else:
            clvlan['members']['update'][0]['interfaces'] = []
            for vlan in active_vlans[node]:
                b = dict(nodeifs)
                b.update({'name': vlan['name'], 'ipv4-address': vlan['ipv4-address'], 'ipv4-mask-length': vlan['ipv4-mask-length']})
                clvlan['members']['update'][0]['interfaces'].append(b)
    if 'passive_vlans' in globals():
        for node in passive_vlans:
            if node == 'name':
                clvlan['members']['update'].append({'name': passive_vlans[node]})
            else:
                clvlan['members']['update'][1]['interfaces'] = []
                for vlan in passive_vlans[node]:
                    c = dict(nodeifs)
                    c.update({'name': vlan['name'], 'ipv4-address': vlan['ipv4-address'], 'ipv4-mask-length': vlan  ['ipv4-mask-length']})
                    clvlan['members']['update'][1]['interfaces'].append(c)
    if do_something:
        return clvlan
    else:
        return False

if __name__ == '__main__':
    config = Config()
    ipamparams = dict(
        url=config.get_ipam_url(),
        app_id=config.get_ipam_app(),
        username=config.get_ipam_username(),
        password=config.get_ipam_password(),
        ssl_verify=True
    )
    pi = phpypam.api(**ipamparams)
    parentsubnet = config.get_parentsubnet()
    childsubnets = ipam_search_childsubnets(parentsubnet)
    fwsections = fwsections_build(childsubnets)
    api_server = config.get_cp_management()
    cpusername = config.get_cp_username()
    cppassword = config.get_cp_password()
    cppolicy = config.get_cp_policy()
    cpinterface = config.get_cp_interface()
    cpnodenr = config.get_cp_nodenr()

    #print(childsubnets)
    #print(fwsections)

    client_args_mgmt = APIClientArgs(server=api_server, unsafe=True)
    with APIClient(client_args_mgmt) as client_mgmt:
        # login to mgmt api
        login_res = client_mgmt.login(cpusername, cppassword)

        if login_res.success is False:
            print('Login failed: {}'.format(login_res.error_message))
            exit(1)
        else:
            print('Web API login succeeded')
        
        target = mgmt_get_target(cppolicy)
        #print('target:', target)
        cluster = mgmt_get_cluster(target)
        print('cluster:', cluster)
        hastatus = gaia_get_hastatus(cluster['ipv4-address'], cpusername, cppassword)
        #print('hastatus:', hastatus)
        if 'active' in hastatus['this-cluster-member']['status']:
            activenode = hastatus['this-cluster-member']['name']
            activepeerid = hastatus['this-cluster-member']['peer-id']
            #print(activenode)
        if hastatus['other-cluster-members']:
            passivepeerid = hastatus['other-cluster-members'][0]['peer-id']

        active_index = 0
        passive_index = 0
        x = 0
        for i in cluster['cluster-members']:
            if i['name'] == activenode:
                i['status'] = 'active'
                active_name = i['name']
                active_vlans = {'name': active_name, 'interfaces': []}
                print('active:', active_name)
                active_index = x
            else:
                i['status'] = 'passive'
                passive_name = i['name']
                passive_vlans = {'name': passive_name, 'interfaces': []}
                print('passive:', passive_name)
                passive_index = x
            x=x+1

        old_vlans = gaia_get_vlanifs(cpinterface, cluster['cluster-members'][active_index]['ip-address'], cpusername, cppassword)
        fwvlanlist = []
        for i in old_vlans['objects']:
            x = i['name'].split('.')
            fwvlanlist.append(x[1])
        #print(fwvlanlist)

        ipamvlanlist = []
        for i in childsubnets:
            ipamvlanlist.append(i['vlan-number'])
        #print(ipamvlanlist)
        s = set(fwvlanlist)
        diffed = [x for x in ipamvlanlist if x not in s]
        if i['vlan-number'] in diffed:
            print('VLANs will be added to the gate(s):')
        activeip = cluster['cluster-members'][active_index]['ip-address']
        client_args_gaia = APIClientArgs(server=activeip, unsafe=True, context='gaia_api')
        with APIClient(client_args_gaia) as client_gaia:
            # login to mgmt api
            login_res = client_gaia.login(cpusername, cppassword)

            if login_res.success is False:
                print('Login failed: {}'.format(login_res.error_message))
                exit(1)
            else:
                print('GAiA login succeeded')

            for i in childsubnets:
                if i['vlan-number'] in diffed:
                    print(i['vlan-number'] + ' - ' + i['subnet'] + '/' + i['mask'] + ' (' + i['description'] + ')')
                    vlan = {'parent': cpinterface,
                            'id': i['vlan-number'],
                            'ipv4-address': i['subnet'],
                            'ipv4-mask-length': i['mask'],
                            'comments': i['description']
                            }

                    print('adding vlan', i['vlan-number'], 'to GW', active_name)
                    active_vlans['interfaces'].append(gaia_add_vlanifs(vlan, activepeerid, cpnodenr))
        if 'passive_name' in locals():
            passiveip = cluster['cluster-members'][passive_index]['ip-address']
            client_args_gaia = APIClientArgs(server=passiveip, unsafe=True, context='gaia_api')
            with APIClient(client_args_gaia) as client_gaia:
                # login to mgmt api
                login_res = client_gaia.login(cpusername, cppassword)

                if login_res.success is False:
                    print('Login failed: {}'.format(login_res.error_message))
                    exit(1)
                else:
                    print('GAiA login succeeded')

                for i in childsubnets:
                    if i['vlan-number'] in diffed:
                        print(i['vlan-number'] + ' - ' + i['subnet'] + '/' + i['mask'] + ' (' + i['description'] + ')')
                        vlan = {'parent': cpinterface,
                                'id': i['vlan-number'],
                                'ipv4-address': i['subnet'],
                                'ipv4-mask-length': i['mask'],
                                'comments': i['description']
                                }
                        activeip = cluster['cluster-members'][active_index]['ip-address']
                        passiveip = cluster['cluster-members'][passive_index]['ip-address']

                        print('adding vlan', i['vlan-number'], 'to GW', passive_name)
                        passive_vlans['interfaces'].append(gaia_add_vlanifs(vlan, passivepeerid, cpnodenr))
        #print('active vlans:', active_vlans)
        #print('passive_vlans:', passive_vlans)

        cluster_vlans = create_cluster_vlans()
        #print('create_cluster_vlans():', json.dumps(cluster_vlans, indent=2))
        if cluster_vlans:
            client_args_mgmt = APIClientArgs(server=api_server, unsafe=True)
            with APIClient(client_args_mgmt) as client_mgmt:
                # login to mgmt api
                login_res = client_mgmt.login(cpusername, cppassword)

                if login_res.success is False:
                    print('Login failed: {}'.format(login_res.error_message))
                    exit(1)
                else:
                    print('Web API login succeeded')

                print('adding interfaces to {} in management...'.format(cluster['name']))
                add_vlanifs = mgmt_add_vlanifs(cluster_vlans)
                print('adding rule sections to policy {}...'.format(cppolicy))
                add_sections = mgmt_add_sections(fwsections, cppolicy)
                #print(cluster_vlans)
                #print(add_vlanifs)
                #print(add_sections)
                print('publishing...')
                mgmt_publish()
                print('done publishing!')
        else:
            print('Nothing to do. Woop-de-doo.')
