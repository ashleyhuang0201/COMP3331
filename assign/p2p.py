#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8
import socket
import sys
import threading
from time import sleep
import select

class Peers:
    def __init__(self, id_number, first_succ, second_succ, ping_interval):
        self.id_number = id_number
        self.first_succ = first_succ
        self.second_succ = second_succ
        self.ping_interval = ping_interval
        
        threading.Thread(target=self.ping_server).start()


    def port_number_og(self): # id + 12000
        self.port_number = 12000 + self.id_number
        return int(self.port_number)

    def port_number_first(self): # first successor id + 12000
        self.first_port_number = 12000 + self.first_succ
        return int(self.first_port_number)

    def port_number_second(self): # second successor id + 12000
        self.second_port_number = 12000 + self.second_succ
        return int(self.second_port_number)

    def start_peer(self):
        threading.Thread(target=self.ping_client).start()

    

    def ping_client(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # from https://stackoverflow.com/questions/4465959/python-errno-98-address-already-in-use/4466035#4466035
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        number = self.port_number
        message = f"Ping request message received from {number}".encode("utf-8")
        

        while True:
            success = [self.port_number_first(), self.port_number_second()]
            for i in success: 
                server.sendto(message, ('127.0.0.1', int(i)))
                sleep(2)

            while select.select([server],[],[],10)[0]:
                try:
                    (data,addr) = server.recvfrom(1024)
                    print(data.decode("utf-8"))
                except:
                    pass
            
                    

  
    def ping_server(self):
        PORT = self.port_number_og()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # from https://stackoverflow.com/questions/4465959/python-errno-98-address-already-in-use/4466035#4466035
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        s.bind(('', PORT))

        print(f"LISTENING FROM {PORT}\n")

        while True:
            data, addr = s.recvfrom(1024)
            print(data.decode("utf-8"))
            
            message_return = f"HI RECEIVED REQUEST and i was sent from {addr}"
            s.sendto(message_return.encode("utf-8"), addr)
            
            


if __name__ == "__main__":
    id_number = int(sys.argv[2])
    first_succ = int(sys.argv[3])
    second_succ = int(sys.argv[4])
    ping_interval = int(sys.argv[5])
    
    if sys.argv[1] == "init":
        new_peer = Peers(id_number, first_succ, second_succ, ping_interval)
        new_peer.start_peer()
        print(f"STARTED PEER {id_number}")

