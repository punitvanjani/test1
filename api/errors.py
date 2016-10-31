from flask import jsonify, url_for, current_app


class ValidationError(ValueError):
    pass


def not_modified():
    response = jsonify({'status': 304, 'error': 'not modified'})
    response.status_code = 304
    return response


def bad_request(message):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': message})
    response.status_code = 400
    return response


def unauthorized(message=None):
    if message is None:
        if current_app.config['USE_TOKEN_AUTH']:
            message = 'Please authenticate with your token.'
        else:
            message = 'Please authenticate.'
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': message})
    response.status_code = 401
    if current_app.config['USE_TOKEN_AUTH']:
        response.headers['Location'] = url_for('token.request_token')
    return response


def not_found(message):
    response = jsonify({'status': 404, 'error': 'not found',
                        'message': message})
    response.status_code = 404
    return response


def not_allowed():
    response = jsonify({'status': 405, 'error': 'method not allowed'})
    response.status_code = 405
    return response


def precondition_failed():
    response = jsonify({'status': 412, 'error': 'precondition failed'})
    response.status_code = 412
    return response


def too_many_requests(message='You have exceeded your request rate'):
    response = jsonify({'status': 429, 'error': 'too many requests',
                        'message': message})
    response.status_code = 429
    return response

def no_records(message='No records found',keyword1=-99,keyword2=-99,keyword3=-99,keyword4=-99,keyword5=-99):
    if(keyword1!=-99):
        message += ' ' + 'key1:' + str(keyword1)
    if(keyword2!=-99):
        message += ' ' + 'key2:' + str(keyword2)
    if(keyword3!=-99):
        message += ' ' + 'key3:' + str(keyword3)
    if(keyword4!=-99):
        message += ' ' + 'key4:' + str(keyword4)
    if(keyword5!=-99):
        message += ' ' + 'key5:' + str(keyword5)
    response = jsonify({'status': 400, 'error': 'db records not found',
                        'message': message})
    response.status_code = 400
    return response


def no_input(message='No input data provided'):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': message})
    response.status_code = 400
    return response

def no_communication(message='No communication possible. Contact Admin.'):
    response = jsonify({'status': 400, 'error': 'No communication possible. Contact Admin.',
                        'message': message})
    response.status_code = 400
    return response


def duplicate_endpoint(message='Endpoint with same parameters already exists'):
    response = jsonify({'status': 400, 'error': 'same sectionid, node id, endpoint id',
                        'message': message})
    response.status_code = 400
    return response


def duplicate_endpoint_type(message='Endpoint type with same parameters already exists'):
    response = jsonify({'status': 400, 'error': 'same node type, endpoint type',
                        'message': message})
    response.status_code = 400
    return response

def duplicate_section_type(message='Section type with same parameters already exists'):
    response = jsonify({'status': 400, 'error': 'same section type',
                        'message': message})
    response.status_code = 400
    return response


def invalid_endpoint(message='This type of node and endpoint is not supported'):
    response = jsonify({'status': 400, 'error': 'incorrect node type and endpoint type',
                        'message': message})
    response.status_code = 400
    return response

def invalid_schedule(message='Schedule does not have proper uuid or expected status'):
    response = jsonify({'status': 400, 'error': 'incorrect uuid or expected_status',
                        'message': message})
    response.status_code = 400
    return response


def invalid_user(message='Username is not valid'):
    response = jsonify({'status': 400, 'error': 'bad username',
                        'message': message})
    response.status_code = 400
    return response

def duplicate_user(message='Username already exists'):
    response = jsonify({'status': 400, 'error': 'bad username',
                        'message': message})
    response.status_code = 400
    return response

def duplicate_property(message='Property already exists'):
    response = jsonify({'status': 400, 'error': 'bad property',
                        'message': message})
    response.status_code = 400
    return response


def duplicate_group(message='Group with same description already exists'):
    response = jsonify({'status': 400, 'error': 'bad groupname',
                        'message': message})
    response.status_code = 400
    return response


def invalid_operation(message='Either Endpoint or status is not correct'):
    response = jsonify({'status': 400, 'error': 'Incorrect input',
                        'message': message})
    response.status_code = 400
    return response

def admin_right(message='Admin rights required'):
    response = jsonify({'status': 402, 'error': 'Incorrect user',
                        'message': message})
    response.status_code = 402
    return response

def hub_not_active(message='Hub not active, contact Admin'):
    response = jsonify({'status': 400, 'error': 'Hub inactive',
                        'message': 'Hub not active, contact Admin. ' + message})
    response.status_code = 400
    return response