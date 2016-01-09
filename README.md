#FriendlyARM Python GPIO#

Simple Python based interface for GPIO pins on FriendlyARM boards.

**Limitations:**

* GPIO 1kHz seems about the max toggle speed on 400 MHz s3c2451.
* GPIO reaction time fluctuates due to Linux scheduling.
* PWM period is about 0.015 seconds to 30 nanoseconds
    * Kernel can be patched for other value ranges.

##Install##
You can use the package directly in your project or,

If your system has Python and setuptools, you can use

     python setup.py install

##Functions##
###Init###
* **fgpio.GPIO(Config())**
     * Main gpio class, init with board Config()
     * GPIO, PWM, and EINT functions are all in this class.
* **fgpio.boards.*.Config()**
     * Board specific configuration

###GPIO###
All pins listed in board config are gpio capable.

* **gpio_init(pin, direction, updown)**
     * Initialize pin to use, corrisponds to pinout on GPIO header on board.
     * **pin:** Pin number.
     * **direction:** Input('in') or Output('out').
     * **updown:** Pull Up('up') Down('down') Neither('both'), Always 0 for outputs.
* **gpio_close(pin)**
     * Close GPIO enabled pin and set to chip reset values.
* **gpio_close_all()**
     * Close all GPIO enabled pins and set to chip reset values.
* **gpio_write(pin, value)**
     * Write value to pin.
     * **pin:** Pin number.
     * **value:** Value 1 (high) 0 (low)
* **gpio_read(pin)**
     * Read pin value, returns Int 1 (high), 0 (low).
     * **pin:** Pin number.
     * **Returns:** Int
* **gpio_direction(pin, direction)**
     * Set direction of pin.
     * **pin:** Pin number.
     * **direction:** Input('in') or Output('out').
* **gpio_updown(pin, updown)**
     * Set pull up or pull down on pin (Don't use with pin as output).
     * **pin:** Pin number.
     * **updown:** Pull Up('up') Down('down') Neither('both'), Always 0 for outputs

###PWM###
board config will show 'pwm' in the pin config.

*  **pwm_init(pin, period, duty_cycle)**
     * Initialize pin as PWM.
     * **pin:** Pin number.
     * **period:** Period in nanoseconds.
     * **duty_cycle:** Duty cycle in nanoseconds.
*  **pwm_close(pin)**
     * Close PWM enabled pin, sys/.../unexport.
     * **pin:** Pin number.
*  **pwm_close_all()**
     * Close all PWM enabled pins, sys/.../unexport.
*  **pwm_get_period(pin)**
     * Get period of pin in nanoseconds.
     * **pin:** Pin number.
     * **Returns:** Int
*  **pwm_period(pin, period)**
     * Set period of pin.
     * **period:** Period in nanoseconds.
*  **pwm_get_duty_cycle(pin)**
     * Get duty cycle of pin in nanoseconds.
     * **pin:** Pin number.
     * **Returns:** Int
*  **pwm_duty_cycle(pin, duty_cycle)**
     * Set duty cycle of pin.
     * **pin:** Pin number.
     * **duty_cycle:** Duty cycle in nanoseconds.
*  **pwm_start(pin)**
     * Start PWM output on pin.
     * **pin:** Pin number.
*  **pwm_stop(pin)**
     * Stop PWM output on pin.
     * **pin:** Pin number.

###Interrupts EINT###
Interrupt pins (EINT in config) can have a condition set, high, low, rising, falling or both, which when met on the selected pin eint_event(pin) will return 1 instead of 0. To retrigger run eint_clear(pin). These are best used in a thread.

*  **eint_init(pin, trigger)**
     * Initialize interrupt on pin.
     * **pin:** Pin number.
     * **trigger:** 'low', 'high', 'rising', 'falling', 'none', or 'both'
*  **eint_close(pin)**
     * Close interrupt pin.
     * **pin:** Pin number.
*  **eint_close_all()**
     * Close all EINT pins.
*  **eint_event(self, pin)**
     * Check if event triggered.
     * **pin:** Pin number.
     * **Returns:** Int 1 for triggered 0 for no event.
*  **eint_clear(self, pin)**
     * Clear triggered event
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

