from model import User, Board, BoardImage, Image, ImageTag, BoardTag, Tag, db
import server
import requests
from flask import Flask, request, render_template, session, jsonify


def save_board_from_pinterest(board, board_request, user_id):

    pinterest_board_id = board_request['data']['id']
    board_name = board_request['data']['name']
    board_description = board_request['data']['description']
    image_url = board_request['data']['image']['60x60']['url']

    # Create new_board for db
    new_board = Board(pinterest_board_id=pinterest_board_id,
                      url_name=board,
                      board_name=board_name,
                      board_description=board_description.lower(),
                      image_url=image_url,
                      user_id=user_id)

    db.session.add(new_board)
    db.session.commit()

    new_tag = Tag(tag_content=new_board.board_description.lower(),
                  user_id=user_id)
    new_tag2 = Tag(tag_content=new_board.board_name.lower(),
                   user_id=user_id)

    db.session.add(new_tag)
    db.session.add(new_tag2)
    db.session.commit()

    new_boardtag = BoardTag(board_id=new_board.board_id,
                            tag_id=new_tag.tag_id)

    new_boardtag2 = BoardTag(board_id=new_board.board_id,
                             tag_id=new_tag2.tag_id)

    db.session.add(new_boardtag)
    db.session.add(new_boardtag2)
    db.session.commit()

    return new_board


def save_images_from_pinterest_board(headers, payload, pins_request, user, board_id):

    # Make multiple requests to pinterest since the pin request limit is 100
    next_request = pins_request['page']['next']
    all_pins = pins_request['data']


    # Do this async so user can still use page. js await
    while next_request is not None:
        new_request = requests.get(next_request, headers=headers, params=payload)
        pins_request = new_request.json()
        all_pins.extend(pins_request['data'])
        next_request = pins_request['page']['next']

    board = Board.query.filter(Board.board_id == board_id).first()

    # Save each image in pins_request['data'] to images table
    for pin in all_pins:
        # Check if image exists in db
        check_image = Image.query.filter(Image.pinterest_image_id == pin['id']).first()

        if check_image is None:
            pinterest_image_id = pin['id']
            original_url = pin['image']['original']['url']
            pinterest_url = pin['url']
            description = pin['note']

            # Create new_image for db
            new_image = Image(pinterest_image_id=pinterest_image_id,
                              original_url=original_url,
                              pinterest_url=pinterest_url,
                              description=description)

            db.session.add(new_image)
            db.session.commit()

            new_tag = Tag(tag_content=new_image.description.lower(),
                          user_id=user.user_id)

            db.session.add(new_tag)
            db.session.commit()

            new_imagetag = ImageTag(image_id=new_image.image_id,
                                    tag_id=new_tag.tag_id)

            db.session.add(new_imagetag)
            db.session.commit()

        else:
            new_image = check_image

        # Create new record for boards_images association table to save each image_id with board_id
        new_boardimage = BoardImage(board_id=board.board_id,
                                    image_id=new_image.image_id)

        db.session.add(new_boardimage)
        db.session.commit()

    return ('Images on Board Saved')

def save_individual_images(board_id, pin_id, image_id):
    # If image not already in db
    if image_id == "No-ID":

        headers = {'Authorization': 'Bearer %s' % session['access_token']}
        payload = {'fields': 'id,url,board,image,note'}
        new_request = requests.get('https://api.pinterest.com/v1/pins/%s' % (pin_id), headers=headers, params=payload)
        pin_request = new_request.json()

        # pinterest_image_id = pin_request['data']['id']
        original_url = pin_request['data']['image']['original']['url']
        pinterest_url = pin_request['data']['url']
        description = pin_request['data']['note']

        new_image = Image(pinterest_image_id=pin_id,
                          original_url=original_url,
                          pinterest_url=pinterest_url,
                          description=description)

        db.session.add(new_image)
        db.session.commit()

        new_tag = Tag(tag_content=new_image.description.lower(),
                      user_id=session['user_id'])

        db.session.add(new_tag)
        db.session.commit()

        new_imagetag = ImageTag(image_id=new_image.image_id,
                                tag_id=new_tag.tag_id)

        db.session.add(new_imagetag)
        db.session.commit()

        image_id = new_image.image_id

    new_boardimage = BoardImage(board_id=board_id,
                                image_id=image_id)

    # check if user id on tag is current user, otherwise add tag for image with current user id
    image = Image.query.filter(Image.image_id == image_id).first()
    tag = image.tags[0]

    if tag.user_id != session['user_id']:
        new_tag = Tag(tag_content=image.description.lower(),
                      user_id=session['user_id'])

        db.session.add(new_tag)
        db.session.commit()

        new_imagetag = ImageTag(image_id=image.image_id,
                                tag_id=new_tag.tag_id)

        db.session.add(new_imagetag)
        db.session.commit()

    db.session.add(new_boardimage)
    db.session.commit()


# delete board and associated boardimages, images, imagetags, tags, and boardtags from db
def delete_board_from_database(board_id):
    images_ids = []
    ok_to_delete_images = []
    tags = []

    images = Board.query.get(board_id).images
    for image in images:
        images_ids.append(image.image_id)

    # Delete from board association tables(foreign keys)
    BoardImage.query.filter(BoardImage.board_id == board_id).delete()
    boardtags = BoardTag.query.filter(BoardTag.board_id == board_id).all()
    for boardtag in boardtags:
        tags.append(Tag.query.filter(Tag.tag_id == boardtag.tag_id).first())
    BoardTag.query.filter(BoardTag.board_id == board_id).delete()

    db.session.commit()

    # Find out which images are still needed in db for other boards
    for next_image_id in images_ids:
        check_board_image = BoardImage.query.filter(BoardImage.image_id == next_image_id).first()

        if check_board_image is None:
            ok_to_delete_images.append(Image.query.filter(Image.image_id == next_image_id).first())
            image_tag = ImageTag.query.filter(ImageTag.image_id == next_image_id).first()
            tags.append(Tag.query.filter(Tag.tag_id == image_tag.tag_id).first())
            ImageTag.query.filter(ImageTag.image_id == next_image_id).delete()

    for image in ok_to_delete_images:
        Image.query.filter(Image.image_id == image.image_id).delete()

    # Delete tags now that they are no longer associated with images
    for tag in tags:
        Tag.query.filter(Tag.tag_id == tag.tag_id).delete()

    # Finally, delete actual board
    Board.query.filter(Board.board_id == board_id).delete()

    db.session.commit()

    return ('Board Deleted from Database')

# Delete image and associated tag, imagetag, and boardtag from db
def delete_image_from_db(board_id, image_id):
    BoardImage.query.filter(BoardImage.image_id == image_id, BoardImage.board_id == board_id).delete()
    db.session.commit()

    # Check if image exists on any boards, if there are no more instances of that image in the association table,
    # Then image and associated tags should be deleted from db
    image_in_boards_images = BoardImage.query.filter(BoardImage.image_id == image_id).all()

    if not image_in_boards_images:
        image_tag = ImageTag.query.filter(ImageTag.image_id == image_id).first()
        tag = Tag.query.get(image_tag.tag_id)
        ImageTag.query.filter(ImageTag.image_id == image_id).delete()
        db.session.commit()

        Tag.query.filter(Tag.tag_id == tag.tag_id).delete()
        Image.query.filter(Image.image_id == image_id).delete()
        db.session.commit()


# Edit board info in db
def edit_board_info(new_title, new_image_url, new_description, board_id):
    board = Board.query.get(board_id)

    if new_title is None:
        new_title = ''
    if new_description is None:
        new_description = ''

    tags = board.tags

    for tag in tags:
        if tag.tag_content == board.board_name.lower():
            tag.tag_content = new_title.lower()
        if tag.tag_content == board.board_description.lower():
            tag.tag_content = new_description.lower()

    board.board_name = new_title
    board.board_description = new_description
    board.image_url = new_image_url

    db.session.commit()


# Edit image info in db
def edit_image_info(new_description, image_id):
    image = Image.query.get(image_id)
    tags = image.tags
    tag = tags[0]

    image.description = new_description
    tag.tag_content = new_description.lower()
    db.session.commit()


# Search database for user images or all images
def search(user_search, kind_of_search):
    images = []
    image_urls = set()
    unique_images = []

    search_words = user_search.lower().split()

    for search_word in search_words:
        if kind_of_search == 'all':
            tag_search = Tag.query.filter(Tag.tag_content.like('%' + search_word + '%')).all()
        elif kind_of_search == 'user':
            tag_search = Tag.query.filter(Tag.tag_content.like('%' + search_word + '%'), Tag.user_id == session['user_id']).all()

        for tag in tag_search:
            images.extend(tag.images)
            boards = tag.boards

            if boards:
                for board in boards:
                    images.extend(board.images)

    for image in images:
        image_urls.add(image.original_url)

    for image_url in image_urls:
        unique_images.append(Image.query.filter(Image.original_url == image_url).first())

    boards_in_blines = Board.query.filter(Board.user_id == session['user_id']).all()

    return unique_images, boards_in_blines


# Create new_board for db
def create_board(board_name, board_description, image_url, url_name):
    new_board = Board(url_name=url_name,
                      board_name=board_name,
                      board_description=board_description,
                      image_url=image_url,
                      user_id=session['user_id'])

    db.session.add(new_board)
    db.session.commit()


# Create new_image for db
def create_image(image_url, description, board_id):
    new_image = Image(original_url=image_url,
                      description=description)

    db.session.add(new_image)
    db.session.commit()

    new_boardimage = BoardImage(board_id=board_id,
                                image_id=new_image.image_id)

    db.session.add(new_boardimage)
    db.session.commit()
