#!/usr/bin/env python3

import random
import concurrent.futures
from scapy.all import IP, TCP, sr1, send

def scanner(target, port):

    sport = random.randint(1024, 65535)

    packet = IP(dst=target)/TCP(sport=sport, dport=port, flags="S")
    response = sr1(packet, timeout=1, verbose=0)

    if response is None:
        return         

    if response.haslayer(TCP):
        if response[TCP].flags == 0x12: # SYN-ACK
            send(IP(dst=target)/TCP(sport=sport, dport=port, flags="R"), verbose=0)
            return "Abierto"

if __name__ == '__main__':

    target = "172.16.3.76"
    ports = range(1, 100)

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        responses = executor.map(lambda p: (p, scanner(target, p)), ports) # map(funcion, iterable)

    for port, response in responses:
        if response:  
            print(f"Puerto {port}: {response}")