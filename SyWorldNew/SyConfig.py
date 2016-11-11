import ConfigParser

cp = ConfigParser.ConfigParser()
cp.read('conf.conf')
config_section = 'info'
debug_section = 'debug'

destination_ip = [0,0,0,0,0]
online = [0,0,0,0,0]
destination_ip[1] = cp.get(config_section, 'right')
destination_ip[2] = cp.get(config_section, 'left')
destination_ip[3] = cp.get(config_section, 'up')
destination_ip[4] = cp.get(config_section, 'down')
my_port = cp.getint(config_section, 'port')
my_port_file = cp.getint(config_section, 'file_port')
SOCKET_SND_BUF_SIZE = cp.getint(config_section, 'SOCKET_SND_BUF_SIZE')
SOCKET_RCV_BUF_SIZE = cp.getint(config_section, 'SOCKET_RCV_BUF_SIZE')
margin = cp.getint(config_section, 'margin')
file_receive_path = cp.get(config_section, 'file_receive_path')

debug_out = cp.getint(debug_section, 'output')
debug_con = 1 - cp.getint(debug_section, 'connection')
debug_esc = cp.getint(debug_section, 'escape_hot_key')

# destination_ip_port = [("127.0.0.1", my_port), ("127.0.0.1", my_port), ("127.0.0.1", my_port), ("127.0.0.1", my_port), ("127.0.0.1", my_port)]
# destination_ip_port_file = [("127.0.0.1", my_port_file), ("127.0.0.1", my_port_file), ("127.0.0.1", my_port_file), ("127.0.0.1", my_port_file), ("127.0.0.1", my_port_file)]
destination_ip_port = [("",0), ("",0), ("",0), ("",0), ("",0)]
destination_ip_port_file = [("",0), ("",0), ("",0), ("",0), ("",0)]

dest_port = cp.getint(config_section, 'dest_port')
dest_port_file = cp.getint(config_section, 'dest_file_port')
# for speed up
# i: should unify with status and online index, which start with 1
for i in [1, 2, 3, 4]:
    #TODO: check if ip correct
    if destination_ip[i] != '0':
        online[i] = True
    else:
        online[i] = False
    destination_ip_port[i] = (destination_ip[i], dest_port)
    destination_ip_port_file[i] = (destination_ip[i], dest_port_file)
print online
my_address = '0.0.0.0'
# dest_address = destaddr
# TODO: tell others my port number

# online = [False, True, True, True, True] # null, right left up down, [0] means nothing, start from 1,
sleep_time = 0
# attention: mouse_pos_hide is used in Hook
pymousepos = pymousepos_old = []

my_address_port = (my_address, my_port)
my_address_port_file = (my_address, my_port_file)
# dest_address_port = (dest_address, my_port)
# dest_address_port_file = (dest_address, my_port_file)

