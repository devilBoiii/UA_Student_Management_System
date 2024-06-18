
"""
Copyright (c) 2024 - Ugyen Academy
"""

from flask import Blueprint

blueprint = Blueprint(
    'admin_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)