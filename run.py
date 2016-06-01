#!venv/bin/python

from app import app


if __name__ == "__main__":
    app.config.update(SQLALCHEMY_TRACK_MODIFICATIONS=True)
    app.run(debug=True)