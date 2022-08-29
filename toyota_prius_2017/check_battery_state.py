#/usr/bin/python3

import argparse
import logging

# Setup the path for the local version of python-OBD
import os
from pathlib import Path
import sys
obd_path = os.path.join(Path(Path(__file__).parent.absolute()).parent.absolute(),\
    "common", "obd", "python-OBD")
sys.path.insert(0, obd_path)

import obd
from obd import OBDStatus
from obd import OBDCommand
from obd.decoders import noop
from obd.protocols import ECU, ECU_HEADER

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Queries the hybrid battery state")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0",\
        help="Name of device to connect to")
    parser.add_argument("--debug", action="store_true", help="Display all logs")
    args = parser.parse_args()

    if args.debug:
        # Want all loggers to print
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            logger.setLevel(logging.INFO)

    connection = obd.OBD(args.port)

    if connection.status() == OBDStatus.CAR_CONNECTED:
        print("Connected!")
    else:
        print("Failure connecting")
        exit(1)

    print("Querying block voltages...")
    block_volt_command = OBDCommand("HY_BATT_V", "", b"2181", 0, noop, ECU.ALL, False, b"7E2")
    block_volt_response = connection.query(block_volt_command, True)

    if block_volt_response.value:
        v = 0
        for i in range(2, 22):
            if i % 2 == 0:
                v += 256 * block_volt_response.value[i]
            else:
                v += block_volt_response.value[i]
                v *= 79.99 / 65535
                print("  Block %i: %.4f" % (int((i - 1)/ 2), v,))
                v = 0
    else:
        print("ERROR: Failed to query block voltages")

    print("Querying battery state...")
    batt_state_command = OBDCommand("HY_BATT_STATE", "", b"2192", 0, noop, ECU.ALL, False, b"7E2")
    batt_state_response = connection.query(batt_state_command, True)

    status_res = batt_state_response.value

    if batt_state_response.value:
        min_cell = batt_state_response.value[4]
        min_v = (batt_state_response.value[2] * 256 + batt_state_response.value[3]) * 79.99 / 65535

        max_cell = batt_state_response.value[7]
        max_v = (batt_state_response.value[5] * 256 + batt_state_response.value[6]) * 79.99 / 65535

        print("  Minimum: %.4f V (Block %d)" % (min_v, min_cell + 1))
        print("  Maximum: %.4f V (Block %d)" % (max_v, max_cell + 1))
        print("  Delta: %.4f V" % abs(max_v - min_v))
    else:
        print("ERROR: Failed to query battery state voltage")

    connection.close()
