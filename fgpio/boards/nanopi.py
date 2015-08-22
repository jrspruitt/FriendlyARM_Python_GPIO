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
        self.GPIO_OFFSET       =  0x56000000
        self.GPIO_LENGTH       =  0x100
        self.GPIO_CON_OFFSET   =  0x00
        self.GPIO_DATA_OFFSET  =  0x04
        self.GPIO_UPD_OFFSET   =  0x08
        self.GPIO_SEL_OFFSET   =  0x0C
        self.PWMCHIP_ID        =  '0'

        self.pins = {7:{'bank':'GPF', 'num': 1, 'f2type':'int', 'f2num': 1 },    # EINT1/GPF1   (7)  161,
                    11:{'bank':'GPF', 'num': 2, 'f2type':'int', 'f2num': 2 },    # EINT2/GPF2   (11) 162,
                    12:{'bank':'GPF', 'num': 3, 'f2type':'int', 'f2num': 3 },    # EINT3/GPF3   (12) 163
                    13:{'bank':'GPF', 'num': 4, 'f2type':'int', 'f2num': 4 },    # EINT4/GPF4   (13) 164
                    15:{'bank':'GPF', 'num': 5, 'f2type':'int', 'f2num': 5 },    # EINT5/GPF5   (15) 165
                    16:{'bank':'GPB', 'num': 2, 'f2type': None, 'f2num': 2 },    # TOUT2/GPB2   (16) 34
                    18:{'bank':'GPG', 'num': 1, 'f2type':'int', 'f2num': 9 },    # EINT9/GPG1   (18) 193
                    22:{'bank':'GPB', 'num': 0, 'f2type':'pwm', 'f2num': 0 },    # TOUT0/GPB0   (22) 32
                    24:{'bank':'GPL', 'num':13, 'f2type': None, 'f2num': 0 },    # SS0/GPL13    (24) 333
                    26:{'bank':'GPB', 'num': 1, 'f2type':'pwm', 'f2num': 1 },    # TOUT1/GPB1   (26) 33
                    27:{'bank':'GPB', 'num': 7, 'f2type': None, 'f2num': 1 },    # SDA1/GPB7    (27) 39
                    28:{'bank':'GPB', 'num': 8, 'f2type': None, 'f2num': 1 },    # SCL1/GPB8    (28) 40
                    29:{'bank':'GPG', 'num': 3, 'f2type':'int', 'f2num': 11},    # EINT11/GPG3  (29) 195
                    31:{'bank':'GPG', 'num': 4, 'f2type':'int', 'f2num': 12},    # EINT12/GPG4  (31) 196
                    32:{'bank':'GPG', 'num': 5, 'f2type':'int', 'f2num': 13},    # EINT13/GPG5  (32) 197
                    33:{'bank':'GPG', 'num': 6, 'f2type':'int', 'f2num': 14},    # EINT14/GPG6  (33) 198
                    35:{'bank':'GPG', 'num': 7, 'f2type':'int', 'f2num': 15},    # EINT15/GPG7  (35) 199
                    36:{'bank':'GPG', 'num': 8, 'f2type':'int', 'f2num': 16},    # EINT16/GPG8  (36) 200
                    37:{'bank':'GPG', 'num': 9, 'f2type':'int', 'f2num': 17},    # EINT17/GPG9  (37) 201
                    38:{'bank':'GPG', 'num':10, 'f2type':'int', 'f2num': 18},    # EINT18/GPG10 (38) 202
                    40:{'bank':'GPG', 'num':11, 'f2type':'int', 'f2num': 19}     # EINT19/GPG11 (40) 203
                    }

        self.banks = {'GPB':0x10,
                'GPF':0x50,
                'GPG':0x60,
                'GPL':0xf0}
