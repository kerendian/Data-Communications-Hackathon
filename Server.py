import socket
import time
import struct
from scapy.all import get_if_addr
import threading
import random

class Server:
    def __init__(self, port, dev):
        self.port = port
        if(dev):
            self.ip = get_if_addr('eth1') 
            self.broadcast = "172.1.255.255"
        else:
            self.ip = get_if_addr('eth2') 
            self.broadcast = "172.99.255.255" 
        # dict for the players in the game
        self.players = {}
        self.gameLock = threading.Lock()
        self.gameMode = False  
        # lock the players dict when writing to it
        self.playersDictLock = threading.Lock()
        udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
        # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
        # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
        # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
        # Thanks to @stevenreddie
        udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Enable broadcasting mode
        udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.bind((self.ip, self.port))

        # Set a timeout so the socket does not block
        # indefinitely when trying to receive data.
        #server.settimeout(0.2)
        #server.bind(("",44444)) do we need to bind? if yes, which port?
        print("Server started, listening on IP address {}".format(self.ip)) #need to update the ip to get_if_addr('eth1')/get_if_addr('eth2').
        self.udpThread = threading.Thread(target=self.sendBroadcast, args=(self.ip,self.port))
        self.tcpThread = threading.Thread(target=self.startGame)

        def sendBroadcast(IP, port):
            message = struct.pack('IbH', 0xabcddcba, 0x2 , port)
            while len(self.players) < 2:
                #need to send in message the UDP format package.
                udpServer.sendto(message, ('<broadcast>', 13117))
                time.sleep(1)
                #maybe we need 
            
            
            self.sendBroadcast(IP, port)

        def startTCP(self):
            while not self.gameMode:
                try:
                    
                    self.tcpServer.listen()
                    client, addr = self.tcpServer.accept()
                    data = self.tcpServer.recv(1027) #reciving name of client's team
                    self.playersDictLock.acquire()
                    self.players[addr] = [data.decode(),1] 
                    self.playersDictLock.release()
                    client2, addr2 = self.tcpServer.accept()
                    data2 = self.tcpServer.recv(1027) #reciving name of client's team
                    self.playersDictLock.acquire()
                    self.players[addr2] = [data2.decode(),2] 
                    self.playersDictLock.release()
                    problem,ans = self.randomQuestion()
                    clientThread1 = threading.Thread(target=self.startGame,args=(problem, ans))
                    clientThread2 = threading.Thread(target=self.startGame,args=(problem, ans))
                    self.gameMode = True
                    clientThread1.start()   
                    clientThread2.start()   
                except: 
                    pass
            time.sleep(1)  #TODO:check how much time to sleep without busy wait.
            self.startTCP()

        def startGame(self,problem,ans):
            time.sleep(10) #after both clients connected- neet to wait 10 seconds
            names = []
            for team in self.players:
                names.append(self.players[team][0])
            message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can\n How much is {}" \
            .format(names[0],names[1],problem)
            # do soctcpServer.settimeout(10) before -> then 
            try:
                tcpServer.settimeout(10)
                tcpServer.sendall(message.encode())
                # here we recieve the ans from one of the teams
                data, addr = tcpServer.recvfrom(1024)
                #     if(data):
                if(data):
                #         mutex.aquier()
                    self.gameLock.acquire()
                        #     win or lose the game to meesage. we will check here if the answer is correct.
                    team1, team2 = self.findSource(addr)
                    if data.decode() == ans: #winner
                        winner = team1 #name of the team
                        loser = team2       
                    else: #wrong answer
                        winner = team2 #name of the team
                        loser = team1
                    
                    #  #      send game summery to the clients -> the clients socket is in the players Dict -> send from the dict
                    summary = "Game over!\nThe correct answer was {}!\n\nCongratulations to the winner: {}".format(ans,winner)
                    tcpServer.sendall(summary.encode())
                    #     mutex.realease()
                    self.gameLock.release()
                        # close socket 
                   # tcpServer.close() TODO: check if we need to close it- need to understand close does-
                # handle exeption after 10 seconds. exept(TimeoutExeption)
            except socket.timeout: #TODO:need to make sure the timeoutexception from socekt.settimeout is this one
                # teko -> send summery to clients
                summary = "Game over!\nThe correct answer was {}!\n\nThe game ended in a tie".format(ans)
                tcpServer.sendall(summary.encode())
            finally:
                self.players={}
                self.gameMode = False
                #we can close here the sockets if needed.

                # close sockets 
                #tcpServer.close() TODO: check if we need to close it
               
        def randomQuestion(self):
            numbers = [1,2,3,4]
            number1 = random.choice(numbers) 
            number2 = random.choice(numbers)
            ans = number1 + number2
            return ("{} + {}?".format(number1, number2),ans) 
        def findSource(self,address): #find out which team returned the answer first
            for addr in self.players:
                if addr == address:
                    team1 = self.players[addr][0]
                else:
                    team2 = self.players[addr][0]
            return team1,team2

