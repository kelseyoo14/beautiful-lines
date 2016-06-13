# Beautiful Lines

Learn more about the developer: www.linkedin.com/in/kelseyonstenk

Beautiful Lines is a visual library and study tool for Artists. In a real life drawing class, a model would pose in front of a class, changing poses at set intervals for students to study while drawing or painting. Beautiful Lines aims to replicate that experience for practice outside of class. Beautiful Lines makes it easy for artists to save images from anywhere online or specifically from their Pinterest account to then use in study sessions. Beautiful Lines is integrated with Pinterest, so that users can easily transfer their saved boards from Pinterest. Users can also use Beautiful Lines to search the images they haved saved or to search all images that have been saved on Beautiful Lines - to find references or new inspiration!


## Table of Contents
* [Technologies Used](#technologies)
* [Logging in with Pinterest](#login)
* [Saving From Pinterest](#pinterest)
* [Creating Boards and Images](#newboardsandimages)
* [Editing Boards and Images](#editboardsandimages)
* [Deleting Boards and Images](#deleteboardsandimages)
* [Studying](#studying)
* [Searching](#searching)
* [Version 2.0](#v2)


## <a name="technologies"></a>Technologies Used
* [Python](https://www.python.org/)
* [Flask](http://flask.pocoo.org/)
* [Flask - SQLAlchemy](http://flask.pocoo.org/)
* [PostgreSQL](https://www.postgresql.org/)
* [Javascript](https://www.javascript.com/)
* [jQuery](https://jquery.com/)
* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* [Bootstrap](http://getbootstrap.com/2.3.2/)
* [Pinterest API](https://developers.pinterest.com/)


## <a name="login"></a>Logging in with Pinterest
####OAutho 2.0
![Logging in with Pinterest](/static/readmeimgs/welcomepage.png)
![Logging in with Pinterest](/static/readmeimgs/oauth.png)
Pinterest uses OAuth 2.0. When clicking on the 'Login' button on the homepage, users are redirected to login with their Pinterest account. In the future users will also have the option to login without a Pinterest account.

## <a name="pinterest"></a>Saving from Pinterest
####Saving Boards
![Saving Boards from Pinterest](/static/readmeimgs/pinterestboards.png)
Beautiful Lines requests the logged in user's boards from Pinterest, which are displayed under 'Your Pinterest'. A user can save an entire board (multiple times if they want).

####Saving Images
![Saving Images from Pinterest](/static/readmeimgs/saveimage.png)
A user can save individual images either from boards requested from Pinterest or from boards saved to Beautiful Lines. After clicking 'Save' on an image, a modal listing the boards a user has saved to or created on Beautiful Lines is displayed, from which they can choose a board to save the image on.



## <a name="newboardsandimages"></a>Creating Boards and Images
####Creating Boards
![Creating Boards](/static/readmeimgs/createboard.png)
Users can create a new board on their homepage of Beautiful Lines, meaning they do not need to save images from Pinterest in order to use the site. The form for creating a new board requires the user to enter a 'Title' and 'Cover Image URL', and has the option for entering a 'Board Description'.

####Creating Images
![Creating Images](/static/readmeimgs/createimage.png)
Users can create new images on Beautiful Lines by navigating to the board they wish to save the image to. The form for creating a new image requires the user to enter the 'Image URL' and has the option for entering an 'Image Description'.


## <a name="#editboardsandimages"></a>Editing or Deleting Boards and Images
![Editing Boards](/static/readmeimgs/editboard.png)
![Editing Images](/static/readmeimgs/editimage.png)
A user can edit or delete a board or image by clicking the 'Edit' or 'Delete' button under the board or image they wish to edit or delete. For boards, the 'Title', 'Cover Image URL', and 'Description' can be edited. For images, the 'Description' can be edited.


## <a name="#studying"></a>Studying
####Setting up a Study Session
![Studying](/static/readmeimgs/setupstudy.png)
The Study feature is the main feature for beautiful lines, where a user can choose how many images they want to study, and at what time interval they want to study each image. 


####Displaying Images
![Studying](/static/readmeimgs/studymodal3.gif)
After a user chooses a number of images to display and a time interval to display them at, the images are shuffled (so that each study session is unique) and then displayed in a modal. The modal displays each image for the selected time interval, and closes after all the images have been displayed.


## <a name="#searching"></a>Searching
####Searching User Images
All descriptions for images and boards, and titles for boards, are saved into a 'tags' table in the database. Each tag has a user ID associated with it so that the database can be queried and searched specifically for images and boards the user has saved. 

####Searching All Images
A user can also search all images that have been saved to Beautiful Lines! Above is an image that returned a search of all images, which includes images not saved by this user. Through this a user can save images that are on beautiful lines, that they have not searched before. 

## <a name="v2"></a>Version 2.0

Next features that will be added are a login for users who don't have or want to use a Pinterest account, an account and settings page, a more robust search that can find words related to a user's search words, a page for creating reference/project boards for saving images, process images, and color palettes together (possibly with an eyedropper for finding colors in an image), and an upload option so that users can upload their own images to boards.


