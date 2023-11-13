#/usr/bin/python3

import argparse
import logging

# Setup the path for the local version of python-OBD
import os
from pathlib import Path
import sys
obd_path = os.path.join(Path(__file__).parent.absolute(), "python-OBD")
sys.path.insert(0, obd_path)

import obd
from obd import OBDStatus
from obd.codes import BASE_TESTS, SPARK_TESTS, COMPRESSION_TESTS

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Checks emissions readiness monitors")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0",\
        help="Name of device to connect to")
    parser.add_argument("--force", action="store_true",\
        help="Query the command even if it is not supported")
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

    response = connection.query(obd.commands["STATUS"], args.force)

    if response:
        print("----- Emissions Readiness -----")
        print("    MIL ACTIVE: %s" % response.value.MIL)
        print("    DTC COUNT: %d" % response.value.DTC_count)

        for test in BASE_TESTS + SPARK_TESTS + COMPRESSION_TESTS:
            if not test:
                continue

            mod_test_name = test.replace("_", " ")
            if getattr(response.value, test).available:
                msg = "PASS" if getattr(response.value, test).complete else "FAIL"
                print("    %s: %s" % (mod_test_name, msg))
            else:
                print("    %s: Not Available" % mod_test_name)

    else:
        print("Empty response")

    connection.close()
