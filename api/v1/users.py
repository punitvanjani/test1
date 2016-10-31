from flask import request, jsonify, g
from ..models import db, Hub, hub_schema, User, user_schemas, user_schema, UserSchema
from . import api
from datetime import datetime
from ..auth import auth
from ..decorators import hub_active
from ..common import valid_user, is_admin, debug_msg, unique_user
from ..errors import no_input, invalid_user, duplicate_user
import traceback

 
@api.route('/users/', methods=['GET'])
def get_users():
    users = User.query.all()
    hub = Hub.query.first()
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    # Serialize the queryset
    result = user_schemas.dump(users)
    return jsonify({'hub': hub_result.data,'users':result})


@api.route('/users/', methods=['POST'])
def new_users():
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = user_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Check Uniqueness (Section_ID, Node_ID and Endpoint_ID combined should be unique)
    if not unique_user(data['username']):
        return duplicate_user()
# 
# Create new User
    user = User(
                username    =data['username'],
                group       =data['group'],
                password    =data['password'],
                mobile_no   =data['mobile_no'],
                email       =data['email'],
                login_date  =data['login_date'],
                created_date=datetime.today()
    )
    db.session.add(user)
    db.session.commit()
    result = user_schema.dump(user.query.get(user.id))
    return jsonify({'message':'User created','User':result})

@api.route('/users/<string:username>', methods=['PUT'])
def edit_users(username):
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Check Valid User
    if not valid_user(username):
        return invalid_user()
# Validate and deserialize input
    user_schema_custom = UserSchema(partial=('username','group','password','mobile_no','email','login_date',))
    data, errors = user_schema_custom.load(json_data)
    if errors:
        return jsonify(errors), 422
# Change User
    user = User.query.filter_by(username=username).first()
#
# Change those parameters that are passed, Group should be changed only by ADMIN user
#     debug_msg(g.user.username)
    if (is_admin(g.user.username)):
        try:    user.group=data['group']
        except: pass
    try:    user.password=data['password']
    except: pass
    try:    user.mobile_no=data['mobile_no']    
    except: pass
    try:    user.email=data['email']
    except: pass
    try:    user.login_date=data['login_date']
    except: pass
#   return jsonify(exception=traceback.format_exc())
    
    db.session.add(user)
    db.session.commit()
    result = user_schema.dump(user.query.filter_by(username=user.username).first())
     
    return jsonify({'message':'User edited','User':result})