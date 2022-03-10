# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import os


def get_file_base64(file_name):
    path = _get_file_path(file_name)
    file = open(path, "rb")
    return base64.b64encode(file.read())


def open_file(file_name):
    path = _get_file_path(file_name)
    return open(path, "r", encoding='cp1252')


def _get_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), "data", file_name)
