
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
        self._type_gpio = 'gpio'
        self._type_pwm = 'int'
        self._type_int = 'pwm'

        self.board = board

        self._sys_pwmchip = '/sys/class/pwm/pwmchip%s' % self.board.PWMCHIP_ID
        self._sys_pwm_export = os.path.join(self._sys_pwmchip, 'export')
        self._sys_pwm_unexport = os.path.join(self._sys_pwmchip, 'unexport')
        self._sys_pwm = os.path.join(self._sys_pwmchip, 'pwm%s')
        self._sys_pwm_period = os.path.join(self._sys_pwm, 'period')
        self._sys_pwm_duty_cycle = os.path.join(self._sys_pwm, 'duty_cycle')
        self._sys_pwm_enable = os.path.join(self._sys_pwm, 'enable')

        for pin in self.board.pins:
            self.board.pins[pin]['used'] = False

        self._base_addr = (self.board.GPIO_OFFSET & ~(mmap.PAGESIZE-1))
        self._base_addr_offset = self.board.GPIO_OFFSET - self._base_addr

        f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
        self.mm = mmap.mmap(f, self.board.GPIO_LENGTH,
                            mmap.MAP_SHARED,
                            mmap.PROT_READ | mmap.PROT_WRITE,
                            offset=self._base_addr)

    def gpio_init(self, pin, direction=0, updown=0):
        """ Initialize a pin for GPIO use.

        Arguments:
            pin:Int             Pin number GPxN on board connector.
            direction:Int        0:Input, 1:Output
            pullup:Int          0:None, 1:Down, 2:Up
        """

        self._pin_available(pin)

        if direction:
            self._gpio_direction(pin, 1)
            self._gpio_updown(pin, 0)     # updown should not be enabled on output.
        else:
            self._gpio_direction(pin, 0)
            self._gpio_updown(pin, updown)

        self.board.pins[pin]['used'] = self._type_gpio

    def gpio_read(self, pin):
        """ Read pin value.

        Arguments:
            pin:Int         Pin number of board connector.

        Returns:Int     1 for high, 0 for low.
        """
        self._pin_check(pin, self._type_gpio)
        return self._gpio_read(pin)

    def gpio_write(self, pin, value):
        """ Set value of pin.

        Arguments:
            pin:Int         Pin number of board connector.
            value:Int       1 or 0.
        """
        self._pin_check(pin, self._type_gpio)

        if value:
            self._gpio_write(pin, 1)
        else:
            self._gpio_write(pin, 0)

    def gpio_direction(self, pin, direction):
        """ Set direction of pin.

        Arguments:
            pin:Int             Pin number of board connector.
            direction:Int        0:Input, 1:Output.
        """
        self._pin_check(pin, self._type_gpio)
        self._int_check(direction, 'direction')

        if direction < 0 or direction > 1:
            raise ValueError('fgpio direction: "%s" out of range [0:Input, 1:Output]' % direction)

        if direction:
            self._gpio_direction(pin, 1)
        else:
            self._gpio_direction(pin, 0)

    def gpio_updown(self, pin, updown=0):
        """ Set pull up or down on the pin.

        Arguments:
            pin:Int         Pin number of board connector.
            updown:Int      0:None, 1:Down, 2:Up
        """
        self._pin_check(pin, self._type_gpio)
        self._int_check(updown, 'updown')

        if updown < 0 or updown > 2:
            raise ValueError('fgpio updown: "%s" out of range [0:None, 1:Down, 2:Up]' % updown)

        if updown == 1:
            self._gpio_updown(pin, 1)
        elif updown == 2:
            self._gpio_updown(pin, 2)
        else:
            self._gpio_updown(pin, 0)

    def pwm_init(self, pin, period, duty_cycle):
        """ Initialize a pin for PWM use.

        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
            period:Int          Period time in ns.
            duty_cycle:Int      Duty cycle in ns.
        """
        self._pin_available(pin)
        self._int_check(period, 'period')
        self._int_check(duty_cycle, 'duty cycle')
        self.board.pins[pin]['used'] = self._type_pwm

        if not os.path.exists(self._sys_pwm_export):
            raise Exception('fgpio sys PWM path does not exist.')

        if period <= 0:
            raise Exception('fgpio period must be greater than 0.')

        if duty_cycle > period:
            raise Exception('fgpio duty cycle must be less than period.')

        # set pin to alternate function.
        self._gpio_direction(pin, 2)

        # Error if pin is already exported.
        try:
            self._pwm_writer(self._sys_pwm_export, self.board.pins[pin]['f2num'])
        except:
            pass

        self._pwm_period(pin, period)
        self._pwm_duty_cycle(pin, duty_cycle)

    def pwm_close(self, pin):
        """ Close PWM pin

        Arguments:
        pin:Int             Pin number of TOUTx on board connector.
        """
        if self.board.pins[pin]['used'] is not False:
            self.board.pins[pin]['used'] = False
            self._pwm_writer(self._sys_pwm_unexport, self.board.pins[pin]['f2num'])

    def pwm_period(self, pin, period):
        """ Set the PWM period in nanoseconds.

        Arguments:
            pin:Int         Pin number of TOUTx on board connector.
            period:Int      Period time in ns.
        """
        self._pin_check(pin, self._type_pwm)
        self._int_check(period, 'period')
        path = self._sys_pwm_period % self.board.pins[pin]['f2num']
        self._pwm_writer(path, period)

    def pwm_duty_cycle(self, pin, duty_cycle):
        """ Set the PWM duty cycle in nanoseconds.

        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
            duty_cycle:Int      Duty Cycle in ns.
        """
        self._pin_check(pin, self._type_pwm)
        self._int_check(duty_cycle, 'duty cycle')
        path = self._sys_pwm_duty_cycle % self.board.pins[pin]['f2num']
        self._pwm_writer(path, duty_cycle)

    def pwm_start(self, pin):
        """ Start the PWM timer

        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
        """
        self._pin_check(pin, self._type_pwm)
        self._pwm_enable(pin, 1)

    def pwm_stop(self, pin):
        """ Stop the PWM timer

        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
        """
        self._pin_check(pin, self._type_pwm)
        self._pwm_enable(pin, 0)

    def _int_check(self, num, msg='argument'):
        if not isinstance(num, int):
            raise Exception('fgpio %s is not an integer. (%s)' % (msg.capitalize(), num))

    def _pin_available(self, pin):
        self._int_check(pin, 'pin')

        if pin not in self.board.pins:
            raise ValueError('fpgio pin number: %s out of range.' % pin)

        if self.board.pins[pin]['used'] != False:
            raise Exception('fgpio pin %s already in use as %s.' % (pin, self.board.pins[pin]['used']))

    def _pin_check(self, pin, ptype):
        self._int_check(pin, 'pin')

        if pin not in self.board.pins:
            raise ValueError('fpgio pin number: %s out of range.' % pin)

        if self.board.pins[pin]['used'] == False:
            raise Exception('fgpio pin %s not initialized as %s.' % (pin, ptype))

        if self.board.pins[pin]['used'] != ptype:
            raise Exception('fgpio pin %s already in use as %s.' % (pin, self.board.pins[pin]['used']))

    def _gpio_read(self, pin):
        self._gpio_seek_addr(pin, self.board.GPIO_DATA_OFFSET)
        data = self._gpio_mem_read()
        return 0x01 & (data >> self.board.pins[pin]['num'])

    def _gpio_write(self, pin, value):
        self._gpio_seek_addr(pin, self.board.GPIO_DATA_OFFSET)
        self._gpio_mem_write(pin, value)

    def _gpio_direction(self, pin, direction):
        self._gpio_seek_addr(pin, self.board.GPIO_CON_OFFSET)
        self._gpio_mem_write2(pin, direction)

    def _gpio_updown(self, pin, updown):
        self._gpio_seek_addr(pin, self.board.GPIO_UPD_OFFSET)
        self._gpio_mem_write2(pin, updown)

    def _gpio_seek_addr(self, pin, offset_bank):
        bank = self.board.pins[pin]['bank']
        self.mm.seek(self._base_addr_offset + self.board.banks[bank] + offset_bank)

    def _gpio_mem_write(self, pin, value):
        pin_num = self.board.pins[pin]['num']
        data = self._gpio_mem_read()
        data = (data & ~(1 << (pin_num))) | ((value & 1) << (pin_num))
        self.mm.write(struct.pack('I', data))

    def _gpio_mem_write2(self, pin, value):
        pin_num = self.board.pins[pin]['num']
        data = self._gpio_mem_read()
        data = (data & ~(3 << (pin_num * 2))) | ((value & 3) << (pin_num * 2))
        self.mm.write(struct.pack('I', data))

    def _gpio_mem_read(self):
        ret = struct.unpack('I',  self.mm.read(4))[0]
        self.mm.seek(self.mm.tell()-4)
        return ret

    def _pwm_period(self, pin, period):
        path = self._sys_pwm_period % self.board.pins[pin]['f2num']

        if not os.path.exists(path):
            raise Exception('fgpio PWM pin %s period path does not exist.' % pin)

        self._pwm_writer(path, period)

    def _pwm_duty_cycle(self, pin, duty_cycle):
        path = self._sys_pwm_duty_cycle % self.board.pins[pin]['f2num']

        if not os.path.exists(path):
            raise Exception('fgpio PWM pin %s duty cycle path does not exist.' % pin)

        self._pwm_writer(path, duty_cycle)

    def _pwm_enable(self, pin, onoff):
        path = self._sys_pwm_enable % self.board.pins[pin]['f2num']

        if not os.path.exists(path):
            raise Exception('fgpio PWM pin %s enable path does not exist.' % pin)

        self._pwm_writer(path, onoff)

    def _pwm_writer(self, path, value):
        if not os.path.exists(path):
            raise Exception('fgpio PWM sys file does not exist. %s' % path)

        with open(path, 'w') as f:
            f.write('%s' % value)

