This is program for sending files over the network.
Can send files over several interfaces. It can continue sending after network fails or interrupt.
At first it cut file to parts and then send it server. After that server solve parts together
Can run both on Windows and Linux
Works on port 5666
Requires python 3, and iproute2 for Linux
Usage:
Server: ~PROGRAMDIR/server.py
Client: ~PROGRAMDIR/client.py <server fqdn or ip> <sending file>
More options for client available in ~PROGRAMDIR/config.txt
If You want to use several interfaces use option "auto" for interface parameter or set ip, nexthop and weight manualy
Directory for receiving file is C:/python_receive on Windows and ~/python_receive on Linux
