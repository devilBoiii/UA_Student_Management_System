
"""
Copyright (c) 2022 - Ugyen Dorji
"""

from flask import Blueprint

blueprint = Blueprint(
    'subject_teacher_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)