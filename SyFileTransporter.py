import threading
import SyTools
import time

class FileTransportThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="filethread")

    def run(self):
        print "ft running!"
        chunk_size = 1024
        file_socket = SyTools.socket_init(SyTools.my_address_port_file)
        if SyTools.debug_out == 1: print "ft running!"
        while True:
            if SyTools.is_files_ready:
                print "is_files_ready!"
                for file in SyTools.files_to_send:
                    file_name = file.split('\\')[-1]
                    if SyTools.debug_out == 1: print "send file name to "+str(SyTools.dest_address_port_file)
                    file_socket.sendto(file_name, SyTools.dest_address_port_file)
                    while file_socket.recv(1024) != "begin": pass
                    if SyTools.debug_out == 1: print "file name:{} sended!".format(file_name)
                    send_count = 0
                    for chunk in SyTools.read_file_by_chunk(file, chunk_size):
                        file_socket.sendto('0'+chunk, SyTools.dest_address_port_file)
                        send_count += 1
                        print "chunk {0} sended".format(send_count)
                        time.sleep(1.0/2048)  # change the speed from 2MB/s into 1MB/s in my test env, so won't be so ka
                        if send_count == 10:
                            while file_socket.recv(1024) != "continue": pass
                            send_count = 0
                    file_socket.sendto('end', SyTools.dest_address_port_file)
                    print "end 1 sended"
                is_files_ready = False
        file_socket.close()
        if SyTools.debug_out == 1: print "ft end!"

