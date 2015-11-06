#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import socket, threading, re, sys, os, hashlib, shutil, queue,time,subprocess
class Init():
    def __init__(self):
        self.run()
    def run(self):
        global start_time
        self.parse_config()
        self.parse_sys()
        self.cutfile()
        start_time=time.time()
        print('Starting client..')
        Client()
    def parse_config(self):
        global config_file_name
        global interface, client_threads, fragment_size,work_directory
        variable_list={}
        try:
            config_file=open(config_file_name,'r+',encoding='utf-8')
        except OSError:
            answer=input('No config file. Create default(YES)?')
            if answer=='Yes' or answer=='':
                config_file=open(config_file_name,'w+')
                username=os.getlogin()
                if os.name()=='nt':
                    default_config='#Interface options \'single\' for one interface \'auto\' for choosing all interfaces that have default route.  In mode auto weight is equal\r\n#If you want to sent manual interface format is \'interface=<interface ip> <nexthop ip> <weight>;<interface ip2> <nexthop ip2> <weight2>\'\r\ninterface=single\r\n#Number of sending threads using in single interface connection\r\nclient_threads=10\r\n#Size of one fragment in bytes\r\nfragment_size=2000000\r\n#Temporary directory to store fragments\r\nwork_directory=C:/Users/'+username+'/python_send/'
                elif username=='root':
                    default_config='#Interface options \'single\' for one interface \'auto\' for choosing all interfaces that have default route.  In mode auto weight is equal\r\n#If you want to sent manual interface format is \'interface=<interface ip> <nexthop ip> <weight>;<interface ip2> <nexthop ip2> <weight2>\'\r\ninterface=single\r\n#Number of sending threads using in single interface connection\r\nclient_threads=10\r\n#Size of one fragment in bytes\r\nfragment_size=2000000\r\n#Temporary directory to store fragments\r\nwork_directory=/root/python_send/'
                else:
                    default_config='#Interface options \'single\' for one interface \'auto\' for choosing all interfaces that have default route.  In mode auto weight is equal\r\n#If you want to sent manual interface format is \'interface=<interface ip> <nexthop ip> <weight>;<interface ip2> <nexthop ip2> <weight2>\'\r\ninterface=single\r\n#Number of sending threads using in single interface connection\r\nclient_threads=10\r\n#Size of one fragment in bytes\r\nfragment_size=2000000\r\n#Temporary directory to store fragments\r\nwork_directory=/home/'+username+'/python_send/'
                config_file.write(default_config)
            else:
                sys.exit(1)
        for line_ in config_file:
            try:
                variable_name=re.findall('(?!#)(\S+)=\S+',line_)[0]
            except IndexError:
                pass
            else:
                variable_value=re.findall('=(.+)',line_)[0]
                variable_list[variable_name]=variable_value
        for key in variable_list:
            if key=='interface':
                interface=variable_list[key]
            elif key=='work_directory':
                work_directory=variable_list[key]
            elif key=='client_threads':
                client_threads=variable_list[key]
                client_threads=int(client_threads)
            elif key=='fragment_size':
                fragment_size=variable_list[key]
                fragment_size=int(fragment_size)
    def parse_sys(self):
        global server_ip, send_filename
        if len(sys.argv)<3:
            print('Usage: ',sys.argv[0],' <server> <file>')
        send_filename=sys.argv[2]
        if send_filename[0]=='"' and send_filename[-1]=='"':
            send_filename=send_filename[1:-1]
        server_ip=sys.argv[1]
    def cutfile(self):
        global send_filename,short_send_filename,fragment_size,work_directory,parts,start_file_size
        short_send_filename=re.findall('.+\/(.+)',send_filename)[0]
        try:
            parentfile=open(send_filename,'rb')
        except FileNotFoundError:
            print('File not found '+send_filename)
            sys.exit(1)
        start_file_size=os.path.getsize(send_filename)
        try:
            os.makedirs(work_directory+short_send_filename)
        except FileExistsError:
            answer=input('Directory ' + work_directory + short_send_filename + ' already exist. Overwrite?(YES)')
            if answer in ['YES','yes','Yes','y','Y','']:
                shutil.rmtree(work_directory+short_send_filename,ignore_errors=True)
                os.makedirs(work_directory+short_send_filename)
            elif os.path.exists(work_directory+short_send_filename+'.index'):
                return
            else:
                print('Indexfile mising. Closing')
                sys.exit(1)
        else:
            print('Creating temporary directory')
        data=parentfile.read(fragment_size)
        i=0
        indexfile=open(work_directory+short_send_filename+'.index','w+b')
        index=short_send_filename+'\r\n'+str(fragment_size)+'\r\n'
        indexfile.write(bytes(index,'utf-8'))
        while data:
            childfile=open(work_directory+short_send_filename+'/'+short_send_filename+'_part'+str(i),'w+b')
            childfile.write(data)
            childfile.close()
            fragment_hash=hashlib.md5(data)
            index=str(i) + ' ' + str(fragment_hash.hexdigest()) + '\r\n'
            indexfile.write(bytes(index,'utf-8'))
            i+=1
            data=parentfile.read(fragment_size)
        parts=i
        indexfile.close()
        parentfile.close()

class fragment_send(threading.Thread):
    def __init__(self,interface):
        self.interface=interface
        print(self.interface)
        self.run()
    def run(self):
        while True:
            global server_ip,queue_
            try:
                filename=queue_.get_nowait()
            except queue.Empty:
                return
            new_socket=socket.socket()
            new_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            new_socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)
            try:
                new_socket.connect((server_ip,5666))
            except socket.error:
                queue_.put(filename)
                return
            short_send_filename=re.findall('.+\/(.+)',filename)[0]
            file_size=str(os.path.getsize(filename))
            file=open(filename,'rb')
            try:
                new_socket.send(bytes('FRAGMENT::','utf-8'))
            except socket.error:
                queue_.put(filename)
                return
            try:
                new_socket.send(bytes(short_send_filename+'\r\n','utf-8'))
            except socket.error:
                queue_.put(filename)
                return
            try:
                new_socket.send(bytes(file_size+'\r\n','utf-8'))
            except socket.error:
                queue_.put(filename)
                return
            data=file.read(1500)
            while data:
                try:
                    new_socket.send(data)
                except socket.error:
                    queue_.put(filename)
                    return
                data=file.read(1500)
            try:
                receive=str(new_socket.recv(5),'utf-8')
            except socket.error:
                queue_.put(filename)
                return
            if receive!='ACK::':
                queue_.put(filename)
            file.close()
            new_socket.close()

class Client():
    def __init__(self):
        self.run()
    def load_balance(self):
        global interface, client_threads,server_ip
        server_ip_numeric=socket.gethostbyname(server_ip)
        if interface=='single':
            for i in range(client_threads):
                fragment_send('')
        elif interface=='auto':
            return
        else:
            client_ip=[]
            nexthop_ip=[]
            metric_list=[]
            interface=interface.split(';')
            for line in interface:
                client_ip.append(line.split(' ')[0])
                nexthop_ip.append(line.split(' ')[1])
                metric_list.append(line.split(' ')[2])
            if os.name=='nt':
                subprocess.call(["route", "delete", server_ip_numeric],shell=True)
            else:
                route_call=subprocess.call(["route del -host", server_ip_numeric],shell=True)
                while route_call==0:
                    route_call=subprocess.call(["route del -host", server_ip_numeric],shell=True)
            for nexthop in nexthop_ip:
                if os.name=='nt':
                    route_call=subprocess.call(["route", "add", server_ip_numeric, "mask", "255.255.255.255",nexthop],shell=True)
                    if route_call!=0:
                        print('Could not set routing. Try to run program from privelege user')
                        sys.exit(1)
                else:
                    route_call=subprocess.call(["route add -host"+server_ip_numeric+"gw"+nexthop],shell=True)
                    if route_call!=0:
                        print ('Could not set routing. Try to run program from privelege user')
                        sys.exit(1)
            sum=0
            for metric in metric_list:
                sum+=int(metric)
            if (client_threads/sum)<0.5:
                for i in range(len(metric_list)):
                    for k in range(int(metric_list[i])):
                        fragment_send(client_ip[i])
            else:
                delimiter=client_threads//sum
                for j in range(delimiter):
                    for i in range(len(metric_list)):
                        for k in range(int(metric_list[i])):
                            fragment_send(client_ip[i])


    def fragments_clean(self):
        global work_directory, short_send_filename
        try:
            shutil.rmtree(work_directory+short_send_filename,ignore_errors=True)
        except:
            print('Could not remove temporary directory')
        else:
            print('Temporary directory removed')
        try:
            os.remove(work_directory+short_send_filename+'.index')
        except:
            print('Could not remove temporary index file')
        else:
            print('Temporary index file removed')
    def index_sent(self,socket_):
        global server_ip, work_directory, short_send_filename
        try:
            socket_.connect((server_ip,5666))
        except socket.error:
            print ('Could not connect to server '+ server_ip)
            sys.exit(1)
        socket_.send(bytes('INDEX::','utf-8'))
        indexfilename=work_directory+short_send_filename+'.index'
        indexfile_short_name=re.findall('.+\/(.+)',indexfilename)[0]
        index_file_size=str(os.path.getsize(indexfilename))
        indexfile=open(indexfilename,'rb')
        socket_.send(bytes(indexfile_short_name+'\r\n','utf-8'))
        socket_.send(bytes(index_file_size+'\r\n','utf-8'))
        data=indexfile.read(1500)
        while data:
            socket_.send(data)
            data=indexfile.read(1500)
        indexfile.close()
    def run(self):
        global server_ip, work_directory, short_send_filename,queue_,client_threads,start_time,start_file_size
        queue_=queue.Queue()
        main_socket=socket.socket()
        main_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        main_socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)
        self.index_sent(main_socket)
        try:
            receive=str(main_socket.recv(1),'utf-8')
        except socket.timeout:
            print('Could not connect to server')
            sys.exit(1)
        if not receive: sys.exit(1)
        while receive[-2:]!='::' and len(receive)<50:
            receive+=str(main_socket.recv(1),'utf-8')
        if receive=='GET_FRAGMENTS::':
            receive=str(main_socket.recv(1),'utf-8')
            while receive[-2:]!='::':
                receive+=str(main_socket.recv(1),'utf-8')
            fragmentlist=receive[:-2].split(',')
            print('Sending fragments...')
            main_socket.close()
            for i in fragmentlist:
                fragment_name=work_directory+short_send_filename+'/'+short_send_filename+'_part'+str(i)
                queue_.put(fragment_name)
            i=0
            self.load_balance()
            while threading.active_count()>4:
                time.sleep(1)
            self.run()
        elif receive=='DONE::':
            print('Send sucessful!')
            end_time=time.time()
            durance=end_time-start_time
            minutes,seconds=divmod(durance,60)
            if durance!=0:
                speed=start_file_size/durance
            else:
                speed=0
            if speed>500000:
                speed=str(round(speed/1048576,2))+' MB/s'
            else:
                speed=str(round(speed/1024,2))+' KB/s'
            if start_file_size>1000000000:
                start_file_size=str(round(start_file_size/1073741824 , 2))+'Gb'
            elif start_file_size>1000000:
                start_file_size=str(round(start_file_size/1048576 , 2))+'Mb'
            elif start_file_size>1000:
                start_file_size=str(round(start_file_size/1024 , 2))+'Kb'
            else:
                start_file_size=str(start_file_size)+'bytes'
            print('Send '+short_send_filename+' ('+start_file_size+') in '+str(minutes)+'min'+str(seconds)+'sec ('+speed+') to '+server_ip )
            self.fragments_clean()
            main_socket.close()
            sys.exit(0)
        else:
            print('GET_FRAGMENTS:: expected, but received'+receive)
            main_socket.close()
            sys.exit(1)

if __name__=="__main__":
    config_file_name=os.path.dirname(sys.argv[0])+'/config.txt'
    Proggramm=Init()
