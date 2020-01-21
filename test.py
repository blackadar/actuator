import argparse
import logging
import time
from logging.handlers import RotatingFileHandler

import gpiozero


def main():
    # Parse the User Args
    parser = argparse.ArgumentParser(description='Run and test an actuator connected to a Pi.')
    parser.add_argument('home_input', metavar='home_input', type=int, nargs='?', default=5,
                        help='input pin for the home signal (BCM) [default 5]')
    parser.add_argument('home_output', metavar='home_output', type=int, nargs='?', default=6,
                        help='output pin for drive to home (BCM) [default 6]')
    parser.add_argument('extend_input', metavar='extend_input', type=int, nargs='?', default=13,
                        help='input pin for the extend signal (BCM) [default 13]')
    parser.add_argument('extend_output', metavar='extend_output', type=int, nargs='?', default=19,
                        help='output pin for drive to extend (BCM) [default 19]')
    parser.add_argument('wait_time', metavar='wait_time', type=int, nargs='?', default=2,
                        help='number of seconds to wait between iterations [default 2]')
    args = parser.parse_args()

    # Start the Logger
    logger = logging.getLogger('actuator')
    handler = RotatingFileHandler('actuator.log', maxBytes=20000000, backupCount=10)
    logger.setLevel('INFO')
    logger.addHandler(handler)

    # Set Up
    home_input = gpiozero.Button(args.home_input)
    home_output = gpiozero.DigitalOutputDevice(args.home_output)
    extend_input = gpiozero.Button(args.extend_input)
    extend_output = gpiozero.DigitalOutputDevice(args.extend_output)
    wait = args.wait_time
    logger.info("Args: " + str(args))

    position = get_position(home_input, extend_input)
    iteration = 0
    logger.info("Initial position: " + position)

    # Test and Log
    while True:
        position = get_position(home_input, extend_input)
        logger.info("Iteration " + str(iteration) + " starts at position " + position + ".")
        if position == "HOME":
            home_output.off()
            extend_output.on()
            extend_input.wait_for_active()
            logger.info("Got to EXTEND successfully.")
        elif position == "EXTEND":
            extend_output.off()
            home_output.on()
            home_input.wait_for_active()
            logger.info("Got to HOME successfully.")
        elif position == "INVALID":
            logger.info("Invalid state, both home and extend detected. Attempting to return to HOME.")
            extend_output.off()
            home_output.on()
            time.sleep(5)
            home_input.wait_for_active()
            logger.info("Got HOME signal.. attempting another iteration to see if things are normal again.")
        else:
            logger.info("Unknown state, attempting return to HOME.")
            extend_output.off()
            home_output.on()
            home_input.wait_for_active()
            logger.info("Got to HOME successfully.")
        time.sleep(wait)
        iteration += 1


def get_position(home_input, extend_input):
    if home_input.value and extend_input.value:  # Both signals
        position = "INVALID"
    elif home_input.value:  # We are already home
        position = "HOME"
    elif extend_input.value:  # We are already extended
        position = "EXTEND"
    else:  # We're somewhere in between
        position = "TRANS"
    return position


if __name__ == "__main__":
    main()
