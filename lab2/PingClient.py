# Using python version 2.7
import sys
import socket
import time 
import select

# make sure valid number of arguments
if len(sys.argv) - 1 != 2:
    print("Host + port required")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])

# open socket
new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = (host,port)

i = 0

RTT_list = []

# 10 pings
while i < 10:
    date = time.strftime("%a %d %b %Y %I:%M:%S %p %Z", time.gmtime())
    send_message = "PING " + str(i) + " " + date + "\r\n"

    start_time = time.time()

    # transmits UDP message
    new_socket.sendto(send_message, address)

    # receives UDP message
    if select.select([new_socket], [], [], 1)[0]:
        (new_socket.recvfrom(1024))
        success = True
    else:
    # unable to receive
        success = False

    end_time = time.time()
    total = end_time - start_time

    if success is True:
        # calculate RTT
        string = "ping to " + str(sys.argv[1]) + ", seq = " + str(i) + ", " + "rtt = " + str(int(total * 1000)) + " ms"
        print(string)
        
        # add to list
        RTT_list.append(total * 1000)
        time.sleep(1)
    else: 
        # time out 
        timeout_string = "ping to " + str(sys.argv[1]) + ", seq = " + str(i) + ", " + "time out"
        print(timeout_string)
        time.sleep(1)
    
    i = i + 1

# print average, minimum and maximum RTT
    
print("Average RTT: " + str(int(sum(RTT_list)/(len(RTT_list)))) + " ms")
print("Minimum RTT: " + str(int(min(RTT_list))) + " ms")
print("Maximum RTT: " + str(int(max(RTT_list))) + " ms")

