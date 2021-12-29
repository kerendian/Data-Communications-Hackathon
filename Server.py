from scapy.all import *
import socket
import time
import struct
# from scapy.all import get_if_addr
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
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
        # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
        # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
        # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
        # Thanks to @stevenreddie
        # self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Enable broadcasting mode
        self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.bind((self.ip, self.port))



        # Set a timeout so the socket does not block
        # indefinitely when trying to receive data.
        #server.settimeout(0.2)
        #server.bind(("",44444)) do we need to bind? if yes, which port?
        print("Server started, listening on IP address {}".format(self.ip)) #need to update the ip to get_if_addr('eth1')/get_if_addr('eth2').
        self.udpThread = threading.Thread(target=self.sendBroadcast, args=(self.ip,self.port))
        self.tcpThread = threading.Thread(target=self.startTCP )
        self.udpThread.start()
        self.tcpThread.start()
        self.udpThread.join()
        self.tcpThread.join()
        
    def sendBroadcast(self,IP, port):
        message = struct.pack('IbH', 0xabcddcba, 0x2 , port)
        while len(self.players) < 2:
            #need to send in message the UDP format package.
            self.udpServer.sendto(message, ('<broadcast>', 13117))
            time.sleep(1)
            #maybe we need      
        # self.sendBroadcast(IP, port)

    def startTCP(self):
        while not self.gameMode:
            try:               
                self.tcpServer.listen()
                client, addr = self.tcpServer.accept()
                data = client.recv(1027) #reciving name of client's team
                self.playersDictLock.acquire()
                self.players[addr] = [data.decode(),1,client] 
                self.playersDictLock.release()
                client2, addr2 = self.tcpServer.accept()
                data2 = client2.recv(1027) #reciving name of client's team
                self.playersDictLock.acquire()
                self.players[addr2] = [data2.decode(),2,client2] 
                self.playersDictLock.release()
                problem,ans = self.randomQuestion()
                clientThread1 = threading.Thread(target=self.startGame,args=(problem, ans,client))
                clientThread2 = threading.Thread(target=self.startGame,args=(problem, ans, client2))
                self.gameMode = True
                time.sleep(10) #after both clients connected- neet to wait 10 seconds
                message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can\n How much is {}" \
                .format(data.decode(),data2.decode(),problem)
                print(message)
                self.sendAllClients(message.encode())
                #client.sendall(message.encode())
                #client2.sendall(message.encode())
                clientThread1.start()   
                clientThread2.start()  
                clientThread1.join()   
                clientThread2.join()  
                # self.udpThread = threading.Thread(target=self.sendBroadcast, args=(self.ip,self.port))
                # self.udpThread.start()
                # self.udpThread.join() 
            except: 
                pass
        time.sleep(1)  #TODO:check how much time to sleep without busy wait.
        self.startTCP()

    def startGame(self,problem,ans, client):
        #time.sleep(10) #after both clients connected- neet to wait 10 seconds
        #names = []
        #for team in self.players:
            #names.append(self.players[team][0])
        #message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can\n How much is {}" \
        #.format(names[0],names[1],problem)
        # do soctcpServer.settimeout(10) before -> then 
        try:
            # TODO: 
            self.tcpServer.settimeout(10)
            self.tcpServer.sendall(message.encode())
            # here we recieve the ans from one of the teams
            #sol, addr = client.recvfrom(1024)
            sol, addr = client.recvfrom(1024)
            #     if(data):
            if(sol):
                #print("in sol")
            #         mutex.aquier()
                self.gameLock.acquire()
                    #     win or lose the game to meesage. we will check here if the answer is correct.
                team1, team2 = self.findSource(addr)
                if sol.decode() == ans: #winner
                    #winner = team1 #name of the team
                    #loser = team2       
                    self.gameOver(team1,ans)
                else: #wrong answer
                    #winner = team2 #name of the team
                    #loser = team1
                    self.gameOver(team2,ans)
                
                #  #      send game summery to the clients -> the clients socket is in the players Dict -> send from the dict
                #summary = "Game over!\nThe correct answer was {}!\n\nCongratulations to the winner: {}".format(ans,winner)
                #client.sendall(summary.encode())
                #     mutex.realease()
                self.gameLock.release()
                    # close socket 
                # tcpServer.close() TODO: check if we need to close it- need to understand close does-
            # handle exeption after 10 seconds. exept(TimeoutExeption)
        except socket.timeout: #TODO:need to make sure the timeoutexception from socekt.settimeout is this one
            # teko -> send summery to clients
            #self.gameLock.release()
            #summary = "Game over!\nThe correct answer was {}!\n\nThe game ended in a tie".format(ans)
            #client.sendall(summary.encode())
            self.gameOver(None,ans)
        finally:
            # print("in finally")
            # self.players={}
            # self.gameMode = False
            #we can close here the sockets if needed.

            # close sockets 
            client.close() # TODO: check if we need to close it
            

            
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

Server(2032, True)
