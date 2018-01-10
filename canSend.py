#!/usr/bin/python3
'''
Script to send data to audi DIS via CANBUS

uses:
    python-can
'''

''' User varibles '''

working_dir = "/tmp"
datafile    = "cansend.dat"
logfile_dir = "/media/pi/DISK_IMG"
logfile     = "cansend.log"
can_interface = 'can0'
can_refresh_rate = 0.1

''' Imports '''

import can
import time
import datetime
import sys

''' Script vairbles '''

bus = can.interface.Bus(can_interface, bustype='socketcan_native')
file_not_found_timeout = 60
timeout = 0
''' functions '''

def print_error(ex="Error", linenumber=0, message="There has been an error"):
    '''
    Function to print errors to an error log file
    :param ex: excepton
    :param linenumber: generated line number, int
    :param message: custom error message
    :return: NONE
    '''
    line = str(datetime.datetime.now()) + " @ " + str(linenumber) + " : " + str(ex) + " : " + str(message + "\n")
    try:
        with open(logile_dir + "/" + logfile_name, "a") as error_file:
            error_file.write(line)
    except:
        print("ERROR WRITING TO FILE > ", line)

def format_can_message(canline):
    '''
    format message ready to send to DIS
    remove white space before and after text
    check remainder is exactly 8 characters long, trim if longer, pad if shorter

    :param canline: string (text to send to the DIS)
    :return:

    '''
    #canline = ''.join(map(str, canline))
    canline = canline.strip()
    ''' if more than 8, trim and stop at 8 '''
    if len(canline) > 8:
        canline = canline[:8]

    ''' if less than 8, center message '''
    if len(canline) < 8:
        canline = '{:^8}'.format(canline)

    canline = canline.upper()

    return bytearray(canline.encode())

def send_message(id, message):
    '''
    takes actual message and sends to the CAN BUS

    :param id: takes a number, padds it out to 8 char with 0x at begining
    :param message: actual string to send
    :return: nothing
    '''
    #print(id)

    data = format_can_message(message)
    canMessage = can.Message(arbitration_id=id, data=data, extended_id=False)
    #print(canMessage)

    bus.send(canMessage)

def send_data(id, data):
    '''
    takes actual message and sends to the CAN BUS

    :param id: takes a number, padds it out to 8 char with 0x at begining
    :param message: actual string to send
    :return: nothing
    '''
    #print(id)

    #data = bytearray(data)
    canMessage = can.Message(arbitration_id=id, data=data, extended_id=False)
    #print(canMessage)

    bus.send(canMessage)
    
def closing():
    print("CAN sender is closing")
    delay = 5

    while delay > 0:
        send_data(0x00000661, [81, 1, 12, 38, 00, 00, 00, 00])
        send_message(0x00000363, "Exiting")
        send_message(0x00000365, "")
        time.sleep(can_refresh_rate)
        delay = delay - can_refresh_rate
    sys.exit(1)

''' Main loop '''
if __name__ == '__main__':
    #print("Try to load file")
    while True:
        try:
            time.sleep(can_refresh_rate)
            with open(working_dir + "/" + datafile, "r") as canfile:
                #print("File loaded")
                #print("Reset file searching delay")
                timeout = 0

                #print("Send stay alive message")
                try:
                    send_data(0x00000661, [81, 1, 12, 38, 00, 00, 00, 00])
                    #canMessage = can.Message(arbitration_id=0x00000661, data=81011238, extended_id=False)
                    #bus.send(canMessage)
                except Exception as ex:
                    tb = sys.exc_info()[2]
                    print_error(ex, tb.tb_lineno, "Error sending keep-alive to CAN")

                ''' load data to varible '''
                lines = canfile.readlines()

                #print("Send First line to DIS")
                try:
                    send_message(0x00000363, lines[0])
                except Exception as ex:
                    tb = sys.exc_info()[2]
                    print_error(ex, tb.tb_lineno, "Error sending first line to CAN")

                #print("Send Second line to DIS")
                try:
                    send_message(0x00000365, lines[1])
                except Exception as ex:
                    tb = sys.exc_info()[2]
                    print_error(ex, tb.tb_lineno, "Error sending second line to CAN")

        except KeyboardInterrupt:
            closing()

        except FileNotFoundError:
            tb = sys.exc_info()[2]

            send_message(0x00000363, "Loading")
            send_message(0x00000365, "")
            timeout = timeout + can_refresh_rate
            print("Looking for file: ", timeout)
            if timeout > file_not_found_timeout :
                delay = 5
                try:
                    while delay > 0:
                        send_message(0x00000363, "Exiting")
                        send_message(0x00000365, "")
                        time.sleep(can_refresh_rate)
                        delay = delay - can_refresh_rate
                    print_error("File Not Found", tb.tb_lineno, working_dir + datafile)
                    sys.exit(1)
                except KeyboardInterrupt:
                    closing()
        except Exception as ex:
            tb = sys.exc_info()[2]
            print_error(ex, tb.tb_lineno, "Error loading file: " + working_dir + datafile)
