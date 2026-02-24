import socket
import struct
import re
import time
from mcstatus import JavaServer
def scan_lan():
    servers=[]
    seen=set()
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,2)
        s.sendto(b'[MOTD]/[/MOTD][AD]0[/AD]',('224.0.2.60',4445))
        s.close()
    except:
        return servers
    recv=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
    recv.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:
        recv.bind(('',4445))
    except:
        return servers
    mreq=struct.pack("4sl",socket.inet_aton('224.0.2.60'),socket.INADDR_ANY)
    recv.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,mreq)
    recv.settimeout(10)
    start=time.time()
    while time.time() - start < 3:
        try:
            data,addr=recv.recvfrom(1024)
            ip=addr[0]
            text=data.decode('utf-8',errors='ignore')
            motd_match=re.search(r'\[MOTD\](.*?)\[/MOTD\]',text)
            port_match=re.search(r'\[AD\](.*?)\[/AD\]',text)
            if port_match:
                port=int(port_match.group(1))
                key=(ip,port)
                if key not in seen:
                    seen.add(key)
                    motd='Unknown'
                    if motd_match:
                        motd=motd_match.group(1)
                    servers.append({'ip':ip,'port':port,'motd':motd})
        except socket.timeout:
            break
        except:
            pass
    recv.close()
    return servers
def server_info(ip, port, timeout=5):
    server=JavaServer.lookup(f"{ip}:{port}",timeout=timeout)
    status=server.status()
    players=[]
    if status.players.sample:
        players=[p.name for p in status.players.sample]
    return {
        'online':status.players.online,
        'max':status.players.max,
        'latency':round(status.latency),
        'players':players
    }
