import socket
import time

message = b"HI"
udpSender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
udpSender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpSender.settimeout(0.2)

udpListener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
udpListener.setblocking(0)
udpListener.bind(("", 8002))


last_send_time = int(time.time())
while True:
    current_time = int(time.time())
    while current_time > last_send_time:
        last_send_time = last_send_time + 1
        udpSender.sendto(message, ("<broadcast>", 8001))
        print("message sent!")

    try:
        data, addr = udpListener.recvfrom(1024)
        print(f"received message {data} from {addr}")
    except socket.error:
        pass
