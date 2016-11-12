import socket
from SyConfig import debug_out, debug_con, sleep_time, destination_ip_port, my_address_port,\
    SOCKET_RCV_BUF_SIZE, SOCKET_SND_BUF_SIZE, online

class ReliableUdpSocket():
    def __init__(self, netType, protocolType):
        self.sock = socket.socket(netType, protocolType)

    def setsockopt(self, config, attr, value):
        return self.sock.setsockopt(config, attr, value)

    def bind(self, tupleAddressPort):
        return self.sock.bind(tupleAddressPort)

    def setblocking(self, isBlock):
        return self.sock.setblocking(isBlock)

    def close(self):
        return self.sock.close()

    def sendto(self, data, flags=None, *args, **kwargs): # real signature unknown; NOTE: unreliably restored from __doc__
        return self.sock.sendto(data, flags, *args, **kwargs)

    def recvfrom(self, buffersize, flags=None): # real signature unknown; restored from __doc__
        if not flags:
            return self.sock.recvfrom(buffersize)
        else:
            return self.sock.recvfrom(buffersize, flags)

class SySocket():
    def __init__(self):
        if debug_con == 0:
            self.sock = self.socket_init(my_address_port)

    def socket_init(self, address_port, blocking=True):
        # soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc = ReliableUdpSocket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_SND_BUF_SIZE)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_RCV_BUF_SIZE)
        soc.bind(address_port)
        soc.setblocking(blocking)
        print "socket_init " + str(address_port)
        #print soc.recvfrom(100)
        return soc


    def socket_close(self):
        # connection.close()
        self.sock.close()
    #
    #               TYPE    TYPE-mean       STR-mean
    # MouseEnter    set     setmousepos     x,y
    # MouseMove     mov     movemouseto     x,y
    # MouseClick    clc     click           l/r
    #
    # TODO:use status to judge to which screen should we send msg
    def socket_send(self, op, arg, dest_id):
        if not online[dest_id]:
            return
        # time.sleep(sleeptime)
        if op == "set":
            sendstr = "b" + arg  # set0,123 -> b#1#123 -> b1123
        elif op == "mov":
            sendstr = "mov" + arg
        elif op == "clc":
            sendstr = "clc" + arg
        elif op == "kd":  # keyboard down
            sendstr = "kd" + arg
        elif op == "ku":  # keyboard up
            sendstr = "ku" + arg
        elif op == "clp":  # keyboard up
            sendstr = "clp" + arg
        else:
            sendstr = arg
        if debug_out == 1:
            print 'dest id', dest_id
            print 'destination ip port [dest id]', destination_ip_port[dest_id]
            print "snd" + sendstr + ' to ' + str(destination_ip_port[dest_id])
        if debug_con == 0:
            self.sock.sendto(sendstr, destination_ip_port[dest_id])

