# Group-17 CN | Receiver/client code.
# Members:
# AU1940151 Purvam Sheth
# AU1940261 Krutin Rathod
# AU1940215 Raj Chauhan
# AU1940119 Nihar Patel
# AU1940171 Mohit Prajapati

import sys
import socket
import struct
import cv2  # for video displaying
import socket
import base64
from multiprocessing import Process  # for creating muliple processes.
import numpy as np
import time

# It runs if no. of command line arguments is less and helps the client in giving them in proper order. 
def helper_function(p):
    print('Usage: ' + p + ' enter host/server ip address | port of host/server ')
    sys.exit(1)

# It takes ip address of device, multicast address, port and message 
def multicast_recv(host_ip, multicast_grp_id, multicast_port):
    bufsize = 65536
    # UDP socket for data streaming video.
    recv_ = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP, fileno=None)

    bind_address = (multicast_grp_id, multicast_port)
    recv_.bind(bind_address)

    if host_ip == '0.0.0.0':
        mreqs = struct.pack("=4sl", socket.inet_aton(
            multicast_grp_id), socket.INADDR_ANY)
    else:
        mreqs = struct.pack("=4s4s",
                            socket.inet_aton(multicast_grp_id), socket.inet_aton(host_ip))
    recv_.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreqs)

    # RECEIVING DATA FROM SERVER
    buf, senderaddr = recv_.recvfrom(bufsize)
    msg = buf.decode()

    return buf

# TCP accepts ip address and served port number
def tcp(host, port):
    HOST = host  # SERVER IP Address.
    PORT = port  # PORT NUMBER

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as service:
        service.connect((HOST, PORT))
        data = service.recv(1024).decode()
        data_1 = service.recv(1024).decode()

    print(f"Received info about 1st station: {data!r}")
    print(f" ")
    print(f"Received info about the 2nd station: {data_1!r}")
    service.close()


def multicasting(host_ip, mcgrpip_user_entered, mcport_user_entered):
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    while True:
        packet = multicast_recv(
            host_ip, mcgrpip_user_entered, mcport_user_entered)
        data = base64.b64decode(packet, ' /')
        npdata = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        frame = cv2.putText(frame, 'FPS: '+str(fps), (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("RECEIVING VIDEO", frame)

        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == ord('x'):
            print("pressed: x")
            sys.exit(1)
            break

        if key_pressed == ord('y'):
            print("pressed: y")
            sys.exit(1)

        if key_pressed == ord('z'):
            print("pressed: z")

        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count/(time.time()-st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1


def main(argv):

    if len(argv) < 3:
        helper_function(argv[0])

    fromnicip = argv[1]  # IP for host where server is running.
    port_serv = int(argv[2])  # port for where server is running.
    # TCP connection for getting information where of multicasting addresses.
    tcp(fromnicip, port_serv)
    mcgrpip_user_entered = input(
        "Enter MULTICAST address of channel you want to join: ")
    print("user entered ip: " + mcgrpip_user_entered)
    mcport_user_entered = input(
        "Enter the MULTICAST address port of channel you want to join: ")
    print("user entered ip: " + mcport_user_entered)
    mcport_user_entered = int(mcport_user_entered)

    try:
        print("In try")
        # creating process for getting video streaming through UDP connection.
        p1 = Process(target=multicasting, args=(
            fromnicip, mcgrpip_user_entered, mcport_user_entered,))
        p1.start()

    except:
        print("Error: unable to start process")

    # for getting continous input from user.
    while(1):
        var = input(
            " Press p for pause, r for restart and t for termination ")
        if(var == 'p'):
            print(" Pause clicked: ")
            p1.terminate()
        elif (var == 'r'):
            print(" r pressed: ")
            p1 = Process(target=multicasting, args=(
                fromnicip, mcgrpip_user_entered, mcport_user_entered,))
            p1.start()
        elif(var == 't'):
            print(" t pressed ")
            p1.terminate()
            sys.exit(1)


if __name__ == '__main__':
    main(sys.argv)
