# -*- coding: utf-8

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data/photos.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'data/repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

if 'FSPOT_PHOTOS_LOCATION_PREFIX' in os.environ:
    FSPOT_PHOTOS_LOCATION_PREFIX = os.environ['FSPOT_PHOTOS_LOCATION_PREFIX'].decode('utf-8')
else:
    FSPOT_PHOTOS_LOCATION_PREFIX = u''
