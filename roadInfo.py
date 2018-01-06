#!/usr/bin/python3

'''
script to take GPS lat + lon, get road number or name and max speed

uses:
	gps3
	urllib2
	json
'''

''' User Defineable Script Varibles '''
working_dir = "/tmp"
logfile_dir = ""
logfile_name = "logfile.log"

cansendfile_name = "cansend.dat"

''' includes '''

import sys
import time
import datetime
import math
import traceback
import urllib.request
import json

from gps3.agps3threaded import AGPS3mechanism

''' script varibles '''

agps_thread = AGPS3mechanism()
agps_thread.stream_data()
agps_thread.run_thread()

gps_timeout = 1.0
web_update_delay = 0.5

roadName = ""
roadSpeed = 0
currentSpeed = 0
speedLine = ""

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

''' main loop '''
if __name__ == '__main__':
    while True:
        try:
            #print("Get GPS location")
            #print("check is valid fix")
            if agps_thread.data_stream.lat != "n/a" and agps_thread.data_stream.lon != "n/a":
                currentSpeed = math.ceil(agps_thread.data_stream.speed / 2236.94)
                #print(str(agps_thread.data_stream.lat) + " : " + str(agps_thread.data_stream.lon))
                try:
                    #print("call website")
                    roaddata_url = "https://overpass-api.de/api/interpreter?data=[out:json];way(around:15," + str(agps_thread.data_stream.lat) + "," + str(agps_thread.data_stream.lon) + ");out;"
                    #print(roaddata_url)
                    try:
                        with urllib.request.urlopen(roaddata_url) as url:
                            roaddata = json.loads(url.read().decode())
                            # print(roaddata)
                            #print("Set maxspeed")
                            try:
                                if "maxspeed" in roaddata["elements"][0]["tags"]:
                                    roadSpeed = roaddata["elements"][0]["tags"]["maxspeed"][:2]
                            except Exception as ex:
                                print("Max speed not found")
                                #roadSpeed = 0
                            #print("Set roadName to name")
                            try:
                                if "name" in roaddata["elements"][0]["tags"]:
                                    roadName = roaddata["elements"][0]["tags"]["name"]

                                #print("If ref is set, set that over road name")
                                if "ref" in roaddata["elements"][0]["tags"]:
                                    roadName = roaddata["elements"][0]["tags"]["ref"]
                            except Exception as ex:
                                print("Road name/number not found")
                                roadName = "locating"

                            speedLine = str(currentSpeed) + "/" + str(roadSpeed)
                    except Exception as ex:
                        tb = sys.exc_info()[2]
                        print_error(ex, tb.tb_lineno, "Error collecting data")

                except Exception as ex:
                    tb = sys.exc_info()[2]
                    print_error(ex, tb.tb_lineno, "Error connecting to website")

                #print("sleep before updating, dont swamp website")
                time.sleep(web_update_delay)
            else:
                #print("sleep for #" + str(gps_timeout) + "\n\n")
                roadName = "locating"
                speedLine = "gps"
                time.sleep(gps_timeout)

            # print("write to temp file")
            try:
                with open(working_dir + "/" + cansendfile_name, "w") as canfile:
                    outlines = roadName + "\n" + speedLine
                    canfile.writelines(outlines)
            except Exception as ex:
                tb = sys.exc_info()[2]
                print_error(ex, tb.tb_lineno, "Error writing to cansend file")

        except KeyboardInterrupt:
            #print("Application closed")
            sys.exit(1)

        except Exception as ex:
            tb = sys.exc_info()[2]
            print_error(ex, tb.tb_lineno, "GPS Error")
