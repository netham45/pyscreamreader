"""Implements PyScreamReader that plays Scream streams using PyAudio"""
from typing import Optional
import pyaudio
import socket
from threading import Thread
from scream_header_parser import ScreamHeader

class ScreamReader():
    """Reads from Scream, writes to PyAudio"""
    BUFFER: int = 10

    def __init__(self):
        self.frames = []
        self.stream: Optional[pyaudio.Stream] = None
        receiver = Thread(target = self.udpStream)
        player = Thread(target = self.play)
        receiver.start()
        player.start()
        receiver.join()
        player.join()

    def udpStream(self) -> None:
        """This thread receives frames and writes them to a buffer"""
        p = pyaudio.PyAudio()
        header: ScreamHeader = ScreamHeader(bytes([1,32,2,0,0]))
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("", 4010))
        while True:
            soundData, _ = udp.recvfrom(1157)
            packet_header: ScreamHeader = ScreamHeader(soundData[:5])
            if packet_header != header:
                print(f"Got new header {packet_header.bit_depth} {packet_header.sample_rate} {packet_header.channels}")
                header = packet_header
                if not self.stream is None:
                    self.stream.close()
                format: int = pyaudio.paInt16
                if header.bit_depth == 24:
                    format = pyaudio.paInt24
                elif header.bit_depth == 32:
                    format = pyaudio.paInt32
                self.stream = p.open(format = format,
                                     channels = header.channels,
                                     rate = header.sample_rate,
                                     output = True
                                    )
            self.frames.append(soundData[5:])

    def play(self) -> None:
        """This thread plays frames that have been received"""
        while True:
            if len(self.frames) >= self.BUFFER:
                try:
                    while True:
                        if not self.stream is None:
                            self.stream.write(self.frames.pop(0))
                        else:
                            self.frames.pop(0)
                except IndexError:  # Buffer is empty, rebuild it
                    print("Buffer underrun")
                    pass

ScreamReader()