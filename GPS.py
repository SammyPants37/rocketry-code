import time
import smbus2
import signal
import sys
BUS = None
address = 0x42
gpsReadInterval = 0.03
def connectBus():
    global BUS
    BUS = smbus2.SMBus(1)

def parseResponse(gpsLine):
    if(gpsLine.count(36) == 1):                           # Check #1, make sure '$' doesnt appear twice
        if len(gpsLine) < 84:                               # Check #2, 83 is maximun NMEA sentenace length.
            CharError = 0
            for c in gpsLine:                               # Check #3, Make sure that only readiable ASCII charaters and Carriage Return are seen.
                if (c < 32 or c > 122) and  c != 13:
                    CharError+=1
            if (CharError == 0):#    Only proceed if there are no errors.
                gpsChars = ''.join(chr(c) for c in gpsLine)
                if (gpsChars.find('txbuf') == -1):          # Check #4, skip txbuff allocation error
                # if True:
                    gpsStr, chkSum = gpsChars.split('*',2)  # Check #5 only split twice to avoid unpack error
                    gpsComponents = gpsStr.split(',')
                    chkVal = 0
                    for ch in gpsStr[1:]: # Remove the $ and do a manual checksum on the rest of the NMEA sentence
                        chkVal ^= ord(ch)
                    if (chkVal == int(chkSum, 16)): # Compare the calculated checksum with the one in the NMEA sentence
                        if gpsChars.startswith("$GNGGA"):
                            return gpsChars
                else:
                    print("bad sentenace")
            else:
                print("bad sentenace")
        else:
            print("bad sentenace")
    return "no data"

def handle_ctrl_c(signal, frame):
        sys.exit(130)
#This will capture exit when using Ctrl-C
signal.signal(signal.SIGINT, handle_ctrl_c)

def readGPS():
    c = None
    response = []
    try:
        while True: # Newline, or bad char.
            c = BUS.read_byte(address)
            if c == 255:
                return ["", 0, "", 0, "", 0, 0, 0, 0, ""]
            elif c == 10:
                break
            else:
                response.append(c)
        stringData = parseResponse(response)
        listdata = stringData.split(',')
        # listdata.remove("$GNGGA")
        return listdata
            
    except IOError:
        connectBus()
        return ["", 0, "", 0, "", 0, 0, 0, 0, ""]
    except Exception as e:
        print(e)
        return ["", 0, "", 0, "", 0, 0, 0, 0, ""]
    


# if __name__ == "main":
connectBus()
prevData = ["", 0, "", 0, "", 0, 0, 0, 0, ""]
listdata = ["", 0, "", 0, "", 0, 0, 0, 0, ""]

while True:
    listdata = readGPS()
    if listdata[0] == "":
        listdata = prevData

    # this method of getting gps data isn't great but it does work
    print("data valid: " + str(listdata[5]) + " | sats used: " + str(listdata[6]))
    print("time: " + listdata[0][:2] + ":" + listdata[0][1:3]+ "." + listdata[0][4:6])
    print("position: " + str(listdata[1]) + listdata[2] + " " + str(listdata[3]) + listdata[4])
    print("altatude: " + str(listdata[8]) + listdata[9])
    prevData = listdata
    time.sleep(gpsReadInterval)
    # time.sleep(0.5)