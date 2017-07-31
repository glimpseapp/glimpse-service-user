import random
import string
import os
from flask import Flask, json, make_response, request
from flaskext.mysql import MySQL


class NotificationType:
    FriendRequest = 1
    FriendStatusUpdate = 2


class FriendStatus:
    Requested = 1
    Accepted = 2
    Rejected = 3
    Canceled = 4
    Blocked = 5

    @staticmethod
    def isRequested(status):
        return int(status) == FriendStatus.Requested

    @staticmethod
    def isAccepted(status):
        return int(status) == FriendStatus.Accepted

    @staticmethod
    def isRejected(status):
        return int(status) == FriendStatus.Rejected

    @staticmethod
    def isCanceled(status):
        return int(status) == FriendStatus.Canceled

    @staticmethod
    def isBlocked(status):
        return int(status) == FriendStatus.isBlocked


class APIStatus:
    OK = 1
    Error = 2
    UsernameUnavailable = 3
    InvalidPassword = 4
    LoginFailed = 5
    NotAuthenticated = 6
    ErrorAccessingDatabase = 7
    UserIDNotFound = 8
    UsernameNotFound = 9
    InvalidRequest = 10


# config
UPLOAD_FOLDER = "/static/upload/"
UPLOAD_PATH = "/home/djnyc/api.juliano.nyc/littlewindow/static/upload"

# mysql
mysql = MySQL()
app = Flask(__name__)

# dev env
app.config['MYSQL_DATABASE_USER'] = os.getEnv('MYSQL_DATABASE_USER', 'root')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getEnv('MYSQL_DATABASE_PASSWORD', 'password')
app.config['MYSQL_DATABASE_DB'] = os.getEnv('MYSQL_DATABASE_DB', 'glimpse')
app.config['MYSQL_DATABASE_HOST'] = os.getEnv('MYSQL_DATABASE_HOST', 'localhost')

mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()


def auth_token():
    return request.headers.get("token", "")


def user_auth():
    user = verify_auth_token(auth_token())
    if user:
        return user


def verify_auth_token(token):
    cursor.execute("SELECT user.* "
                   "FROM user "
                   "JOIN user_auth ON user.user_id = user_auth.user_id "
                   "WHERE user_auth.token = %s", token)
    return cursor.fetchone()


def find_user_by_username(username):
    cursor.execute("SELECT user_id, username FROM user WHERE username = %s", (username))
    user = cursor.fetchone()
    if user:
        return user


def find_user_by_id(user_id):
    cursor.execute("SELECT user_id, username FROM user WHERE user_id = %s", (user_id))
    user = cursor.fetchone()
    if user:
        return user


@app.route("/")
def healthcheck():
    return json.dumps({"status": APIStatus.OK})


@app.route("/health")
def healthzcheck():
    return json.dumps({"status": APIStatus.OK})


@app.route("/login", methods=['POST'])
def login():
    # get data
    username = request.form['username']
    password = request.form['password']

    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if not user:
        return make_response(json.dumps({"status": APIStatus.LoginFailed}), 401)

    cursor.execute("DELETE FROM user_auth WHERE user_id = %s", (user[0]))

    token = generate_token()
    cursor.execute("INSERT INTO user_auth (user_id, token) VALUES (%s, %s)", (user[0], token))
    conn.commit()

    return json.dumps({
        "status": APIStatus.OK,
        "token": token,
        "user": {
            "user_id": user[0],
            "username": user[1]
        }
    })


@app.route("/logout", methods=['POST'])
def logout():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"status": APIStatus.NotLoggedIn}), 401)

    token = auth_token()
    cursor.execute("DELETE FROM user_auth WHERE token = %s", (token))
    conn.commit()
    return json.dumps({
        "status": APIStatus.OK,
    })


def generate_token():
    length = 30
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


@app.route("/me")
def me():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"error": "Not Authenticated"}), 401)
    return json.dumps({
        "token": user['token'],
        "user": {
            "username": user['username']
        }
    })


@app.route("/user/id/<search_user_id>")
def user_by_id():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"error": "Not Authenticated"}), 401)
    other_user = find_user_by_id(search_user_id)
    if other_user is None:
        return json.dumps({"error": APIStatus.UserIDNotFound})
    else:
        return json.dumps({
            "user_id": other_user[0],
            "username": other_user[1]
        })


@app.route("/send", methods=['POST'])
def send():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"error": "Not Authenticated"}), 401)

    # get data
    from_id = request.form['from_id']
    to_id = request.form['to_id']
    image = request.files['image']

    # save image
    filename_first, file_extension = os.path.splitext(image.filename)
    filename = filename_first + file_extension
    image.save(os.path.join(UPLOAD_PATH, filename))

    # save to db
    try:
        cursor.execute("INSERT INTO image (filename) VALUES (%s)", (filename))
        image_id = cursor.lastrowid
        cursor.execute("INSERT INTO message (from_id, to_id, image_id, time_sent) VALUES (%s, %s, %s, NOW())",
                       (from_id, to_id, image_id))
        message_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        return json.dumps({
            "error": e
        })

    return json.dumps({
        "status": APIStatus.OK,
        "from_id": from_id,
        "to_id": to_id,
        "image_id": image_id,
        "message_id": message_id,
        "filename": UPLOAD_FOLDER + filename
    })


@app.route("/messages/<handle_id>")
def read_messages(handle_id):
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"error": "Not Authenticated"}), 401)

    # read from db
    try:
        cursor.execute("SELECT message.*, from_handle.handle AS from_name, image.* "
                       "FROM message "
                       "JOIN image ON message.image_id = image.image_id "
                       "LEFT JOIN handle AS from_handle ON from_handle.handle_id = message.from_id "
                       "WHERE message.to_id = %s OR message.from_id = %s", (handle_id, handle_id))
        data = cursor.fetchall()
        messages = []
        for row in data:
            # refactor this:
            user_id = user[0]
            from_id = row[1]
            to_id = row[2]
            handle_id = from_id
            is_from_me = False
            if from_id == user_id:
                handle_id = to_id
                is_from_me = True

            messages.append({
                'message_id': row[0],
                'handle_id': handle_id,
                'is_from_me': is_from_me,
                'image_id': row[3],
                'time_sent': row[4],
                'from_name': row[5],
                'filename': row[7]
            })

    except Exception as e:
        return json.dumps({
            "status": APIStatus.ErrorAccessingDatabase,
            "error": str(e)
        })
    return json.dumps({
        "status": APIStatus.OK,
        "results": messages,
        "count": len(messages)
    })


@app.route("/register", methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    cursor.execute("SELECT username FROM user WHERE username = %s", (username))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        return json.dumps({"status": APIStatus.UsernameUnavailable})

    cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password))
    user_id = cursor.lastrowid
    token = generate_token()
    cursor.execute("INSERT INTO user_auth (user_id, token) VALUES (%s, %s)", (user_id, token))
    conn.commit()

    return json.dumps({
        "status": APIStatus.OK,
        "token": token,
        "user": {
            "user_id": user_id,
            "username": username
        }
    })


@app.route("/friendList")
def friend_list():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"status": APIStatus.NotAuthenticated}), 401)
    user_id = user[0]

    try:
        cursor.execute("SELECT user_id, username FROM user WHERE user_id IN\
        (SELECT user_id FROM user_friendship_join WHERE user_id != %s AND friendship_id IN \
        (SELECT friendship_id FROM user_friendship_join WHERE user_id = %s))", (user_id, user_id))

        data = cursor.fetchall()
        friends = []
        for row in data:
            friends.append({
                "user_id": row[0],
                "username": row[1]
            })

    except Exception as e:
        return json.dumps({
            "status": APIStatus.Error
        })

    return json.dumps({
        "status": APIStatus.OK,
        "results": friends,
        "count": len(friends)
    })


# FIXME: untested code
@app.route("/update_friend", methods=['POST'])
def update_friend_request():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"status": APIStatus.NotAuthenticated}), 401)

    user_id = user[0]
    other_user_id = request.form['user_id']
    other_user = find_user_by_id(other_user_id)

    if other_user is None:
        return json.dumps({"status": APIStatus.UsernameNotFound})

    new_status = request.form['friend_status']

    cursor.execute(
        "SELECT friend_request_id, friend_status, from_id, to_id FROM friend_request WHERE (from_id = %s AND to_id = %s) OR (from_id = %s AND to_id = %s)",
        (user_id, other_user_id, other_user_id, user_id))
    existing_request = cursor.fetchone()
    if existing_request:
        friend_request_id = existing_request[0]
        current_status = existing_request[1]
        from_id = existing_request[2]
        to_id = existing_request[3]

        other_user_id = from_id
        # the current user is updating its own friend request
        if user_id == from_id:
            other_user_id = to_id
            if FriendStatus.isCanceled(new_status) or FriendStatus.isBlocked(new_status):
                return json.dumps({"status": APIStatus.InvalidRequest})

        # the current user is updating a friend request made by someone else
        else:
            if FriendStatus.isCanceled(new_status):
                return json.dumps({"status": APIStatus.InvalidRequest})
            if FriendStatus.isAccepted(current_status) or FriendStatus.isRejected(
                    current_status) or FriendStatus.isBlocked(current_status):
                return json.dumps({"status": APIStatus.InvalidRequest})

        cursor.execute("UPDATE friend_request SET friend_status = %s WHERE friend_request_id = %s",
                       (new_status, friend_request_id))

        if FriendStatus.isAccepted(new_status) or FriendStatus.isBlocked(new_status):
            cursor.execute("INSERT INTO friendship (friend_status) VALUES (%s)", new_status)
            friendship_id = cursor.lastrowid
            cursor.execute("INSERT INTO user_friendship_join (friendship_id, user_id) VALUES (%s, %s)",
                           (friendship_id, user_id))
            cursor.execute("INSERT INTO user_friendship_join (friendship_id, user_id) VALUES (%s, %s)",
                           (friendship_id, other_user_id))

        conn.commit()
        return json.dumps({"status": APIStatus.OK})
    else:
        return json.dumps({"status": APIStatus.InvalidRequest})


@app.route("/add_friend", methods=['POST'])
def friend_request():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"status": APIStatus.NotAuthenticated}), 401)

    user_id = user[0]
    other_user_id = request.form['user_id']
    other_user = find_user_by_id(other_user_id)

    if other_user is None:
        return json.dumps({"status": APIStatus.UsernameNotFound})

    cursor.execute("SELECT friend_request_id FROM friend_request WHERE from_id = %s AND to_id = %s",
                   (user_id, other_user_id))
    existing_request = cursor.fetchone()
    if existing_request:
        return json.dumps({"status": APIStatus.InvalidRequest})

    cursor.execute("INSERT INTO friend_request (from_id, to_id, friend_status) VALUES (%s, %s, %s)",
                   (user_id, other_user_id, FriendStatus.Requested))
    conn.commit()
    return json.dumps({
        "status": APIStatus.OK
    })


@app.route("/notifications")
def get_notifications():
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"status": APIStatus.NotAuthenticated}), 401)
    user_id = user[0]

    try:
        cursor.execute("SELECT * from friend_request WHERE from_id = %s OR to_id = %s", (user_id, user_id))
        data = cursor.fetchall()
        notes = []
        for row in data:
            note_type = NotificationType.FriendRequest
            friend_status = row[3]
            if friend_status != FriendStatus.Requested:
                note_type = NotificationType.FriendStatusUpdate

            friend_request_id = row[0]
            from_id = row[1]
            to_id = row[2]

            is_from_me = False
            other_user_id = from_id

            if user_id == from_id:
                is_from_me = True
                other_user_id = to_id

            other_user = find_user_by_id(other_user_id)
            if other_user is None:
                json.dumps({"status": APIStatus.UserIDNotFound})

            other_user_name = other_user[1]

            notes.append({
                "notification_type": note_type,
                "friend_request_id": friend_request_id,
                "is_from_me": is_from_me,
                "user": {
                    'user_id': other_user_id,
                    'username': other_user_name
                },
                "friend_status": friend_status
            })

    except Exception as e:
        return json.dumps({
            "status": APIStatus.ErrorAccessingDatabase
        })

    return json.dumps({
        "status": APIStatus.OK,
        "results": notes,
        "count": len(notes)
    })


@app.route("/search/username/<search_username>")
def search_username(search_username):
    user = user_auth()
    if user is None:
        return make_response(json.dumps({"status": APIStatus.NotAuthenticated}), 401)

    # read from db
    search_string = "%" + '%'.join(list(search_username)) + "%"
    try:
        cursor.execute("SELECT user_id, username FROM user WHERE username LIKE %s", (search_string))
        data = cursor.fetchall()
        users = []
        for row in data:
            users.append({
                'user_id': row[0],
                'username': row[1]
            })

    except Exception as e:
        return json.dumps({
            "status": APIStatus.ErrorAccessingDatabase
        })

    return json.dumps({
        "status": APIStatus.OK,
        "results": users,
        "count": len(users)
    })


if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0')
