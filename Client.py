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
    def __init__(self):
        self.tcpConected = None
        self.teamName = "Amen"   
        UDP_PORT = 13117
        print("Client started, listening for offer requests...")
        # UDP socket creation
        udpClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udpClient.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udpClient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpClient.bind(("", UDP_PORT))
        tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
           # recieve input from client in UDP Socket
            data, addr = udpClient.recvfrom(1024)
            if data is None:
                    continue
            try:
                message = struct.unpack('IbH' , data)
                # checking if the UDP message is in the correct format
                if(message[0]!= 0xabcddcba or message[1]!= 0x2): 
                   continue
            except:
                continue
           
            else:

                print(("Received offer from {}, attempting to connect...".format(str(addr[0]))))
                try:
                    # client connection to TCP socket
                    tcpClient.connect((addr[0], message[2]))
                    print("connected to server")
                    # sending the Team Name over the TCP socket
                    tcpClient.sendall((self.teamName + "\n").encode())
                    # recieving the Math Problem from the server 
                    problem, addr1 = tcpClient.recvfrom(1024)
                    print(problem.decode())
                    self.tcpConected = tcpClient
                    # define selector to listen to server TCP messages and key presses non blokingly 
                    self.currSelector = selectors.DefaultSelector()
                    self.currSelector.register(sys.stdin, selectors.EVENT_READ, self.pressedKeyboard)
                    self.currSelector.register(self.tcpConected, selectors.EVENT_READ, self.printServerSummary)
                    old_settings = termios.tcgetattr(sys.stdin)
                    tty.setcbreak(sys.stdin.fileno())
                    while self.tcpConected is not None:
                        events = self.currSelector.select()
                        for k, mask in events:
                            callback = k.data
                            callback(k.fileobj)
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    tcpClient.close()
                except Exception as e:
                    print(e)
                  
                else:  
                    self.tcpConected = None
                    print("Server disconnected, listening for offer requests...")
    # function to handdle keyboard press event within the selector
    def pressedKeyboard(self, stdin):
        if self.tcpConected is not None:
            sol = sys.stdin.readline(1)
            self.tcpConected.sendall(sol.encode())

    # function to handdle server TCP messages events within the selector
    def printServerSummary(self, currSocket):
        summary, addr = currSocket.recvfrom(1024)
        print(summary.decode())
        self.tcpConected = None
        self.currSelector.unregister(sys.stdin)
        self.currSelector.unregister(currSocket)


Client()