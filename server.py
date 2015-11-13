#!/usr/bin/env python3
import socket, threading, sys, os, select, hashlib
class file_receive(threading.Thread):                       #thread code for receiving fragment
    def __init__(self,conn):
        threading.Thread.__init__(self)
        self.conn=conn                                      #get connection
    def run(self):
        global work_directory                               #getting begging of file byte by byte. format:
        try:                                                #foo.bar\r\n
            data=str(self.conn.recv(1),'utf-8')             #filesize\r\n
            if not data:                                    #file
                        return
        except socket.error:
                return
        while data[-2:]!='\r\n':
            try:
                data+=str(self.conn.recv(1),'utf-8')
            except socket.error:
                return
        filename = data[:-2]
        try:
            data=str(self.conn.recv(1),'utf-8')
            if not data:
                return
        except socket.error:
                return
        filesize_data=data
        while filesize_data[-2:]!='\r\n':
            try:
                data=str(self.conn.recv(1),'utf-8')
                if not data:
                    return
                filesize_data+=data
            except socket.error:
                return
        filesize = int(filesize_data[:-2])
        file = open(work_directory+filename, 'wb')      #create new file
        while filesize>0:                               #receive the rest of file
            if filesize>4096:
                try:
                    data = self.conn.recv(4096)
                    if not data:
                        file.close()
                        return
                except socket.error:
                    file.close()
                    return
                datasize=len(data)
                filesize=filesize-datasize
                file.write(data)
            else:
                try:
                    data = self.conn.recv(filesize)
                    if not data:
                        file.close()
                        return
                except socket.error:
                    file.close()
                    return
                datasize=len(data)
                filesize=filesize-datasize
                file.write(data)
        file.close()
        try:
            self.conn.send(bytes('ACK::','utf-8'))              #say client "All right"
        except socket.error:
            self.conn.close()
            return
        self.conn.close()


def index_receive(conn):                                        #same as file_receive, but return commection
    global work_directory
    try:
        data=str(conn.recv(1),'utf-8')
        if not data:
            return
    except socket.error:
            return
    while data[-2:]!='\r\n':
        try:
            data+=str(conn.recv(1),'utf-8')
        except socket.error:
            return
    filename = data[:-2]
    try:
        data=str(conn.recv(1),'utf-8')
        if not data:
            return
    except socket.error:
        return
    filesize_data=data
    while filesize_data[-2:]!='\r\n':
        try:
            data=str(conn.recv(1),'utf-8')
            if not data:
                return
            filesize_data+=data
        except socket.error:
            return
    filesize = int(filesize_data[:-2])
    file = open(work_directory+filename, 'wb')
    while filesize>0:
        if filesize>4096:
            try:
                data = conn.recv(4096)
                if not data:
                    file.close()
                    return
            except socket.error:
                file.close()
                return
            datasize=len(data)
            filesize=filesize-datasize
            file.write(data)
        else:
            try:
                data = conn.recv(filesize)
                if not data:
                    file.close()
                    return
            except socket.error:
                file.close()
                return
            datasize=len(data)
            filesize=filesize-datasize
            file.write(data)
    file.close()
    return conn,filename

def Parse_index(indexfilename):                                         #in this method we parse indexfile: read filename then try to open fragment and then check hashsum.
    global work_directory,fragmentsize,total_fragments                  #if file not exist or hash is wrong ask client to send it
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
                if index_hashsumd==file_hashsumd:
                    file.close()
                else:
                    file.close()
                    os.remove(filename+'_part'+fragmentnumber)
                    need_fragments.append(fragmentnumber)
            line=str(indexfile.readline()[:-2],'utf-8')
    total_fragments=int(fragmentnumber)+1
    need_fragments=','.join(need_fragments)
    return need_fragments

class server():
    def __init__(self):
        self.run()
    def solving_file(self,filename):                                                           #when all fragment received join them to 1 big file
        global work_directory,total_fragments
        full_file=open(work_directory+filename,'w+b')
        for i in range (total_fragments):
            try:
                fragment_file=open(work_directory+filename+'_part'+str(i),'rb')
            except:
                break
            else:
                data=fragment_file.read()
                full_file.write(data)
                fragment_file.close()
                os.remove(work_directory+filename+'_part'+str(i))
        full_file.close()
        print('Received file '+filename +' To directory: '+work_directory)
        os.remove(work_directory+filename+'.index')
    def run(self):                                                              #main method
        global work_directory
        username=os.getlogin()
        if os.name=='nt':
            work_directory='C:/python_receive/'                                 #choose receiving directory depending on OS
        else:
            work_directory=os.path.join(os.path.expanduser('~'), 'python_receive/')
        if not os.path.exists(work_directory):                                  #create directory if not exist
                    try:
                        os.makedirs(work_directory)
                    except:
                        print('Could not create work directory' +work_directory)
                        sys.exit(1)
        sock=socket.socket()                                                    #open socket
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)
        try:
            sock.bind(('',5666))
        except OSError:
            print('Socket is busy. Free it or try a bit later')                 #sometimes on linux socket is not free immediately after closing proggramm
            sys.exit(1)
        sock.listen(50)
        inputs=[sock]
        while inputs:                                                           #open connection with select, later we send it to independent thread
            r,w,e=select.select(inputs,[],[])
            for current_socket in r:
                conn,addr=current_socket.accept()
                try:
                    flag=str(conn.recv(1),'utf-8')                              #receiving first bytes
                except socket.error:
                    break
                while flag[-2:]!='::' and len(flag)<50:
                    try:
                        flag+=str(conn.recv(1),'utf-8')
                    except socket.error:
                        break
                if flag == 'INDEX::':                                           #if we receiving index go to index_receive
                    try:
                        returned_connection,indexfilename=index_receive(conn)
                    except:
                        print ('Index receiving failed')
                        conn.close()
                        break
                    print('Receiving indexfile: '+indexfilename)
                    need_fragments=Parse_index(indexfilename)
                    if need_fragments=='':                                      #we received all fragment
                        try:
                            returned_connection.send(bytes('DONE::','utf-8'))
                        except socket.error:
                            break
                        self.solving_file(indexfilename[:-6])
                    else:
                        try:                                                    #we don't received all fragment tell client to send it
                            returned_connection.send(bytes('GET_FRAGMENTS::' + need_fragments+'::','utf-8'))
                        except socket.error:
                            break

                elif flag== 'FRAGMENT::':                                       #if we receving fragment start new thread
                    th=file_receive(conn)
                    th.start()

                else:
                    print('Error')
                    conn.close()


if __name__=="__main__":
    server()
