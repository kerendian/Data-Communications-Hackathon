import socket
#tcp example
    #https://gist.github.com/Integralist/3f004c3594bbf8431c15ed6db15809ae#file-python-tcp-client-example-py-L7
    #udp example
    #https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
    #another udp example
    #https://python-forum.io/thread-13611.html

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
# Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
# Thanks to @stevenreddie
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

client.bind(("", 13117))
while True:
    data, addr = client.recvfrom(1024) #this is a udp socket
    #TODO:need to make sure addr is the ip address of the server
    print("Received offer from " + str(addr) + ", attempting to connect...")
    #print("received message: %s"%data)
    #TODO:need to unpack the udp format packet to get the port 
    #TODO:create tcp connection- including creating a new TCP socket - tcpClient
    #TODO:send the team name over the TCP connection, followed by a line break (‘\n’)
    #TODO:response = tcpClient.recv(4096) #maybe need to change buffer size, now 4096
    #TODO: print(response)
    #TODO: need to know how to listen to keyboard while listening to TCP server.
    #TODO: if keyboard -> send to TCP server.
    #TODO:check how to see if game over, and the tcp connection is closed by cheking if tcpClient.recv
    #TODO: close the tcp socekt
    #TODO:after connection is closed- print("Server disconnected, listening for offer requests...")
