#/usr/bin/python3

import argparse
import can
import time

BASE_ID = 0x406

FL_CONST = 0x4E20
FR_CONST = 0x4E22
RL_CONST = 0x4E24
RR_CONST = 0x4E26

def send_can_msg(bus, msg_data):
    msg = can.Message(arbitration_id=BASE_ID, data=msg_data, is_extended_id=False)
    try:
        bus.send(msg)
    except can.CanError:
        print("Message NOT sent")

def send_can_msg_10s(bus, msg_data):
    count = 0
    while count < 10:
        send_can_msg(bus, msg_data)
        time.sleep(1)
        count += 1

def send_basic_prog_msg(bus):
    # Bytes 1-2: 0x7530 (Programming constant)
    # Bytes 3-4: 0x406 (Default CAN Id)
    # Byte 5: 2 (Custom sensor assignment)
    # Byte 6: 1 (1 Mbit/s baud rate)
    # Byte 7: 1 (Default emissivity)
    # Byte 8: Empty
    prog_data = [0] * 8
    prog_data[0] = 0x7530 >> 8
    prog_data[1] = 0x7530 & 255
    prog_data[2] = BASE_ID >> 8
    prog_data[3] = BASE_ID & 255
    prog_data[4] = 2
    prog_data[5] = 1
    prog_data[6] = 1
    send_can_msg_10s(bus, prog_data)

def send_corner_data(bus, prog_const, node_id):
    # Bytes 1-2: Programming constant
    # Byte 3: New node id
    corner_data = [0] * 8
    corner_data[0] = prog_const >> 8
    corner_data[1] = prog_const & 255
    corner_data[2] = node_id
    send_can_msg_10s(bus, corner_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=\
    "Assigns a new serial number to a specific corner for the IZZE TTPMS system")
    parser.add_argument("--FL", type=int, default=-1, help="New FL node Id")
    parser.add_argument("--FR", type=int, default=-1, help="New FR node Id")
    parser.add_argument("--RL", type=int, default=-1, help="New RL node Id")
    parser.add_argument("--RR", type=int, default=-1, help="New RR node Id")

    parser.add_argument("--send_prog_message", action="store_true",
        help="Also send the basic receiver programming message")
    parser.add_argument("--interface", type=str, default="can0", help="CAN iterface")
    parser.add_argument("--bitrate", type=int, default="1000000", help="CAN bitrate")
    args = parser.parse_args()

    with can.interface.Bus(bustype="socketcan", channel=args.interface, bitrate=args.bitrate) as bus:
        if args.send_prog_message:
            print("Sending basic receiver programming message..")
            send_basic_prog_msg(bus)

        if args.FL != -1:
            print("Setting FL node Id to %i..." % args.FL)
            send_corner_data(bus, FL_CONST, args.FL)

        if args.FR != -1:
            print("Setting FR node Id to %i..." % args.FR)
            send_corner_data(bus, FR_CONST, args.FR)

        if args.RL != -1:
            print("Setting RL node Id to %i..." % args.RL)
            send_corner_data(bus, RL_CONST, args.RL)

        if args.RR != -1:
            print("Setting RR node Id to %i..." % args.RR)
            send_corner_data(bus, RR_CONST, args.RR)
