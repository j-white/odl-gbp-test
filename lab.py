#!/usr/bin/python
import os
import sys
from subprocess import call
import time

import mininet.cli
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Node

from odl_gbp import *

switches = [
    {
        'name': 's1',
        'dpid': '1',
        'instance': None
    },
    {
        'name': 's2',
        'dpid': '2',
        'instance': None
    }
]

hosts = [
    {
        'name': 'h35_2',
        'mac': '00:00:00:00:35:02',
        'ip': '10.0.35.2',
        'prefix': 24,
        'switch': 's1'
    },
    {
        'name': 'h35_3',
        'mac': '00:00:00:00:35:03',
        'ip': '10.0.35.3',
        'prefix': 24,
        'switch': 's2'
    }
]

swobjs = {}
swports = {}
hostobjs = {}

def addTunnel(switchName, index, sourceIp=None):
    ifaceName = '{}_vxlan0'.format(switchName)
    cmd = ['ovs-vsctl', 'add-port', switchName, ifaceName,
           '--', 'set', 'Interface', ifaceName,
           'type=vxlan',
           # FIXME
           "option:local_ip=127.0.0.{}".format(index),
           'options:remote_ip=flow',
           'options:key=flow']
    if sourceIp is not None:
        cmd.append('options:source_ip={}'.format(sourceIp))
    call(cmd)

def setOFVersion(sw, version='OpenFlow13'):
    call(['ovs-vsctl', 'set', 'bridge', sw, 'protocols={}'.format(version)])

def setup_mininet(controller):
    setLogLevel('info')

    net = Mininet(controller=None, autoSetMacs=True, listenPort=6634)
    net.addController('c0', controller=RemoteController, ip=controller, port=6653)

    try:
        for sw in switches:
            swobjs[sw['name']] = net.addSwitch(sw['name'], dpid=sw['dpid'], protocols='OpenFlow13')
            swports[sw['name']] = 0
        for host in hosts:
            if host['switch'] not in swobjs:
                raise Exception("No switch named: {}".format(host['switch']))
            swobj = swobjs[host['switch']]

            hostobj = net.addHost(host['name'], ip="{}/{}".format(host['ip'], host['prefix']), mac=host['mac'])
            net.addLink(hostobj, swobj)

            hostobjs[host['name']] = hostobj
            host['port'] = swports[host['switch']]
            swports[host['switch']] += 1

        net.start()

        i = 1
        for sw in switches:
            addTunnel(sw['name'], i)
            i += 1
            #setOFVersion(sw['name'])

        time.sleep(3)

        return net
    except Exception, e:
        net.stop()
        raise e


def main():
    controller = os.environ.get('ODL')
    if controller == None:
        sys.exit("No controller set.")

    net = None
    try:
        # Setup Mininet with the configured topology
        net = setup_mininet(controller)

        print "Creating Tenant"
        put(controller, DEFAULT_PORT, get_tenant_uri(), get_tenant_data(), True)
        print "Sending Tunnel"
        put(controller, DEFAULT_PORT, get_tunnel_uri(), get_tunnel_data(switches), True)
        print "Registering Endpoints"
        for endpoint in get_endpoint_data(hosts):
            post(controller, DEFAULT_PORT, get_endpoint_uri(), endpoint, True)

        if net is not None:
            mininet.cli.CLI(net)
    finally:
        if net is not None:
            net.stop()


if __name__ == '__main__':
    main()
