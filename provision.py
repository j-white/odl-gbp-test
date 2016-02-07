#!/usr/bin/python
from odl import odl_gbp
from odl.config import TENANT, L3CTX, L2BD
import re

controller_ip = "10.255.1.1"

EG1="1eaf9a67-a171-42a8-9282-71cf702f61dd"

hosts = [{'name': 'h35_2',
          'mac': '00:00:00:00:35:02',
          'ip': '10.0.35.2/24',
          'switch': 's1',
          'tenant': TENANT,
          'endpointGroup': EG1,
          'port': 1}]

def main():
    nodes = [{
        "id": "openflow:{}".format(1),
       # "ofoverlay:tunnel-ip": "10.255.1.2"
    }]
    odl_gbp.register_nodes(controller_ip, nodes)

    eps = []
    for host in hosts:
        ep = odl_gbp.get_ep(TENANT,
                       host['endpointGroup'],
                       L3CTX,
                       re.sub(r'/\d+$', '', host['ip']),
                       L2BD,
                       host['mac'],
                       1, host['port'])
        eps.append(ep)
    odl_gbp.register_eps(controller_ip, eps)


    g1_ep = odl_gbp.get_epg(TENANT, 'g1')


    tenant = odl_gbp.get_tenant(TENANT)
    odl_gbp.get_l3c(TENANT, L3CTX)
    odl_gbp.get_bd(TENANT, L2BD, L3CTX)
    odl_gbp.register_tenants(controller_ip, [tenant])


if __name__ == '__main__':
    main()
