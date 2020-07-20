# Python 3
# Ashley Huang z5259842 

import socket
import sys
import threading
from time import sleep
import select

LOCALHOST = "127.0.0.1"

class Peers:
    def __init__(self, id_number, first_succ, second_succ, ping_interval,known_peer):
        self.id_number = id_number
        self.first_succ = int(first_succ)
        self.second_succ = int(second_succ)
        self.ping_interval = ping_interval
        self.known_peer = known_peer
        self.dead = False
        
        # from https://pymotw.com/2/threading/
        # start UDP ping server
        threading.Thread(target=self.ping_server).start()

        # start TCP server
        threading.Thread(target=self.tcp_server).start()

    def port_number_og(self): # id + 15000
        self.port_number = 15000 + int(self.id_number)
        return int(self.port_number)

    def port_number_first(self): # first successor id + 15000
        self.first_port_number = 15000 + int(self.first_succ)
        return int(self.first_port_number)

    def port_number_second(self): # second successor id + 15000
        self.second_port_number = 15000 + int(self.second_succ)
        return int(self.second_port_number)

    # starts peer ping client 
    def start_peer(self):
        # calls ping_client and starts it
        if self.dead is False:
            threading.Thread(target=self.ping_client).start()

    # sends tcp message given a port number and encodes the given message
    def tcp_message_send(self,port_number, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((LOCALHOST, port_number)) 
        sock.sendall(message.encode("utf-8"))
        sock.close()

    # TCP server 
    def tcp_server(self):

        # set up the socket for receiving
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        PORT = self.port_number_og()
        address = (LOCALHOST, PORT)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(address)
        s.listen(1)

        # keep receiving messages unless the peer has left (dead)
        while True and self.dead is False:
            conn,addr = s.accept()

            # decode and split the message received
            data = conn.recv(1024).decode("utf-8")
            data = data.split()

            # if peer is looking to join and its position is between its first succ and second succ
            if data[0] == "looking" and (int(self.first_succ) < int(data[1]) < int(self.second_succ)):
                self.tcp_message_send(self.port_number_first(), f"looking {data[1]}")
                print(f"Peer {data[1]} Join request forward to my successor")
                
                self.second_succ = data[1]
                print("Successor change request received")
                print(f"My new first successor is Peer {self.first_succ}")
                print(f"My new second successor is Peer {self.second_succ}")

            # if peer is looking to join and its position is between itself and its first_succ
            elif data[0] == "looking" and (int(self.id_number) < int(data[1]) < int(self.first_succ)):

                # assign its current first_succ and second_succ to variables before it gets changed
                first_successor = self.first_succ
                second_successor = self.second_succ

                # update successors
                self.second_succ = self.first_succ
                self.first_succ = data[1]
                
                msg = f"joining {first_successor} {second_successor}"
                self.tcp_message_send(self.port_number_first(), msg)
                print(f"Peer {data[1]} join request received")
                print(f"My new first successor is Peer {self.first_succ}")
                print(f"My new second successor is Peer {self.second_succ}")

            # CASE FOR EDGE
            # if peer is looking to join and its between the first_succ and the second_succ at the end and start of the circle
            elif data[0] == "looking" and (int(self.second_succ) < int(self.first_succ) < int(data[1])):
                self.tcp_message_send(self.port_number_first(), f"looking {data[1]}")
                print(f"Peer {data[1]} Join request forward to my successor")
                
                self.second_succ = data[1]
                print("Successor change request received")
                print(f"My new first successor is Peer {self.first_succ}")
                print(f"My new second successor is Peer {self.second_succ}")

            # CASE FOR EDGE
            # if peer is looking to join and its between the first succ and itself at the end and start of the circle
            elif data[0] == "looking" and (int(self.first_succ) < int(self.id_number) < int(data[1])):

                first_successor = self.first_succ
                second_successor = self.second_succ

                # reassign first and second succ
                self.second_succ = self.first_succ
                self.first_succ = data[1]
                
                # message the new joining peer its first succ and second succ 
                msg = f"joining {first_successor} {second_successor}"
                self.tcp_message_send(self.port_number_first(), msg)

                print(f"Peer {data[1]} join request received")
                print(f"My new first successor is Peer {self.first_succ}")
                print(f"My new second successor is Peer {self.second_succ}")

            # assign the new joining peer its first succ and second succ
            elif data[0] == "joining":
                print("Join request has been accepted")

                # update new successors
                self.first_succ = data[1]
                self.second_succ = data[2]
                print(f"My first successor is Peer {self.first_succ}")
                print(f"My second successor is Peer {self.second_succ}")
            
            # else if the peer has not found its position yet, keep forwarding to the first successor
            elif data[0] == "looking":
                self.tcp_message_send(self.port_number_first(), f"looking {data[1]}")
                print(f"Peer {data[1]} Join request forward to my successor")

            # if it is the one that quit, send a message with its peer id, first succ and second succ
            elif data[0] == "quit" and len(data) == 1:
                quit_peer = self.id_number
                msg = (f"quit {quit_peer} {self.first_succ} {self.second_succ}")
                self.tcp_message_send(self.port_number_first(), msg)
                self.dead = True
            
            # receives peer that wants to quit, first succ and second succ
            # if its first or second successor is the same as the peer that wants to quit
            # change its successors
            elif data[0] == "quit" and len(data) == 4:
                if int(data[1]) == int(self.second_succ):
                
                    self.second_succ = data[2]
                    
                    print(f"Peer {data[1]} will depart from the network")
                    print(f"My new first successor is Peer {self.first_succ}")
                    print(f"My new second successor is Peer {self.second_succ}")
                    data = " ".join(data)
                    self.tcp_message_send(self.port_number_first(), data)

                elif int(data[1]) == int(self.first_succ):
                    self.first_succ = data[2]
                    self.second_succ = data[3]
                    print(f"Peer {data[1]} will depart from the network")
                    print(f"My new first successor is Peer {self.first_succ}")
                    print(f"My new second successor is Peer {self.second_succ}")
            # if first successor or second successor is not the peer that wants to quit
            # continue passing the message on
                else:
                    data = " ".join(data)
                    self.tcp_message_send(self.port_number_first(),data)
                   

            conn.close()

    # UDP ping client
    def ping_client(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # from https://stackoverflow.com/questions/4465959/python-errno-98-address-already-in-use/4466035#4466035
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while True and (self.dead is False):
            print(f"Ping requests sent to Peer {self.first_succ} and {self.second_succ}")
            # PING INTERVAL
            sleep(self.ping_interval)

            # needs to ping first successor and second successor
            success = [self.port_number_first(), self.port_number_second()]
            for i in success: 
                message = (f"Ping request message received from {self.id_number}").encode("utf-8")
                server.sendto(message, (LOCALHOST, int(i)))
            
            # be open to receive responses
            while select.select([server],[],[],10)[0]:
                (data,address) = server.recvfrom(1024)
                print(data.decode("utf-8"))

    # UDP ping server
    def ping_server(self):
        PORT = self.port_number_og()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # from https://stackoverflow.com/questions/4465959/python-errno-98-address-already-in-use/4466035#4466035
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        s.bind((LOCALHOST, PORT))

        while True and self.dead is False:
            # open to receiving messages
            if select.select([s], [], [], 1)[0]:
                (data, address) = s.recvfrom(1024)
                print(data.decode("utf-8"))
                sleep(3)
                # sends a response back to where the message came from
                data_return = f"Ping response received from Peer {self.id_number}"
                s.sendto(data_return.encode("utf-8"), address)
        
        s.close()

if __name__ == "__main__":
    # for initialising
    if sys.argv[1] == "init":
        id_number = int(sys.argv[2])
        first_succ = int(sys.argv[3])
        second_succ = int(sys.argv[4])
        ping_interval = int(sys.argv[5])

        new_peer = Peers(id_number, first_succ, second_succ, ping_interval, known_peer = None)
        new_peer.start_peer()

        # allows usage of standard I/O and detects when "quit" is entered
        for read_line in sys.stdin:
            if "quit" == read_line.rstrip():
                message = "quit"
                new_peer.tcp_message_send(id_number + 15000, message)
                new_peer.dead = True

    # for joining
    elif sys.argv[1] == "join":
        id_number = int(sys.argv[2])
        known_peer = int(sys.argv[3])
        ping_interval = int(sys.argv[4])
        new_peer = Peers(id_number, 0, 0, ping_interval, known_peer=known_peer)
        sleep(5)

        message = f"looking {id_number}"
        port_sending = int(known_peer + 15000)
        # sends tcp message to known port
        new_peer.tcp_message_send(port_sending, message)
        sleep(2)
        new_peer.start_peer()
         # allows usage of standard I/O and detects when "quit" is entered
        for line in sys.stdin:
            if "quit" == line.rstrip():
                message = "quit"
                new_peer.tcp_message_send(id_number + 15000, message)
                new_peer.dead = True
                
        
    
            
        
    
    
