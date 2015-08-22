#PyFA_GPIO#

###Work in progress, interface may change###

Simple Python based interface for GPIO pins on FriendlyARM boards.

**Limitations:**

* 1kHz seems about the max toggle speed on 400 MHz s3c2451.
* Reaction time fluctuates due to Linux scheduling.

##Install##
You can use the package directly in your project or,

If your system has Python and setuptools, you can use

     python setup.py install

##Functions##
###GPIO###
all pins listed in board config are gpio capable.

* **fgpio.GPIO(Config())**
     * Main gpio class, init with board Config()
* **fgpio.boards.*.Config()**
     * Board specific configuration
* **gpio_init(pin, direction, updown)**
     * Initialize pin to use, corrisponds to pinout on GPIO header on board.
     * **pin:** Pin number.
     * **direction:** Input(0) or Output(1).
     * **updown:** Pull Up(2) Down(1) Neither(0), Always 0 for outputs.
* **gpio_write(pin, value)**
     * Write value to pin.
     * **pin:** Pin number.
     * **value:** Value 1 (high) 0 (low)
* **gpio_read(pin)**
     * Read pin value, returns Int 1 (high), 0 (low).
     * **pin:** Pin number.
* **gpio_direction(pin, direction)**
     * Set direction of pin.
     * **pin:** Pin number.
     * **direction:** Input(0) or Output(1).
* **gpio_updown(pin, updown)**
     * Set pull up or pull down on pin (Don't use with pin as output).
     * **pin:** Pin number.
     * **updown:** Pull Up(2) Down(1) Neither(0), Always use 0 for outputs.

###PWM###
board config will show 'pwm' as f2type for pin.

*  **pwm_init(pin, period, duty_cycle)**
     * Initialize pin as PWM.
     * **pin:** Pin number.
     * **period:** Period in nanoseconds.
     * **duty_cycle:** Duty cycel in nanoseconds.
*  **pwm_close(pin)**
     * Close pin, clean up sys/ exports.
     * **pin:** Pin number.
*  **pwm_period(pin, period)**
     * Set period of pin.
     * **pin:** Pin number.
     * **period:** Period in nanoseconds.
*  **pwm_duty_cycle(pin, duty_cycle)**
     * Set duty cycle of pin.
     * **pin:** Pin number.
     * **duty_cycle:** Duty cycel in nanoseconds.
*  **pwm_start(pin)**
     * Start PWM output on pin.
     * **pin:** Pin number.
*  **pwm_stop(pin)**
     * Stop PWM output on pin.
     * **pin:** Pin number.

##Example Code##
Sample script toggles pin 40 until pin 38 is pulled low and then exits.

        from fgpio import GPIO
        from fgpio.boards.nanopi import Config
        from time import sleep
        
        # Initialize GPIO
        gpio = GPIO(Config())
        
        # Initialize pin 40 as output (1).
        gpio.gpio_init(40, 1)
        
        # Initialize pin 38 as input (0) with pullup (2)
        gpio.gpio_init(38, 0, 2)
        
        # While pin 38 is high toggle pin 40.
        value = 1
        while gpio.gpio_read(38) != 0:
            if value:
                value = 0
            else:
                value = 1
            gpio.gpio_write(40, value)
            sleep(.5)

