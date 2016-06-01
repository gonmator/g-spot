import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data/photos.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'data/repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False