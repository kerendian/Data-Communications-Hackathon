import socket
import time
import struct

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
# Thanks to @stevenreddie
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
#server.settimeout(0.2)
#server.bind(("",44444)) do we need to bind? if yes, which port?
print("Server started, listening on IP address 172.1.0.32") #need to update the ip to get_if_addr('eth1')/get_if_addr('eth2').
message = b"your very important message"
while True:
    #need to send in message the UDP format package.
    server.sendto(message, ('<broadcast>', 13117))
    print("message sent!")
    time.sleep(1)
    #maybe we need 