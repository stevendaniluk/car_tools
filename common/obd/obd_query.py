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
from obd.commands import Commands

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Runs a custom OBD command")
    parser.add_argument("cmd", type=str, help="Command to query")
    parser.add_argument("--list_supported", action="store_true",\
        help="List all supported commands and exit")
    parser.add_argument("--force", action="store_true",\
        help="Query the command even if it is not supported")
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

    if args.list_supported:
        print("Supported commands:")
        for valid_cmd in connection.supported_commands:
            print("\t", valid_cmd.name)

        connection.close()
        exit(0)

    if connection.supports(obd.commands[args.cmd]):
        response = connection.query(obd.commands[args.cmd])
        print(response.value)
    else:
        print(args.cmd, " not supported!")

    connection.close()
