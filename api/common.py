import socket
import fcntl
import struct
import requests
from requests.auth import HTTPBasicAuth
import os
import time
from flask import current_app, g, jsonify
from models import db, Hub, Endpoint, User, EndpointTypes, SectionTypes, EndpointGroup, Schedule, Properties, EndpointSchema, HubSchema
from datetime import datetime
import uuid
# from api.v1.interfaces import server_update_hub

def is_admin(user):
    is_admin = False
    
    users = User.query.filter_by(username=user).first()
    if users.group == 'ADMIN':
        is_admin = True
    else:
        is_admin = False
    return is_admin

def unique_endpoint(section_id, node_id, endpoint_id):
    unique = False
    endpoint = Endpoint.query.filter_by(internal_sec_id=section_id,internal_nod_id=node_id,internal_end_id=endpoint_id).first()
    
    if endpoint == None:
        unique = True
    else:
        unique = False
    return unique

def unique_endpoint_type(node_type, endpoint_type):
    unique = False
    endpointtypes = EndpointTypes.query.filter_by(node_type=node_type,endpoint_type=endpoint_type).first()
    
    if endpointtypes == None:
        unique = True
    else:
        unique = False
    return unique

def unique_section_type(section_type):
    unique = False
    sectiontypes = SectionTypes.query.filter_by(section_type=section_type).first()
    
    if sectiontypes == None:
        unique = True
    else:
        unique = False
    return unique

def unique_user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        unique = True
    else:
        unique = False
    return unique

def valid_user(username):
    user = User.query.filter_by(username=username).first()
    if user != None:
        valid = True
    else:
        valid = False
    return valid

def endpoint_validation(data):
    valid = False
    endpointtypes = EndpointTypes.query.filter_by(node_type=data['node_type'],endpoint_type=data['endpoint_type']).first()
    if endpointtypes == None:
        valid = False
    else:
        valid = True
    return valid

def schedule_validation(data):
    valid = False
    endpoint = Endpoint.query.filter_by(endpoint_uuid = data['uuid_id']).first()
    if endpoint == None:
        group = EndpointGroup.query.filter_by(group_uuid = data['uuid_id']).first()
        if group == None:
            valid = False
        else:
            valid = True
    else:
# As the endpoint is found, then check expected_status is according to endpoint types
        endpointtypes = EndpointTypes.query.filter_by(node_type=endpoint.node_type,endpoint_type=endpoint.endpoint_type).first()        
        if (endpointtypes.status_min <= data['expected_status']) and (endpointtypes.status_max >= data['expected_status']):
            valid = True
        else:
            valid = False
    return valid


def operate_validation(endpoint_uuid, status):
    valid = False
    endpoint = Endpoint.query.filter_by(endpoint_uuid = endpoint_uuid).first()
    if endpoint == None:
        valid = False
        return valid
    else:
        valid = True
    
    endpoint_types = EndpointTypes.query.filter_by(node_type=endpoint.node_type,endpoint_type=endpoint.endpoint_type).first()
    
    if endpoint_types != None:
        if (status >= endpoint_types.status_min) and (status <= endpoint_types.status_max):
            valid = True
        else:
            valid = False
    else:
        valid = False
    return valid

def unique_property(key):
    property = Properties.query.filter_by(key = key).first()
    if property == None:
        unique = True
    else:
        unique = False
    return unique


def unique_group_desc(group_desc):
    group = EndpointGroup.query.filter_by(group_desc = group_desc).first()
    if group == None:
        unique = True
    else:
        unique = False
    return unique


def debug_msg(message,file=__file__,keyword1=-99,keyword2=-99,keyword3=-99,keyword4=-99,keyword5=-99):
    msg = ''
    property = Properties.query.filter_by(key = 'DEBUG').first()
    if property.value != None and property.value == 'true':
        try:
            msg += '\t' + 'USER:' + str(g.user.username)
        except:
            msg += '\t' + 'USER:' + str("BackendUser")
        msg += '\t' + 'FILE:' + str(file)
        msg += '\t'
        if(keyword1!=-99):
            msg += 'KEY1:' + str(keyword1)
        msg += '\t'
        if(keyword2!=-99):
            msg += 'KEY2:' + str(keyword2)
        msg += '\t'
        if(keyword3!=-99):
            msg += 'KEY3:' + str(keyword3)
        msg += '\t'        
        if(keyword4!=-99):
            msg += 'KEY4:' + str(keyword4)
        msg += '\t'
        if(keyword5!=-99):
            msg += 'KEY5:' + str(keyword5)
        msg += '\t' + 'MSG:' + str(message)
# Open log file in append mode
        f = open(current_app.config['LOG_FILE'],'a')
        f.write(str(datetime.today()))
        f.write(msg)
        print msg
        f.write('\n')
        f.close()

def get_intranet_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except:
        return "0.0.0.0"
    
def get_server_credentials():
    prop = Properties.query.filter_by(key='ServerUsr').first()
    user = prop.value
    prop = Properties.query.filter_by(key='ServerPwd').first()
    password = prop.value

    return (user, password)
    
def get_serial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
        cpuserial_int = int(cpuserial,16)
    except:
        cpuserial = "ERROR000000000"
        cpuserial_int = 9999999999999999
    return cpuserial_int

def get_external_url():
    try:
        r = requests.get('http://localhost:4040/api/tunnels')
        datajson = r.json()
        msg=None
        for i in datajson['tunnels']:
# populate only https ngrok url
            if 'https' in i['public_url']:
                msg = i['public_url']
    except requests.exceptions.ConnectionError:
        r = None
        msg = "Error"
    except requests.exceptions.RequestException:
        r = None
        msg = "ERROR"
#  
    return msg

def server_hub_string(hubdetails):
#     hub_schema_custom = HubSchema(exclude=('last_changed_on', 'last_changed_by'))
#     hubstring = hub_schema_custom.dump(hubdetails).data

    hubstring = '{"description":"'+ str(hubdetails.description) +'", "external_url":"'+hubdetails.external_url+'","hub_id":"'+str(hubdetails.hub_id)+'","internal_url":"'+str(hubdetails.internal_url)+'"}'
    return hubstring

def server_update_hub(hubdetails):
    resp = None
    server = Properties.query.filter_by(key='ServerAPI').first()
    serverurl = server.value
    serverurl = serverurl + 'et_update_hub_info.php?arg={"hub":'  
    url = serverurl + str(server_hub_string(hubdetails)) + '}'
    debug_msg('hub_defined__server_updated', __file__, url)
    try:
        user,password = get_server_credentials()
        req = requests.get(url,auth=HTTPBasicAuth(user, password)).json()
        debug_msg('response', __file__, req)
#         resp = req['success']
    except requests.exceptions.ConnectionError:
        req = None
        msg = "Error"
        resp = None
    except requests.exceptions.RequestException:
        req = None
        msg = "ERROR"
        resp = None
    except:
        req = None
        msg = "ERROR"
        resp = None
    return resp

def server_endpoint_string(endpoints):
#     endpoint_schemas_custom = EndpointSchema(exclude=('last_changed_on', 'last_changed_by'), many = True, extra={"qwe":'123',"qbc":1234})
#     endpoint_schemas_custom = EndpointSchema(exclude=('last_changed_on', 'last_changed_by'), many = True)
#     endpointstring = endpoint_schemas_custom.dump(endpoints).data
# #     endpointstring = jsonify({'endpoints':endpointstring})
#     debug_msg('endpoint_defined__server_updated', __file__, endpointstring)
    endpointstring = ''
    for endpoint_single in endpoints:
        endpointstring += '{"internal_sec_id":"'+ str(endpoint_single.internal_sec_id) +'", "section_type":"' + str(endpoint_single.section_type)+'","internal_sec_desc":"'+str(endpoint_single.internal_sec_desc)+'","internal_nod_id":"'+str(endpoint_single.internal_nod_id)+'","node_type":"'+str(endpoint_single.node_type)+'","internal_nod_desc":"'+str(endpoint_single.internal_nod_desc)+'","internal_end_id":"'+str(endpoint_single.internal_end_id)+'","endpoint_type":"'+str(endpoint_single.endpoint_type)+'","endpoint_uuid":"'+str(endpoint_single.endpoint_uuid)+'","internal_end_desc":"'+str(endpoint_single.internal_end_desc)+'"}'
        endpointstring += ','
    endpointstring = endpointstring[:-1]
    return endpointstring

def server_sync_endpoints():
    server = Properties.query.filter_by(key='ServerAPI').first()
    serverurl = server.value
    serverurl = serverurl + 'et_update_hub_info.php?arg='
    endpoints = Endpoint.query.all()
    hubdetails = Hub.query.first()
    url = serverurl + '{"endpoints":[['+ str(server_endpoint_string(endpoints)) + '],{}],"hub":' + str(server_hub_string(hubdetails)) + '}'
    debug_msg('endpoint_defined__server_updated', __file__, url)

    try:
        user,password = get_server_credentials()
        req = requests.get(url,auth=HTTPBasicAuth(user, password)).json()
        debug_msg('response', __file__, req)
#         resp = req['success']
    except requests.exceptions.ConnectionError:
        req = None
        msg = "Error"
        resp = None
    except requests.exceptions.RequestException:
        req = None
        msg = "ERROR"
        resp = None
    except:
        req = None
        msg = "ERROR"
        resp = None
#     return resp

def get_scheduler_current_timestamp():
    year    = int(str(datetime.today())[:4])
    month   = int(str(datetime.today())[5:7])
    weekday = datetime.weekday(datetime.today())
    date    = int(str(datetime.today())[8:10])
    hour    = int(str(datetime.today())[11:13])
    min     = int(str(datetime.today())[14:16])
# Return year, month, Weekday, date, hour and min based on today's datetime
    return (year, month, weekday, date, hour, min)

def scheduled_endpoints_groups():
    hourly_tasks = scheduled_hourly_tasks()
    daily_tasks = scheduled_daily_tasks()
    weekly_tasks = scheduled_weekly_tasks()
    monthly_tasks = scheduled_monthly_tasks()
    yearly_tasks = scheduled_yearly_tasks()
    onlyonce_tasks  = scheduled_onlyonce_tasks()
    endpoints = []
    endpoint_status = []
#     endpoints = Endpoint.query.all()
    endpointgroup = {}
    for tasks in hourly_tasks:
        endpoint = Endpoint.query.filter_by(endpoint_uuid=tasks.uuid_id).first()
        if endpoint != None:
            endpoints.append(endpoint)
            endpoint_status.append(tasks.expected_status)
    for tasks in daily_tasks:
        endpoint = Endpoint.query.filter_by(endpoint_uuid=tasks.uuid_id).first()
        if endpoint != None:
            endpoints.append(endpoint)
            endpoint_status.append(tasks.expected_status)
    for tasks in weekly_tasks:
        endpoint = Endpoint.query.filter_by(endpoint_uuid=tasks.uuid_id).first()
        if endpoint != None:
            endpoints.append(endpoint)
            endpoint_status.append(tasks.expected_status)
    for tasks in monthly_tasks:
        endpoint = Endpoint.query.filter_by(endpoint_uuid=tasks.uuid_id).first()
        if endpoint != None:
            endpoints.append(endpoint)
            endpoint_status.append(tasks.expected_status)
    for tasks in yearly_tasks:
        endpoint = Endpoint.query.filter_by(endpoint_uuid=tasks.uuid_id).first()
        if endpoint != None:
            endpoints.append(endpoint)
            endpoint_status.append(tasks.expected_status)
    for tasks in onlyonce_tasks:
        endpoint = Endpoint.query.filter_by(endpoint_uuid=tasks.uuid_id).first()
        if endpoint != None:
            endpoints.append(endpoint)
            endpoint_status.append(tasks.expected_status)
    for endpoint1 in endpoints:
        print endpoint1.endpoint_uuid
    
    return (endpoints, endpointgroup, endpoint_status)

# def delete_all_except(endpoint):

def scheduled_hourly_tasks():
# Get current date time and weekday in variables
    year, month, weekday, date, hour, min = get_scheduler_current_timestamp()
# Query the tasks which are marked true for hourly, and has current min
    tasks = Schedule.query.filter_by(status = True, hourly = True, min = min)
    return tasks

def scheduled_daily_tasks():
# Get current date time and weekday in variables
    year, month, weekday, date, hour, min = get_scheduler_current_timestamp()
# Query the tasks which are marked true for daily, and has current hour and min
    tasks = Schedule.query.filter_by(status = True, daily = True, hour = hour, min = min)
    return tasks

def scheduled_weekly_tasks():
# Get current date time and weekday in variables
    year, month, weekday, date, hour, min = get_scheduler_current_timestamp()
# Query the tasks which are marked true for weekly, and has current weekday, hour and min
    tasks = Schedule.query.filter_by(status = True, weekly = True, weekday = weekday, hour = hour, min = min)
    return tasks

def scheduled_monthly_tasks():
# Get current date time and weekday in variables
    year, month, weekday, date, hour, min = get_scheduler_current_timestamp()
# Query the tasks which are marked true for monthly, and has current weekday, hour and min
    tasks = Schedule.query.filter_by(status = True, monthly = True, date = date, hour = hour, min = min)
    return tasks

def scheduled_yearly_tasks():
# Get current date time and weekday in variables
    year, month, weekday, date, hour, min = get_scheduler_current_timestamp()
# Query the tasks which are marked true for yearly, and has current weekday, hour and min
    tasks = Schedule.query.filter_by(status = True, yearly = True, month = month, date = date, hour = hour, min = min)
    return tasks

def scheduled_onlyonce_tasks():
# Get current date time and weekday in variables
    year, month, weekday, date, hour, min = get_scheduler_current_timestamp()
# Query the tasks which are marked true for yearly, and has current weekday, hour and min
    tasks = Schedule.query.filter_by(status = True, onlyonce = True, year = year, month = month, date = date, hour = hour, min = min)
    return tasks

def system_start():
    str_ip = get_intranet_ip_address('eth0')
    if str_ip == "0.0.0.0":
        str_ip = get_intranet_ip_address('wlan0')
    int_serial = get_serial()
    str_ext_url = get_external_url()
    hubdetails = Hub.query.first()
# Commit to db and call Server API only if there are any changes to PI Serial, internal_url, external_url 
    if (hubdetails.hub_id != int_serial and int_serial != 9999999999999999) or (hubdetails.internal_url != str_ip and str_ip != "0.0.0.0") or (hubdetails.external_url != str_ext_url and (str_ext_url != "Error" or str_ext_url != "ERROR")):
        hubdetails.hub_id       = int_serial
        hubdetails.internal_url = str_ip
        hubdetails.external_url = str_ext_url
        try:
            hubdetails.last_changed_by = g.user.username
        except:
            hubdetails.last_changed_by = str("BackendUser")
        hubdetails.last_changed_on = datetime.today()

        db.session.add(hubdetails)
        db.session.commit()
# Call Server API
        resp = server_update_hub(hubdetails)
# External URL is fetched, Server is updated
        if (str_ext_url != 'Error' or str_ext_url != 'ERROR') and resp != None:
            debug_msg('hub_started__external_url_fetched__server_updated', __file__, int_serial, str_ip, str_ext_url, resp, hubdetails.status)
# External URL is fetched, Server is not updated
        elif (str_ext_url != 'Error' or str_ext_url != 'ERROR') and resp == None:
            debug_msg('hub_started__external_url_fetched__server_not_updated', __file__, int_serial, str_ip, str_ext_url, resp, hubdetails.status)
# External URL is not fetched, Server is updated
        elif (str_ext_url == 'Error' or str_ext_url == 'ERROR') and resp != None:
            debug_msg('hub_started__external_url_not_fetched__server_updated', __file__, int_serial, str_ip, str_ext_url, resp, hubdetails.status)
# External URL is not fetched, Server is not updated
        else:
            debug_msg('hub_started__external_url_not_fetched__server_not_updated', __file__, int_serial, str_ip, str_ext_url, resp, hubdetails.status)