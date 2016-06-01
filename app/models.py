from app import db


class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    base_uri = db.Column(db.String)
    filename = db.Column(db.String)
    description = db.Column(db.Text)
    roll_id = db.Column(db.Integer)
    default_version_id = db.Column(db.Integer)
    rating = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<id %r, base_uri %r, filename %r>' % (self.id, self.base_uri, self.filename)