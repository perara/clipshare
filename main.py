import errno
import socket
import struct
from lz4.block import compress, decompress
import pyperclip
import asyncio

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
IS_ALL_GROUPS = True


class MulticastReceiver(asyncio.DatagramProtocol):
    def __init__(self, clipboard):
        self.clipboard = clipboard
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        pyperclip.copy(decompress(data).decode('utf-8'))


class MulticastSender:
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        self.sock = sock

    def send(self, msg):
        self.sock.sendto(compress(msg), (MCAST_GRP, MCAST_PORT))


class Clipboard:

    def __init__(self, loop):
        self.loop = loop
        self._handled = False
        self._current_clipboard = None

        self.sender = MulticastSender()

    async def clipboard_listener(self):

        while True:

            curr = pyperclip.paste()

            if curr != self._current_clipboard:
                print("Setting Clipboard")
                self._current_clipboard = curr
                self._handled = True
                self.sender.send(curr.encode("utf-8"))

            await asyncio.sleep(1)

    async def recieve_service(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if IS_ALL_GROUPS:
            # on this port, receives ALL multicast groups
            sock.bind(('', MCAST_PORT))
        else:
            # on this port, listen ONLY to MCAST_GRP
            sock.bind((MCAST_GRP, MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        return await self.loop.create_datagram_endpoint(
            lambda: MulticastReceiver(self),
            sock=sock,
        )


async def block():
    while True:
        await asyncio.sleep(5)

def main():
    loop = asyncio.get_event_loop()
    clip = Clipboard(loop=loop)

    loop.create_task(clip.clipboard_listener())
    loop.create_task(clip.recieve_service())

    loop.run_forever()






if __name__ == "__main__":
    main()

#pyperclip.copy("TEST")
# https://stackoverflow.com/questions/34826133/udp-broadcast-and-automatic-server-discovery-in-python-tcp-socket-unavailable
