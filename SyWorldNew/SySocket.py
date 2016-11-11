import socket
from SyConfig import debug_out, debug_con, sleep_time, destination_ip_port, my_address_port, SOCKET_RCV_BUF_SIZE, SOCKET_SND_BUF_SIZE
class SySocket():
    def __init__(self):
        if debug_con == 0:
            self.sock = self.socket_init(my_address_port)

    def socket_init(self, address_port, blocking=True):
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        if debug_out == 1:print "snd" + sendstr + ' to ' + str(destination_ip_port[dest_id])
        if debug_con == 0:self.sock.sendto(sendstr, destination_ip_port[dest_id])

