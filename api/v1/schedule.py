from flask import request, jsonify, g
from ..models import db, Hub, Endpoint, EndpointTypes, Schedule, hub_schema, schedule_schema, schedule_schemas
from . import api
from datetime import datetime
from ..auth import auth
from ..common import schedule_validation
from ..errors import no_input, invalid_schedule
import uuid


@api.route('/schedules/', methods=['GET'])
def get_schedules():
    schedules = Schedule.query.all()
    if schedules == None:
        return no_records('schedule.get_schedule.schedule')
    # Serialize the queryset
    hub = Hub.query.first()
    if hub == None:
        return no_records(schedule.get_schedule.hub)
    # Serialize the queryset
    hub_result = hub_schema.dump(hub)
    results = schedule_schemas.dump(schedules)
    return jsonify({'hub': hub_result.data, 'schedules':results})


@api.route('/schedules/', methods=['POST'])
def new_schdeule():
    json_data = request.get_json()
    if not json_data:
        return no_input()
# Validate and deserialize input
    data, errors = schedule_schema.load(json_data)
    if errors:
        return jsonify(errors), 422
# Validation logic eg. UUID should be valid Endpoint or Group UUID, expected status should match EndpointTypes
    if not (schedule_validation(data)):
        return invalid_schedule()
# Create new Schedule
    print data['uuid_id']
    schedule = Schedule(
                            uuid_id             = data['uuid_id'],
                            expected_status     = data['expected_status'],
                            year                = data['year'],
                            month               = data['month'],
                            weekday             = data['weekday'],
                            date                = data['date'],
                            hour                = data['hour'],
                            min                 = data['min'],
                            hourly              = data['hourly'],
                            daily               = data['daily'],
                            weekly              = data['weekly'],
                            monthly             = data['monthly'],
                            yearly              = data['yearly'],
                            onlyonce            = data['onlyonce'],
                            status              = data['status'],
                            last_changed_by     = g.user.username,
                            last_changed_on     = datetime.today()
    )
    
    db.session.add(schedule)
    db.session.commit()

    result = schedule_schema.dump(Schedule.query.get(schedule.id))
    
    return jsonify({'message':'Schedule added', 'schedule':result})

# @api.route('/endpoints/<uuid:id>', methods=['PUT'])
# def edit_endpoint(id):
#     json_data = request.get_json()
#     if not json_data:
#         return no_input()
# # Check if valid endpoint id is supplied    
#     endpoint = Endpoint.query.filter_by(endpoint_uuid=id).first()
#     if endpoint == None:
#         return no_records('endpoint_conf.edit_endpoints.endpoint',id)
# # Deserialize and check for errors
#     endpoint_schema_custom = EndpointSchema(partial=('section_type','internal_sec_id','internal_sec_desc','internal_nod_id','node_type','internal_nod_desc','internal_end_id','endpoint_type','internal_end_desc',))
#     data, errors = endpoint_schema_custom.load(json_data)
#     if errors:
#         return jsonify(errors), 422
# 
# # Edit only descriptions in endpoint, though based on schema internal ID are compulsory
#     if (is_admin(g.user.username)):
#         try:    endpoint.section_type       =data['section_type']
#         except: pass
#         try:    endpoint.internal_sec_id    =data['internal_sec_id']
#         except: pass
#         try:    endpoint.internal_nod_id    =data['internal_nod_id']
#         except: pass
#         try:    endpoint.node_type          =data['node_type']
#         except: pass
#         try:    endpoint.internal_end_id    =data['internal_end_id']
#         except: pass
#         try:    endpoint.endpoint_type      =data['endpoint_type']
#         except: pass
#     try:    endpoint.internal_sec_desc      =data['internal_sec_desc']
#     except: pass
#     try:    endpoint.internal_nod_desc      =data['internal_nod_desc']
#     except: pass
#     try:    endpoint.internal_end_desc      =data['internal_end_desc']
#     except: pass
#     
#     db.session.add(endpoint)
#     db.session.commit()
# # Sync endpoints with server
#     server_sync_endpoints()
# #  
#     result = endpoint_schema.dump(Endpoint.query.get(endpoint.id))
#     return jsonify({'message':'Endpoint edited', 'endpoint':result})
# 
# @api.route('/endpoints/<uuid:id>', methods=['DELETE'])
# @admin_role_required
# def delete_endpoint(id):
#     endpoint = Endpoint.query.filter_by(endpoint_uuid=id).first()
#     if endpoint == None:
#         return no_records('endpoint_conf.delete_endpoints.endpoint',id)
#     result = endpoint_schema.dump(Endpoint.query.get(endpoint.id))
#     db.session.delete(endpoint)
# 
#     endpointstatus = EndpointStatus.query.filter_by(endpoint_uuid=id).first()
#     if endpointstatus == None:
#         return no_records('endpoint_conf.delete_endpoints.endpointstatus',id)
# #     result_status = endpoint_schema.dump(Endpoint.query.get(endpoint.id))
#     db.session.delete(endpointstatus)
#     
#     db.session.commit()
#     return jsonify({'message':'Endpoint deleted','endpoint':result})