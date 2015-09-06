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

class Config(object):
    def __init__(self):
        self.MEM_OFFSET             =  0x56000000
        self.MEM_LENGTH             =  0x100
        self.GPIO_CON_OFFSET        =  0x00
        self.GPIO_DATA_OFFSET       =  0x04
        self.GPIO_UPD_OFFSET        =  0x08
        self.GPIO_SEL_OFFSET        =  0x0C
        self.UPDN_UP                =  1
        self.UPDN_DOWN              =  0
        self.UPDN_NONE              =  2
        self.FUNC_IN                =  0
        self.FUNC_OUT               =  1
        self.FUNC_EINT              =  2
        self.FUNC_PWM               =  2
        self.FUNC_RESET             =  0
        self.DATA_RESET             =  0
        self.UPDN_RESET             =  1

        self.EINT_CONT_OFFSET       =  0x88
        self.EINT_CONT_LENGTH       =  0x60
        self.EINT_EN_OFFSET         =  0xA4
        self.EINT_PEND_OFFSET       =  0xA8
        self.EINT_LOW               =  0x00
        self.EINT_HIGH              =  0x01
        self.EINT_FALL              =  0x02
        self.EINT_RISE              =  0x04
        self.EINT_BOTH              =  0x07
        self.EINT_RESET             =  0

        self.PWMCHIP_ID             =  0

        self.pins = {7:{'bank':'GPF', 'gpio':{'num': 1 }},                         # EINT1/GPF1   (7)  161,
                    11:{'bank':'GPF', 'gpio':{'num': 2 }},                         # EINT2/GPF2   (11) 162,
                    12:{'bank':'GPF', 'gpio':{'num': 3 }},                         # EINT3/GPF3   (12) 163
                    13:{'bank':'GPF', 'gpio':{'num': 4 }, 'eint': {'num': 4 }},    # EINT4/GPF4   (13) 164
                    15:{'bank':'GPF', 'gpio':{'num': 5 }, 'eint': {'num': 5 }},    # EINT5/GPF5   (15) 165
                    16:{'bank':'GPB', 'gpio':{'num': 2 }},                         # TOUT2/GPB2   (16) 34
                    18:{'bank':'GPG', 'gpio':{'num': 1 }, 'eint': {'num': 9 }},    # EINT9/GPG1   (18) 193
                    22:{'bank':'GPB', 'gpio':{'num': 0 }, 'pwm':  {'num': 0 }},    # TOUT0/GPB0   (22) 32
                    24:{'bank':'GPL', 'gpio':{'num': 13}},                         # SS0/GPL13    (24) 333
                    26:{'bank':'GPB', 'gpio':{'num': 1 }, 'pwm':  {'num': 1 }},    # TOUT1/GPB1   (26) 33
                    27:{'bank':'GPB', 'gpio':{'num': 7 }},                         # SDA1/GPB7    (27) 39
                    28:{'bank':'GPB', 'gpio':{'num': 8 }},                         # SCL1/GPB8    (28) 40
                    29:{'bank':'GPG', 'gpio':{'num': 3 }, 'eint': {'num': 11}},    # EINT11/GPG3  (29) 195
                    31:{'bank':'GPG', 'gpio':{'num': 4 }, 'eint': {'num': 12}},    # EINT12/GPG4  (31) 196
                    32:{'bank':'GPG', 'gpio':{'num': 5 }, 'eint': {'num': 13}},    # EINT13/GPG5  (32) 197
                    33:{'bank':'GPG', 'gpio':{'num': 6 }, 'eint': {'num': 14}},    # EINT14/GPG6  (33) 198
                    35:{'bank':'GPG', 'gpio':{'num': 7 }, 'eint': {'num': 15}},    # EINT15/GPG7  (35) 199
                    36:{'bank':'GPG', 'gpio':{'num': 8 }, 'eint': {'num': 16}},    # EINT16/GPG8  (36) 200
                    37:{'bank':'GPG', 'gpio':{'num': 9 }, 'eint': {'num': 17}},    # EINT17/GPG9  (37) 201
                    38:{'bank':'GPG', 'gpio':{'num': 10}, 'eint': {'num': 18}},    # EINT18/GPG10 (38) 202
                    40:{'bank':'GPG', 'gpio':{'num': 11}, 'eint': {'num': 19}}     # EINT19/GPG11 (40) 203
                    }

        self.banks = {'GPB':0x10,
                'GPF':0x50,
                'GPG':0x60,
                'GPL':0xf0}
