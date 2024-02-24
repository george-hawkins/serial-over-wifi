import select
import sys

import micropython
from machine import UART
from micropython import const

BAUD_RATE = 230400

BUFFER_SIZE = const(2048)


def run():
    buffer = memoryview(bytearray(BUFFER_SIZE))

    uart0 = UART(0, baudrate=BAUD_RATE)
    uart_input = sys.stdin.buffer
    uart_output = sys.stdout.buffer

    # Disable keyboard interrupt on receiving a 0x03 (ctrl-C) byte.
    micropython.kbd_intr(-1)

    poller = select.poll()
    poller.register(uart_input, select.POLLIN)

    end_count = BAUD_RATE
    count = 0

    failure = None

    try:
        read = uart_input.readinto
        write = uart_output.write
        while count < end_count:
            offset = 0
            # Reading bytes into a larger buffer first didn't improve performance.
            for _, event in poller.ipoll():
                next_offset = offset + 1
                read(buffer[offset:next_offset])
                count += 1
                offset = next_offset
                if offset == BUFFER_SIZE:
                    break
            write(buffer[0:offset])
    except Exception as e:
        failure = e

    micropython.kbd_intr(3)
    uart0.init(baudrate=115200)


run()
