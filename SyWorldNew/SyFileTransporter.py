import threading
import time
from SyConfig import *

class FileTransportThread(threading.Thread):
    is_files_ready = False
    files_to_send = []
    def __init__(self):
        threading.Thread.__init__(self, name="filethread")

    def build(self, sy):
        self.sy = sy

    def run(self):
        print "ft running!"
        chunk_size = 1024
        buf = ""
        recip = ""
        file_socket = self.sy.sySock.socket_init(my_address_port_file, blocking=False)
        if debug_out == 1: print "ft running!"
        while True:
            if self.is_files_ready:
                print "is_files_ready!"
                for file in self.files_to_send:
                    file_name = file.split('\\')[-1]
                    file_socket.sendto(file_name, destination_ip_port_file[self.sy.status])
                    if debug_out == 1:
                        print "send file %s to " %(file_name) +str(destination_ip_port_file[self.sy.status])
                    buf = ''
                    while buf not in ['begin', 'cancel'] or recip != destination_ip_port_file[self.sy.status]:
                        try:
                            buf, recip = file_socket.recvfrom(1024)
                        except Exception, e:
                            pass
                    if buf == 'cancel':
                        if debug_out:
                            print 'file cancelled'
                        continue
                    if debug_out == 1:
                        print "file name:{} sended!".format(file_name)
                    send_count = 0
                    for chunk in self.read_file_by_chunk(file, chunk_size):
                        file_socket.sendto('0'+chunk, destination_ip_port_file[self.sy.status])
                        send_count += 1
                        print "chunk {0} sended".format(send_count)
                        time.sleep(1.0/2048)  # change the speed from 2MB/s into 1MB/s in my test env, so won't be so ka
                        if send_count == 10:
                            buf = ''
                            while buf != "continue" or recip != destination_ip_port_file[self.sy.status]:
                                try:
                                    buf, recip = file_socket.recvfrom(1024)
                                except Exception, e:
                                    pass
                            send_count = 0
                    file_socket.sendto('end', destination_ip_port_file[self.sy.status])
                    print "end 1 sended"
                self.is_files_ready = False
            else:
                # print "no file ready"
                buf = ''
                try:
                    buf, recip = file_socket.recvfrom(1024)
                except Exception, e:
                    continue
                if buf:
                    if debug_out: print "recv file: " + buf + " from " + str(recip)
                    # just in "else"
                    file_name = buf
                    # TODO: already have file
                    if debug_out:
                        print "going to open file"
                    file_exist = True
                    try:
                        f = open(file_receive_path + file_name)
                        f.close()
                    except Exception, e:
                        file_exist = False
                        if debug_out:
                            print 'creating file'
                    if file_exist:
                        print '\n\n\n\n\nfile already exist, cancel transporting\n\n\n\n\n'
                        file_socket.sendto('cancel', recip)
                        continue
                    file_socket.sendto('begin', recip)
                    # TODO: catch this error, maybe sprang an alert window.
                    # TODO: maybe check the file path at the very beginning.
                    with open(file_receive_path + file_name, "ab") as fd:
                        if debug_out:
                            print 'recving: ' + file_name
                        recv_count = 0
                        while True:
                            if debug_out:
                                print 'waiting for data'
                            ip = ''
                            buf = ''
                            while not buf or ip != recip:
                                try:
                                    buf, ip = file_socket.recvfrom(1030)
                                except Exception, e:
                                    # TODO: do something
                                    pass
                            if buf[:3] == 'end':
                                break
                            recv_count += 1
                            if recv_count == 10:
                                file_socket.sendto('continue', recip)
                                recv_count = 0
                            fd.write(buf[1:])
                        if debug_out:
                            print 'recv_count' + str(recv_count)
                    if debug_out:
                        print 'finish!'
        file_socket.close()
        if debug_out == 1: print "ft end!"


    def read_file_by_chunk(self, filename, chunksize = 1024):
        file_obj = None
        try:
            file_obj = open(filename,'rb')
            while True:
                chunk = file_obj.read(chunksize)
                if not chunk:
                    break
                yield chunk
        except Exception as e:
            print e
        finally:
            if file_obj: file_obj.close()


