"""Implements PyScreamReader that plays Scream streams using PyAudio"""
from socket import socket, AF_INET, SOCK_DGRAM
from pyaudio import PyAudio, Stream, paInt16, paInt24, paInt32
stream: Stream | None = None
active_header: bytes | None = None
udp: socket = socket(AF_INET, SOCK_DGRAM)
udp.bind(("", 4010))
while True:
    pcm: bytes = udp.recvfrom(1157)[0]
    if active_header != pcm[:5]:
        stream = PyAudio().open(rate=(44100 if (pcm[0] >> 7) else 48000) * (pcm[0] & 127),
            channels=pcm[2], format={16: paInt16, 24: paInt24, 32: paInt32}[pcm[1]], output=True)
        active_header = pcm[:5]
    stream.write(pcm[5:])  # type: ignore
