# odl-gpb-test

Scripts for testing Group Based Policy in OpenDaylight

# Controller setup

```
feature:install odl-groupbasedpolicy-ofoverlay odl-groupbasedpolicy-ui odl-restconf odl-dlux-yangui
```

# Useful OVS commands

## Dump flows

```sh
sudo ovs-ofctl -O Openflow13 dump-flows s1
sudo ovs-ofctl -O Openflow13 dump-flows s2
```

## Port name and port id mapping
See http://openvswitch.org/pipermail/discuss/2015-July/018099.html

```sh
sudo ovs-vsctl -- --columns=name,ofport list Interface
```

## Dump database

```sh
sudo ovsdb-client dump
```
