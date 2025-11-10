"""Simple smoke test for Roboclaw library without hardware.

Creates a FakeSerial that can be preloaded with bytes and captures writes.
Runs a couple of basic operations to verify bytes handling in Python 3.
"""
import sys
import time

from roboclaw import Roboclaw


class FakeSerial:
    def __init__(self):
        self.inbuf = bytearray()
        self.outbuf = bytearray()
        self.timeout = None

    def write(self, data):
        # record all outgoing bytes
        if isinstance(data, (bytes, bytearray)):
            self.outbuf += data
        else:
            # try to coerce
            self.outbuf += bytes(data)

    def read(self, n=1):
        # return up to n bytes
        if not self.inbuf:
            return b""
        to_return = self.inbuf[:n]
        self.inbuf = self.inbuf[n:]
        return bytes(to_return)

    def flushInput(self):
        self.inbuf = bytearray()

    def preload(self, data):
        # accept bytes or iterable of ints
        if isinstance(data, (bytes, bytearray)):
            self.inbuf += data
        else:
            self.inbuf += bytes(data)


def smoke_test():
    rc = Roboclaw("FAKE", 115200)
    fake = FakeSerial()
    rc._port = fake

    # Test: SendRandomData writes bytes
    fake.outbuf = bytearray()
    rc.SendRandomData(4)
    assert len(fake.outbuf) == 4, "SendRandomData did not write 4 bytes"

    # Test: _sendcommand writes two bytes (address, command)
    fake.outbuf = bytearray()
    rc._sendcommand(0x80, 0x21)
    assert fake.outbuf[0] == 0x80 and fake.outbuf[1] == 0x21, "_sendcommand wrote unexpected bytes"

    # Test: _writebyte writes a single byte
    fake.outbuf = bytearray()
    rc._writebyte(0x7F)
    assert fake.outbuf == b"\x7f", "_writebyte failed"

    # Test: _readbyte reads from fake.inbuf
    fake.preload(b"\x05")
    ok, val = rc._readbyte()
    assert ok == 1 and val == 5, "_readbyte returned wrong value"

    print("All smoke tests passed")


if __name__ == "__main__":
    smoke_test()
