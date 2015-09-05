#FriendlyARM Python GPIO#

###Work in progress###

Simple Python based interface for GPIO pins on FriendlyARM boards.

**Limitations:**

* GPIO 1kHz seems about the max toggle speed on 400 MHz s3c2451.
* GPIO reaction time fluctuates due to Linux scheduling.
* PWM period is about 4 seconds to 31ns

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
     * **direction:** Input(0) or Output(1).
     * **updown:** Pull Up(2) Down(1) Neither(0), Always 0 for outputs.
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
     * **direction:** Input(0) or Output(1).
* **gpio_updown(pin, updown)**
     * Set pull up or pull down on pin (Don't use with pin as output).
     * **pin:** Pin number.
     * **updown:** Pull Up(2) Down(1) Neither(0), Always use 0 for outputs.

###PWM###
Board config will show 'pwm' in pin config section. On NanoPi TOUT0 and TOUT1 share prescaler value.

*  **pwm_init(pin, period, duty_cycle)**
     * Initialize pin as PWM.
     * **pin:** Pin number.
     * **period:** Period in nanoseconds.
     * **duty_cycle:** Duty cycel in nanoseconds.
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
     * This can cause blocking issues with PyQt if used too often.
     * **period:** Period in nanoseconds.
     * **Returns:** Int difference in ns of actual and requested period.
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

###PWM Direct###
These functions are for setting the PWM registers manually, you will need to set _gpio_function(2). For the NanoPi the equation for the Timer clock frequency is 66666666/(prescaler+1)/divider. Prescaler is 0-255 and divider is 2,4,8, or 16, bit values 0, 1, 2, 3 respectively. Know what you are doing warning.

*  **pwm_get_counter(pin)**
     * **Returns:** Int
*  **pwm_counter(pin, value)**
*  **pwm_get_compare(pin)**
     * **Returns:** Int
*  **pwm_compare(pin, value)**
*  **pwm_get_prescaler(pin)**
     * **Returns:** Int
*  **pwm_prescaler(pin, value)**
*  **pwm_get_divider(pin)**
     * **Returns:** Int
*  **pwm_divider(pin, value)**
*  **pwm_get_tcon(pin)**
     * **Returns:** Int
*  **pwm_tcon(pin, value)**

###Interrupts EINT###
Interrupt pins (EINT in config) can have a condition set, high, low, rising, falling or both, which when met on the selected pin eint_event(pin) will return 1 instead of 0. To retrigger run eint_clear(pin). These are best used in a thread.

*  **eint_init(pin, trigger)**
     * Initialize interrupt on pin.
     * **pin:** Pin number.
     * **trigger:** high, low, rising, falling, or both
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

