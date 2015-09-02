
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
import math
import mmap
import struct
from time import sleep

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
        self._type_eint = 'eint'


        self.board = board

        for pin in self.board.pins:
            self.board.pins[pin]['used'] = False

        self._mm = None
        self._pwm_mm = None
        self._mem_base_addr = (self.board.MEM_OFFSET & ~(mmap.PAGESIZE-1))
        self._mem_base_addr_offset = self.board.MEM_OFFSET - self._mem_base_addr

        self._pwm_mem_base_addr = (self.board.PWM_OFFSET & ~(mmap.PAGESIZE-1))
        self._pwm_mem_base_addr_offset = self.board.PWM_OFFSET - self._pwm_mem_base_addr

    def gpio_init(self, pin, direction='in', updown='none'):
        """ Initialize a pin for GPIO use.

        Arguments:
            pin:Int             Pin number GPxN on board connector.
            direction:Str       Input or output, 'in' or 'out'
            updown:Str          Pullup/down, 'up', 'down', or 'none'
        """

        self._pin_available(pin, self._type_gpio)

        if self._mm == None:
            self._mem_open()

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
        self._mem_close()

    def gpio_close_all(self):
        """ Close all GPIO pins."""

        for pin in self.board.pins:
            self._gpio_close(pin)

        self._mem_close()

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

    def eint_init(self, pin, trigger, func=None):
        """ Configure interrupt pin.

        Arguments:
            pin:Int         Pin number of board connector.
            trigger:Str     Trigger low, high, rising, falling, or both
            func:func       Callback function.
        """
        self._pin_available(pin, self._type_eint)

        if self._mm == None:
            self._mem_open()

        self._gpio_function(pin, self.board.FUNC_EINT)

        if trigger not in ['low', 'high', 'rising', 'falling', 'none', 'both']:
            self._value_error('Trigger must be low,  high, rising, falling, none, or both.')

        self._eint_trigger(pin, trigger)
        self._eint_clear_event(pin)
        self.board.pins[pin]['used'] = self._type_eint

    def eint_close(self, pin):
        """Close interrupt pin.

        Arguments:
            Pin:Int     Pint number of the board connector.
        """
        self._pin_check(pin, self._type_eint)
        self._eint_close(pin)
        self._mem_close()

    def eint_close_all(self):
        """ Close all EINT pins."""

        for pin in self.board.pins:
            self._eint_close(pin)

        self._mem_close()

    def eint_event(self, pin):
        """Poll for event trigger.

        Returns:Int 0 for False 1 for True.
        """
        self._pin_check(pin, self._type_eint)
        return self._eint_get_event(pin)

    def eint_clear(self, pin):
        """Clear triggered event."""
        self._pin_check(pin, self._type_eint)
        self._eint_clear_event(pin)

    def pwm_init(self, pin, period, duty_cycle):
        """ Initialize a pin for PWM use.
            This will have an unknown amount of error as it tries
            to guess the values to use to get close to this period
            and duty cycle. Use direct access functions if higher
            precision is needed. Observed error of a few uS.
            
        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
            period:Int          Period time in ns.
            duty_cycle:Int      Duty cycle in ns.
        """

        self._pin_available(pin, self._type_pwm)

        if self._mm == None:
            self._mem_open()

        if self._pwm_mm == None:
            self._pwm_mem_open()

        self._gpio_function(pin, self.board.FUNC_PWM)
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

    def pwm_get_period(self, pin):
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

        Returns:Int         Error in ns
        """

        self._pin_check(pin, self._type_pwm)
        return self._pwm_period(pin, period)

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
        self._pwm_enable(pin)

    def pwm_stop(self, pin):
        """ Stop the PWM timer

        Arguments:
            pin:Int             Pin number of TOUTx on board connector.
        """

        self._pin_check(pin, self._type_pwm)
        self._pwm_disable(pin)

    def pwm_counter(self, pin, value):
        """Direct access to counter TCNTBn register."""
        self._pwm_counter(pin, value)

    def pwm_compare(self, pin, value):
        """Direct access to compare TCMPBn register."""
        self._pwm_compare(pin, value)

    def pwm_prescaler(pin, value):
        """Direct access to prescaler TCFG0 register."""
        self._pwm_prescaler(pin, value)

    def pwm_divider(pin, value):
        """Direct access to divider TCFG1 register."""
        self._pwm_divider(pin, value)

    def pwm_tcon(pin, value):
        """Direct access to TCON register."""
        self._pwm_tcon(pin, value)

    def _exception(self, msg):
        raise Exception('fgpio: %s' % msg)

    def _value_error(self, msg):
        raise ValueError('fgpio: %s' % msg)

    def _int_check(self, num, msg='argument'):
        if not isinstance(num, int):
            self._value_error('%s is not an integer. (%s)' % (msg.capitalize(), num))

        if not num >= 0:
            self._value_error('%s is not greater than 0.')

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
        if self.board.pins[pin]['used'] in [self._type_gpio, self._type_eint]:
            self._gpio_write(pin, self.board.DATA_RESET)
            self._gpio_function(pin, self.board.FUNC_RESET)
            self._gpio_updn(pin, self.board.UPDN_RESET)
            self.board.pins[pin]['used'] = False

    def _gpio_read(self, pin):
        self._gpio_mem_seek_addr(pin, self.board.GPIO_DATA_OFFSET)
        data = self._mem_read()
        return 0x01 & (data >> self.board.pins[pin][self._type_gpio]['num'])

    def _gpio_write(self, pin, value):
        if value:
            value = 1
        else:
            value =  0

        self._gpio_mem_seek_addr(pin, self.board.GPIO_DATA_OFFSET)
        self._gpio_mem_write(pin, value)

    def _gpio_direction(self, pin, direction):
        direction = direction.lower()
        if direction == 'out':
            func_num = self.board.FUNC_OUT
        elif direction == 'in':
            func_num = self.board.FUNC_IN
        else:
            self._value_error('Bad GPIO func: %s' % direction)

        self._gpio_function(pin, func_num)

    def _gpio_function(self, pin, func):
        self._gpio_mem_seek_addr(pin, self.board.GPIO_CON_OFFSET)
        self._gpio_mem_write2(pin, func)

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
        self._gpio_mem_seek_addr(pin, self.board.GPIO_UPD_OFFSET)
        self._gpio_mem_write2(pin, updn)

    def _gpio_mem_seek_addr(self, pin, offset_bank):
        bank = self.board.pins[pin]['bank']
        self._mm.seek(self._mem_base_addr_offset + self.board.banks[bank] + offset_bank)

    def _gpio_mem_write(self, pin, value):
        pin_num = self.board.pins[pin][self._type_gpio]['num']
        data = self._mem_read()
        data = (data & ~(1 << (pin_num))) | ((value & 1) << (pin_num))
        self._mem_write(data)

    def _gpio_mem_write2(self, pin, value):
        pin_num = self.board.pins[pin][self._type_gpio]['num']
        data = self._mem_read()
        data = (data & ~(3 << (pin_num * 2))) | ((value & 3) << (pin_num * 2))
        self._mem_write(data)

    def _eint_close(self, pin):
        self._eint_control(pin, self.board.EINT_RESET)
        self._gpio_close(pin)

    def _eint_trigger(self, pin, trigger):
        if trigger == 'low':
            trig_num = self.board.EINT_LOW
        elif trigger == 'high':
            trig_num = self.board.EINT_HIGH
        elif trigger == 'rising':
            trig_num = self.board.EINT_RISE
        elif trigger == 'falling':
            trig_num = self.board.EINT_FALL
        elif trigger == 'both':
            trig_num = self.board.EINT_BOTH
        else:
            self._value_error('Trigger must be low, high, rising, falling, or both.')

        self._eint_control(pin, trig_num)

    def _eint_control(self, pin, value):
        pin_num = self.board.pins[pin][self._type_eint]['num']
        self._eint_mem_seek_addr(self.board.EINT_CONT_OFFSET + (((pin_num * 4) / 32))*4)
        data = self._mem_read()
        pin_offset = ((pin_num * 4) % 32)
        data = (data & ~(7 << pin_offset)) | ((value & 7) << pin_offset)
        self._mem_write(data)

    def _eint_get_event(self, pin):
        self._eint_mem_seek_addr(self.board.EINT_PEND_OFFSET)
        data = self._mem_read()
        return 0x01 & (data >> self.board.pins[pin][self._type_eint]['num'])

    def _eint_clear_event(self, pin):
        self._eint_mem_seek_addr(self.board.EINT_PEND_OFFSET)
        data = self._mem_read()
        pin_num = self.board.pins[pin][self._type_eint]['num'] 
        data = (data & ~(1 << pin_num)) | (1 << pin_num)
        self._mem_write(data)

    def _eint_mem_seek_addr(self, offset):
        self._mm.seek(self._mem_base_addr_offset + offset)

    def _mem_open(self):
        f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
        self._mm = mmap.mmap(f, self.board.MEM_LENGTH,
                            mmap.MAP_SHARED,
                            mmap.PROT_READ | mmap.PROT_WRITE,
                            offset=self._mem_base_addr)

    def _mem_close(self):
        for pin in self.board.pins:
            if self.board.pins[pin]['used'] is not False:
                break
        else:
            self._mm.close()
            self._mm = None

    def _mem_read(self):
        ret = struct.unpack('I',  self._mm.read(4))[0]
        self._mm.seek(self._mm.tell()-4)
        return ret

    def _mem_write(self, data):
        self._mm.write(struct.pack('I', data))

    def _pwm_close(self, pin):
        if self.board.pins[pin]['used'] in [self._type_pwm]:
            self._pwm_disable(pin)
            self._pwm_divider(pin, self.board.PWM_TCFG_RESET)
            self._pwm_tcon(pin, self.board.PWM_TCON_RESET)
            self._pwm_compare(pin, self.board.PWM_BUFF_RESET)
            self._pwm_counter(pin, self.board.PWM_BUFF_RESET)
            self._gpio_function(pin, self.board.FUNC_RESET)
            self.board.pins[pin]['used'] = False

            for pin in self.board.pins:
                if self.board.pins[pin]['used'] == self._type_pwm:
                    break
            else:
                self._mem_close()
                self._pwm_prescaler(pin, self.board.PWM_TCFG_RESET)
                self._pwm_mm.close()
                self._pwm_mm = None

    def _pwm_enable(self, pin):
        self._pwm_tcon(pin, 10)
        self._pwm_tcon(pin, 9)

    def _pwm_disable(self, pin):
        self._pwm_tcon(pin, 0)

    def _pwm_period(self, pin, period_ns):
        div_idx = len(self.board.PWM_DIVIDERS)-1
        pre_cnt = 255

        clk_s_max = 1 / (float(self.board.PWM_CLK) / 256 / self.board.PWM_DIVIDERS[len(self.board.PWM_DIVIDERS)-1])
        clk_ns_max = (clk_s_max * 65535) * 1000000000.0
        clk_s_min = 1 / (float(self.board.PWM_CLK) / self.board.PWM_DIVIDERS[0])
        clk_ns_min = clk_s_min * 1000000000.0

        if clk_ns_max < period_ns or clk_ns_min > period_ns:
            self._value_error('Period out of range. max %sns min %sns' % (int(clk_ns_max), int(math.ceil(clk_ns_min))))

        best = {'diff':65535, 'counter':None, 'prescaler':None, 'divider':None}

        while pre_cnt >= 0:
            clk_s_max = 1 / (float(self.board.PWM_CLK) / (pre_cnt + 1) / self.board.PWM_DIVIDERS[div_idx])
            clk_ns_max = (clk_s_max * 65535) * 1000000000.0
            clk_s_min = 1 / (float(self.board.PWM_CLK) / (pre_cnt + 1) / self.board.PWM_DIVIDERS[div_idx])
            clk_ns_min = clk_s_min * 1000000000.0

            if period_ns <= clk_ns_max and period_ns >= clk_ns_min:
                counter_fl =  (period_ns / clk_ns_max ) * 65535
                counter = int(round(counter_fl))
                diff = abs(counter - counter_fl)

                if diff < best['diff']:
                    best['diff'] = diff
                    best['counter'] = counter
                    best['prescaler'] = pre_cnt
                    best['divider'] = div_idx
 
            pre_cnt -= 1

            if pre_cnt < 0 and div_idx > 0:
                pre_cnt = 255
                div_idx -= 1

        if best['counter'] is None:
            self._value_error('Period configuration could not be determined.')

        self._pwm_counter(pin, best['counter'])
        self._pwm_prescaler(pin, best['prescaler'])
        self._pwm_divider(pin, best['divider'])

        clk_s_err = 1 / (float(self.board.PWM_CLK) / (best['prescaler'] + 1) / self.board.PWM_DIVIDERS[best['divider']])
        return ((clk_s_err * best['counter']) * 1000000000.0) - period_ns


    def _pwm_get_period(self, pin):
        counter = self._pwm_get_counter(pin)
        return int(round(self._pwm_freq_seconds(pin) * counter * 1000000000))

    def _pwm_duty_cycle(self, pin, duty_cycle_ns):
        counter = self._pwm_get_counter(pin)
        freq_s = self._pwm_freq_seconds(pin)
        freq_ns = freq_s * 1000000000.0
        period_ns = counter * freq_s * 1000000000.0
        compare = int(round(duty_cycle_ns / freq_ns))

        if period_ns < duty_cycle_ns:
            self._value_error('Duty cycle must be shorter than period.')

        self._pwm_compare(pin, compare)

        return ((compare * freq_s) * 1000000000) - duty_cycle_ns

    def _pwm_get_duty_cycle(self, pin):
        compare = self._pwm_get_compare(pin)
        return int(round(self._pwm_freq_seconds(pin) * compare * 1000000000))

    def _pwm_freq_seconds(self, pin):
        prescaler = self._pwm_get_prescaler(pin)
        divider = self._pwm_get_divider(pin)

        for d in self.board.PWM_DIVIDERS:
            if self.board.PWM_DIVIDERS.index(d) == divider:
                divider = d
                break

        return 1 / round(self.board.PWM_CLK / (prescaler + 1) / divider)

    def _pwm_counter(self, pin, counter):
        pin_num = self.board.pins[pin][self._type_pwm]['num']
        offset = self.board.PWM_BUFFER_OFFSET + (pin_num * self.board.PWM_BUFFER_LENGTH)
        self._pwm_mem_seek_addr(offset)
        data = self._pwm_mem_read()
        data = (data & ~(0xFFFF)) | (counter & 0xFFFF)
        self._pwm_mem_write(data)

    def _pwm_get_counter(self, pin):
        pin_num = self.board.pins[pin][self._type_pwm]['num']
        offset = self.board.PWM_BUFFER_OFFSET + (pin_num * self.board.PWM_BUFFER_LENGTH)
        self._pwm_mem_seek_addr(offset)
        data = self._pwm_mem_read()
        return 0xFFFF & data

    def _pwm_compare(self, pin, compare):
        pin_num = self.board.pins[pin][self._type_pwm]['num']
        offset = self.board.PWM_BUFFER_OFFSET + (pin_num * self.board.PWM_BUFFER_LENGTH)
        self._pwm_mem_seek_addr(offset + 4)
        data = self._pwm_mem_read()
        data = (data & ~(0xFFFF)) | (compare & 0xFFFF)
        self._pwm_mem_write(data)

    def _pwm_get_compare(self, pin):
        pin_num = self.board.pins[pin][self._type_pwm]['num']
        offset = self.board.PWM_BUFFER_OFFSET + (pin_num * self.board.PWM_BUFFER_LENGTH)
        self._pwm_mem_seek_addr(offset + 4)
        data = self._pwm_mem_read()
        return 0xFFFF & data

    def _pwm_prescaler(self, pin, value):
        pin_offset = (self.board.pins[pin][self._type_pwm]['num'] / 2)
        self._pwm_mem_seek_addr(self.board.PWM_TCFG0_OFFSET)
        data = self._pwm_mem_read()
        data = (data & ~0xFF) | (value & 0xFF)
        self._pwm_mem_write(data)

    def _pwm_get_prescaler(self, pin):
        pin_offset = (self.board.pins[pin][self._type_pwm]['num'] / 2)
        self._pwm_mem_seek_addr(self.board.PWM_TCFG0_OFFSET)
        data = self._pwm_mem_read()
        return 0xFF & data

    def _pwm_divider(self, pin, value):
        pin_num = self.board.pins[pin][self._type_pwm]['num']
        self._pwm_mem_seek_addr(self.board.PWM_TCFG1_OFFSET)
        data = self._pwm_mem_read()
        data = (data & ~(0x0F << (pin_num * 4))) | ((value & 0x0F) << (pin_num * 4))
        self._pwm_mem_write(data)

    def _pwm_get_divider(self, pin):
        pin_num = self.board.pins[pin][self._type_pwm]['num']
        self._pwm_mem_seek_addr(self.board.PWM_TCFG1_OFFSET)
        data = self._pwm_mem_read()
        return 0x0F & (data >> (pin_num * 4))

    def _pwm_tcon(self, pin, value):
        pin_num = self.board.pins[pin][self._type_pwm]['num']
        self._pwm_mem_seek_addr(self.board.PWM_TCON_OFFSET)
        data = self._pwm_mem_read()
        data = (data & ~(0x0F << (pin_num * 8))) | ((value & 0x0F) << (pin_num * 8))
        self._pwm_mem_write(data)


    def _pwm_mem_open(self):
        f = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
        self._pwm_mm = mmap.mmap(f, self.board.PWM_LENGTH,
                            mmap.MAP_SHARED,
                            mmap.PROT_READ | mmap.PROT_WRITE,
                            offset=self._pwm_mem_base_addr)

    def _pwm_mem_seek_addr(self, offset):
        self._pwm_mm.seek(self._pwm_mem_base_addr_offset + offset)

    def _pwm_mem_read(self):
        ret = struct.unpack('I',  self._pwm_mm.read(4))[0]
        self._pwm_mm.seek(self._pwm_mm.tell()-4)
        return ret

    def _pwm_mem_write(self, data):
        self._pwm_mm.write(struct.pack('I', data))
