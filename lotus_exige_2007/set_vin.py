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
from obd.decoders import encoded_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Assigns a new VIN number")
    parser.add_argument("--VIN", type=str, help="New VIN number to assign")
    parser.add_argument("--read_only", action="store_true", help="Only read the current VIN")
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

    print("Checking current VIN")
    if connection.supports(obd.commands.VIN):
        print("VIN supported!")
    else:
        print("VIN not supported, adding it")
        connection.supported_commands.add(obd.commands.VIN)

    vin_response = connection.query(obd.commands.VIN, True)
    print(vin_response.value)

    if args.read_only:
        connection.close()
        exit(0)

    # Extract the appropriate components of the VIN
    vin_cmd_pt1_bytes = bytes("3B01", "utf-8") + bytes((args.VIN[8] + args.VIN[11] + args.VIN[12] \
        + args.VIN[13] + args.VIN[14]).encode("utf-8").hex(), "utf-8")
    vin_cmd_pt2_bytes = bytes("3B02", "utf-8") \
        + bytes((args.VIN[15] + args.VIN[16]).encode("utf-8").hex(), "utf-8") \
        + bytes("000000", "utf-8")

    vin_cmd_pt1 = OBDCommand("VIN_SET_PT1", "", vin_cmd_pt1_bytes, 0, encoded_string(2))
    vin_cmd_pt2 = OBDCommand("VIN_SET_PT1", "", vin_cmd_pt2_bytes, 0, encoded_string(2))

    print("Setting VIN part 1...")
    response_pt1 = connection.query(vin_cmd_pt1, True)
    print(response_pt1.value)

    print("Setting VIN part 2...")
    response_pt2 = connection.query(vin_cmd_pt2, True)
    print(response_pt2.value)

    print("Done!")

    connection.close()
