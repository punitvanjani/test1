from flask import request, jsonify, g
from ..models import db, Hub, Endpoint, EndpointTypes, EndpointStatus, hub_schema, endpoint_schema, endpoint_status_schema
from . import api
from datetime import datetime
from ..auth import auth
from ..decorators import hub_active
from ..common import operate_validation, operate_endpoint_group, debug_msg, endpoint_update_status
from ..errors import invalid_operation, no_records
import interfaces                                       # This has to be in same folder as operate, import does not accept relative path

@api.route('/operate/<uuid:id>/<int:status>', methods=['POST'])
def operate(id,status):
# # ####################    Validate UUID and Validate if status is possible
#     if not (operate_validation(id,status)):
#         return invalid_operation()
# # ####################    Get the parameters stored in Endpoint
    endpoint = Endpoint.query.filter_by(endpoint_uuid = id).first()
    if endpoint == None:
        return no_records('operate.operate.endpoint',id)
# ####################    Call method common for endpoint / group, it should automatically find endpointtype
    status,errors = operate_endpoint_group(id, status)
    debug_msg("operate.operate",status,errors)
    if errors == "":
# ####################    update the status table
        endpoint_status = EndpointStatus.query.filter_by(endpoint_uuid=id).first()
        if endpoint_status == None:
            return no_records('operate.operate.endpoint_status',endpoint.endpoint_uuid)
        endpoint_status.status = status
        endpoint_status.last_changed_by = g.user.username
        endpoint_status.last_changed_on = datetime.today()
        db.session.commit()
        hub = Hub.query.first()
        if hub == None:
            return no_records('operate.operate.hub')
        # Serialize the queryset
        hub_result = hub_schema.dump(hub)
        endpoint_result = endpoint_schema.dump(endpoint)
        endpoint_status_result = endpoint_status_schema.dump(endpoint_status)
        return jsonify({'hub': hub_result.data, 'endpoint':endpoint_result.data, 'endpointstatus':endpoint_status_result.data})
    else:
        return errors, 400

@api.route('/operate1/<uuid:id>/<string:status>', methods=['POST'])
def operate1(id,status):
    endpoint_update_status(str(id),str(status))
    return jsonify({'updated':'endpoint gcm triggered'})
