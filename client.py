#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import socket, threading, re, sys, os, time, hashlib, shutil
class Server():
    def __init__(self):
        print('Initiating server...')
    def run(self):
        print('Starting server...')
class Client():
    def __init__(self,filename,state,ident):
        print('Initiating client')
    def run(self):
        print('Starting client')

class Init():
    def __init__(self):
        print('Hello!')
    def run(self):
        self.parse_config()
        self.parse_sys()
        self.cutfile()
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
                default_config='interface=single\r\nclient_threads=10\r\nfragment_size=2000000\r\nwork_directory=C:/python_send/'
                config_file.write(default_config)
            else:
                sys.exit(1)
        for line_ in config_file:
            try:
                variable_name=re.findall('(?!#)(\S+)=\S+',line_)[0]
            except IndexError:
                pass
            else:
                variable_value=re.findall('=(\S+)',line_)[0]
                variable_list[variable_name]=variable_value
        for key in variable_list:
            if key=='interface':
                interface=variable_list[key]
                print (interface)
            elif key=='work_directory':
                work_directory=variable_list[key]
                print (work_directory)
            elif key=='client_threads':
                client_threads=variable_list[key]
                print(client_threads)
            elif key=='fragment_size':
                fragment_size=variable_list[key]
                print(fragment_size)
                fragment_size=int(fragment_size)
    def parse_sys(self):
        global server_ip, send_filename
        if len(sys.argv)<3:
            print('Usage: ',sys.argv[0],' <seerver> <file>')
        send_filename=sys.argv[2]
        server_ip=sys.argv[1]
    def cutfile(self):
        global send_filename,short_send_filename,fragment_size,work_directory,parts
        short_send_filename=re.findall('\S+\/(\S+)',send_filename)[0]
        parentfile=open(send_filename,'rb')
        try:
            os.makedirs(work_directory+short_send_filename)
        except FileExistsError:
            shutil.rmtree(work_directory+short_send_filename,ignore_errors=True)
            os.makedirs(work_directory+short_send_filename)
        data=parentfile.read(fragment_size)
        i=0
        index=short_send_filename+'\r\n'+str(fragment_size)+'\r\n'
        while data:
            childfile=open(work_directory+short_send_filename+'/'+short_send_filename+'_part'+str(i),'w+b')
            childfile.write(data)
            childfile.close()
            #q.put(i)
            fragment_hash=hashlib.md5(data)
            index+=str(i) + ' ' + str(fragment_hash.hexdigest()) + '\r\n'
            i+=1
            data=parentfile.read(fragment_size)
        parts=i
        with open(work_directory+short_send_filename+'.index','w+b') as indexfile:
            indexfile.write(bytes(index,'utf-8'))
            indexfile.close()
        parentfile.close()
if __name__=="__main__":
    config_file_name='./config.txt'
    Proggramm=Init()
    Proggramm.run()
