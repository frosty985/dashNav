import can
import sys
import time
import datetime
import sys
import math

from gps3.agps3threaded import AGPS3mechanism

can_interface = "can0"
iginition_code = 0x151
iginition_off_delay = 5
iginition_delay = 0

workingdir = "/media/pi/DISK_IMG"
kmlfile_name = str(datetime.datetime.now().strftime("%Y%m%d_%H%M")) + ".kml"

mph_ratio = 10

can_bus_refresh_rate = 0.1
can_bus = can.interface.Bus(can_interface, bustype='socketcan_native', can_filters=[{"can_id": iginition_code, "can_mask": 0xFFFFFFF}])
#can_bus = can.interface.Bus(can_interface, bustype='socketcan_native')

gps_refresh = 1

agps_thread = AGPS3mechanism()
agps_thread.stream_data()
agps_thread.run_thread()



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

def header():
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

def footer():
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


def open_kml_file():
    kmlfile = None
    try:
        kmlfile = open(workingdir + "/" + kmlfile_name, "w")
        kmlfile.writelines(header())
    except Exception as expt:
        tb = sys.exc_info()[2]
        print_error(str(expt), tb, "Error opening file")
    return kmlfile

def close_kml_file(kmlfile):
    print("Close function")
    if not kmlfile.closed:
        kmlfile.writelines(footer())
        kmlfile.close

def main():
    iginition_delay = 0
    try:
        while True:
            print("Wait for ignition")
            try:
                can_message = can_bus.recv(can_bus_refresh_rate)
            except KeyboardInterrupt:
                if 'kmlfile' in locals():
                    print("Close file")
                    close_kml_file(kmlfile)
                    kmlfile = None
                    del kmlfile
                sys.exit(0)
            except Exception as expt:
                tb = sys.exc_info()[2]
                print_error(str(expt), tb, "Can Error")
            print("CAN Message")
            if can_message:
                if can_message.arbitration_id == iginition_code:
                    iginition_delay = 0
                    print("Iginition on")
                    iginition = True
                    print("check for open file")
                    if 'kmlfile' not in locals():
                        kmlfile = open_kml_file()
                        if kmlfile == None:
                            continue
                    print("check for gps")
                    if agps_thread.data_stream.lat != "n/a" and agps_thread.data_stream.lon != "n/a":
                        currentSpeed = math.ceil(agps_thread.data_stream.speed * 2.23694)
                        line = "\t\t\t\t" + agps_thread.data_stream.lat + "," + agps_thread.data_stream.lon, + "," + str(math.ceil(currentSpeed * mph_ratio))
                        print(line)
                        if not kmlfile.closed:
                            kmlfile.writelines(line)
            else:
                if 'kmlfile' in locals():
                    print(kmlfile)
                    if not kmlfile.closed:
                        iginition_delay = iginition_delay + 1
                        print(iginition_delay)
                        print(iginition_delay, ">", iginition_off_delay)
                        if iginition_delay > iginition_off_delay:
                            print("Close file")
                            ''' resset counters '''
                            iginition_delay = 0
                            close_kml_file(kmlfile)
                            kmlfile = None
                            del kmlfile

                    time.sleep(gps_refresh)
    except KeyboardInterrupt:
        if 'kmlfile' in locals():
            print("Close file")
            if not kmlfile.closed:
                close_kml_file(kmlfile)
                kmlfile = None
                del kmlfile
        sys.exit(0)


if __name__ == "__main__":
    main()
