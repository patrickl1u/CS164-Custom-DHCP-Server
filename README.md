# CS164 Custom DHCP Project

## About

Custom DHCP implementation using Python3.

Requires `mininet` to run.

## Details

DHCP Server is hardcoded to the `10.0.0/24` subnet, and the DHCP server takes the first available IP at `10.0.0.1`.

A capture of the DHCP packets can be found at: https://www.cloudshark.org/captures/c109b95db0af

Once started, the program initializes the DHCP server and waits for incoming requests. IPs are assigned sequentially from the first available address, and remembers the MAC addresses of requestors. Only `BOOTREQUEST`, `BOOTREPLY`, `DHCPDISCOVER`, `DHCPREQUEST`, `DHCPOFFER`, and `DHCPACK` type packets are supported. 

