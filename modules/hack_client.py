import socket
import struct
target_host = "127.0.0.1"
target_port = 9999

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((target_host,target_port))
while True:
    cmd = raw_input(">")
    if cmd == "exit":
        exit()
    if cmd == "":
        cmd = "\r"
    client.send(struct.pack('B',0x00) + cmd)
    resp = ""
    data = client.recv(4096)
    resp = data
    while len(data) == 4096:
        data = client.recv(4096)
        resp += data
    print resp.decode("GBK")