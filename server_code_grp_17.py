# Group-17 CN | Sender/server code.
# Members:
# AU1940151 Purvam Sheth
# AU1940261 Krutin Rathod
# AU1940215 Raj Chauhan
# AU1940119 Nihar Patel
# AU1940171 Mohit Prajapati

import socket
import sys
import socket
import time
import base64
import cv2  # for video displaying
import imutils
from multiprocessing import Process  # for creating muliple processes.

BUFF_SIZE = 65536

# It runs if no. of command line arguments is less and helps the client in giving them in proper order. 
def helper_function(p):
    print('Usage: ' + p + ' Host_IP | Multicast-Address-1 | Multicast-Port-1 | Multicast-Address-2 | Multicast-Port-2 | Host_IP-PORT | Message if any',
          file=sys.stderr)
    sys.exit(1)

# It takes ip address of device, multicast address, port and message 
def multicast_send(host_ip, multicast_grp_id, multicast_port, msgbuf):
    # This creates a UDP socket
    send_ = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM,
                          proto=socket.IPPROTO_UDP, fileno=None)
    # This defines a multicast end point, that is a pair
    #   (multicast group ip address, send-to port nubmer)
    multicast_grp = (multicast_grp_id, multicast_port)

    send_.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

    send_.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                     socket.inet_aton(host_ip))

    # Datagram transfer using buffer msgbuf
    send_.sendto(msgbuf, multicast_grp)

    # closing the socket.
    send_.close()


def video_multicasting(host_ip_addr, multicast_grp_ip_addr, multicast_port, video_path, msg):
    print("In thread")
    vid = cv2.VideoCapture(video_path)
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    frame_counter = 0
    while True:
        WIDTH = 400
        _, frame = vid.read()
        # The following code allows the video to run in continous loop 
        frame_counter += 1
        frame = imutils.resize(frame, width=WIDTH)
        if frame_counter == vid.get(cv2.CAP_PROP_FRAME_COUNT):
            frame_counter = 0
            vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        encoded, buffer = cv2.imencode(
            '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        msg = base64.b64encode(buffer)
        multicast_send(host_ip_addr, multicast_grp_ip_addr,
                       multicast_port, msg)
        # FPS are calculated using these
        frame = cv2.putText(frame, 'FPS: '+str(fps), (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow('TRANSMITTING VIDEO', frame)
        key = cv2.waitKey(1) & 0xFF
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count/(time.time()-st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1

# TCP accepts arguments like, ip address, served port no., multicast ip address-1, multicast ip address-2, port no.1, port no.2. 
def tcp(HOST_IP, HOST_PORT, multicast_ip_1, multicast_ip_2, multicast_port_1, multicast_port_2):
    HOST = HOST_IP
    PORT = HOST_PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv:
        serv.bind((HOST, PORT))
        serv.listen()
        conn_, addr = serv.accept()
        # Offers various stations to client to choose any one from given below. 
        STATION_1 = "Station-1 Name: M || Multicast Address: " + \
            multicast_ip_1 + " || Multicast Port:" + str(multicast_port_1)
        STATION_2 = "Station-2 || Name: S || Multicast Address: " + \
            multicast_ip_2 + "|| Multicast Port:" + str(multicast_port_2)

        with conn_:
            print(f"Connected by {addr}")
            conn_.send(STATION_1.encode())
            conn_.send(STATION_2.encode())
            print("sent")

    serv.close()


def main(argv):
    if len(argv) < 8:
        helper_function(argv[0])
    print("In Main")

    # To collect required data via command line arguments like ip address of host, multicast address, port no. 
    host_ip_addr = argv[1]
    print(host_ip_addr)
    multicast_grp_ip_addr_1 = argv[2]
    print(multicast_grp_ip_addr_1)
    multicast_port_1 = int(argv[3])
    print(multicast_port_1)
    # provides the absolute location of video
    video_path = "/Users/krutinrahtod/Desktop/pyporoj2/video/video.mp4"
    video_path_1 = "/Users/krutinrahtod/Desktop/pyporoj2/video/video2.mp4"
    multicast_grp_ip_addr_2 = argv[4]
    print(multicast_grp_ip_addr_2)
    multicast_port_2 = int(argv[5])
    print(multicast_port_2)
    server_port = int(argv[6])
    msg = argv[7]
    print(msg)

    # Create two processes as follows in order to stream more than one video by the server. This will enable us to transmit two videos simultaneously. 
    try:
        print("In try")
        p1 = Process(target=video_multicasting, args=(
            host_ip_addr, multicast_grp_ip_addr_1, multicast_port_1, video_path, msg,))
        p2 = Process(target=video_multicasting, args=(
            host_ip_addr, multicast_grp_ip_addr_2, multicast_port_2, video_path_1, msg,))
        p1.start()
        p2.start()

    except:
        print("Error: unable to start process")

    tcp(host_ip_addr, server_port, multicast_grp_ip_addr_1,
        multicast_grp_ip_addr_2, multicast_port_1, multicast_port_2)


if __name__ == '__main__':
    main(sys.argv)
