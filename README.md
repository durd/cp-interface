# cp-interfaces.py

Adds VLAN-interfaces to CheckPoint firewalls and it's object on the Management-server, read from a supernet in phpIPAM.

## Caveats

This script has no error-checking except what is in the SDKs/APIs that I've used. It will add the wrong VLANs to the wrong gateway and policy!  
Also, a feature. It will add all the VLANs as rule sections even if only one VLAN was added. Easy enough to clean up, but annoying.  
I didn't have a proper test environment when making this, once I used the script in production I didn't have time to fix things, so it's quick and dirty and ugly. I blame my python-skills.

## Requisites

* only adds NEW VLAN-interfaces
* not tested if a VLAN is removed from IPAM
* can not be used to "sync" a node to another node, please se `cp-clone-interface` instead
* IP-adressering antar att kluster-ip, och båda nod-IP:na kommer efter varandra: vip, nod-1, nod-2
* IP-addressing assumes that cluster-ip and both node-IPs are after eachother, ex: vip .1, node-1 .2, node-2 .3
* cluster object IP needs to be reachable, ie create a vip for the cluster IP

## Requirements

### phpIPAM

* \>v1.4
* access to the phpIPAM in question:
  * HTTP or HTTPS (self-signed works, generates a bunch of warnings)
  * A user for API
  * a group with read-permissions in the "Section" in question(, also permission to read certain VLANs??)
  * need an API application with read permission
  * App security bör vara "SSL with User token" - en användare loggar in och får en ny token vid inloggning. Vid byggandet av script fungerade detta även med http.
  * "App security" should be "SSL with User token" - a user logs in and gets a new token at login. When building this script, HTTP worked even though SSL was selected.
* data structure
  * the script reads from a parent subnet (supernet)
  * from the parent subnet the child subnets are read
  * the child subnets MUST have a VLAN-id (id in phpIPAM) that is NOT zero
  * child subnets VLAN and VLAN-number are read
  * unused subnets MUST have at least three x's in its description: `subnet-description-xxx` to not be added in the firewalls
  * the script assumes that within a section there aren't any VLAN's that contain several subnets
  * antagande är också att ett parent-subnät INTE innehåller ett nät som ska till en annan brandvägg
  * the script also assumes that a parent subnet does NOT contain a subnet that should belong to a different firewall. (
  * every subnet under a supernet that has a VLAN-id (not number) is added to the same firewall. Issues within your network could arrise

### CheckPoint

* API version \>1.6.1 (R80.40 JHF 78 or newer)
* access to both Management and the gateways/nodes in question
  * HTTPS, self-signed certificates are fine
  * a user for API, or your own user
  * same user and password on both Management and gateways/nodes
  * bug, not needed currently: the user on the gate must belong to the API-role or have access to the GAiA API according to [https://sc1.checkpoint.com/documents/latest/GaiaAPIs/?#api_access-v1.3%20](GAiA API Reference)
* data structure
  * cluster object in question is read from the supplied policy package on commandline
  * existing VLANs are fetched from the active node (actually the cluster, but that is the active node)
  * the gateways VLANs are diffed against the VLANs from IPAM and a list is created with VLANs that are not on the gateway
  * a description for the interface on the gateway and in the cluster object is built from IPAM subnet description
  * Rule section names are created with the following convention: `<vlan-id>-<subnet>_<mask>-<vlan-description>`
  * VLAN is added to a parent interface (bond, physical etc), first on the active node and then the passive node. This so that the cluster doesn't fail unnecessarily.
  * the VLANs added to the gateway are added to the cluster object
  * Rule sections are added at the bottom of the policy package supplied on commandline
  * if any VLANs have been added to the cluster object, the changes are published/saved but not installed

### The script

Install python3 dependencies with:
`pip3 install -r requirements.txt`

Tested with Python3.9.5. Please create a virtualenv before installing dependencies.

#### Syntax

```text
python3 ./cp-interfaces2.py -i <ipam url> -iu <user> -ip <password -ia <api_app> -csms <IP or hostname> -cu <user> -cp <password> -cnnr <#> <supernet> <policy name> <parent interface>

<-i>                URL to phpIPAM
<-iu>               username in phpIPAM
<-ip>               password for the above user
<-ia>               API-app in phpIPAM
<-csms>             IP or hostname CP Management in question
<-cu>               username in CheckPoint
<-cp>               password for the above user
<-cnnr>             Cluster Node Number, if you for some reason are setting up your secondary gateways first, put a 2 here - else 1.
<supernet>          supernet from phpIPAM
<policy name>       name of policy package which cluster/gateway belongs to as an 'Installation target'
<parent interface>  interface that will have the VLANs added to

Example:  
python3 ./cp-interfaces.py -i http://ipam.example.com -iu user -ip password -ia api_app -csms cp-mgmt -cu user -cp password -cnnr 1 10.10.10.16/28 Standard eth1
```
