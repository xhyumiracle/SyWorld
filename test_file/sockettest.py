import threading
import socket
import time

class ClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="client thread")

    def run(self):
        print "st running!"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        sock.bind(('localhost',10141))
        sock.sendto("--------------------------------",('localhost',10142))


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="server thread")

    def run(self):
        print "st running!"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost',10142))
        try:
            buf = sock.recv(99)
            print buf
        except Exception as e:
            print e
            pass

ct = ClientThread()
st = ServerThread()

ct.setDaemon(True)
st.setDaemon(True)

st.start()
ct.start()

ct.join()
st.join()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)
print sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print sock1.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)