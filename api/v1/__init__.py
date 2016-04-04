from flask import Blueprint, g, url_for
from ..errors import ValidationError, bad_request, not_found
from ..auth import auth
from ..decorators import rate_limit, hub_active


api = Blueprint('api', __name__)


def get_catalog():
    return {
            'hub': url_for('api.get_hub', _external=True),
            'endpoints': url_for('api.get_endpoints', _external=True),
            'endpoints_group': url_for('api.get_groups', _external=True),
            'endpoints_status': url_for('api.get_endpointstatuses', _external=True),
            'endpoints_types': url_for('api.get_endpoint_types', _external=True),
            'users':url_for('api.get_users', _external=True)
            }


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(str(e))


@api.errorhandler(400)
def bad_request_error(e):
    return bad_request('invalid request')


@api.before_request
@hub_active
@auth.login_required
@rate_limit(limit=5, period=15)
def before_request():
    pass


@api.after_request
def after_request(response):
    if hasattr(g, 'headers'):
        response.headers.extend(g.headers)
    return response

# do this last to avoid circular dependencies
from . import hub_conf,endpoint_conf,users,operate,endpoint_status,endpoint_types,interfaces,endpoint_group,properties,schedule#,students,registrations,classes