from flask import request, jsonify, g
from ..models import db, Hub, hub_schema, EndpointStatus, endpoint_status_schema, endpoint_status_schemas
from . import api
from datetime import datetime
from ..auth import auth
from ..decorators import hub_active
# from ..common import unique_endpoint, endpoint_validation
from ..errors import no_records

 
@api.route('/status/', methods=['GET'])
def get_endpointstatuses():
    endpointstatus = EndpointStatus.query.all()
    if endpointstatus == None:
        return no_records('endpoint_status.get_endpointstatuses.endpointstatus')
        
    # Serialize the queryset
    hub = Hub.query.first()
    if hub == None:
        return no_records('endpoint_status.get_endpointstatuses.hub')
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    endpoint_status_results = endpoint_status_schemas.dump(endpointstatus)
    return jsonify({'hub': hub_result.data, 'status':endpoint_status_results.data})

@api.route('/status/<uuid:id>', methods=['GET'])
def get_endpointstatus(id):
    endpointstatus = EndpointStatus.query.filter_by(endpoint_uuid=id).first()
    if endpointstatus == None:
        return no_records('endpoint_status.get_endpointstatus.endpointstatus',id)
    # Serialize the queryset
    hub = Hub.query.first()
    if hub == None:
        return no_records('endpoint_status.get_endpointstatus.hub')
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    endpoint_status_result = endpoint_status_schema.dump(endpointstatus)
    return jsonify({'hub': hub_result.data, 'status':endpoint_status_result.data})