#!/usr/bin/env python3
import socket, threading, re, sys, os, time
import socket
import os
import time
import threading
import select
threads=10
s=socket.socket()
s.bind(('',5566))
s.listen(10)
inputs=[s]
th=[]
while inputs:
	r,w,e=select.select(inputs,[],[])
	for j in r:
            conn,addr=r.accept()
            flag=str(conn.recv(1),'utf-8')
            while flag[-2:]!='::': or len(flag)<50
                flag+=str(conn.recv(1),'utf-8')
            if flag == 'INDEX::':
                th=server(conn)
                result=th.run()
                if result=0:
                    conn.send(bytes('GET_FRAGMENTS::2,4,6,8,77,888::'))
            elif flag== 'FRAGMENT':
            else:
                print('Error')
                conn.close()
class server(threading.Thread):
        def __init__(self,conn):
                threading.Thread.__init__(self)
                self.conn=conn
				print(conn)
        def run(self):
                while True:
                    #conn,addr=s.accept()
                    data=str(self.conn.resv(1),'utf-8')
                    while data[-2:]!='\r\n':
                            data+=str(self.conn.resv(1),'utf-8')
                    filename = data[:-2]
                    data=str(self.conn.resv(1),'utf-8')
                    while data[-2:]!='\r\n':
                            data+=str(self.conn.resv(1),'utf-8')
                    filesize = int(data[:-2])
                    startfilesize=filesize
                    file = open('C:/Users/Vaenrise/Downloads/'+filename, 'wb')
                    print('Receving file',filename,'(',filesize, 'bytes) from ',addr, ' in thread ',self.number)
                    start_time=time.time()
                    while filesize>0:
                        if filesize>4096:
                                data = self.conn.recv(4096)
                                #print(str(filesize),str(data))
                                datasize=len(data)
                                filesize=filesize-datasize
                                file.write(data)
                                #if (filesize%50000000)<4000:
                                #        print(str(round(filesize/1048576)),' MB Left to recieve')
                        else:
                            data = self.conn.recv(filesize)
                            datasize=len(data)
                            filesize=filesize-datasize
                            file.write(data)
                            #print(str(filesize),str(data))
                    file.close()
                    end_time=time.time()
                    minutes,seconds=divmod(end_time-start_time,60)
                    speed=startfilesize/(end_time-start_time)
                    if speed>500000:
                        speed=str(round(speed/1048576,2))+' MB/s'
                    else:
                        speed=str(round(speed/1024,2))+' KB/s'
                    print('Received file ',filename,' in ',int(minutes),'min',int(seconds),'sec. Speed: ',speed,' from ',addr, ' in thread ',self.number)
                    self.conn.close()
                    return 0

if __name__=="__main__":
	#todo
