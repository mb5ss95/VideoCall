from pyaudio import PyAudio
import socket
import pickle
from time import sleep

host = ("192.168.100.41", 10050)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000)
# client_socket.bind(host)
client_socket.sendto(b"11", host)
print("start")
r = 4096
p = PyAudio()
stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    output=True)

packet = b'0'
while 1:
    try:

        packet = client_socket.recv(4096)
    except BlockingIOError as e:
        print(e)
        continue

    stream.write(packet)

stream.stop_stream()
stream.close()
p.terminate()