from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from .helpers import args_from_url
from .errors import ValidationError
from sqlalchemy import types
from sqlalchemy.databases import mysql
from marshmallow import Schema, fields, ValidationError, pre_load, validate
import uuid

db = SQLAlchemy()

class UUID(types.TypeDecorator):
    impl = mysql.MSBinary
    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self,length=self.impl.length)

    def process_bind_param(self,value,dialect=None):
        if value and isinstance(value,uuid.UUID):
            return value.bytes
        elif value and not isinstance(value,uuid.UUID):
            raise ValueError,'value %s is not a valid uuid.UUID' % value
        else:
            return None

    def process_result_value(self,value,dialect=None):
        if value:
            uniq_uuid = uuid.UUID(bytes=value)
            return uniq_uuid
        else:
            return None

    def is_mutable(self):
        return False

    
class Properties(db.Model):
    __tablename__       = 'properties'
    id                  = db.Column(db.Integer, primary_key=True)
    key                 = db.Column(db.String, unique=True, index = True)        # Defines any properties key, value
    value               = db.Column(db.String, index=True)
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)


class Hub(db.Model):
    __tablename__       = 'hub'
    id                  = db.Column(db.Integer, primary_key=True)
    hub_id              = db.Column(db.Integer, unique=True)        # Hub ID internally populated by other script
    hub_type            = db.Column(db.Integer)
    description         = db.Column(db.String(255))
    external_url        = db.Column(db.String(255))
    internal_url        = db.Column(db.String(255))
    status              = db.Column(db.Boolean, default=True)       # Hub's status (Active = True, Inactive = False
    activated_at        = db.Column(db.DateTime)                    # When was Hub activated, as of 17-Jan-16 it would when the record was created
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)
    

class HubTypes(db.Model):
    __tablename__       = 'hub_types'
    id                  = db.Column(db.Integer, primary_key=True)
    hub_type            = db.Column(db.Integer)                     # Section Types eg. 10=Switching, 11=TV remote, 12=Camera, etc
    hub_type_desc       = db.Column(db.String)
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)    


class SectionTypes(db.Model):
    __tablename__       = 'section_types'
    id                  = db.Column(db.Integer, primary_key=True)
    section_type        = db.Column(db.Integer)                     # Section Types eg. 10=House:Living Room, 11=Kitchen, 12=Bedroom, 13=Bathroom etc,
    section_type_desc   = db.Column(db.String)
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)    


class EndpointTypes(db.Model):
    __tablename__       = 'endpoint_types'
    id                  = db.Column(db.Integer, primary_key=True)
    node_type           = db.Column(db.Integer)                     # Node Types eg. 10=Webswitch, 11=TouchPanel, 12=TV, 13=Music, 14=AC
    node_type_desc      = db.Column(db.String)
    node_category       = db.Column(db.String, default = 'simple')  # This field marks if the Node is of complex or simple type
    endpoint_type       = db.Column(db.Integer)                     # Endpoint types depends on NodeTypes eg. NodeType 10 - 10=Switch 11=Dimmer
    endpoint_type_desc  = db.Column(db.String)
    status_min          = db.Column(db.Integer)
    status_max          = db.Column(db.Integer)
    method              = db.Column(db.String)
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)


class Endpoint(db.Model):
    __tablename__       = 'endpoint'
    id                  = db.Column(db.Integer, primary_key=True)
    internal_sec_id     = db.Column(db.Integer)        # Defines the Room/Section number that has been given during Installation, this is what is considered during operation
    section_type        = db.Column(db.Integer)                     # Section Types eg. 10=House:Living Room, 11=Kitchen, 12=Bedroom, 13=Bathroom etc, 
    internal_sec_desc   = db.Column(db.String(255), index=True)
    internal_nod_id     = db.Column(db.Integer)        # Defines the Node number that has been given during Installation, this is what is considered during operation
    node_type           = db.Column(db.Integer)                     # Node Types eg. 10=Webswitch, 11=TouchPanel, 12=TV, 13=Music, 14=AC
    internal_nod_desc   = db.Column(db.String(255), index=True)
    internal_end_id     = db.Column(db.Integer)        # Defines the Endpoint number that has been given during Installation, this is what is considered during operation
    endpoint_type       = db.Column(db.Integer)                     # Endpoint types depends on NodeTypes eg. NodeType 10 - 10=Switch 11=Dimmer
    endpoint_uuid       = db.Column(UUID(), default = uuid.uuid4, index=True)
    internal_end_desc   = db.Column(db.String(255), index=True)
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)

class WSNodeStatus(db.Model):
    __tablename__       = 'ws_node_status'
    internal_nod_id     = db.Column(db.Integer, primary_key=True)
    status              = db.Column(db.Integer)

class EndpointStatus(db.Model):
    __tablename__       = 'endpoint_status'
    endpoint_uuid       = db.Column(UUID(), primary_key=True)
    status              = db.Column(db.Integer)
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)


class EndpointGroup(db.Model):
    __tablename__       = 'endpoint_group'
    group_uuid          = db.Column(UUID(), primary_key=True, default = uuid.uuid4)
    endpoint_uuid       = db.Column(UUID(), primary_key=True)
    group_desc          = db.Column(db.String)
    expected_status     = db.Column(db.Integer)
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)

class Schedule(db.Model):
    __tablename__       = 'schedule'
    id                  = db.Column(db.Integer, primary_key=True)
    uuid_id             = db.Column(UUID(), index=True)        # UUID = Endpoint UUID or Group UUID
    expected_status     = db.Column(db.Integer)                                      # Expected Status when scheduler value is true
    year                = db.Column(db.Integer)
    month               = db.Column(db.Integer)
    weekday             = db.Column(db.Integer)
    date                = db.Column(db.Integer)
    hour                = db.Column(db.Integer)
    min                 = db.Column(db.Integer)
    hourly              = db.Column(db.Boolean, default = False)
    daily               = db.Column(db.Boolean, default = False)
    weekly              = db.Column(db.Boolean, default = False)
    monthly             = db.Column(db.Boolean, default = False)
    yearly              = db.Column(db.Boolean, default = False)
    onlyonce            = db.Column(db.Boolean, default = True)
    status              = db.Column(db.Boolean, default=True)                        # Schedule status (Active = True, Inactive = False
    last_changed_by     = db.Column(db.String)
    last_changed_on     = db.Column(db.DateTime)                                     # When was Hub activated, as of 17-Jan-16 it would when the record was created


class User(db.Model):
    __tablename__ = 'users'
    id                  = db.Column(db.Integer, primary_key=True)
    username            = db.Column(db.String(), index=True)
    group               = db.Column(db.String(), default = 'USER')
    password_hash       = db.Column(db.String(128))
    mobile_no           = db.Column(db.Integer)
    email               = db.Column(db.String)
    login_date          = db.Column(db.DateTime)
    created_date        = db.Column(db.DateTime)
    

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


##### SCHEMAS #####
# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class PropertiesSchema(Schema):
    id                  = fields.Int(dump_only=True)
    key                 = fields.Str()
    value               = fields.Str()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class HubSchema(Schema):
    id                  = fields.Int(dump_only=True)
    hub_id              = fields.Int()
    hub_type            = fields.Int()
    description         = fields.Str()
    external_url        = fields.Str()
    internal_url        = fields.Str()
    status              = fields.Bool()
    activated_at        = fields.DateTime(dump_only=True)
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class HubTypesSchema(Schema):
    id                  = fields.Int(dump_only=True)
    hub_type            = fields.Number(validate=lambda n: 10 <= n <= 99)
    hub_type_desc       = fields.Str()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class SectionTypesSchema(Schema):
    id                  = fields.Int(dump_only=True)
    section_type        = fields.Number(validate=lambda n: 10 <= n <= 99)
    section_type_desc   = fields.Str()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class EndpointTypesSchema(Schema):
    id                  = fields.Int(dump_only=True)
    node_type           = fields.Number(validate=lambda n: 10 <= n <= 99)
    node_type_desc      = fields.Str()
    node_category       = fields.Str()
    endpoint_type       = fields.Number(validate=lambda n: 1000 <= n <= 9999)
    endpoint_type_desc  = fields.Str()
    status_min          = fields.Int()
    status_max          = fields.Int()
    method              = fields.Str()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class EndpointSchema(Schema):
    id                  = fields.Int(dump_only=True)
    internal_sec_id     = fields.Int(required=True)
    section_type        = fields.Number(validate=lambda n: 10 <= n <= 99)
    internal_sec_desc   = fields.Str()
    internal_nod_id     = fields.Int(required=True)
    node_type           = fields.Number(validate=lambda n: 10 <= n <= 99)
    internal_nod_desc   = fields.Str()
    internal_end_id     = fields.Int(required=True)
    endpoint_type       = fields.Number(validate=lambda n: 1000 <= n <= 9999)
    endpoint_uuid       = fields.UUID(dump_only=True)
    internal_end_desc   = fields.Str()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class EndpointStatusSchema(Schema):
    endpoint_uuid       = fields.UUID()
    status              = fields.Int()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class EndpointGroupSchema(Schema):
    group_uuid          = fields.UUID(dump_only=True)
    endpoint_uuid       = fields.UUID()
    group_desc          = fields.Str(required=True)
    expected_status     = fields.Int()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)

class ScheduleSchema(Schema):
    id                  = db.Column(db.Integer, primary_key=True)
    uuid_id             = fields.UUID()
    expected_status     = fields.Int()                                      # Expected Status when scheduler value is true
    year                = fields.Int() 
    month               = fields.Int() 
    weekday             = fields.Int() 
    date                = fields.Int() 
    hour                = fields.Int() 
    min                 = fields.Int() 
    hourly              = fields.Bool()
    daily               = fields.Bool()
    weekly              = fields.Bool()
    monthly             = fields.Bool()
    yearly              = fields.Bool()
    onlyonce            = fields.Bool()
    status              = fields.Bool()
    last_changed_by     = fields.Str(validate=[validate.Length(max=64)])
    last_changed_on     = fields.DateTime(dump_only=True)


class UserSchema(Schema):
    id                  = fields.Int(dump_only=True)
    username            = fields.Str(validate=[validate.Length(max=64)])
    group               = fields.Str(validate=[validate.Length(max=50)])
    password            = fields.Str(validate=[validate.Length(min=6, max=36)],load_only=True)
    mobile_no           = fields.Int()
    email               = fields.Str()    
    login_date          = fields.DateTime()
    created_date        = fields.DateTime()



# properties_schema       = PropertiesSchema(exclude=('id',))
properties_schema       = PropertiesSchema()
properties_schemas      = PropertiesSchema(many=True)
hub_schema              = HubSchema()
section_types_schema    = SectionTypesSchema()
section_types_schemas   = SectionTypesSchema(many=True)
endpoint_types_schema   = EndpointTypesSchema()
endpoint_types_schemas  = EndpointTypesSchema(many=True)
endpoint_schema         = EndpointSchema()
endpoint_schemas        = EndpointSchema(many=True)
endpoint_status_schema  = EndpointStatusSchema()
endpoint_status_schemas = EndpointStatusSchema(many=True)
endpoint_group_schema   = EndpointGroupSchema()
endpoint_group_schemas  = EndpointGroupSchema(many=True)
schedule_schema         = ScheduleSchema()
schedule_schemas        = ScheduleSchema(many=True) 
user_schema             = UserSchema()
user_schemas            = UserSchema(many=True)