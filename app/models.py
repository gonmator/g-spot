from app import db


photo_tags = db.Table('photo_tags',
                      db.Column('photo_id', db.Integer, db.ForeignKey('photos.id')),
                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                      db.UniqueConstraint('photo_id', 'tag_id'))


class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    time = db.Column(db.Integer)
    base_uri = db.Column(db.String)
    filename = db.Column(db.String)
    description = db.Column(db.Text)
    roll_id = db.Column(db.Integer)
    default_version_id = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer)
    tags = db.relationship('Tags', secondary='photo_tags', backref=db.backref('photos.id'))

    def __repr__(self):
        return '<id %r, base_uri %r, filename %r>' % (self.id, self.base_uri, self.filename)


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, unique=True)
    category_id = db.Column(db.Integer)
    is_category = db.Column(db.Boolean)
    sort_priority = db.Column(db.Integer)
    icon = db.Column(db.Text)

    def __repr__(self):
        return '<id %r, name %r, category_id %r>' % (self.id, self.name, self.category_id)

