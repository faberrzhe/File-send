#!/usr/bin/env python3
import socket, threading, re, sys, os, time, select, hashlib
class file_receive(threading.Thread):
    def __init__(self,conn):
        threading.Thread.__init__(self)
        self.conn=conn
        print(conn)
    def run(self):
        global work_directory
        while True:
            data=str(self.conn.recv(1),'utf-8')
            while data[-2:]!='\r\n':
                data+=str(self.conn.recv(1),'utf-8')
            filename = data[:-2]
            data=str(self.conn.recv(1),'utf-8')
            while data[-2:]!='\r\n':
                data+=str(self.conn.recv(1),'utf-8')
            filesize = int(data[:-2])
            file = open(work_directory+filename, 'wb')
            while filesize>0:
                if filesize>4096:
                    data = self.conn.recv(4096)
                    datasize=len(data)
                    filesize=filesize-datasize
                    file.write(data)
                else:
                    data = self.conn.recv(filesize)
                    datasize=len(data)
                    filesize=filesize-datasize
                    file.write(data)
            file.close()
            return self.conn,filename

def Parse_index(indexfilename):
    global work_directory
    with open(work_directory+indexfilename,'rb') as indexfile:
        need_fragments=[]
        filename=work_directory+str(indexfile.readline()[:-2],'utf-8')
        fragmentsize=int(indexfile.readline()[:-2])
        line=str(indexfile.readline()[:-2],'utf-8')
        while line:
            fragmentnumber,index_hashsumd=line.split(" ")
            try:
                file=open(filename+'_part'+fragmentnumber,'rb')
            except FileNotFoundError:
                need_fragments.append(fragmentnumber)
            else:
                fileread=file.read(fragmentsize)
                file_hashsumd=hashlib.md5(fileread).hexdigest()
                #file_hashsumd=file_hashsum.hexdigits()
                if index_hashsumd==file_hashsumd:
                    file.close()
                else:
                    file.close()
                    os.remove(filename+'_part'+fragmentnumber)
                    need_fragments.append(fragmentnumber)
            line=str(indexfile.readline()[:-2],'utf-8')
    need_fragments=','.join(need_fragments)
    return need_fragments

class server():
    def __init__(self):
        self.run()
    def run(self):
        global work_directory
        work_directory='C:/Users/eberezhnoy/python/'
        sock=socket.socket()
        sock.bind(('',5666))
        sock.listen(50)
        inputs=[sock]
        while inputs:
            r,w,e=select.select(inputs,[],[])
            for current_socket in r:
                conn,addr=current_socket.accept()
                flag=str(conn.recv(1),'utf-8')
                while flag[-2:]!='::' and len(flag)<50:
                    flag+=str(conn.recv(1),'utf-8')
                if flag == 'INDEX::':
                    th=file_receive(conn)
                    returned_connection,indexfilename=th.run()
                    print(returned_connection,indexfilename)
                    need_fragments=Parse_index(indexfilename)
                    print(need_fragments)
                    if need_fragments='':
                        returned_connection.send(bytes('DONE::','utf-8'))
                    else:
                        returned_connection.send(bytes('GET_FRAGMENTS::' + need_fragments+'::','utf-8'))
                elif flag== 'FRAGMENT::':
                    th=file_receive(conn)
                    returned_connection,indexfilename=th.run()
                    print(returned_connection,indexfilename)
                    returned_connection.send(bytes('ACK::','utf-8'))
                    returned_connection.close()
                else:
                    print('Error')
                    conn.close()


if __name__=="__main__":
    server()
