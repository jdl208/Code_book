from codebook import login_manager, mongo


@login_manager.user_loader
def load_user(username):
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return None
    return User(user['username'], user['email'], user['password'], user['profile_pic'])


class User():
    def __init__(self, username, email, password, profile_pic):
        self.username = username
        self.email = email
        self.password = password
        self.profile_pic = profile_pic

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username
