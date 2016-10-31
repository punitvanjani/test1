import serial
import time
from api.app import create_app
from api.models import db, User, Hub, Schedule, HubTypes, Endpoint, EndpointTypes, SectionTypes, Properties, WSNodeStatus, EndpointStatus
from api.debugger import debug_msg
from api.common import endpoint_update_status
from datetime import datetime


table = (
0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040 )


def convert(int_value):
   encoded = format(int_value, 'x')
   length = len(encoded)
   encoded = encoded.zfill(length+length%2)
   return encoded.decode('hex')

def bit_from_string(string, index):
       i, j = divmod(index, 8)

       if ord(string[i]) & (1 << j):
              return 1
       else:
              return 0

def calcString(st, crc=0xFFFF):
    """Given a hex string and starting CRC, Calc a final CRC-16 """
    for ch in st:
#         crc = (crc >> 8) ^ table[(crc ^ ord(ch)) & 0xFF]
        crc = table[(crc ^ ord(ch)) & 0xFF] ^ (crc >> 8)
# after calculation, interchange LSB and MSB
    crc1 = crc & 0xFF00
    crc1 = crc1 >> 8
    
    crc2 = crc & 0x00FF
    crc2 = crc2 << 8
    
    crc = crc2 ^ crc1
    return crc

# Initiate the App so that we can use all variables and objects
app = create_app()
with app.app_context():
# Fetch the mode of communication and Baud Rate for Webswitch
    wbs_comm = Properties.query.filter_by(key='WbSwtComm').first()
    if wbs_comm == None:
        print "comm not found"
    wbb_comm = Properties.query.filter_by(key='WbSwtBaud').first()
    if wbb_comm == None:
        print "baud not found"
        wbs_baud_rate = '9600'
    else:
        wbs_baud_rate = wbb_comm.value
    wsf_prop = Properties.query.filter_by(key='WbSwtSFrq').first()
    if wsf_prop == None:
        print "frequency not found"
        wbs_scan_freq = '3'
    else:
        wbs_scan_freq = wsf_prop.value
# Fetch unique WebSwitch Node IDs from Endpoint table
# Get all Endpoints which are Webswitch type
    endpoints = Endpoint.query.filter_by(node_type=10).all()
# Clear all the nodes to be checked on restart
    nodes = []
#     debug_msg("testing")
# Fetch unique WebSwitch Node IDs from Endpoint table
    for endpoint_single in endpoints:
        found = 2
        for node in nodes:
            if endpoint_single.internal_nod_id == node:
                found = 1
                continue
            else:
                found = 0
        if found == 0 or found == 2:
            nodes.append(endpoint_single.internal_nod_id)
# Check if node exists in checking DB, if not then add it
    node_commit = 0
    for node in nodes:
        nodestatus = WSNodeStatus.query.filter_by(internal_nod_id = node).first()
        if nodestatus == None:
# Create new Node Status
            nodestatus = WSNodeStatus(
                                internal_nod_id = node,
                                status          = 0
            )
            
            db.session.add(nodestatus)
            node_commit = 1
            print "Nodes:", node
    if node_commit == 1:
        db.session.commit()
        print "node commit called"
    
# Establish Serial communication
    try:
        serusb = serial.Serial(wbs_comm.value, int(wbs_baud_rate))
        serusb.close()
    except:
        pass
# Go in endless loop, keep on scanning all the slaves statuses
    while True:
        commit_flag = 0
        time.sleep(int(wbs_scan_freq))
        serusb.open()
        serusb.flushInput()
        for node in nodes:
            st0 = convert(node)
            st1 = convert(2)
            st2 = convert(0)
            st3 = convert(0)
            st4 = convert(0)
            st5 = convert(1)
            st6 = convert(calcString(st0+st1+st2+st3+st4+st5))
            serusb.flushInput()
            print "ReadCoil sent:", int(st0.encode('hex'), 16), int(st1.encode('hex'), 16), int(st2.encode('hex'), 16), int(st3.encode('hex'), 16), int(st4.encode('hex'), 16), int(st5.encode('hex'), 16), int(st6.encode('hex'), 16)
# Send reading code to all nodes one by one
            serusb.write(st0+st1+st2+st3+st4+st5+st6)
            serusb.timeout=1
# Read contents received from node
            read_val = serusb.read(size=6)
            if read_val != '':
# Contents read, check if there is any difference in previous status and current status
                nodestatus = WSNodeStatus.query.filter_by(internal_nod_id = node).first()
                if nodestatus.status != int(read_val[3].encode('hex'), 16):
# Get all the endpoints where internal_nod_id is equals to just changed node
                    endpoints = Endpoint.query.filter_by(internal_nod_id = node).all()
                    for endpoint in endpoints:
                        endpointstatus = EndpointStatus.query.filter_by(endpoint_uuid = endpoint.endpoint_uuid).first()
#                         print  endpoint.endpoint_uuid, endpoint.internal_end_id
                        if endpointstatus.status != bit_from_string(read_val[3], endpoint.internal_end_id):
                            endpoint_status = bit_from_string(read_val[3], endpoint.internal_end_id)
                            endpointstatus.status = endpoint_status
                            endpointstatus.last_changed_by = 'BackendUser'
                            endpointstatus.last_changed_on = datetime.today()
                            nodestatus.status = int(read_val[3].encode('hex'), 16)
                            endpoint_update_status(str(endpoint.endpoint_uuid),str(endpoint_status))
                            debug_msg('response')
                            commit_flag = 1
                print "ReadCoil receive:", int(read_val[0].encode('hex'), 16), int(read_val[1].encode('hex'), 16), int(read_val[2].encode('hex'), 16), int(read_val[3].encode('hex'), 16), int(read_val[4].encode('hex'), 16), int(read_val[5].encode('hex'), 16)
            else:
                print "Not read"
        if commit_flag == 1:
            db.session.commit()
            print "endpoint commit called"
        serusb.close()

