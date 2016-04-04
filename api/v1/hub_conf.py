from flask import request, jsonify
from ..models import db, Hub, hub_schema, HubSchema
from . import api
from ..auth import auth
from ..decorators import hub_active, admin_role_required
from ..errors import no_records


@api.route('/hub/', methods=['GET'])
def get_hub():
    hub = Hub.query.first()
    if hub == None:
        return no_records('hub_conf.get_hub.hub')
    # Serialize the queryset
    result = hub_schema.dump(hub)
    return jsonify({'hub': result.data})

@api.route('/hub/', methods=['PUT'])
def edit_hub():
# Edit the first record, as Hub table will contain only one record
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    data, errors = hub_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# As there are no errors, allow Hub's description, external_url and Status to change
    hub = Hub.query.first()
    if hub == None:
        return no_records('hub_conf.edit_hub.hub')
    hub.description         = data['description']
    hub.external_url        = data['external_url']
    hub.status              = data['status']
    db.session.commit()
    
    result = hub_schema.dump(hub)
    return jsonify({'hub': result.data})

@api.route('/hubstatus/', methods=['PUT'])
@admin_role_required
def edit_hubstatus():
# Edit the first record, as Hub table will contain only one record
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    hub_schema_status = HubSchema(only=('hub_id','status',))
    data, errors = hub_schema_status.load(json_data)
#     data, errors = hub_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# As there are no errors, allow Hub's description, external_url and Status to change
    hub = Hub.query.first()
    if hub == None:
        return no_records('hub_conf.edit_hub.hub')
    hub.status              = data['status']
    db.session.commit()
    
    result = hub_schema.dump(hub)
    return jsonify({'hub': result.data})