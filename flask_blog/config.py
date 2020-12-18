import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY                      = os.environ.get('SECRET_KEY') or 'you\'ll...never...guess'
    SQLALCHEMY_DATABASE_URI         = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS  = False

    #MAIL CONFIG
    MAIL_SERVER                     = os.environ.get('MAIL_SERVER')
    MAIL_PORT                       = int(os.environ.get('MAIL_PORT') or 25) #MAIL_PORT for DebuggingServer should be 8025 
    MAIL_USE_TLS                    = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME                   = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD                   = os.environ.get('MAIL_PASSWORD')
    ADMINS                          = ['achmadfebryanto@gmail.com']

    #POST
    POSTS_PER_PAGE                  = 5

    #LANGUAGES
    LANGUAGES                       = ['en', 'id']