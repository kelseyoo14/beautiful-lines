"""Models and database functions for Beautiful Lines project."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """A user of Pinterest and Beautiful Lines Website"""

    __tablename__ = 'users'


    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    pinterest_url = db.Column(db.String(150), nullable=False)
    access_token = db.Column(db.String(100), nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<User user_id=%s first_name=%s last_name=%s>" % (
            self.user_id, self.first_name, self.last_name)


class Board(db.Model):
    """A board that stores images and belongs to a user."""

    __tablename__ = 'boards'


    board_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    board_name = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<User board_id=%s board_name=%s user_id=%s>" % (
            self.board_id, self.board_name, self.user_id)


class Image(db.Model):

    __tablename__ = 'images'


    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    board_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    url = db.Column(db.String(150), nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<User image_id=%s board_id=%s>" % (self.image_id, self.board_id)



class Tag(db.Model):

    __tablename__ = 'tags'


    tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tag_name = db.Column(db.String(20), nullable=False)


    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<User tag_id=%s tag_name=%s>" % (self.tag_id, self.tag_name)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blines'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."


