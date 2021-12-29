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
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CEND      = '\33[0m'
class Client:
    def __init__(self):
        self.tcpConected = None
        self.teamName = "Amen"   
        UDP_PORT = 13117
        print(f'{CBOLD}{CRED}Client started, listening for offer requests...{CEND}')
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

                print(f'{CITALIC}{CYELLOW}Received offer from %s, attempting to connect...{CEND}' %str(addr[0]))
                try:
                    # client connection to TCP socket
                    tcpClient.connect((addr[0], message[2]))
                    print(f'{CBLUE}connected to server{CEND}')
                    # sending the Team Name over the TCP socket
                    tcpClient.sendall((self.teamName + "\n").encode())
                    # recieving the Math Problem from the server 
                    problem, addr1 = tcpClient.recvfrom(1024)
                    print(f'{CVIOLET}{CBOLD}problem.decode(){CEND}')
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
                    print(f'{CITALIC}{CRED}Server disconnected, listening for offer requests...{CEND}')
    # function to handdle keyboard press event within the selector
    def pressedKeyboard(self, stdin):
        if self.tcpConected is not None:
            sol = sys.stdin.readline(1)
            self.tcpConected.sendall(sol.encode())

    # function to handdle server TCP messages events within the selector
    def printServerSummary(self, currSocket):
        summary, addr = currSocket.recvfrom(1024)
        print(f'{CITALIC}{CBOLD}{CGREEN}summary.decode(){CEND}')
        self.tcpConected = None
        self.currSelector.unregister(sys.stdin)
        self.currSelector.unregister(currSocket)


Client()