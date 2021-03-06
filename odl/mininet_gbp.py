
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Node

import re
import time
from subprocess import call
from subprocess import check_output

def addSwitch(net, name, dpid=None):
    switch = net.addSwitch(name, dpid=dpid)
    return switch

def addHost(net, switch, name, ip, mac):
    host = net.addHost(name, ip=ip, mac=mac)
    net.addLink(host, switch)

def setOFVersion(sw, version='OpenFlow13'):
    call(['ovs-vsctl', 'set', 'bridge', sw, 'protocols={}'.format(version)])

def addTunnel(sw, sourceIp=None):
    ifaceName = '{}_vxlan0'.format(sw)
    cmd = ['ovs-vsctl', 'add-port', sw, ifaceName,
           '--', 'set', 'Interface', ifaceName,
           'type=vxlan', 
           'options:remote_ip=flow',
           'options:key=flow']
    if sourceIp is not None:
        cmd.append('options:source_ip={}'.format(sourceIp))
    call(cmd)

#ovs-ofctl dump-ports-desc s1 -OOpenFlow13

def startMininet(switches, hosts, contIP='127.0.0.1'):
    setLogLevel('info')

    net = Mininet(controller=None,
                  autoSetMacs=True,
                  listenPort=6634)
    net.addController('c0', controller=RemoteController, 
                      ip=contIP, port=6653)

    swobjs = {}
    swports = {}

    for sw in switches:
        swobj = addSwitch(net, sw['name'])
        swobjs[sw['name']] = swobj
        swports[sw['name']] = 0;
    for host in hosts:
        if host['switch'] not in swobjs:
            continue
        sw = swobjs[host['switch']]
        swports[host['switch']] += 1;
        port = swports[host['switch']]
        addHost(net, sw, host['name'], host['ip'], host['mac'])
        host['port'] = port

    try:
        net.start()
        for sw in switches:
            addTunnel(sw['name'], sw['tunnelIp'])

        for host in net.hosts:
            gw = re.sub(r'.\d+$', ".1", host.IP())
            host.cmd('route add default gw {}'.format(gw))

        # ODL is very fragile so let's give it some time
        time.sleep(1)

        for sw in switches:
            setOFVersion(sw['name'])

        return net
    except Exception, e:
        net.stop()
        raise e
