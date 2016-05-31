"""Models and database functions for Beautiful Lines project."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """A user of Pinterest and Beautiful Lines Website"""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pinterest_user_id = db.Column(db.String(200), nullable=False)
    # pinterest_user_id = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    bio = db.Column(db.String(2000), nullable=True)
    # pinterest_url = db.Column(db.String(300), nullable=False)
    access_token = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<User user_id=%s first_name=%s last_name=%s>" % (
            self.user_id, self.first_name, self.last_name)


class Board(db.Model):
    """A board that stores images and belongs to a user."""

    __tablename__ = 'boards'

    board_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pinterest_board_id = db.Column(db.String(100), nullable=True)
    # Don't need Url name for boards created on beautiful lines - should be nullable=True
    url_name = db.Column(db.String(100), nullable=False)
    board_name = db.Column(db.String(100), nullable=False)
    board_description = db.Column(db.String(2000), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    image_url = db.Column(db.String(1000), nullable=True)

    user = db.relationship('User', backref=db.backref('boards'))

    tags = db.relationship('Tag',
                           secondary="boards_tags",
                           backref=db.backref('boards'))

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
    """Table for User Saved Images"""

    __tablename__ = 'images'

    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pinterest_image_id = db.Column(db.String(100), nullable=True)
    original_url = db.Column(db.String(1000), nullable=False)
    pinterest_url = db.Column(db.String(1000), nullable=True)
    description = db.Column(db.String(2000), nullable=True)

    boards = db.relationship('Board',
                             secondary="boards_images",
                             backref=db.backref('images'))

    tags = db.relationship('Tag',
                           secondary="images_tags",
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


class BoardTag(db.Model):
    """Association table for images and tags"""

    __tablename__ = 'boards_tags'

    board_tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.board_id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id'), nullable=False)

    board = db.relationship('Board', backref=db.backref('boards_tags'))
    tag = db.relationship('Tag', backref=db.backref('boards_tags'))

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<ImageTag image_tag_id=%s image_id=%s tag_id=%s>" % (
            self.image_tag_id, self.image_id, self.tag_id)


class Tag(db.Model):
    """Table for tags"""

    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tag_content = db.Column(db.String(2000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed to console"""

        return "<Tag tag_id=%s tag_content=%s user_id=%s>" % (self.tag_id, self.tag_content, self.user_id)



# End Classes -------------------------------------------------------------------------------
def test_example_data():
    # User.query.delete()
    # Board.query.delete()
    # BoardImage.query.delete()
    # Image.query.delete()
    # ImageTag.query.delete()
    # Tag.query.delete()

    kelsey = User(pinterest_user_id='testPinterestID',
                  username='kelseyoo14',
                  first_name='Kelsey',
                  last_name='Onstenk',
                  bio='testBio',
                  access_token='testToken')

    db.session.add(kelsey)
    db.session.commit()

    test_board = Board(url_name='testboard',
                       board_name='Test Board',
                       board_description='test board description',
                       user_id=kelsey.user_id,
                       image_url='https://s-media-cache-ak0.pinimg.com/60x60/dc/0d/2a/dc0d2aac9b6afa3958b3225fa3e84c93.jpg')

    image1 = Image(pinterest_image_id='testPinterestImageID',
                   original_url='https://s-media-cache-ak0.pinimg.com/originals/af/de/11/afde1166effd46c7acf87d2d33d617fb.jpg',
                   pinterest_url='',
                   description='test image description 1')

    image2 = Image(pinterest_image_id='testPinterestImageID',
                   original_url='https://s-media-cache-ak0.pinimg.com/originals/19/f5/02/19f50221e774267bee10d32a5bc278d6.jpg',
                   pinterest_url='',
                   description='test image description 2')

    tag1 = Tag(tag_content='test tag content 1')

    tag2 = Tag(tag_content='test tag content 2')

    tag3 = Tag(tag_content='test board tag content')

    db.session.add(test_board)
    db.session.add(image1)
    db.session.add(image2)
    db.session.add(tag1)
    db.session.add(tag2)
    db.session.add(tag3)
    db.session.commit()

    board_image1 = BoardImage(board_id=test_board.board_id,
                              image_id=image1.image_id)

    board_image2 = BoardImage(board_id=test_board.board_id,
                              image_id=image2.image_id)

    image_tag1 = ImageTag(image_id=image1.image_id,
                          tag_id=tag1.tag_id)

    image_tag2 = ImageTag(image_id=image2.image_id,
                          tag_id=tag2.tag_id)

    board_tag = BoardTag(board_id=test_board.board_id,
                         tag_id=tag3.tag_id)

    db.session.add(board_image1)
    db.session.add(board_image2)
    db.session.add(image_tag1)
    db.session.add(image_tag2)
    db.session.add(board_tag)
    db.session.commit()


##############################################################################
# Helper functions

def connect_to_db(app, database='postgresql:///blines'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
