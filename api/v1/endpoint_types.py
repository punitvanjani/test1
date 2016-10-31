from flask import request, jsonify, g
from ..models import db, Hub, EndpointTypes, SectionTypes, EndpointTypesSchema, SectionTypesSchema, hub_schema, endpoint_types_schemas, endpoint_types_schema, section_types_schemas, section_types_schema
from . import api
from ..auth import auth
from ..common import unique_section_type
from datetime import datetime
from ..decorators import admin_role_required
from ..common import unique_endpoint_type
from ..errors import no_input, duplicate_endpoint_type, duplicate_section_type, no_records, admin_right


@api.route('/endpoint_types/', methods=['GET'])
@admin_role_required
def get_endpoint_types():
    endpoint_types = EndpointTypes.query.all()
    if endpoint_types == None:
        return no_records('endpoint_types.get_endpoint_types.endpoint_types')
    # Serialize the queryset
    endpoint_types_results = endpoint_types_schemas.dump(endpoint_types)
#  
    hub = Hub.query.first()
    if hub == None:
        return no_records('endpoint_types.get_endpoint_types.hub')
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
#  
    section_types = SectionTypes.query.all()
    if section_types == None:
        return no_records('endpoint_types.get_endpoint_types.section_types')
    # Serialize the queryset
    section_types_results = section_types_schemas.dump(section_types)

    return jsonify({'hub': hub_result.data, 'endpoint_types':endpoint_types_results.data, 'section_types':section_types_results.data})


@api.route('/endpoint_types/', methods=['POST'])
@admin_role_required
def new_endpoint_types():
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = endpoint_types_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Check Uniqueness (Section_ID, Node_ID and Endpoint_ID combined should be unique)
    if not unique_endpoint_type(data['node_type'], data['endpoint_type']):
        return duplicate_endpoint_type()

# Create new Endpoint
    endpointtype = EndpointTypes(
                                    node_type=data['node_type'],
                                    node_type_desc=data['node_type_desc'],
                                    node_category=data['node_category'],
                                    endpoint_type=data['endpoint_type'],
                                    endpoint_type_desc=data['endpoint_type_desc'],
                                    status_min=data['status_min'],
                                    status_max=data['status_max'],
                                    method=data['method']
    )
    
    db.session.add(endpointtype)
    db.session.commit()

    result = endpoint_types_schema.dump(EndpointTypes.query.get(endpointtype.id))
   
    return jsonify({'message':'Endpoint Type created', 'endpoint_type':result.data})

@api.route('/endpoint_types/<int:node_type_id>/<int:endpoint_type_id>', methods=['PUT'])
@admin_role_required
def edit_endpoint_types(node_type_id,endpoint_type_id):
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Check valid NodeType and Endpoint Type
    if unique_endpoint_type(node_type_id, endpoint_type_id):
        return duplicate_endpoint_type(message="Invalid combination of Node Type and Endpoint Type")

# Validate and deserialize input
    endpoint_types_schema_custom = EndpointTypesSchema(partial=('node_type','node_category','endpoint_type','node_type_desc','endpoint_type_desc','status_min','status_max','method',))
    data, errors = endpoint_types_schema_custom.load(json_data)
    if errors:
        return jsonify(errors), 422
    endpoint_types = EndpointTypes.query.filter_by(node_type=node_type_id,endpoint_type=endpoint_type_id).first()
    try:    endpoint_types.node_type_desc=data['node_type_desc']
    except: pass
    try:    endpoint_types.endpoint_type_desc=data['endpoint_type_desc']
    except: pass
    try:    endpoint_types.status_min=data['status_min']    
    except: pass
    try:    endpoint_types.status_max=data['status_max']
    except: pass
    try:    endpoint_types.method=data['method']
    except: pass
#   return jsonify(exception=traceback.format_exc())

    
    db.session.add(endpoint_types)
    db.session.commit()

#     result = EndpointTypes.query.filter_by(node_type=node_type_id,endpoint_type=endpoint_type_id).first()

    result = endpoint_types_schema.dump(EndpointTypes.query.filter_by(node_type=node_type_id,endpoint_type=endpoint_type_id).first())
   
    return jsonify({'message':'Endpoint Type edited', 'endpoint_type':result.data})

@api.route('/section_types/', methods=['POST'])
@admin_role_required
def new_section_types():
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = section_types_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Check Uniqueness (Section_ID, Node_ID and Endpoint_ID combined should be unique)
    if not unique_section_type(data['section_type']):
        return duplicate_section_type()

# Create new Endpoint
    sectiontype = SectionTypes(
                                    section_type        = data['section_type'],
                                    section_type_desc   = data['section_type_desc'],
                                    last_changed_by     = g.user.username,
                                    last_changed_on     = datetime.today()                                    
    )
    
    db.session.add(sectiontype)
    db.session.commit()

    result = section_types_schema.dump(SectionTypes.query.get(sectiontype.id))
   
    return jsonify({'message':'Section Type created', 'section_type':result})

@api.route('/section_types/<int:section_type_id>', methods=['PUT'])
@admin_role_required
def edit_section_types(section_type_id):
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Check valid NodeType and Endpoint Type
    if unique_section_type(section_type_id):
        return duplicate_section_type(message="Invalid Section Type")

# Validate and deserialize input
    section_types_schema_custom = SectionTypesSchema(partial=('section_type',))
    data, errors = section_types_schema_custom.load(json_data)
    if errors:
        return jsonify(errors), 422
    section_types = SectionTypes.query.filter_by(section_type=section_type_id).first()
    try:    section_types.section_type_desc=data['section_type_desc']
    except: pass
    section_types.last_changed_by     = g.user.username
    section_types.last_changed_on     = datetime.today()       
    
    db.session.add(section_types)
    db.session.commit()

#     result = EndpointTypes.query.filter_by(node_type=node_type_id,endpoint_type=endpoint_type_id).first()

    result = section_types_schema.dump(SectionTypes.query.filter_by(section_type=section_type_id).first())
   
    return jsonify({'message':'Section Type edited', 'section_type':result.data})


