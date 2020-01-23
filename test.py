import argparse
import logging
import time
from logging.handlers import RotatingFileHandler

import gpiozero


def main():
    # Parse the User Args
    parser = argparse.ArgumentParser(description='Run and test an actuator connected to a Pi.')
    parser.add_argument('input', metavar='input', type=int, nargs='?', default=5,
                        help='input pin for the home signal (BCM) [default 5]')
    parser.add_argument('output', metavar='output', type=int, nargs='?', default=6,
                        help='output pin for drive (BCM) [default 6]')
    parser.add_argument('wait_time', metavar='wait_time', type=int, nargs='?', default=5,
                        help='number of seconds to wait between iterations [default 5]')
    args = parser.parse_args()

    # Start the Logger
    logger = logging.getLogger('actuator')
    handler = RotatingFileHandler('actuator.log', maxBytes=20000000, backupCount=10)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger.setLevel('INFO')
    logger.addHandler(handler)

    # Set Up
    logger.info("Args: " + str(args))
    output_pin = gpiozero.DigitalOutputDevice(args.output)
    input_pin = gpiozero.DigitalInputDevice(args.input)
    wait = args.wait_time

    iteration = 0
    extended = False
    output_pin.off()
    input_pin.wait_for_active()

    # Test and Log
    end = 0
    start = 0
    while True:
        direction = " -> Extend" if not extended else " -> Home"
        logger.info("Iteration " + str(iteration) + direction)
        if not input_pin.value:  # Should never really happen
            logger.error("Input signal not found! Trying to return to home.")
            output_pin.off()
            time.sleep(0.5)
            input_pin.wait_for_active()
            extended = False
        elif extended:  # Last thing we did was turn output_pin ON
            start = time.time()
            output_pin.off()
            time.sleep(0.5)
            input_pin.wait_for_active()
            end = time.time()
            extended = False
        else:  # Last thing we did was turn output_pin OFF
            start = time.time()
            output_pin.on()
            time.sleep(0.5)
            input_pin.wait_for_active()
            end = time.time()
            extended = True
        logger.info("Elapsed " + str(end - start))
        time.sleep(wait)
        iteration += 1


if __name__ == "__main__":
    main()
