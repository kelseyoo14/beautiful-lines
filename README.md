# Beautiful Lines

Learn more about the developer: www.linkedin.com/in/kelseyonstenk

Beautiful Lines is a visual library and study tool for Artists. In a real life drawing class, a model would pose in front of a class, changing poses at set intervals for students to study while drawing or painting. Beautiful Lines aims to replicate that experience for practice outside of class. Beautiful Lines makes it easy for artists to save images from anywhere online or specifically from their Pinterest account to then use in study sessions. Beautiful Lines is integrated with Pinterest, so that users can easily transfer their saved boards from Pinterest. Users can also use Beautiful Lines to search the images they haved saved or to search all images that have been saved on Beautiful Lines - to find references or new inspiration!


## Table of Contents
* [Technologies Used](#technologies)
* [Terms](#terms)
* [Logging in with Pinterest](#login)
* [Saving From Pinterest](#pinterest)
* [Creating Boards and Images](#newboardsandimages)
* [Editing Boards and Images](#editboardsandimages)
* [Deleting Boards and Images](#deleteboardsandimages)
* [Studying](#studying)
* [Searching](#searching)
* [Version 2.0](#v2)
* [Author](#author)


## <a name="technologies"></a>Technologies Used
* [Javascript](https://www.javascript.com/)
* [Python](https://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Flask - SQLAlchemy](http://flask.pocoo.org/)
* [jQuery](https://jquery.com/)
* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* [Bootstrap](http://getbootstrap.com/2.3.2/)
* [PostgreSQL](https://www.postgresql.org/)

## <a name="terms"></a>Terms
####Art Terminology
Beautiful Lines' main focus is to be a study tool for artists - for artists to practice life and gesture drawing. In the art world, studying forms and other works of art are important for progression as an artist, and for developing skills and a good eye for recognizing colors, values, and lines. The mind fills in gaps for what we see constantly, which blurs the line between what we think we see and the reality of what we are actually looking at. Beautiful Lines is a tool to make that practice easier.

[Life or Figure Drawing] (https://en.wikipedia.org/wiki/Figure_drawing) - a drawing of the human form in any of its various shapes and postures. Simply put, practicing drawing the human form, inlcuding the body, face and the ever so complicated hands and feet.

[Gesture Drawing](https://en.wikipedia.org/wiki/Gesture_drawing) - is a laying in of the action, form, and pose of a model/figure. It is generally a quick drawing done in under 2 minutes to quickly capture the general shape or movement of a model/figure, but can also can be applied to any form of life or object.


## <a name="login"></a>Logging in with Pinterest
####OAutho 2.0
![Logging in with Pinterest](/static/img/welcomepage)
![Logging in with Pinterest](/static/img/oauth.png)
Pinterest uses OAuth 2.0. When clicking on the 'Login' button on the homepage, users are redirected to login with their Pinterest account. In the future users will be able to login without a Pinterest account.

## <a name="pinterest"></a>Saving from Pinterest
####Boards
![Saving Boards from Pinterest](/static/img/pinterestboards.png)
Beautiful Lines requests the logged in user's boards from Pinterest, which are displayed under 'Your Pinterest'. A user can save an entire board multiple times.

####Images
![Saving Images from Pinterest](/static/img/imagesonpinboard.png)
A user can save individual images either from boards requested from Pinterest or from boards saved to Beautiful Lines. After clicking 'Save' on an image, a modal listing the boards a user has saved to or created on Beautiful Lines is displayed, from which they can choose a board to save the image on.



## <a name="newboardsandimages"></a>Creating Boards and Images
####Boards
![Creating Boards](/static/img/createboard.png)
Users can create a new board on their homepage of Beautiful Lines, meaning they do not need to save images from Pinterest in order to use the site. The form for creating a new board requires the user to enter a 'Title' and 'Cover Image URL', and has the option for entering a 'Board Description'.

####Images
![Creating Images](/static/img/createimage.png)
Users can create new images on Beautiful Lines by navigating to the board they wish to save the image to, and using an image URL. The form for creating a new image requires the user to enter the 'Image URL' and has the option for entering an 'Image Description'.


## <a name="#editboardsandimages"></a>Editing Boards and Images
![Editing Boards](/static/img/editboard.png)
![Editing Images](/static/img/editimage.png)
A user can edit a board or image by clicking the 'Edit' button under the board or image they wish to edit. For boards, the 'Title', 'Cover Image URL', and 'Description' can be edited. For images, the 'Description' can be edited.


## <a name="#deleteboardsandimages"></a>Deleting Boards and Images
A user can delete a board or image by clicking the 'Delete' button under the board or image they wish to delete.


## <a name="#studying"></a>Studying
####Setting up a Study Session
![Studying](/static/img/setupstudy.png)
![Selecting Base Measurements](/static/img/screen-shot-base.png)
The Study feature is the main feature for beautiful lines, where a user can choose how many images they want to study, and at what time interval they want to study each image. 


####Recursively Displaying Images
![Studying](/static/img/studymodal.png)
This feature may have been the most difficult but also the most rewarding feature of the website (since it is the main feature!). After a user chooses a number of images to display and a time interval to display them at, on the front end in javascript, the images are shuffled (so that each study session is unique) and then displayed in a modal. The modal displays each image for the selected time interval, and closes after all the images have been displayed. This was accomplished with a function that edits the "img src"of the modal, and then recursively calls itself after a setTimeout(), which is set to the time interval the user selects for their study session.


## <a name="#searching"></a>Searching
####Searching User Images
![Studying](/static/img/usersearch.png)
All descriptions for images and boards, and titles for boards, are saved into a 'tags' table in the database. Each tag has a user ID associated with it so that the database can be queried and searched specifically for images and boards the user has saved. 

####Searching All Images
![Studying](/static/img/allsearch.png)
A user can also search all images that have been saved to Beautiful Lines! Above is an image that returned a search of all images, which includes images not saved by this user. Through this a user can save images that are on beautiful lines, that they have not searched before. 

## <a name="v2"></a>Version 2.0

Next features that will be added are a login for users who don't have or want to use a Pinterest account, 

## <a name="author"></a>Author
Kelsey Onstenk is a software engineer from San Francisco, CA.