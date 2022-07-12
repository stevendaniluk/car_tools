#/usr/bin/python3

import argparse

# Setup the path for the local version of python-OBD
import os
from pathlib import Path
import sys
obd_path = os.path.join(Path(__file__).parent.absolute(), "python-OBD")
sys.path.insert(0, obd_path)

import obd
from obd import OBDStatus

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Checks for Diagnostic Trouble Codes")
    parser.add_argument("--clear", action="store_true", help="Clear all DTCs")
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

    print("Checking current CELs...")
    if connection.supports(obd.commands.GET_DTC):
        dtc_response = connection.query(obd.commands.GET_DTC)
        print(dtc_response.value)
    else:
        print("GET_DTC not supported, skipping")

    if args.clear:
        print("Clearing CELs...")
        if connection.supports(obd.commands.CLEAR_DTC):
            clear_dtc_response = connection.query(obd.commands.CLEAR_DTC)
            print(clear_dtc_response.value)
        else:
            print("CLEAR_DTC not supported, skipping")

    connection.close()
