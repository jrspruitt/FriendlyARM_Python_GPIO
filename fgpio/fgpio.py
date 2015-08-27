
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

        Also provides PWM configuration for TOUTx capable pins.
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
        self._type_pwm = 'pwm'
        self._type_int = 'eint'

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

    def gpio_init(self, pin, direction='in', updown='none'):
        """ Initialize a pin for GPIO use.

        Arguments:
            pin:Int             Pin number GPxN on board connector.
            direction:Str       Input or output, 'in' or 'out'
            updown:Str          Pullup/down, 'up', 'down', or 'none'
        """

        self._pin_available(pin, self._type_gpio)
        self._gpio_direction(pin, direction)

        # Safety check
        if direction.lower() == self.board.FUNC_OUT:
            self._gpio_updown(pin, 'none')
        else:
            self._gpio_updown(pin, updown)

        self.board.pins[pin]['used'] = self._type_gpio

    def gpio_close(self, pin):
        """ Close GPIO setting values to chip reset values.

        Arguments:
            pin:Int             Pin number GPxN on board connector.
        """

        self._pin_check(pin, self._type_gpio)
        self._gpio_close(pin)

    def gpio_close_all(self):
        """ Close all GPIO pins."""

        for pin in self.board.pins:
            self._gpio_close(pin)

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
        self._gpio_write(pin, value)

    def gpio_direction(self, pin, direction):
        """ Set direction of pin.

        Arguments:
            pin:Int             Pin number of board connector.
            direction:Str       Input or output, 'in' or 'out'
        """

        self._pin_check(pin, self._type_gpio)
        self._gpio_direction(pin, direction)

    def gpio_updown(self, pin, updown='none'):
        """ Set pull up or down on the pin.

        Arguments:
            pin:Int         Pin number of board connector.
            updown:Str      Pullup/down, 'up', 'down', or 'none'
        """

        self._pin_check(pin, self._type_gpio)
        self._gpio_updown(pin, updown)

    def pwm_init(self, pin, period, duty_cycle):
        """ Initialize a pin for PWM use.

        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
            period:Int          Period time in ns.
            duty_cycle:Int      Duty cycle in ns.
        """

        self._pin_available(pin, self._type_pwm)

        if not os.path.exists(self._sys_pwm_export):
            self._exception('sys PWM path does not exist.')


        # set pin to alternate function.
        self._gpio_function(pin, self.board.FUNC_PWM)

        # Error if pin is already exported.
        try:
            self._pwm_writer(self._sys_pwm_export, self.board.pins[pin][self._type_pwm]['num'])
        except:
            pass

        # clear old value if any.
        self._pwm_duty_cycle(pin, 0)
        self._pwm_period(pin, period)
        self._pwm_duty_cycle(pin, duty_cycle)
        self.board.pins[pin]['used'] = self._type_pwm

    def pwm_close(self, pin):
        """ Close PWM pin

        Arguments:
        pin:Int             Pin number of TOUTx on board connector.
        """

        self._pin_check(pin, self._type_pwm)
        self._pwm_close(pin)

    def pwm_close_all(self):
        """ Close all PWM pins."""

        for pin in self.board.pins:
            self._pwm_close(pin)

    def pwm_get_period(self, pin, period):
        """ Get the PWM period in nanoseconds.

        Returns:Int         Period in nanoseconds.
        """

        self._pin_check(pin, self._type_pwm)
        return self._pwm_get_period(pin)

    def pwm_period(self, pin, period):
        """ Set the PWM period in nanoseconds.

        Arguments:
            pin:Int         Pin number of TOUTx on board connector.
            period:Int      Period time in ns.
        """

        self._pin_check(pin, self._type_pwm)
        self._pwm_period(pin, period)

    def pwm_get_duty_cycle(self, pin):
        """Get duty cycle value.

        Returns:Int     Duty cycle in nanoseconds.
        """

        self._pin_check(pin, self._type_pwm)
        return self._pwm_get_duty_cycle(pin)

    def pwm_duty_cycle(self, pin, duty_cycle):
        """ Set the PWM duty cycle in nanoseconds.

        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
            duty_cycle:Int      Duty Cycle in ns.
        """

        self._pin_check(pin, self._type_pwm)
        self._pwm_duty_cycle(pin, duty_cycle)

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

    def _exception(self, msg):
        raise Exception('fgpio: %s' % msg)

    def _value_error(self, msg):
        raise ValueError('fgpio: %s' % msg)

    def _int_check(self, num, msg='argument'):
        if not isinstance(num, int):
            self._value_error('%s is not an integer. (%s)' % (msg.capitalize(), num))

    def _pin_available(self, pin, ptype):
        if pin not in self.board.pins:
            self._value_error('Not a valid pin number: %s' % pin)

        if ptype not in self.board.pins[pin]:
            self._exception('Bad function type %s for pin %s' % (ptype, pin))

        if self.board.pins[pin]['used'] != False:
            self._exception('pin %s already in use as %s.' % (pin, self.board.pins[pin]['used']))

    def _pin_check(self, pin, ptype):
        if pin not in self.board.pins:
            self._value_error('Not a valid pin number: %s' % pin)

        if self.board.pins[pin]['used'] == False:
            self._exception('pin %s not initialized as %s.' % (pin, ptype))

        if self.board.pins[pin]['used'] != ptype:
            self._exception('pin %s already in use as %s.' % (pin, self.board.pins[pin]['used']))

    def _gpio_close(self, pin):
        if self.board.pins[pin]['used'] == self._type_gpio:
            self._gpio_write(pin, self.board.DATA_RESET)
            self._gpio_function(pin, self.board.FUNC_RESET)
            self._gpio_updn(pin, self.board.UPDN_RESET)
            self.board.pins[pin]['used'] = False

    def _gpio_read(self, pin):
        self._mem_seek_addr(pin, self.board.GPIO_DATA_OFFSET)
        data = self._mem_read()
        return 0x01 & (data >> self.board.pins[pin][self._type_gpio]['num'])

    def _gpio_write(self, pin, value):
        if value:
            value = 1
        else:
            value =  0

        self._mem_seek_addr(pin, self.board.GPIO_DATA_OFFSET)
        self._mem_write(pin, value)

    def _gpio_direction(self, pin, direction):
        direction = direction.lower()
        if direction == 'out':
            func_num = self.board.FUNC_OUT
        elif direction == 'in':
            func_num = self.board.FUNC_IN
        elif direction == 'pwm':
            func_num = self.board.FUNC_PWM
        elif direction == 'eint':
            func_num = self.board.FUNC_EINT
        else:
            self._value_error('Bad GPIO func: %s' % direction)

        self._gpio_function(pin, func_num)

    def _gpio_function(self, pin, func):
        self._mem_seek_addr(pin, self.board.GPIO_CON_OFFSET)
        self._mem_write2(pin, func)

    def _gpio_updown(self, pin, updown):
        updown = updown.lower()
        if updown == 'up':
            updn = self.board.UPDN_UP
        elif updown == 'down':
            updn = self.board.UPDN_DOWN
        elif updown == 'none':
            updn = self.board.UPDN_NONE
        else:
            self._value_error('Bad GPIO updown: %s' % updown)

        self._gpio_updn(pin, updn)

    def _gpio_updn(self, pin, updn):
        self._mem_seek_addr(pin, self.board.GPIO_UPD_OFFSET)
        self._mem_write2(pin, updn)

    def _mem_seek_addr(self, pin, offset_bank):
        bank = self.board.pins[pin]['bank']
        self.mm.seek(self._base_addr_offset + self.board.banks[bank] + offset_bank)

    def _mem_write(self, pin, value):
        pin_num = self.board.pins[pin][self._type_gpio]['num']
        data = self._mem_read()
        data = (data & ~(1 << (pin_num))) | ((value & 1) << (pin_num))
        self.mm.write(struct.pack('I', data))

    def _mem_write2(self, pin, value):
        pin_num = self.board.pins[pin][self._type_gpio]['num']
        data = self._mem_read()
        data = (data & ~(3 << (pin_num * 2))) | ((value & 3) << (pin_num * 2))
        self.mm.write(struct.pack('I', data))

    def _mem_read(self):
        ret = struct.unpack('I',  self.mm.read(4))[0]
        self.mm.seek(self.mm.tell()-4)
        return ret

    def _pwm_close(self, pin):
        if self.board.pins[pin]['used'] == self._type_pwm:
            self.board.pins[pin]['used'] = False

            try:
                self._pwm_duty_cycle(pin, 0)
                self._pwm_enable(pin, 0)
                self._pwm_writer(self._sys_pwm_unexport, self.board.pins[pin][self._type_pwm]['num'])
            except:
                pass

    def _pwm_get_period(self, pin):
        path = self._sys_pwm_period % self.board.pins[pin][self._type_pwm]['num']

        if not os.path.exists(path):
            self._exception('PWM pin %s period path does not exist.' % pin)

        return self._pwm_reader(path)

    def _pwm_period(self, pin, period):
        self._int_check(period, 'period')

        if period <= 0:
            self._value_error('PWM period must be greater than 0.')

        path = self._sys_pwm_period % self.board.pins[pin][self._type_pwm]['num']

        if not os.path.exists(path):
            self._exception('PWM pin %s period path does not exist.' % pin)

        self._pwm_writer(path, period)

    def _pwm_get_duty_cycle(self, pin):
        path = self._sys_pwm_duty_cycle % self.board.pins[pin][self._type_pwm]['num']

        if not os.path.exists(path):
            self._exception('PWM pin %s duty cycle path does not exist.' % pin)

        return self._pwm_reader(path)

    def _pwm_duty_cycle(self, pin, duty_cycle):
        self._int_check(duty_cycle, 'duty cycle')

        if duty_cycle > self._pwm_get_period(pin):
            self._exception('PWM duty cycle must be less than period.')

        path = self._sys_pwm_duty_cycle % self.board.pins[pin][self._type_pwm]['num']

        if not os.path.exists(path):
            self._exception('PWM pin %s duty cycle path does not exist.' % pin)

        self._pwm_writer(path, duty_cycle)

    def _pwm_enable(self, pin, onoff):
        path = self._sys_pwm_enable % self.board.pins[pin][self._type_pwm]['num']

        if not os.path.exists(path):
            self._exception('PWM pin %s enable path does not exist.' % pin)

        self._pwm_writer(path, onoff)

    def _pwm_writer(self, path, value):
        if not os.path.exists(path):
            self._exception('PWM sys file does not exist. %s' % path)

        with open(path, 'w') as f:
            f.write('%s' % value)

    def _pwm_reader(self, path):
        if not os.path.exists(path):
            self._exception('PWM sys file does not exist. %s' % path)

        ret = -1
        with open(path, 'r') as f:
            ret = f.read(32)

        return int(ret)

