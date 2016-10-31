from flask import request, jsonify, g
from ..models import db, Hub, hub_schema, Endpoint, EndpointTypes, EndpointSchema, EndpointStatus, endpoint_schema, endpoint_schemas#, endpoint_status_schema
from . import api
from datetime import datetime
from ..auth import auth
from ..decorators import admin_role_required
from ..common import unique_endpoint, endpoint_validation, is_admin, server_sync_endpoints
from ..errors import no_input, duplicate_endpoint, invalid_endpoint, no_records, admin_right


@api.route('/endpoints/', methods=['GET'])
def get_endpoints():
    endpoints = Endpoint.query.all()
    if endpoints == None:
        return no_records('endpoint_conf.get_endpoints.endpoint')
    # Serialize the queryset
    hub = Hub.query.first()
    if hub == None:
        return no_records(endpoint_conf.get_endpoints.hub)
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    endpoint_results = endpoint_schemas.dump(endpoints)
    return jsonify({'hub': hub_result.data, 'endpoints':endpoint_results.data})


@api.route('/endpoints/', methods=['POST'])
@admin_role_required
def new_endpoint():
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = endpoint_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Validation logic eg. NodeTypes should match EndpointTypes
    if not (endpoint_validation(data)):
        return invalid_endpoint()
# Check Uniqueness (Section_ID, Node_ID and Endpoint_ID combined should be unique)
    if not unique_endpoint(data['internal_sec_id'], data['internal_nod_id'], data['internal_end_id']):
        return duplicate_endpoint()

# Create new Endpoint
    endpoint = Endpoint(
                        section_type        =data['section_type'],
                        internal_sec_id     =data['internal_sec_id'],
                        internal_sec_desc   =data['internal_sec_desc'],
                        internal_nod_id     =data['internal_nod_id'],
                        node_type           =data['node_type'],
                        internal_nod_desc   =data['internal_nod_desc'],
                        internal_end_id     =data['internal_end_id'],
                        endpoint_type       =data['endpoint_type'],
                        internal_end_desc   =data['internal_end_desc'],
                        last_changed_by     =g.user.username,
                        last_changed_on     =datetime.today()
    )
    
    db.session.add(endpoint)
    db.session.commit()
# Create new entry in EndpointStatus, so that status can be accessed from single source
    endpointstatus = EndpointStatus(
                                    endpoint_uuid   =endpoint.endpoint_uuid,
                                    status          =0,
                                    last_changed_by =g.user.username,
                                    last_changed_on =datetime.utcnow()                               
    )
    
    db.session.add(endpointstatus)
    db.session.commit()
# Sync endpoints with server
    server_sync_endpoints()

    result = endpoint_schema.dump(Endpoint.query.get(endpoint.id))
    
    return jsonify({'message':'Endpoint created', 'endpoint':result.data})

@api.route('/endpoints/<uuid:id>', methods=['PUT'])
def edit_endpoint(id):
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Check if valid endpoint id is supplied    
    endpoint = Endpoint.query.filter_by(endpoint_uuid=id).first()
    if endpoint == None:
        return no_records('endpoint_conf.edit_endpoints.endpoint',id)
# Deserialize and check for errors
    endpoint_schema_custom = EndpointSchema(partial=('section_type','internal_sec_id','internal_sec_desc','internal_nod_id','node_type','internal_nod_desc','internal_end_id','endpoint_type','internal_end_desc',))
    data, errors = endpoint_schema_custom.load(json_data)
    if errors:
        return jsonify(errors), 422

# Edit only descriptions in endpoint, though based on schema internal ID are compulsory
    if (is_admin(g.user.username)):
        try:    endpoint.section_type       =data['section_type']
        except: pass
        try:    endpoint.internal_sec_id    =data['internal_sec_id']
        except: pass
        try:    endpoint.internal_nod_id    =data['internal_nod_id']
        except: pass
        try:    endpoint.node_type          =data['node_type']
        except: pass
        try:    endpoint.internal_end_id    =data['internal_end_id']
        except: pass
        try:    endpoint.endpoint_type      =data['endpoint_type']
        except: pass
    try:    endpoint.internal_sec_desc      =data['internal_sec_desc']
    except: pass
    try:    endpoint.internal_nod_desc      =data['internal_nod_desc']
    except: pass
    try:    endpoint.internal_end_desc      =data['internal_end_desc']
    except: pass
    
    db.session.add(endpoint)
    db.session.commit()
# Sync endpoints with server
    server_sync_endpoints()
#  
    result = endpoint_schema.dump(Endpoint.query.get(endpoint.id))
    return jsonify({'message':'Endpoint edited', 'endpoint':result.data})

@api.route('/endpoints/<uuid:id>', methods=['DELETE'])
@admin_role_required
def delete_endpoint(id):
    endpoint = Endpoint.query.filter_by(endpoint_uuid=id).first()
    if endpoint == None:
        return no_records('endpoint_conf.delete_endpoints.endpoint',id)
    result = endpoint_schema.dump(Endpoint.query.get(endpoint.id))
    db.session.delete(endpoint)

    endpointstatus = EndpointStatus.query.filter_by(endpoint_uuid=id).first()
    if endpointstatus == None:
        return no_records('endpoint_conf.delete_endpoints.endpointstatus',id)
#     result_status = endpoint_schema.dump(Endpoint.query.get(endpoint.id))
    db.session.delete(endpointstatus)
    
    db.session.commit()
    return jsonify({'message':'Endpoint deleted','endpoint':result.data})