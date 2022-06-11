# https://github.com/ericwhyne/webcam-over-udp-example
import yaml
import sys
import time
import socket
import cv2
import math
import numpy as np

config = yaml.safe_load(open("config.yaml"))

def bytesToPackets(bytes, etimesec):
    max_payload_bytes = config["udp_buffer_size"] # packets will be this big plus the bytes of our header which is under 30 bytes (depending on OS clock accuracy)
    size = len(bytes) # measure size of the bytes to be transmitted
    num_of_segments = math.ceil(size/max_payload_bytes) # calculate how many packets we need to trasnport it
    array_pos_start = 0 # used to track our position as we traverse the bytes
    packets = [] # list used to store the packets we'll return
    segnum = 0 # used to track our way through the packets
    while segnum <= num_of_segments:
      array_pos_end = min(size, array_pos_start + max_payload_bytes) # calculate the end of the piece of bytes we'll put in this packet
      byte_chunk = bytes[array_pos_start:array_pos_end] # the chunk of bytes we're putting in this packet
      segnum_header = str(segnum).zfill(5).encode('latin-1') # we make sure the segnum is 5 single byte characters when we build the packet
      numofseg_header = str(num_of_segments).zfill(5).encode('latin-1') # we make sure the numofseg is 5 single byte characters when we build the packet
      etimesec_header = str(etimesec).encode('latin-1') # this is always the same length, we'll ensure it's encoded in single byte characters
      packet = segnum_header + numofseg_header + etimesec_header + byte_chunk # put the packet together
      packets.append(packet) # add the packet to our list of packets to be returned
      array_pos_start = array_pos_end # jump to start of next position in the bytes
      segnum += 1 # move onto the next packet
    return packets # give the compiled packets back

send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create socket we'll send video over
init_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create socket for client address discovery
init_sock.bind(('', config["server_video_port"])) # bind to the init socket on all host interfaces

client_address = "" # we'll store the client address here
while client_address == "": # wait for a client to connect so we can get their address
    print("Waiting for a client to connect")
    bytesAddressPair = init_sock.recvfrom(1024) # this is blocking
    message = str(bytesAddressPair[0]) # the first value of the received tuple is the payload
    client_address = str(bytesAddressPair[1][0]) # the second value of the received tuple is another tuple containing (address, port)
print("Connection initilized from client " + client_address + " which said " + message)

cam = cv2.VideoCapture(0) # initialize the first webcam we see plugged into the system
cam.set(cv2.CAP_PROP_FRAME_WIDTH, config["cam_size"][0])
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, config["cam_size"][1])

while True:
    success,frame = cam.read() # read from the camera
    if not success:
        print("failed to capture webcam image")
        sys.exit()
    image_bytes = cv2.imencode('.jpg', frame)[1].tobytes() # compress and convert opencv image to bytes
    etimesec = str(time.time_ns()) # grab the epoch time in milliseconds to label the frame with
    packets = bytesToPackets(image_bytes, etimesec) # convert the frame to packrets
    for packet in packets: # send each packet to the client
        print("sending packet of size " + str(len(packet)))
        send_sock.sendto(packet, (client_address, config["client_video_port"]))









#'''EOF
