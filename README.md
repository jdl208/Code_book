# devNotes

During my eductation to become a developer. I saw a lot of recurring questions in the community slack channels about how to set things up or about how somethings should be coded.
devNotes is trying to be a hub before for these issues and share knowledge about issues developers have run into and want to help other who will probably run into the same problem.

The website can be viewed [here](https://devnotes-ms3.herokuapp.com/).

## UX
The website is developed with starting developers in mind, but is also usefull for experienced developers just starting with something new or just for remembering stuff that you don't use that often.

- Users should be able to log in without any hassle to reach their notes. This is reached by putting a login right at the frontpage.
- Users can search public notes without an account.
- Users should be able to search through all notes with keywords.
- Users should be able to post notes and edit and delete their own notes when they are signed in.

## Features
### Existing features
* Making a user account.
* Making, editing and deleting notes.
* Searching public notes.
* Searching your own notes.
### Future Features
* A password reset function when you can't access your account.
* A delete account function.
* Being able to copy someone else's note to your own collection, or mark notes as favorites.
* Comment on notes.
* Rate notes
## Technologies
* [HTML](https://www.w3.org/TR/html52/)\
Is used for the semantics of the website.
* [CSS](https://www.w3.org/Style/CSS/)\
The styling of the website that wasn't done by bootstrap is done with CSS.
* [Bootstrap](https://getbootstrap.com/)\
Bootstrap is used for the styling and layout of the website and the navbar with the toggler.
* [Font Awesome](https://fontawesome.com/)\
Used to implement some icons on the page.
* [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)\
The little JavaScript that is used is being used for making the website more interactive.
* [Python](https://www.python.org/)\
Python is used for rendering all the views and connecting to the backend of the website. The python Flask library is used to create the app.
* [MongoDB](https://www.mongodb.com/)\
Is a noSQL database. Used to store all the user information and all the notes.
* [Heroku](https://www.heroku.com/)\
Is a hostingplatform for apps. It is used to deploy this website.
* [CKEditor 4](https://ckeditor.com/ckeditor-4/)\
Used for the formatting options in the textarea on the create and edit notes page.

## Testing
All functionality have been tested manually.

There is an issue with Heroku because it will not save changes to the filesystem.

Info from Heroku site:
> The Heroku filesystem is ephemeral - that means that any changes to the filesystem whilst the dyno is running only last until that dyno is shut down or restarted. Each dyno boots with a clean copy of the filesystem from the most recent deploy. This is similar to how many container based systems, such as Docker, operate.

When the site will be deployed in a production environment we will make sure that images can be saved to the filesystem permanently or save to an external bucket.

Further testing have been done by fellow students. I posted the link to the site and they found one bug. When someone made an account. A default image with .jpg would be added, while the default image is a .png. That has been corrected in the code.
## Deployment
The app is hosted on Heroku. Whenever the master branch is updated it will be pushed to Heroku to directly update the live site.

### Run the app locally
To make the app function on your local machine you have to have an IDE and Python 3 and Git installed. With the installation of Python, pip will also be installed. Furthermore a MongoDB acoount is necessary which can be created for free [here](https://www.mongodb.com/). 

#### Local installation:
1. go to the location in your terminal where the repository should be installed and then enter on the command line:
   >_`git clone https://github.com/jdl208/devNotes.git`_
2. install all the requirements by entering on the command line:
   >_`pip3 install -r requirements`_
3. Set the environment variables for SECRET_KEY and MONGO_URI. The mongo_uri must contain the correct database name. So the code can reach it.
4. To your MongoDB Database add 2 collections. One named users and one named posts. 
5. When all of this is done correctly. You can run the app by entering the following command on the command line:
    > _`python3 run.py`_

#### Deploy to Heroku:
1. Make an account on heroku and create a new app. Choose the region based closest to where you reside.
2. In Heroku go to settings. Reveal config vars and supply the variabels like below:
    **Key** | **Value**
    --- | ---
    PORT| 5000
    IP | 0.0.0.0
    MONGO_URI | mongodb+srv://\<username>:\<password>@\<clustername>-b7hpq.mongodb.net/\<databasename>?retryWrites=true&w=majority
    SECRET_KEY | \<Your Secret Key>

3. In Heroku go to the deploy tab and copy the cli code to link the repositorie to Heroku.
4. In the command line login by entering heroku login and enter your credentials.
5. Paste in the code in the terminal copied at step 3.
6. Now you can push to heroku by entering the following in the command line:
   >`push origin heroku master` 

The app is now deployed on Heroku.

## Credits
### Content
All content is written by me.
### Code
For the use of the WTForms and how to make a login and loginmanager. I used the tutorials from Corey Schafer on Youtube. The code has been modified to work with MongoDB by myself.