from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink
from time import sleep
import os

class MyTopo( Topo ):
    def __init__( self ):
        Topo.__init__( self )

        Host=[]
        Server=[]
        SW=[]
        for i in range(3):
            Host.append(self.addHost('h%s' %(i+1), ip='192.168.1.%s/24' %(i+1)))
            if i < 2:
                Server.append(self.addHost('srv%s' %(i+1), ip='192.168.1.20%s/24' %i))

        for i in range(7):
            SW.append(self.addSwitch('s%s' % (i+1)))

        linkopts1 = dict(bw=1000, delay='5ms')
        linkopts2 = dict(bw=100, delay='1ms')

        for i in range(3):
            for ii in range(3):
                v1 = ii%3 + i*2
                v2 = (ii+1)%3 + i*2
                if i==1:
                    if v1==2:
                        v1=1
                    if v2==2:
                        v2=1
                if i==2:
                    if v1==4:
                        v1=2
                    if v2==4:
                        v2=2
                self.addLink(SW[v1], SW[v2], **linkopts1)

        for i in range(4):
            if i < 3:
               self.addLink(SW[i+3], Host[i], **linkopts2)
            else:
                for ii in range(2):
                    self.addLink(SW[i+3], Server[ii], **linkopts1)

def SimpleSW(mn):
    for i in range(2):
        for ii in range(2,7,2):
            s_node = mn.getNodeByName('s%s' %(ii+i))
            s_node.cmd ('ifconfig s%s-eth%s down' %(ii+i, 2-i))
            print('ifconfig s%s-eth%s down' %(ii+i, 2-i))
    sleep(1)
    print('Enable OFS with OpenlFlow version 1.3')
    for i in range(7):
        sw_node = mn.getNodeByName('s%s' %(i+1))
        sw_node.cmd('ovs-vsctl set Bridge s%s protocols=OpenFlow13' %(i+1))

    c_node = mn.getNodeByName('c0')
    c_node.cmd ('ryu-manager ryu.app.simple_switch &')
    CLI(mn)


def SimpleFW(mn):
    for i in range(2):
        for ii in range(2,7,2):
            s_node = mn.getNodeByName('s%s' %(ii+i))
            s_node.cmd ('ifconfig s%s-eth%s down' %(ii+i, 2-i))
            print('ifconfig s%s-eth%s down' %(ii+i, 2-i))
    sleep(1)
    print('Enable OFS with OpenlFlow version 1.3')
    for i in range(7):
        sw_node = mn.getNodeByName('s%s' %(i+1))
        sw_node.cmd('ovs-vsctl set Bridge s%s protocols=OpenFlow13' %(i+1))
    sleep(1)
    c_node = mn.getNodeByName('c0')
    c_node.cmd ('ryu-manager ryu.app.simple_switch &')
    sleep(1)
    c_node.cmd('ryu-manager ryu.app.rest_firewall &')
    print('Please wait 5 seconds for staring the service')
    sleep(6)
    c_node.cmd('sudo curl -X PUT http://localhost:8080/firewall/module/enable/all')
    sleep(1)
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.3/32", "nw_proto": "ICMP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.0/30", "nw_dst": "192.168.1.200/31", "nw_proto": "ICMP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.200/31", "nw_proto": "ICMP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.1/32", "nw_dst": "192.168.1.200/32", "nw_proto": "TCP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.2/32", "nw_dst": "192.168.1.201/32", "nw_proto": "UDP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.3/32", "nw_dst": "192.168.1.200/31", "nw_proto": "TCP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.3/32", "nw_dst": "192.168.1.200/31", "nw_proto": "UDP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.200/31", "nw_proto": "TCP"}\' http://localhost:8080/firewall/rules/all')
    c_node.cmd ('curl -X POST -d \'{"nw_src": "192.168.1.200/31", "nw_proto": "UDP"}\' http://localhost:8080/firewall/rules/all')
    CLI(mn)


tests = {'ssw': SimpleSW, 'sfw': SimpleFW}
topos = { 'mytopo': ( lambda: MyTopo() ) }
