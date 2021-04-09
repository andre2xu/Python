import sys, os, sqlite3
ROOT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT_DIRECTORY)

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')

from flask import Flask, g
app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



# custom dictionary generators

def userAccountModel(db_data):
    userAccountModel = {}

    userAccountModelKeys = ['username', 'password', 'joined', 'pfp', 'cover', 'name', 'bio', 'clique', 'niche'] # new columns are added here
    count = 0

    for key in userAccountModelKeys:
        tempDict = {key:db_data[0][count]}
        count += 1
        userAccountModel.update(tempDict)

    return userAccountModel

def userURLsModel(db_data):
    userUrlsModel = {}

    userUrlsModelKeys = ['username', 'clique', 'role', 'url'] # new columns are added here
    count = 0

    for key in userUrlsModelKeys:
        tempDict = {key:db_data[count]}
        count += 1
        userUrlsModel.update(tempDict)

    return userUrlsModel

def userClique1PostsModel(db_data):
    userClique1PostsModel = {}

    userClique1PostsModelKeys = ['id', 'username', 'clique', 'title', 'body', 'file', 'file_type'] # new columns are added here
    count = 0

    for key in userClique1PostsModelKeys:
        tempDict = {key:db_data[count]}
        count += 1
        userClique1PostsModel.update(tempDict)

    return userClique1PostsModel

def userClique1RatedPostsModel(db_data):
    # unused but kept for just in case

    userClique1RatedPostsModel = {}

    userClique1RatedPostsModelKeys = ['post_owner', 'post_id', 'viewer', 'is_rated'] # new columns are added here
    count = 0

    for key in userClique1RatedPostsModelKeys:
        tempDict = {key:db_data[count]}
        count += 1
        userClique1RatedPostsModel.update(tempDict)

    return userClique1RatedPostsModel

def userClique2PostsModel(db_data):
    userClique2PostsModel = {}

    userClique2PostsModelKeys = ['id', 'username', 'clique', 'colgroup', 'caption', 'file', 'file_type', 'timestamp', 'likes'] # new columns are added here
    count = 0

    for key in userClique2PostsModelKeys:
        tempDict = {key:db_data[count]}
        count += 1
        userClique2PostsModel.update(tempDict)

    return userClique2PostsModel



# extras

def settings_upload_extension_validator(unverified_extension):
    # this is used for profile pictures & covers

    valid_extensions = ['png', 'jpg', 'jpeg']

    for extension in valid_extensions:
        if unverified_extension == extension:
            return True
    else:
        return False

def url_trimmer(untrimmed_url):
    '''
    This function ensures that any link provided by the user will work as intended - it does this by removing (trimming) the protocol part of the URL.
    
    I found that users could potentially add a URL that is not valid with the 'href' attribute and so I fixed this issue by prefixing a double slash at the beginning of the path specified within the attribute itself: <a href="//{{url}}">. This allows URLs to be written in any way, and still work, as long as the protocols have been removed from any absolute paths given; that is the purpose of this function.
    '''

    try:
        trimmed_url = untrimmed_url.split('//')[1] # this only grabs the part of the URL after the protocol
        return trimmed_url
    except:
        return untrimmed_url # if there are no protocols in the link provided, return it without any changes

def clique1_posts_file_upload_validator(unverified_extension):
    valid_image_extensions = ['png', 'jpg', 'jpeg', 'gif']
    valid_other_extensions = ['txt', 'zip', 'rar', '7z']

    if unverified_extension in valid_image_extensions:
        return True, 'img'
    elif unverified_extension in valid_other_extensions:
        return True, 'other'
    else:
        return False, None

def clique2_posts_file_upload_validator(unverified_extension):
    valid_image_extensions = ['png', 'jpg', 'jpeg', 'gif']
    valid_video_extensions = ['mp4']

    if unverified_extension in valid_image_extensions:
        return True, 'img'
    elif unverified_extension in valid_video_extensions:
        return True, 'vid'
    else:
        return False, None