#!/usr/bin/env python
#############################################################################
# The MIT License (MIT)
# 
# Copyright (c) 2015 Jason Pruitt
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#############################################################################

import os
import mmap
import struct

class GPIO(object):
    """ GPIO gives access to the board gpio pins on the main connector.
        Limitations: Must be run as root, and 1kHz toggle time.
    """
    def __init__(self, board):
        """ Initialize GPIO

        Arguments:
        board:Config    board config from boards/

        Example:
            from boards import nanopi
            brd_cfg = nanopi.Config()
            gpio = GPIO(brd_cfg)
        """
        self.board = board
        self.base_addr = (self.board.GPIO_OFFSET & ~(mmap.PAGESIZE-1))
        self.base_addr_offset = self.board.GPIO_OFFSET - self.base_addr

        f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
        self.mm = mmap.mmap(f, self.board.GPIO_LENGTH,
                            mmap.MAP_SHARED,
                            mmap.PROT_READ | mmap.PROT_WRITE,
                            offset=self.base_addr)

    def init_pin(self, pin, direction=0, updown=0):
        """ Initialize a pin for use.

        Arguments:
        pin:Int             Pin number of board connector.
        direction:Int       0:Input, 1:Output
        pullup:Int          0:None, 1:Down, 2:Up
        """
        self._pin_check(pin)
        self.set_direction(pin, direction)

        if direction == 0:
            self.set_updown(pin, updown)
        else:
            # updown should not be enabled on output.
            self.set_updown(pin, 0)

    def read(self, pin):
        """ Read pin value.

        Arguments:
        pin:Int         Pin number of board connector.

        Returns:Int     1 for high, 0 for low.
        """
        self._pin_check(pin)
        return self._read_pin(pin)

    def write(self, pin, value):
        """ Set value of pin.

        Arguments:
        pin:Int         Pin number of board connector.
        value:Int       True or False if setting low.
        """
        self._pin_check(pin)

        if value:
            self._write_pin(pin, 1)
        else:
            self._write_pin(pin, 0)

    def set_direction(self, pin, direction):
        """ Set direction of pin.

        Arguments:
        pin:Int             Pin number of board connector.
        direction:Int       0:Input, 1:Output
        """
        self._pin_check(pin)

        if direction:
            self._set_direction(pin, 1)
        else:
            self._set_direction(pin, 0)

    def set_updown(self, pin, updown=0):
        """ Set pull up or down on the pin.

        Arguments:
        pin:Int         Pin number of board connector.
        updown:Int      0:None, 1:Down, 2:Up
        """
        self._pin_check(pin)

        if updown == 1:
            self._set_updown(pin, 1)
        elif updown == 2:
            self._set_updown(pin, 2)
        else:
            self._set_updown(pin, 0)

    def _pin_check(self, pin):
        if self.board.pins[pin]['bank'] not in board.banks:
            raise Exception('Bad gpio bank.')

        if pin not in self.board.pins:
            raise Exception('Bad pin.')

    def _read_pin(self, pin):
        self._set_seek_addr(pin, board.GPIO_DATA_OFFSET)
        data = self._mem_read()
        return 0x01 & (data >> self.board.pins[pin]['num'])

    def _write_pin(self, pin, value):
        self._set_seek_addr(pin, board.GPIO_DATA_OFFSET)
        self._mem_write(pin, value)

    def _set_direction(self, pin, direction):
        self._set_seek_addr(pin, board.GPIO_CON_OFFSET)
        self._mem_write2(pin, direction)

    def _set_updown(self, pin, updown):
        self._set_seek_addr(pin, board.GPIO_UPD_OFFSET)
        self._mem_write2(pin, updown)

    def _set_seek_addr(self, pin, offset_bank):
        bank = self.board.pins[pin]['bank']
        self.mm.seek(self.base_addr_offset + board.banks[bank] + offset_bank)

    def _mem_write(self, pin, value):
        pin_num = self.board.pins[pin]['num']
        data = self._mem_read()
        data = (data & ~(1 << (pin_num))) | ((value & 1) << (pin_num))
        self.mm.write(struct.pack('I', data))

    def _mem_write2(self, pin, value):
        pin_num = self.board.pins[pin]['num']
        data = self._mem_read()
        data = (data & ~(3 << (pin_num * 2))) | ((value & 3) << (pin_num * 2))
        self.mm.write(struct.pack('I', data))

    def _mem_read(self):
        ret = struct.unpack('I',  self.mm.read(4))[0]
        self.mm.seek(self.mm.tell()-4)
        return ret

if __name__ == '__main__':
    from boards import nanopi
    from time import sleep

    # Initialize GPIO
    brd_cfg = nanopi.Config()
    gpio = GPIO(brd_cfg)

    # Initialize pin 40 as output (1).
    gpio.init_pin(40, 1)

    # Initialize pin 38 as input (0) with pullup (2)
    gpio.init_pin(38, 0, 2)

    # While pin 38 is high toggle pin 40.
    value = False
    while gpio.read(38) != 0:
        value =  not value
        gpio.write(40, value)
        sleep(.5)

