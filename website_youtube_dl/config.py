import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True