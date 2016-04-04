from flask import request, jsonify, g
from ..models import db, Hub, Endpoint, EndpointTypes, EndpointStatus, hub_schema, endpoint_schema, endpoint_status_schema
from . import api
from datetime import datetime
from ..auth import auth
from ..decorators import hub_active
from ..common import operate_validation
from ..errors import invalid_operation, no_records
import interfaces                                       # This has to be in same folder as operate, import does not accept relative path
 
@api.route('/operate/<uuid:id>/<int:status>', methods=['POST'])
def operate(id,status):
# ####################    Validate UUID and Validate if status is possible
    if not (operate_validation(id,status)):
        return invalid_operation()
# ####################    Get the parameters stored in Endpoint
    endpoint = Endpoint.query.filter_by(endpoint_uuid = id).first()
    if endpoint == None:
        return no_records('operate.operate.endpoint',id)
    endpointtype = EndpointTypes.query.filter_by(node_type=endpoint.node_type, endpoint_type=endpoint.endpoint_type).first()
    if endpointtype != None:
        return no_records('operate.operate.endpointtype',endpoint.node_type,endpoint.endpoint_type)
# ####################    Call the corresponding method based on node_type and endpoint_type and get the status from endspoint
    interfaces_method_name = getattr(interfaces,endpointtype.method)
    status = interfaces_method_name(endpoint,endpointtype,status)
# ####################    update the status table
    endpoint_status = EndpointStatus.query.filter_by(endpoint_uuid=endpoint.endpoint_uuid).first()
    if endpoint_status == None:
        return no_records('operate.operate.endpoint_status',endpoint.endpoint_uuid)
    endpoint_status.status = status
    endpoint_status.last_oper_by = g.user.username
    endpoint_status.last_oper_at=datetime.today()
    db.session.commit()
    
# ####################    create response from status table for this endpoint
# 
#     endpoint_status = EndpointStatus.query.filter_by(endpoint_uuid = id).first()
#     if endpoint_status != None:
#         if (status == 1) or (status == 0):
#             endpoint_status.status = status
#             endpoint_status.last_oper_by = g.user.username
#             endpoint_status.last_oper_at=datetime.utcnow()
#             db.session.commit()

    hub = Hub.query.first()
    if hub == None:
        return no_records('operate.operate.hub')
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    endpoint_result = endpoint_schema.dump(endpoint)
    endpoint_status_result = endpoint_status_schema.dump(endpoint_status)
    return jsonify({'hub': hub_result.data, 'endpoint':endpoint_result, 'endpointstatus':endpoint_status_result})