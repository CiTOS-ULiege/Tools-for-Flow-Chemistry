# -*- coding: utf-8 -*-
"""
Author: skoehler
From github (this code fragment was shared with full permision to reuse and modification for everyone)
Here's a class that serves as a wrapper to a pyserial object. It allows you to read lines without 100% CPU.
It does not contain any timeout logic. If a timeout occurs, self.s.read(i) returns an empty string and you
might want to throw an exception to indicate the timeout.

Modifications by Hubert Hellwig:
- Simple timeout exception added.
- 26/08/2024 - modification of two "find(b"\n")" functions, to "find(b"\r")", because '\n' character was not
  present in data sent from Knauer Azura P4.1S pump. After changing readline works with all data streams.
- 27/08/2024 - modifications
"""

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s
        #self.s.reset_input_buffer()  # Clear any old data in the buffer

    def readline(self):
        while True:
            # Find the first occurrence of either \n or \r
            newline_index = self.buf.find(b"\n")
            carriage_return_index = self.buf.find(b"\r")

            # Determine the earliest line ending found
            if newline_index == -1:
                i = carriage_return_index
            elif carriage_return_index == -1:
                i = newline_index
            else:
                i = min(newline_index, carriage_return_index)

            # If either \n or \r is found
            if i >= 0:
                r = self.buf[:i+1]
                self.buf = self.buf[i+1:]
                return r

            # Read more data from the serial port
            i = max(1, min(2048, self.s.in_waiting))  # Read up to 2048 bytes at a time
            data = self.s.read(i)
            if data == b'':  # Timeout occurred
               raise TimeoutError("Readline timeout occurred")
            self.buf.extend(data)
