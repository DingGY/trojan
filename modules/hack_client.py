import socket
import struct
import shlex
import os
target_host = "127.0.0.1"
target_port = 9999


def cmd_parse():
    data = raw_input(">")
    if data == "":
        act_type = 0x00
        cmd = struct.pack('B',act_type) + "\r"
        return cmd,act_type,None
    cmd_input = data.split(" ")
    if cmd_input[0] == '-d':
        '''download file action'''
        act_type = 0x01
        cmd = struct.pack('B',act_type) + cmd_input[1]
        opt = cmd_input[1]
    elif cmd_input[0] == '-u':
        '''upload file action'''
        act_type = 0x02
        cmd = struct.pack('B',act_type) + cmd_input[1]
        opt = cmd_input[1]
    elif cmd_input[0] == '--exit':
        '''exit server command'''
        act_type = 0xff
        cmd = struct.pack('B',act_type)
        opt = None
    elif cmd_input[0] == 'exit':
        '''exit command'''
        exit()
    else:
        '''run command'''
        act_type = 0x00
        cmd = struct.pack('B',act_type) + data
        opt = data
    return cmd,act_type,opt

def client_recv(conn):
    resp = ""
    data = conn.recv(4096)
    resp = data
    while len(data) == 4096:
        data = conn.recv(4096)
        resp += data
    return resp

def download_file(data,file):
    try:
        fd = open(os.path.basename(file),"wb")
        fd.write(data)
        fd.close()
    except Exception as e:
        print e
        return False
    return True

def main():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((target_host,target_port))
    while True:
        (cmd,act_type,opt) = cmd_parse()
        client.send(cmd)
        resp = client_recv(client)
        if act_type == 0x00:
            print resp.decode("GBK")
        elif act_type == 0x01:
            if download_file(resp,opt):
                print  "[+] download %s successed!" % opt
            else:
                print "[-] download %s failure!" % opt


__name__ = "__main__"

if __name__ == "__main__":
    main()