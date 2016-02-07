#!/usr/bin/python
import os
import sys
from subprocess import call

import mininet.cli
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Node

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
        'ip': '10.0.35.2/24',
        'switch': 's1'
    },
    {
        'name': 'h35_3',
        'mac': '00:00:00:00:35:03',
        'ip': '10.0.35.3/24',
        'switch': 's2'
    }
]

swobjs = {}
swports = {}
hostobjs = {}

def addTunnel(switchName, sourceIp=None):
    ifaceName = '{}_vxlan0'.format(switchName)
    cmd = ['ovs-vsctl', 'add-port', switchName, ifaceName,
           '--', 'set', 'Interface', ifaceName,
           'type=vxlan',
           'options:remote_ip=flow',
           'options:key=flow']
    if sourceIp is not None:
        cmd.append('options:source_ip={}'.format(sourceIp))
    call(cmd)

def setup_mininet(controller):
    setLogLevel('info')

    net = Mininet(controller=None, autoSetMacs=True, listenPort=6634)
    net.addController('c0', controller=RemoteController, ip=controller, port=6653)

    try:
        for sw in switches:
            swobjs[sw['name']] = net.addSwitch(sw['name'], dpid=sw['dpid'])
            swports[sw['name']] = 0
        for host in hosts:
            if host['switch'] not in swobjs:
                raise Exception("No switch named: {}".format(host['switch']))
            swobj = swobjs[host['switch']]

            hostobj = net.addHost(host['name'], ip=host['ip'], mac=host['mac'])
            net.addLink(hostobj, swobj)

            hostobjs[host['name']] = hostobj
            host['port'] = swports[host['switch']]
            swports[host['switch']] += 1
        net.start()

        for sw in switches:
            addTunnel(sw['name'])

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
        net = setup_mininet(controller)
        if net is not None:
            mininet.cli.CLI(net)
    finally:
        if net is not None:
            net.stop()


if __name__ == '__main__':
    main()
