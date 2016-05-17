"""Models and database functions for Beautiful Lines project."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """A user of Pinterest and Beautiful Lines Website"""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pinterest_user_id = db.Column(db.String(100), nullable=False)
    # pinterest_user_id = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    bio = db.Column(db.String(64), nullable=True)
    # pinterest_url = db.Column(db.String(300), nullable=False)
    access_token = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<User user_id=%s first_name=%s last_name=%s>" % (
            self.user_id, self.first_name, self.last_name)


class Board(db.Model):
    """A board that stores images and belongs to a user."""

    __tablename__ = 'boards'

    board_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pinterest_board_id = db.Column(db.String(100), nullable=False)
    url_name = db.Column(db.String(100), nullable=False)
    # Board name needs to be: unique=True (do next time I drop and create db)
    board_name = db.Column(db.String(100), nullable=False)
    board_description = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)

    user = db.relationship('User', backref=db.backref('boards'))

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<Board board_id=%s board_name=%s user_id=%s>" % (
            self.board_id, self.board_name, self.user_id)


class BoardImage(db.Model):
    """Association table for boards and images"""

    __tablename__ = 'boards_images'

    board_image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.board_id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.image_id'), nullable=False)

    board = db.relationship('Board', backref=db.backref('boards_images'), single_parent=True, cascade="all, delete-orphan")
    image = db.relationship('Image', backref=db.backref('boards_images'), single_parent=True, cascade="all, delete-orphan")

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "\n<BoardImage board_image_id=%s board_id=%s image_id=%s>" % (
            self.board_image_id, self.board_id, self.image_id)


class Image(db.Model):

    __tablename__ = 'images'

    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pinterest_image_id = db.Column(db.String(100), nullable=False)
    original_url = db.Column(db.String(300), nullable=False)
    pinterest_url = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(1000), nullable=True)

    boards = db.relationship('Board',
                              secondary="boards_images",
                              backref=db.backref('images'))

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<%s image_id=%s pinterest_image_id=%s>" % (type(self).__name__, self.image_id, self.pinterest_image_id)


class ImageTag(db.Model):
    """Association table for images and tags"""

    __tablename__ = 'images_tags'

    image_tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.image_id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id'), nullable=False)

    image = db.relationship('Image', backref=db.backref('images_tags'))
    tag = db.relationship('Tag', backref=db.backref('images_tags'))

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<ImageTag image_tag_id=%s image_id=%s tag_id=%s>" % (
            self.image_tag_id, self.image_id, self.tag_id)


class Tag(db.Model):

    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tag_name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<Tag tag_id=%s tag_name=%s>" % (self.tag_id, self.tag_name)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blines'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
