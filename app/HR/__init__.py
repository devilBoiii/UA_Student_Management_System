
"""
Copyright (c) 2022 - Ugyen Dorji
"""

from flask import Blueprint

blueprint = Blueprint(
    'human_resource_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)

