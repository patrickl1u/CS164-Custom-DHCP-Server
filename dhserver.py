import dhcppython
import ipaddress

DHCP_SERVER = ('', 67)
DHCP_CLIENT = ('255.255.255.255', 68)

# Create a UDP socket
s = socket(AF_INET, SOCK_DGRAM)

# Allow socket to broadcast messages
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

# Bind socket to the well-known port reserved for DHCP servers
s.bind(DHCP_SERVER)

def decode(msg):
	return format(msg, 'x')

def createsubnet():
	# hardcode /24 subnet
	# also assume first IP is 10.0.0.1
	# create pairs of ipaddress_ipv4 and string (MAC)
	avail_ips = []
	for x in range(2, 255):
		tmpip = '10.0.0.{}'.format(x)
		avail_ips.append((ipaddress.ip_address(tmpip),""))
	return avail_ips

def searchmac(avail_ips, macaddr):
	for (x, y) in avail_ips:
		if(y == ""):
			continue
		if(y == macaddr):
			return x
	return -1

# return first free IP
def nextfreeip(avail_ips):
	for (x, y) in avail_ips:
		if(y == ""):
			return x
		continue
	# reach here if no free IP's are available
	return -1

# given ip and mac, set accordingly and return new list
# should have written this better in the beginning but w/e
def setipformac(avail_ips, ipaddr, macaddr):
	for x in range(len(avail_ips)):
		a, b = avail_ips[x]
		if(a == ipaddr):
			avail_ips[x] = (ipaddr, macaddr)
			return 0
	# did not successfully set an IP address
	return -1

avail_ips = createsubnet()
# print(avail_ips)
dhcpserveripaddr = ipaddress.ip_address('10.0.0.1')
while(1):
	msg, addr = s.recvfrom(1024)
	# for i in range(0, len(msg)):
	# 	print(format(msg[i], 'x'))
	pkt = dhcppython.packet.DHCPPacket.from_bytes(msg)
	print(pkt)
	print(pkt.op)

	if(pkt.op == "BOOTREQUEST"):
		# we are dealing with receiving message (DHCP Request)

		# determine if this is dhcp discover or request
		# print(pkt.options[0].code)
		pkttype = 0
		for x in pkt.options:
			if(x.code == 53):
				if(x.data == b'\x01'):
					print("DHCP DISCOVER")
					# so primitive
					pkttype = 1
				elif(x.data == b'\x03'):
					print("DHCP REQUEST")
					pkttype = 3
			if(x.code == 255):
				break
		if(pkttype == 0):
			# \x03 is possibly wrong
			print("errorjsfoiwejiofwea")

		# modify received packet to be DHCP Offer

		macaddr = pkt.chaddr
		newip = searchmac(avail_ips, macaddr)
		if(newip == -1):
			# find next free IP and assign
			newip = nextfreeip(avail_ips)
			if(newip == -1):
				# need sys (probably?) for exit so this will suffice
				print("massive error...")
			else:
				# record in our very primitive database new ip assignment
				setipformac(avail_ips, newip, macaddr)
		# else we have an IP already for this MAC

		# print(searchmac(avail_ips, macaddr))
		# avail_ips[0] = (ipaddress.ip_address('10.0.0.2'), macaddr)
		# print(searchmac(avail_ips, macaddr))

		# change boot options
		# tosend_options = dhcppython.options.short_value_to_object(53, "DHCPOFFER")
		if(pkttype == 1):
			# constructor does not allow specification of siaddr=dhcpserveripaddr
			# issue? we will see...
			tosend = dhcppython.packet.DHCPPacket.Offer(macaddr, seconds=0, tx_id=pkt.xid, yiaddr=newip)
		if(pkttype == 3):
			tosend = dhcppython.packet.DHCPPacket.Ack(macaddr, seconds=0, tx_id=pkt.xid, yiaddr=newip)
			tosend.options.insert(1, dhcppython.options.options.short_value_to_object(51, 3600))
			# "no expiry time on offered lease. Server added to list of rejected servers."
			# opt_list = dhcppython.options.OptionList(
			# 	[
			# 		dhcppython.options.options.short_value_to_object(53, "DHCPOFFER"),
			# 		dhcppython.options.options.short_value_to_object(51, 3600),
			# 		dhcppython.options.options.short_value_to_object(255, '')
			# 	]
			# )
			# tosend.options = opt_list
		print(tosend)
		# tosend = pkt
		# tosend.op = "BOOTREPLY"

		# # ciaddr: ip of client (null @ dhcp discover/request) 
		# # yiaddr: ip to assign
		# # siaddr: ip of dhcp server
		# # giaddr: don't use
		# # print(type(tosend.siaddr))

		# # pick IP from pool somewhere
		# tosend.yiaddr = newip
		# tosend.siaddr = ipaddress.ip_address('10.0.0.1')

		# send packet over UDP
		# convert to bytes
		s.sendto(tosend.asbytes, DHCP_CLIENT)

	else:
		# not too sure lol...
		# only we should be sending these packets?
		# probably safe to ignore
		pass