#!/usr/bin/env python
from flask import current_app, Flask, g, jsonify
from flask.ext.script import Manager, Server
from api.app import create_app
from api.models import db, User, Hub, Schedule, HubTypes, Endpoint, EndpointTypes, SectionTypes, Properties
from api.common import system_start, server_sync_endpoints, server_update_hub, debug_msg, scheduled_endpoints_groups
from api.v1.interfaces import webswitch
from datetime import datetime
import os
import time
import requests
import uuid

manager = Manager(create_app)


@manager.command
def createdb():
    """Drop all the data from tables and create/rearrange new tables"""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
# Adding default data if data is dropped and created again
#         u1 = User(username='vin',       group = 'USER',     password='asdfgh')
        u2 = User(username='admin',     group = 'ADMIN',    password='asdfgh')
        u3 = User(username='appadmin',  group = 'ADMIN',    password='asdfgh')
#  
        hub1 = Hub(hub_id=1234, hub_type = 10, description='testinghub',external_url='192.168.0.117',internal_url='10.0.0.2',status=True,activated_at=datetime.today(),last_changed_by='BackendUser',last_changed_on=datetime.today())
# Section Types eg. # Hub Types eg. 10=Switching, 11=TV Remote, 12=Camera, 11=Kitchen, 12=Bedroom, 13=Bathroom etc,
        hub_type1 = HubTypes(hub_type=10,   hub_type_desc='Switching',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        hub_type2 = HubTypes(hub_type=11,   hub_type_desc='TV Remote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        hub_type3 = HubTypes(hub_type=12,   hub_type_desc='Camera',         last_changed_by='BackendUser',    last_changed_on=datetime.today())
# Section Types eg. # Section Types eg. 10=House:Living Room, 11=Kitchen, 12=Bedroom, 13=Bathroom etc,
        sec_type1  = SectionTypes(section_type=10, section_type_desc='Balcony',          last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type2  = SectionTypes(section_type=11, section_type_desc='Bathroom',        last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type3  = SectionTypes(section_type=12, section_type_desc='Bedroom',         last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type4  = SectionTypes(section_type=13, section_type_desc='Cellar',          last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type5  = SectionTypes(section_type=14, section_type_desc='Common Room',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type6  = SectionTypes(section_type=15, section_type_desc='Dining Room',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type7  = SectionTypes(section_type=16, section_type_desc='Drawing Room',    last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type8  = SectionTypes(section_type=17, section_type_desc='Dressing Room',   last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type9  = SectionTypes(section_type=18, section_type_desc='Family Room',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type10 = SectionTypes(section_type=19, section_type_desc='Front Room',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type11 = SectionTypes(section_type=20, section_type_desc='Garden',          last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type12 = SectionTypes(section_type=21, section_type_desc='Guest Room',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type13 = SectionTypes(section_type=22, section_type_desc='Kitchen',         last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type14 = SectionTypes(section_type=23, section_type_desc='Living room',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type15 = SectionTypes(section_type=24, section_type_desc='Lobby',           last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type16 = SectionTypes(section_type=25, section_type_desc='Servant room',    last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type17 = SectionTypes(section_type=26, section_type_desc='Store room',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type18 = SectionTypes(section_type=27, section_type_desc='Terrace',         last_changed_by='BackendUser',    last_changed_on=datetime.today())
        sec_type19 = SectionTypes(section_type=28, section_type_desc='Waiting Room',    last_changed_by='BackendUser',    last_changed_on=datetime.today())

# Node Types eg. 10=Webswitch, 11=TouchPanel, 12=TV, 13=Music, 14=AC
        ep_type1 = EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1000, endpoint_type_desc = 'Switch',        status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type2 = EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1001, endpoint_type_desc = 'Dimmer',        status_min=1, status_max=10,method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type3 = EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1002, endpoint_type_desc = '30A Switch',    status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type4 = EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1003, endpoint_type_desc = 'Curtain',       status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type5 = EndpointTypes(node_type=11, node_type_desc = 'SparshTouchSwitch',    endpoint_type=1100, endpoint_type_desc = 'Switch',        status_min=0, status_max=1, method='touchswitch',   last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type6 = EndpointTypes(node_type=11, node_type_desc = 'SparshTouchSwitch',    endpoint_type=1101, endpoint_type_desc = 'Dimmer',        status_min=1, status_max=10,method='touchswitch',   last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type7 = EndpointTypes(node_type=11, node_type_desc = 'SparshTouchSwitch',    endpoint_type=1102, endpoint_type_desc = '30A Switch',    status_min=0, status_max=1, method='touchswitch',   last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type8 = EndpointTypes(node_type=11, node_type_desc = 'SparshTouchSwitch',    endpoint_type=1103, endpoint_type_desc = 'Curtain',       status_min=0, status_max=1, method='touchswitch',   last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type9 = EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1200, endpoint_type_desc = 'Channel +',     status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type10= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1201, endpoint_type_desc = 'Channel -',     status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type11= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1202, endpoint_type_desc = 'Volume +',      status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type12= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1203, endpoint_type_desc = 'Volume -',      status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type13= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1204, endpoint_type_desc = 'Mute',          status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type14= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1205, endpoint_type_desc = 'Menu',          status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type15= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1206, endpoint_type_desc = 'Ok',            status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type16= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1207, endpoint_type_desc = 'Source',        status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type17= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1208, endpoint_type_desc = 'On/Off',        status_min=2, status_max=2, method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type49= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1299, endpoint_type_desc = 'TV',            status_min=99,status_max=99,method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   node_category='complex')
        ep_type18= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1300, endpoint_type_desc = 'On/Off',        status_min=2, status_max=2, method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type19= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1301, endpoint_type_desc = 'Channel +',     status_min=2, status_max=2, method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type20= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1302, endpoint_type_desc = 'Channel -',     status_min=2, status_max=2, method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type21= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1303, endpoint_type_desc = 'Volume +',      status_min=2, status_max=2, method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type22= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1304, endpoint_type_desc = 'Volume -',      status_min=2, status_max=2, method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type23= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1305, endpoint_type_desc = 'Mute',          status_min=2, status_max=2, method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type24= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1306, endpoint_type_desc = 'Menu',          status_min=2, status_max=2, method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type50= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1399, endpoint_type_desc = 'Settop Box',    status_min=99,status_max=99,method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today(),   node_category='complex')
        ep_type25= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1400, endpoint_type_desc = 'Temp +',        status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type26= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1401, endpoint_type_desc = 'Temp -',        status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type27= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1402, endpoint_type_desc = 'Fan +',         status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type28= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1403, endpoint_type_desc = 'Fan -',         status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type29= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1404, endpoint_type_desc = 'Swing',         status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type30= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1405, endpoint_type_desc = 'Mode',          status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type48= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1406, endpoint_type_desc = 'On/Off',        status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type51= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1499, endpoint_type_desc = 'AC',            status_min=99,status_max=99,method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   node_category='complex')
        ep_type31= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1004, endpoint_type_desc = 'Computer',      status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type32= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1005, endpoint_type_desc = 'Iron',          status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type33= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1006, endpoint_type_desc = 'Refrigerator',  status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type34= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1007, endpoint_type_desc = 'Washing Machine',status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type35= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1008, endpoint_type_desc = 'Printer',       status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type36= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1009, endpoint_type_desc = 'Geyser',        status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type37= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1010, endpoint_type_desc = 'Dressing Table',status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type38= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1011, endpoint_type_desc = 'Microwave',     status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type39= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1012, endpoint_type_desc = 'Tubelight',     status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type40= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1013, endpoint_type_desc = 'Focus Lamp',    status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type41= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1014, endpoint_type_desc = 'Table Lamp',    status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type42= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1015, endpoint_type_desc = 'Outer Light',   status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type43= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1016, endpoint_type_desc = 'CFL',           status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type44= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1017, endpoint_type_desc = 'Socket',        status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type45= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1018, endpoint_type_desc = 'Chandelier',    status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type46= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1019, endpoint_type_desc = 'Music Player',  status_min=0, status_max=1, method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
        ep_type47= EndpointTypes(node_type=10, node_type_desc = 'Webswitch',            endpoint_type=1020, endpoint_type_desc = 'Fan',           status_min=1, status_max=10,method='webswitch',     last_changed_by='BackendUser',    last_changed_on=datetime.today())
#         ep_type48= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1406, endpoint_type_desc = 'On/Off',        status_min=2, status_max=2, method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today())
#         ep_type49= EndpointTypes(node_type=12, node_type_desc = 'TV',                   endpoint_type=1299, endpoint_type_desc = 'TV',            status_min=99,status_max=99,method='tvremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   node_category='complex')
#         ep_type50= EndpointTypes(node_type=13, node_type_desc = 'Settop Box',           endpoint_type=1399, endpoint_type_desc = 'Settop Box',    status_min=99,status_max=99,method='settopbox',     last_changed_by='BackendUser',    last_changed_on=datetime.today(),   node_category='complex')
#         ep_type51= EndpointTypes(node_type=14, node_type_desc = 'AC',                   endpoint_type=1499, endpoint_type_desc = 'AC',            status_min=99,status_max=99,method='acremote',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   node_category='complex')

        dbg_prop = Properties(key='DEBUG',          last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='true')
        ser_prop = Properties(key='ServerAPI',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='http://shubansolutions.com/etct/ws/')
        cph_prop = Properties(key='ContactPh',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='1234567890')
        cad_prop = Properties(key='ContactAd',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='1, street2, area3, city4, pin5')
        cws_prop = Properties(key='ContactWs',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='http://www.etct.in')
        cml_prop = Properties(key='ContactMl',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='etct.in@gmail.com')
        seu_prop = Properties(key='ServerUsr',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='admin')
        sep_prop = Properties(key='ServerPwd',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='et111ct')
        wsc_prop = Properties(key='WbSwtComm',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='/dev/ttyUSB0')
        wsb_prop = Properties(key='WbSwtBaud',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='9600')
        wsf_prop = Properties(key='WbSwtSFrq',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='3')
        stc_prop = Properties(key='StSwtComm',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='/dev/ttyAMA0')
        stb_prop = Properties(key='StSwtBaud',      last_changed_by='BackendUser',    last_changed_on=datetime.today(),   value='19200')
# 
        db.session.add(hub1)
# 
        db.session.add(hub_type1)
        db.session.add(hub_type2)
        db.session.add(hub_type3)
# 
#         db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
#
        db.session.add(sec_type1)
        db.session.add(sec_type2)
        db.session.add(sec_type3)
        db.session.add(sec_type4)
        db.session.add(sec_type5)
        db.session.add(sec_type6)
        db.session.add(sec_type7)
        db.session.add(sec_type8)
        db.session.add(sec_type9)
        db.session.add(sec_type10)
        db.session.add(sec_type11)
        db.session.add(sec_type12)
        db.session.add(sec_type13)
        db.session.add(sec_type14)
        db.session.add(sec_type15)
        db.session.add(sec_type16)
        db.session.add(sec_type17)
        db.session.add(sec_type18)
        db.session.add(sec_type19)
#
        db.session.add(ep_type1)
        db.session.add(ep_type2)
        db.session.add(ep_type3)
        db.session.add(ep_type4)
        db.session.add(ep_type5)
        db.session.add(ep_type6)
        db.session.add(ep_type7)
        db.session.add(ep_type8)
        db.session.add(ep_type9)
        db.session.add(ep_type10)
        db.session.add(ep_type11)
        db.session.add(ep_type12)
        db.session.add(ep_type13)
        db.session.add(ep_type14)
        db.session.add(ep_type15)
        db.session.add(ep_type16)
        db.session.add(ep_type17)
        db.session.add(ep_type18)
        db.session.add(ep_type19)
        db.session.add(ep_type20)
        db.session.add(ep_type21)
        db.session.add(ep_type22)
        db.session.add(ep_type23)
        db.session.add(ep_type24)
        db.session.add(ep_type25)
        db.session.add(ep_type26)
        db.session.add(ep_type27)
        db.session.add(ep_type28)
        db.session.add(ep_type29)
        db.session.add(ep_type30)
        db.session.add(ep_type31)
        db.session.add(ep_type32)
        db.session.add(ep_type33)
        db.session.add(ep_type34)
        db.session.add(ep_type35)
        db.session.add(ep_type36)
        db.session.add(ep_type37)
        db.session.add(ep_type38)
        db.session.add(ep_type39)
        db.session.add(ep_type40)
        db.session.add(ep_type41)
        db.session.add(ep_type42)
        db.session.add(ep_type43)
        db.session.add(ep_type44)
        db.session.add(ep_type45)
        db.session.add(ep_type46)
        db.session.add(ep_type47)
        db.session.add(ep_type48)
        db.session.add(ep_type49)
        db.session.add(ep_type50)
        db.session.add(ep_type51)
#
        db.session.add(dbg_prop)
        db.session.add(ser_prop)
        db.session.add(cph_prop)
        db.session.add(cad_prop)
        db.session.add(cws_prop)
        db.session.add(cml_prop)
        db.session.add(seu_prop)
        db.session.add(sep_prop)
        db.session.add(wsc_prop)
        db.session.add(wsb_prop)
        db.session.add(wsf_prop)
        db.session.add(stc_prop)
        db.session.add(stb_prop)
#
        db.session.commit()


@manager.command
def adduser(username):
    """Register a new user."""
    from getpass import getpass
    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys
        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))

@manager.command
def ngrokstart():
    """Starting services running in crontab for every minute"""
    try:
        r = requests.get('http://localhost:4040/api/tunnels')
        datajson = r.json()
        msg=None
        for i in datajson['tunnels']:
# Check if https ngrok url is present or not
            if 'https' in i['public_url']:
                msg = i['public_url']
    except requests.exceptions.ConnectionError:
        r = None
        msg = "Error"
    except requests.exceptions.RequestException:
        r = None
        msg = "ERROR"
# Launch ngrok agent only if there are URL service running
    if msg == 'Error' or msg == 'ERROR':
        try:
            cmd = "./vin/ngrok http 8083"
            p = os.popen(cmd,"r")
# Sleep for 10 secs as ngrok agent takes around 4-5 seconds to be up
            time.sleep(10)
        except:
            pass

@manager.command
def start():
    """Starting services running in crontab for every minute"""
    system_start()

@manager.command
def startonlyonce():
    """Starting services only during restart"""
    hubdetails = Hub.query.first()
    server_update_hub(hubdetails)
    server_sync_endpoints()


@manager.command
def scheduled_tasks():
    """Run the Schedule tasks, this command is called every min by cron jobs"""
# Get Endpoints / Groups that are to be triggered at this min
    endpoints,endpointgroups, endpoint_status = scheduled_endpoints_groups()
# Need to comment next line
    endpointtypes = EndpointTypes.query.get(1)
    status = 1
    if endpoints != None:
        i = 0
        for endpoint in endpoints:
            interface_status = webswitch(endpoint,endpointtypes,endpoint_status[i])
            debug_msg(interface_status, endpoint.endpoint_uuid)
            i += 1

if __name__ == '__main__':
    server = Server(host="0.0.0.0", port="8083", use_debugger=True)
    manager.add_command("runserver", server)
    manager.run()
