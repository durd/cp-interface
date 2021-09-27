import argparse

class Config:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('parentsubnet', help='Master subnet, can not be a subnet that has VLAN assigned and whos child subnets don\'t have VLANs assigned')
        parser.add_argument('-i', '--ipamurl', help='IPAMs URL: http://<hostname or IP> | https://<hostname or ip>')
        parser.add_argument('-ip', '--ipampassword', help='IPAM password')
        parser.add_argument('-iu', '--ipamusername', help='IPAM username')
        parser.add_argument('-ia', '--ipamapp', help='IPAM API app')
        parser.add_argument('-csms', '--cpmanagement', help='CheckPoint Managements hostname or IP')
        parser.add_argument('-cp', '--cppassword', help='CheckPoint username')
        parser.add_argument('-cu', '--cpusername', help='CheckPoint password')
        parser.add_argument('-cnnr', '--cpnodenr', help='Cluster Node number')
        parser.add_argument('cppolicy', help='CheckPoint policy to add VLAN interfaces to. Gate will be derived from Installation target')
        parser.add_argument('cpinterface', help='Interface of gate to add VLAN interface to')
        self.config = parser.parse_args()

    def get_parentsubnet(self):
        return self.config.parentsubnet

    def get_ipam_url(self):
        return self.config.ipamurl

    def get_ipam_app(self):
        return self.config.ipamapp

    def get_ipam_username(self):
        return self.config.ipamusername

    def get_ipam_password(self):
        if self.config.ipampassword is not None:
            return self.config.ipampassword
        else:
            return ''

    def get_cp_management(self):
        return self.config.cpmanagement

    def get_cp_username(self):
        return self.config.cpusername
    def get_cp_nodenr(self):
        return self.config.cpnodenr

    def get_cp_password(self):
        if self.config.cppassword is not None:
            return self.config.cppassword
        else:
            return ''

    def get_cp_policy(self):
        return self.config.cppolicy

    def get_cp_interface(self):
        return self.config.cpinterface
