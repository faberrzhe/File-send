# File-transfer-server
"""
TODO:
1. Describe protocol
2. Write about

"""
"""
Protocol:
All messages begins with uppercase flag, ending with ::
Flags:
	server(or client)-ident_server
HELLO::"All active interface once in a minute sends hello to iden server or to receive server. In case to create or keepalive NAT translation
Structure:"HELLO::ident(10digits)"

GET_IDENT::"Used when need to resolve ident to ip-port pair"
Structure:"GET_IDENT::ident(10digits)"

IDENT::"Answer to GET_IDENT"
Structure:"IDENT::ident(10digits)-ip-port,ident(10digits)-ip-port..."
	client-server

INDEX::"Client send indexfile, contains filename, client ident, part number,size,and checksum"
Structure:"INDEX::size(bytes)::indexfile"

GET_FRAGMENT::"Server send to client fragmet didn't yet received"
Structure:"GET_FRAGMENT::ident(10digits)::fragment_id(int),fragment_id(int),..."

FRAGMENT::"Send fragment to server"
Structure:"FRAGMENT::filename(str)::fragment_id(int)::fragment_file"

DONE::"Send acknowlage to client all fragments received"
Structure:"DONE::filename"
"""
