#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import socket, threading, re, sys, os, time, random, getopt
def keepalive(socket):
    global server_id, ident_server
    socket.connect(ident_server,5666)
    socket.send(bytes('HELLO::'+server_id),'utf-8')

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
    def parse_config(self):
        global config_file_name
        global server_id, interface,ident_server, hello_interval, client_threads, fragment_size
        variable_list={}
        try:
            config_file=open(config_file_name,'r+',encoding='utf-8')
        except OSError:
            answer=input('No config file. Create default(YES)?')
            if answer=='Yes' or answer=='':
                config_file=open(config_file_name,'w+')
                random.seed()
                server_id='00000000000'+str(random.randint(1,9999999999))
                server_id=server_id[-10:]
                default_config='server_id='+server_id+'\r\ninterface=single\r\nident_server=none\r\nhello_interval=60\r\nclient_threads=10\r\nfragment_size=2000000'
                config_file.write(default_config)
            else:
                sys.exit(1)
        for line_ in config_file:
            try:
                variable_name=re.findall('(?!#)(\S+)=\S+',line_)[0]
            except IndexError:
                pass
            else:
                variable_value=re.findall('=(\S+)[\\n|\\r\\n]',line_)[0]
                variable_list[variable_name]=variable_value
        for key in variable_list:
            if key=='server_id':
                server_id=variable_list[key]
                print(server_id)
            elif key=='interface':
                interface=variable_list[key]
                print (interface)
            elif key=='ident_server':
                ident_server=variable_list[key]
                print(ident_server)
            elif key=='hello_interval':
                hello_interval=variable_list[key]
                print(hello_interval)
            elif key=='client_threads':
                client_threads=variable_list[key]
                print(client_threads)
            elif key=='fragment_size':
                fragment_size=variable_list[key]
                print(fragment_size)
    def parse_sys(self):
        server_state='server'
        state=''
        send_filename=''
        ident=''
        ip=''
        try:
            opts,args=getopt.getopt(sys.argv[1:],"hsci:d:f:")
        except getopt.GetoptError:
            print('Usage [-s|-c] [-i <ident> | -d <ip:port>] , -f <file>')
            sys.exit(1)
        for opt,arg in opts:
            if opt=='-s': server_state='server'
            elif opt=='-c': server_state='client'
            elif opt=='-f': send_filename=arg
            elif opt=='-i':
                state='ident'
                ident=arg
            elif opt=='-d':
                state='ip'
                ip=arg
        if server_state=='server':
            server=Server()
            server.run()
        elif server_state=='client' and state=='ident' and send_filename!='':
            client=Client(send_filename,state,ident)
            client.run()
        elif server_state=='client' and state=='ip' and send_filename!='':
            client=Client(send_filename,state,ip)
            client.run()
        elif state=='':
            print('Wrong argument -i or -d requred')
            sys.exit(1)
        elif server_state=='client' and send_filename=='':
            print('Filename with -f key required')
            sys.exit(1)


if __name__=="__main__":
    config_file_name='./config.txt'
    Proggramm=Init()
    Proggramm.run()
