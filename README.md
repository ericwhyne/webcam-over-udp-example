# webcam-over-udp-example
Most implementations of RTP or RTSP have a few seconds of delay. This is unacceptable when using them as part of robotics remote control projects.

This minimal code shows how to: 
- read a webcam
- convert each frame to packets with a minimal application header (inspired by RTP/RTSP)
- initialize a connection
- send and then reassemble the packets in order
- manage a frame buffer and discard partial older frames (in case of packet loss) 
- view the image on client side

This is accomplished with as little delay as possible using IP packet networking via UDP. It's possible to tune this further by chancing host packet size limitations, camera size, and compression styles.  

