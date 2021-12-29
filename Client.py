import errno
import multiprocessing
import os
import socket
import sys
import threading
import time
import selectors
import termios
import tty
import struct

class Client:
    def __init__(self, dev):
        self.tcpConected = None
        self.teamName = "Amen"   
        UDP_PORT = 13117
        # Mode = 0 #0 for listening, 1 for playing
        print("Client started, listening for offer requests...")
        udpClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        udpClient.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udpClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpClient.bind(("", UDP_PORT))
        tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            data, addr = udpClient.recvfrom(1024)
            if data is None:
                    continue
            try:
                message = struct.unpack('IbH' , data)
                if(message[0]!= 0xabcddcba):
                   continue
            except:
                continue
           
            else:
                print(("Received offer from {}, attempting to connect...".format(str(addr[0]))))
                udpClient.close()
                try:
                    # tcpClient.connect((addr[0], message[2]))
                    tcpClient.connect((socket.gethostname(), message[2]))
                    tcpClient.sendall((self.teamName + "\n").encode())
                    problem, addr1 = tcpClient.recvfrom(1024)
                    print(problem.decode())
                    self.tcpConected = tcpClient
                    self.currSelector = selectors.DefaultSelector()
                    self.currSelector.register(sys.stdin, selectors.EVENT_READ, self.got_keyboard_data)
                    self.currSelector.register(tcpConected, selectors.EVENT_READ, self.printServerSummary)
                    old_settings = termios.tcgetattr(sys.stdin)
                    tty.setcbreak(sys.stdin.fileno())
                    while self.tcpConected is not None:
                        events = self.currSelector.select()
                        for k, mask in events:
                            callback = k.data
                            callback(k.fileobj)
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    tcpClient.close()
                except Exception:
                    tcpClient.close()
                  
                tcpConected = None
                self.clearSocket(udpClient)
                print("Server disconnected, listening for offer requests...")
    
    def got_keyboard_data(self, stdin):
        if self.tcpConected is not None:
            sol = stdin.read()
            self.tcpConected.send(sol.encode())


    def printServerSummary(self, currSocket):
        summary, addr = currSocket.recvfrom(1024)
        print(summary.decode())
        self.tcpConected = None
        self.currSelector.unregister(sys.stdin)
        self.currSelector.unregister(currSocket)


    def clearSocket(self,currSocket):
        currSocket.setblocking(False) # set the socket to non blocking
        while True:
            try:
                currSocket.recv(1024)
            except socket.error as e: # no data availible in the socket
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    break
        currSocket.setblocking(True)  
Client(True)