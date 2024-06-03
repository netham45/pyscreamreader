from typing import Optional
import pyaudio
import socket
from threading import Thread
from scream_header_parser import ScreamHeader
import time

frames = []
stream: Optional[pyaudio.Stream] = None

def udpStream() -> None:
    global stream
    p = pyaudio.PyAudio()
    header: ScreamHeader = ScreamHeader(bytes([1,32,2,0,0]))
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("", 4010))
    while True:
        soundData, _ = udp.recvfrom(1157)
        packet_header: ScreamHeader = ScreamHeader(soundData[:5])
        if packet_header != header:
            print(soundData[:5])
            print(f"Got new header {packet_header.bit_depth} {packet_header.sample_rate} {packet_header.channels}")
            header = packet_header
            format: int = pyaudio.paInt16
            if header.bit_depth == 24:
                format = pyaudio.paInt24
            elif header.bit_depth == 32:
                format = pyaudio.paInt32
            if not stream is None:
                stream.close()
            stream = p.open(format=format,
                            channels = header.channels,
                            rate = header.sample_rate,
                            output = True
                            )
        frames.append(soundData[5:])
    udp.close()

def play() -> None:
    global stream
    BUFFER = 5
    while True:
        if len(frames) >= BUFFER:
            try:
                while True:
                    if not stream is None:
                        stream.write(frames.pop(0))
                    else:
                        frames.pop(0)
            except IndexError:  # Buffer is empty, rebuild it
                print("Buffer underrun")
        else:
            time.sleep(.05)

if __name__ == "__main__":
    receiver = Thread(target = udpStream)
    player = Thread(target = play)
    receiver.start()
    player.start()
    receiver.join()
    player.join()