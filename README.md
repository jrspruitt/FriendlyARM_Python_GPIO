#PyFA_GPIO#

Simple Python based interface for GPIO pins on FriendlyARM boards.

**Limitations:**

* 1kHz seems about the max toggle speed on 400 MHz s3c2451.
* Reaction time fluctuates due to Linux scheduling.

##Install##
You can use the package directly in your project or,

If your system has Python and setuptools, you can use

     _python setup.py install_

##Functions##
* fgpio.GPIO(Config())
    * Main gpio class, init with board Config()
* fgpio.boards.*.Config()
    * Board specific configuration

* fgpio.init_pin(pin, direction, updown)
    * Initialize pin to use, corrisponds to pinout on GPIO header on board.
    * **pin:** Pin number.
    * **direction:** Input(0) or Output(1).
    * **updown:** Pull Up(2) Down(1) Neither(0), Always 0 for outputs.

* fgpio.write(pin, value)
    * Write value to pin.
    * **pin:** Pin number.
    * **value:** Value 1 (high) 0 (low)

* fgpio.read(pin)
    * Read pin value, returns Int 1 (high), 0 (low).
    * **pin:** Pin number.

* fgpio.set_direction(pin, direction)
    * Set direction of pin.
    * **pin:** Pin number.
    * **direction:** Input(0) or Output(1).

* fgpio.set_updown(pin, updown)
    * Set pull up or pull down on pin (Don't use with pin as output).
    * **pin:** Pin number.
    * **updown:** Pull Up(2) Down(1) Neither(0), Always use 0 for outputs.

##Example Code##
Sample script toggles pin 40 until pin 38 is pulled low and then exits.

        from fgpio import GPIO
        from fgpio.boards.nanopi import Config
        from time import sleep

        # Initialize GPIO
        gpio = GPIO(Config())

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

