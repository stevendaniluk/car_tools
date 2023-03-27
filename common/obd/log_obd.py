#/usr/bin/python3

import argparse
import atexit
import csv
import datetime
import logging
import time

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
    parser = argparse.ArgumentParser(description="Logs OBD queries to a CSV file")
    parser.add_argument("--filename", type=str, help="Path to file to write to")
    parser.add_argument("--rate", type=float, default=1.0, help="Rate to query at [Hz]")
    parser.add_argument("--cmds", nargs='+', type=str, help="Commands to log")
    parser.add_argument("--force", action="store_true",\
        help="Query the command(s) even if it is not supported")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0",\
        help="Name of device to connect to")
    parser.add_argument("--debug", action="store_true", help="Display all logs")
    args = parser.parse_args()

    connection = obd.OBD(args.port)

    if connection.status() == OBDStatus.CAR_CONNECTED:
        print("Connected!")
    else:
        print("Failure connecting")
        exit(1)

    # Set the connection to close when the program exits
    def exit_handler():
        connection.close()

    atexit.register(exit_handler)

    if args.debug:
        # Want all loggers to print
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            logger.setLevel(logging.INFO)

    # Determine what commands we can query
    query_cmds = []
    if args.force:
        query_cmds = args.cmds
    else:
        for cmd in args.cmds:
            if not connection.supports(obd.commands[cmd]):
                print(cmd, " not supported, will be ignored")
            else:
                query_cmds.append(cmd)

    print("Will query:")
    for cmd in query_cmds:
        print("\t", cmd)

    # Start our CSV file
    if args.filename:
        args.filename = os.path.expanduser(args.filename)
    else:
        args.filename = "obd_log_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"

    with open(args.filename, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write the header
        csv_writer.writerow(["time"] + query_cmds)

        # Periodically loop through all commands to query and log them
        print("Beginning logging...")
        sleep_dur = 1.0 / args.rate
        while(True):
            query_start_stamp = time.time()

            data = []
            data.append(query_start_stamp)
            for cmd in query_cmds:
                response = connection.query(obd.commands[cmd])
                data.append(response.value.magnitude)

            csv_writer.writerow(data)

            # Wait for the next query time, accounting for how long the query took
            time.sleep(max(query_start_stamp + sleep_dur - time.time(), 0))
