from flask import request, jsonify, g
from ..models import db, Hub, hub_schema, Endpoint, EndpointTypes, EndpointGroup, endpoint_schema, endpoint_schemas, endpoint_group_schema, endpoint_group_schemas
from . import api
from datetime import datetime
from ..auth import auth
from ..common import unique_endpoint, endpoint_validation, unique_group_desc
from ..errors import no_input, no_records, duplicate_group


@api.route('/groups/', methods=['GET'])
def get_groups():
    endpointgroups = EndpointGroup.query.all()
    if endpointgroups == None:
        return no_records('endpoint_group.get_groups.endpointgroup')
    # Serialize the queryset
    hub = Hub.query.first()
    if hub == None:
        return no_records('endpoint_group.get_groups.hub')
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    group_results = endpoint_group_schemas.dump(endpointgroups)
    return jsonify({'hub': hub_result.data, 'groups':group_results})


@api.route('/groups/', methods=['POST'])
def new_group():
    json_data = request.get_json()
    if not json_data:
        return no_input()
#         return jsonify({'message': 'No input data provided'}), 400
# Validate and deserialize input
    data, errors = endpoint_group_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Check Uniqueness (Group description should be unique)
    if not unique_group_desc(data['group_desc']):
        return duplicate_group()

# Create new Group
    endpointgroup = EndpointGroup(
                                    endpoint_uuid       = data['endpoint_uuid'],
                                    group_desc          = data['group_desc'],
                                    expected_status     = data['expected_status'],
                                    last_oper_by        = g.user.username,
                                    last_oper_at        = datetime.utcnow()
    )
    
    db.session.add(endpointgroup)
    db.session.commit()
    result = endpoint_group_schema.dump(EndpointGroup.query.get(endpointgroup.group_uuid))
    
    return jsonify({'message':'Group created', 'group':result})

@api.route('/groups/<uuid:gid>', methods=['PUT'])
def edit_group(gid):
    json_data = request.get_json()
    if not json_data:
        return no_input()
    data, errors = endpoint_group_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    endpointgroup = EndpointGroup.query.filter_by(group_uuid=gid).first()
    if endpointgroup == None:
        return no_records('endpoint_group.edit_group.endpointgroup',gid)
# Edit only descriptions in endpoint, though based on schema internal ID are compulsory
    endpointgroup.group_desc=data['group_desc']

    db.session.add(endpointgroup)
    db.session.commit()
    result = endpoint_group_schema.dump(EndpointGroup.query.get(endpointgroup.group_uuid))
    return jsonify({'message':'Group edited', 'group':result})


@api.route('/groups/<uuid:gid>', methods=['DELETE'])
def delete_group(gid):
    endpointgroup = EndpointGroup.query.filter_by(group_uuid=gid).first()
    if endpointgroup == None:
        return no_records('endpoint_group.delete_group.endpointgroup',gid)

    result = endpoint_group_schema.dump(Endpoint.query.get(endpointgroup.group_uuid))
    db.session.delete(endpointgroup)
    db.session.commit()
    return jsonify({'message':'Group deleted','Group':result})


@api.route('/groups/<uuid:gid>/<uuid:id>', methods=['DELETE'])
def delete_group_endpoint(gid,id):
    endpointgroup = EndpointGroup.query.filter_by(group_uuid=gid,endpoint_uuid=id).first()
    if endpointgroup == None:
        return no_records('endpoint_group.delete_group_endpoint.endpointgroup',gid,id)

    result = endpoint_group_schema.dump(Endpoint.query.get(endpointgroup.group_uuid))    
    db.session.delete(endpointgroup)
    db.session.commit()
    return jsonify({'message':'Endpoint deleted','Group':result})


@api.route('/groups/<uuid:gid>/<uuid:id>', methods=['POST'])
def new_group_endpoint(gid,id):
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = endpoint_group_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Check if group id exists or not    
    endpointgroup = EndpointGroup.query.filter_by(group_uuid=gid).first()
    if endpointgroup == None:
        return no_records('endpoint_group.new_group_endpoint.endpointgroup',gid,id)
# Validate Endpoint UUID and corresponding status
    if not (operate_validation(id,data['expected_status'])):
        return invalid_operation()
# Create new Endpoint in group
    endpointgroup = EndpointGroup(
                                    group_uuid          = gid,
                                    endpoint_uuid       = id,
                                    expected_status     = data['expected_status'],
                                    last_oper_by        = g.user.username,
                                    last_oper_at        = datetime.utcnow()
    )
    db.session.add(endpointgroup)
    db.session.commit()
    result = endpoint_group_schema.dump(EndpointGroup.query.get(endpointgroup.group_uuid))
    
    return jsonify({'message':'Endpoint created in group', 'group':result})


@api.route('/groups/<uuid:gid>/<uuid:id>', methods=['PUT'])
def edit_group_endpoint(gid,id):
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = endpoint_group_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    endpointgroup = EndpointGroup.query.filter_by(group_uuid=gid,endpoint_uuid=id).first()
    if endpointgroup == None:
        return no_records('endpoint_group.edit_group_endpoint.endpointgroup',gid,id)
# Validate Endpoint UUID and corresponding status
    if not (operate_validation(id,data['expected_status'])):
        return invalid_operation()

# Edit Endpoint in Group
    endpointgroup.expected_status     = data['expected_status']
    endpointgroup.last_oper_by        = g.user.username,
    endpointgroup.last_oper_at        = datetime.utcnow()

    db.session.add(endpointgroup)
    db.session.commit()

    result = endpoint_group_schema.dump(endpointgroup)
    
    return jsonify({'message':'Endpoint edited in group', 'group':result})