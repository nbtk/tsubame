#!/usr/bin/env python3

__author__ = "NBTK"
__copyright__ = "Copyright 2022, NBTK"
__license__ = "BSD-3-Clause"
__version__ = "1.0"

import threading
import socket
import os
import sys
import time
import ipaddress


class traceroute:
    # icmp types with code
    __ICMP_ECHO_REPLY = b'\x00\x00'
    __ICMP_ECHO_REQUEST = b'\x08\x00'
    __ICMP_TIME_EXCEEDED = b'\x0b\x00'

    # icmp echo requests will be xmited with this message
    __ECHO_MSG = b'underway on nuclear power'

    # icmp socket arguments
    __sk_args = (socket.AF_INET,
                 socket.SOCK_RAW,
                 socket.getprotobyname('icmp'))

    def __recv_probe(self, sk, host_ip, count, hop_limit, ident,
                     recv_records):
        for _ in range(count * hop_limit):
            try:
                ip_msg, (addr, port) = sk.recvfrom(4096)
            except socket.timeout:
                break
            recv_timestamp = time.time()
            reached = False
            icmp_msg = ip_msg[(ip_msg[0] & 0x0f) * 4:]
            icmp_type_code = icmp_msg[0:2]
            if icmp_type_code == self.__ICMP_TIME_EXCEEDED:
                org_dgram = org_iphdr = icmp_msg[8:]
                org_dst_ip = ipaddress.ip_address(org_iphdr[16:20])
                # shifts an ip header size
                icmp_msg = org_dgram[(org_iphdr[0] & 0x0f) * 4:]
            elif icmp_type_code == self.__ICMP_ECHO_REPLY:
                org_dst_ip = ipaddress.ip_address(addr)
                reached = True
            else:
                continue
            if org_dst_ip != host_ip:
                # the received message is not destined to me
                continue
            if icmp_msg[4:6] != ident:
                # the xmited message was sent by someone else
                continue
            record = icmp_msg[6:8]
            recv_records[record] = (recv_timestamp,
                                    addr,
                                    reached)

    def __xmit_probe(self, sk, host, count, hop_limit, ident):
        xmit_records = []
        for ttl in range(1, hop_limit + 1):
            sk.setsockopt(socket.SOL_IP,
                          socket.IP_TTL,
                          ttl)
            for seq in range(1, count + 1):
                record = ((ttl << 8) + seq).to_bytes(2, 'big')
                msg = ident + record + self.__ECHO_MSG
                csum = int.from_bytes(self.__ICMP_ECHO_REQUEST,
                                      sys.byteorder)
                for i in range(0, len(msg), 2):
                    csum += int.from_bytes(msg[i: i + 2],
                                           sys.byteorder)
                while csum >> 16:
                    csum = (csum >> 16) + (csum & 0xffff)
                csum = (~csum & 0xffff).to_bytes(2,
                                                 sys.byteorder)
                msg = self.__ICMP_ECHO_REQUEST + csum + msg
                xmit_records.append((record, time.time()))
                sk.sendto(msg, (host.__str__(), 33434))
                # the port number 33434 has no particular meaning
        return xmit_records

    def probe(self, host, hop_limit=8, count=1, timeout=1.0, ident=None):
        host = socket.getaddrinfo(host,
                                  None,
                                  *self.__sk_args)[0][4][0]
        host_ip = ipaddress.ip_address(host)
        if not isinstance(hop_limit, int):
            raise TypeError('the "hop_limit" argument must be int type but ' +
                            type(hop_limit).__name__ + ' type was given')
        if hop_limit < 1 or hop_limit > 64:
            raise ValueError('the "hop_limit" argument must be an int from 1 to 64 but ' +
                             str(hop_limit) + ' was given')
        if not isinstance(count, int):
            raise TypeError('the "count" argument must be int type but ' +
                            type(count).__name__ + ' type was given')
        if count < 1 or count > 4:
            raise ValueError('the "count" argument must be an int from 1 to 4 but ' +
                             str(count) + ' was given')
        if ident is None:
            ident = (os.getpid() & 0xffff).to_bytes(2, 'big')
        if not (isinstance(ident, bytes) or isinstance(ident, bytearray)):
            raise TypeError('the "ident" argument must be bytes type or bytearray type but ' +
                            type(ident).__name__ + ' type was given')
        if len(ident) != 2:
            raise ValueError('the size of "ident" argument must be 2 bytes')
        recv_records = {}  # the resluts will be stored to this map
        sk = socket.socket(*self.__sk_args)
        try:
            sk.settimeout(timeout)
            recv_thread = threading.Thread(target=self.__recv_probe,
                                           args=(sk,
                                                 host_ip,
                                                 count,
                                                 hop_limit,
                                                 ident,
                                                 recv_records))
            recv_thread.start()
            xmit_records = self.__xmit_probe(sk,
                                             host_ip,
                                             count,
                                             hop_limit,
                                             ident)
            recv_thread.join()
        except Exception as error:
            raise error
        finally:
            sk.close()
        results = [[] for i in range(hop_limit)]
        for record, xmit_timestamp in xmit_records:
            ttl = record[0]
            try:
                recv_timestamp, addr, reached = recv_records[record]
            except KeyError:
                results[ttl - 1].append(None)
                continue
            delay = recv_timestamp - xmit_timestamp
            if delay < 0:
                raise ValueError('negative rtt')
            results[ttl - 1].append((addr,
                                     delay,
                                     reached))
        return results


def main():
    if len(sys.argv) != 2:
        print('usage: tsubame example.com', file=sys.stderr)
        return 1
    sk_args = (socket.AF_INET,
               socket.SOCK_RAW,
               socket.getprotobyname('icmp'))

    try:
        host = socket.getaddrinfo(sys.argv[1],
                                  None,
                                  *sk_args)[0][4][0]
    except Exception as e:
        print('could not resolve the target host: %s' % e, file=sys.stderr)
        return 1
    hop_limit = 32
    count = 3
    print('traceroute to %s (%s), %s hops max' %
          (sys.argv[1], host, hop_limit))
    try:
        results = traceroute().probe(host, hop_limit, count)
    except Exception as e:
        print('an error occurred while sending probe packets: %s' % e, file=sys.stderr)
        return 1
    reached = False
    no_reply = '*'
    for ttl, seq_results in enumerate(results):
        print('%2d ' % (ttl + 1), end='')
        prev_addr = None
        for result in seq_results:
            addr = no_reply
            if result is not None:
                addr, delay, reached = result
            if prev_addr is not None and addr != prev_addr:
                print('\n   ', end='')
            if addr is None:
                addr = no_reply
            if prev_addr != addr or addr == no_reply:
                print(' %s' % addr, end='')
            if addr != no_reply:
                print('  %0.3f ms' % (delay * 1e3),
                      end='')
            prev_addr = addr
        print('')
        if reached is True:
            break

    return 0


if __name__ == '__main__':
    sys.exit(main())
