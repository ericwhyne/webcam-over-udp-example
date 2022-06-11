# https://github.com/ericwhyne/webcam-over-udp-example
import yaml
import sys
import socket
import cv2
import numpy as np

config = yaml.safe_load(open("config.yaml"))

rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rcv_sock.bind(('', config["client_video_port"]))

init_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = "Start the video."
init_sock.sendto(message.encode(), (config["server_ip"], config["server_video_port"]))

framebuffer = {} # initialize our buffer where we will compile packets into frames
while True:
    bytesAddressPair = rcv_sock.recvfrom(65507) # read in max udp size from socket
    packet = bytesAddressPair[0]
    send_address = str(bytesAddressPair[1])
    print("Received packet from " + send_address + " of size " + str(len(packet)))

    segnum = packet[0:5].decode('latin-1') # which number is this packet
    num_of_segments = int(packet[5:10].decode('latin-1')) # how many packets to expect
    etimesec = str(packet[10:29].decode('latin-1')) # the epoch millisecond of this frame (which we use as a UID)
    payload = packet[29:] # the part of the image the packet is transporting
    if etimesec not in framebuffer.keys(): # if we haven't seen this UID
        framebuffer[etimesec] = [] # then create an array in the buffer for it
    framebuffer[etimesec].append((segnum, payload)) # we add the payload as a tuple so we can sort on segnum later
    if len(framebuffer[etimesec]) >= num_of_segments + 1: # if we have all the pieces of the frame
        received_frame_bytes = b"" # initialize an empty string of bytes to build the frame in
        for frame_segment in sorted(framebuffer[etimesec]): # iterate through the pieces in order
            received_frame_bytes += frame_segment[1] # compile them into the byte string
        received_frame = cv2.imdecode(np.asarray(bytearray(received_frame_bytes), dtype=np.uint8), 1) #convert byte stream back to an opencv image
        cv2.imshow('Video',received_frame) # show the image
        framebuffer.pop(etimesec) # once displayed, take this frame out of the buffer
        for key in framebuffer.keys(): # get rid of any older incomplete frames sitting in buffer
            if int(key) < int(etimesec):
                framebuffer.pop(key)
        if cv2.waitKey(20) & 0xFF==ord('d'):
            break






#'''EOF
