from flask import current_app, request, jsonify, g, send_from_directory
from ..models import db, Hub, Properties, hub_schema, properties_schema, properties_schemas
from . import api
from datetime import datetime
from ..auth import auth
from ..common import debug_msg, is_admin, unique_property
from ..mail import send_mail
from ..decorators import admin_role_required
from ..errors import no_input, no_records, admin_right, duplicate_property


@api.route('/properties/', methods=['GET'])
@admin_role_required
def get_properties():
# Check if user is admin or not
    if not is_admin(g.user.username):
        return admin_right()
    properties = Properties.query.all()
    if properties == None:
        return no_records('properties.get_properties.properties')
# Serialize the queryset
    properties_results = properties_schemas.dump(properties)
#
    hub = Hub.query.first()
    if hub == None:
        return no_records('properties.get_properties.hub')
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    return jsonify({'hub': hub_result.data, 'properties':properties_results.data})


@api.route('/properties/', methods=['POST'])
@admin_role_required
def new_properties():
# Check if user is admin or not
    if not is_admin(g.user.username):
        return admin_right()
#
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = properties_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Check Uniqueness (Group description should be unique)
    if not unique_property(data['key']):
        print "entered"
        return duplicate_property()
# Create new Property
    property = Properties(
                            key             = data['key'],
                            value           = data['value'],
                            last_changed_by = g.user.username,
                            last_changed_on = datetime.utcnow()
                        )
    
    db.session.add(property)
    db.session.commit()
    result = properties_schema.dump(Properties.query.get(property.id))
    
    return jsonify({'message':'Property created', 'property':result})

@api.route('/properties/<string:key>', methods=['PUT'])
@admin_role_required
def edit_properties(key):
    json_data = request.get_json()
    if not json_data:
        return no_input()
    data, errors = properties_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# 
    properties = Properties.query.filter_by(key=key).first()
    if properties == None:
        return no_records('properties.edit_properties.properties',key)

    properties.value=data['value']
    properties.last_changed_by = g.user.username
    properties.last_changed_on = datetime.today()
# Check if the value is 'logfileclear' then clear the log file and mark debug = true
    if properties.key == 'DEBUG' and data['value'] == 'logfileclear':
#         send_mail('punit.vanjani@gmail.com', 'vinrap@gmail.com', 'subject', 'texthere', files=current_app.config['LOG_FILE'])
        f = open(current_app.config['LOG_FILE'],'w')
        f.write('')
        f.close()
        properties.value='true'
#
    db.session.add(properties)
    db.session.commit()
    result = properties_schema.dump(Properties.query.filter_by(key=properties.key).first())
    return jsonify({'message':'Property edited', 'properties':result})

@api.route('/properties/logfile', methods=['GET'])
@admin_role_required
def get_logfile():
    return send_from_directory(current_app.config['BASE_DIR'], 'log.log',as_attachment=True)

