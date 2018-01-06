#!/bin/usr/python3
'''
GPS to google maps tracker
'''

''' user varibles '''
working_dir   = "/home/pi"
out_file_name = "journey"
log_dir       = "/home/pi"
log_file_name = "tracker.log"

''' imports '''

from gps3.agps3threaded import AGPS3mechanism
import sys
import datetime
import math
import time

'''' script varibles '''

refresh_rate = 1.0
agps_thread = AGPS3mechanism()
agps_thread.stream_data()
agps_thread.run_thread()
out_file_name = out_file_name + "-" + str(datetime.datetime.now().strftime("%Y%m%d_%H%M")) + ".kml"


''' functions '''
def create_header():
    '''
    creates the xml header for googleearth file
    :return: header
    '''
    header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>Jounery """ + datetime.datetime.now().strftime(("%Y-%m-%d @ %H:%M")) + """</name>
	<Style id="redLineBluePoly">
		<LineStyle>
			<color>ff0000ff</color>
		</LineStyle>
		<PolyStyle>
			<color>ffff0000</color>
		</PolyStyle>
	</Style>
	<Placemark>
		<name>Jounery on """ + datetime.datetime.now().strftime(("%Y-%m-%d @ %H:%M")) + """</name>
		<description>Opaque blue walls with red outline, height tracks terrain</description>
		<styleUrl>#redLineBluePoly</styleUrl>
		<gx:balloonVisibility>1</gx:balloonVisibility>
		<LineString>
			<extrude>1</extrude>
			<tessellate>1</tessellate>
			<altitudeMode>relativeToGround</altitudeMode>
			<coordinates>"""
    return header

def create_footer():
    '''
    adds footer to file
    :return: footer
    '''
    footer = """
\t\t\t</coordinates>
		</LineString>
	</Placemark>
</Document>
</kml>"""

    return footer

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
    try:
        print("create file")
        with open(working_dir + "/" + out_file_name, "w") as outfile:
            outfile.writelines(create_header())
            print(create_header())
            while True:
                try:
                    if agps_thread.data_stream.lat != "n/a" and agps_thread.data_stream.lon != "n/a":
                        try:
                            coords = "\t\t\t\t" + str(agps_thread.data_stream.lat) + "," + str(agps_thread.data_stream.lon)
                            coords = coords + "," + str(math.ceil((agps_thread.data_stream.speed / 2236.94) * 10 ))
                            print(coords)
                            outfile.writelines(coords)
                            time.sleep(refresh_rate)
                            #try:
                            #print("check gps")
                            #print("insert line")
                        except KeyboardInterrupt:
                            outfile.writelines(create_footer())
                            print(create_footer())
                            sys.exit(0)
                        except Exception as ex:
                            tb = sys.exc_info()[2]
                            print_error(ex, tb.tb_lineno, "data error" + working_dir + out_file_name)
                except Exception as ex:
                    tb = sys.exc_info()[2]
                    print_error(ex, tb.tb_lineno, "gps error " + working_dir + out_file_name)
    except Exception as ex:
        tb = sys.exc_info()[2]
        print_error(ex, tb.tb_lineno, "Error creating file: " + working_dir + out_file_name)

    except KeyboardInterrupt:
        sys.exit(0)
