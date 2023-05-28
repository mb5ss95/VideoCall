import socket
from pyaudio import PyAudio
from time import sleep


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
#host_ip = "192.168.100.105"
port = 10050

print("host name => ", host_name)
print("host ip => ", host_ip)
print("host port => ", port)

print("socekt created")

server_socket.bind((host_ip, port))
print("socket bind complete")
# server_socket.setblocking(False)

p = PyAudio()
stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    input=True)
while 1:
    try:
        packet = server_socket.recvfrom(40960)
    except BlockingIOError as e:
        print(e)
        continue
    
    #print(type(data)) #<class 'bytes'>
    # data = pickle.loads(data)
    # if not packet:
    #     continue
    #print(type(data)) #<class 'numpy.ndarray'>
    # data = cv2.decode(data, cv2.IMREAD_COLOR) 
    print(packet[0])
    stream.write(packet[0])

stream.stop_stream()
stream.close()
p.terminate()