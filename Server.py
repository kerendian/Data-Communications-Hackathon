from scapy.all import *
import socket
import time
import struct
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
        # Enable broadcasting mode
        self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.bind((self.ip, self.port))
        print("Server started, listening on IP address {}".format(self.ip)) 
        #starting 2 threads- udp for broadcast and tcp for game
        self.udpThread = threading.Thread(target=self.sendBroadcast, args=(self.ip,self.port))
        self.tcpThread = threading.Thread(target=self.startTCP )
        self.udpThread.start()
        self.tcpThread.start()
        self.udpThread.join()
        self.tcpThread.join()
    
    def sendBroadcast(self,IP, port):
        print("sending broadcast messages")
        #sending broadcast message every second until the game starts
        message = struct.pack('IbH', 0xabcddcba, 0x2 , port)
        while len(self.players) < 2:
            self.udpServer.sendto(message, (self.broadcast, 13117))
            time.sleep(1)

    def startTCP(self):
        #start the tcp conection with both clients and start game- each client in different thread
        while not self.gameMode:
            try:               
                self.tcpServer.listen()
                client, addr = self.tcpServer.accept()
                print("Player 1 connected, waiting for player 2")
                data = client.recv(1027) #reciving name of client's team
                self.playersDictLock.acquire() #adding the first player to the dictionary
                self.players[addr] = [data.decode(),1,client] 
                self.playersDictLock.release()
                client2, addr2 = self.tcpServer.accept()
                print("Player 2 connected, the game will start in a few seconds")
                data2 = client2.recv(1027) #reciving name of client's team
                self.playersDictLock.acquire()  #adding the second player to the dictionary
                self.players[addr2] = [data2.decode(),2,client2] 
                self.playersDictLock.release()
                problem,ans = self.randomQuestion() #random math question to solve
                clientThread1 = threading.Thread(target=self.startGame,args=(problem, ans,client,addr))
                clientThread2 = threading.Thread(target=self.startGame,args=(problem, ans, client2,addr2))
                self.gameMode = True
                time.sleep(10) #after both clients connected- neet to wait 10 seconds
                message = "Welcome to Quick Maths.\nPlayer 1: {}\nPlayer 2: {}\n==\nPlease answer the following question as fast as you can\n How much is {}" \
                .format(data.decode(),data2.decode(),problem)
                print(message)
                self.sendAllClients(message.encode())
                clientThread1.start()   
                clientThread2.start()  
                clientThread1.join()   
                clientThread2.join()  
            except: 
                pass
        time.sleep(1)  
        self.startTCP()

    def startGame(self,problem,ans, client,addr):
        
        try:
            client.settimeout(10) # if 10 seconds passed- the game ends in a tie
            # here we recieve the ans from one of the teams
            sol = client.recv(1024)
            if(sol):
                self.gameLock.acquire()
                #find out which client sent sol
                team1, team2 = self.findSource(addr)
                if sol.decode() == ans: #winner       
                    self.gameOver(team1,ans)
                else: #wrong answer
                    self.gameOver(team2,ans)
                self.gameLock.release()
                   
        except socket.timeout:
            # tie -> send summery to clients
            self.gameOver(None,ans)
        except exception as e:
            print(e)
        finally:
            client.close() #TODO: check if we need to close it
              
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

#########################################
    def sendAllClients(self, msg):
        for player in self.players:
            try:
                self.players[player][2].sendall(msg)
            except socket.error as e:
                pass
    
    def gameOver(self, winner, ans):
        if winner is None:
            summary = "Game over!\nThe correct answer was {}!\nThe game finished in a tie.".format(ans)
        else:
            summary = "Game over!\nThe correct answer was {}!\n\nCongratulations to the winner: {}".format(ans,winner)
        print(summary)
        self.sendAllClients(summary.encode())
        self.playersDictLock.acquire()
        self.players={}
        self.playersDictLock.release()
        self.gameMode = False
        print("Game over, sending out offer requests...")
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable broadcasting mode
        self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udpThread = threading.Thread(target=self.sendBroadcast, args=(self.ip,self.port))
        self.udpThread.start()
        self.udpThread.join()
        #self.sendBroadcast(self.ip,self.port)
        return
Server(2032, True)