from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

import bcrypt

from pymongo import MongoClient  #import the pymongo
from bson.objectid import ObjectId #import this to convert ObjectID from string to its datatype in MongoDB
from werkzeug.utils import secure_filename #for secure name
from datetime import datetime  #datetime
from gridfs import GridFS

# Import necessary modules and packages
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

#login
client = MongoClient("mongodb://localhost:27017/")  #connect on the "localhost" host and port 27017
log_db = client["users"]
records = log_db.users
fs = GridFS(log_db, collection = "images")

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = records.find_one({"email": email})

        if email_found:
            email_val = email_found["email"]
            passwordcheck = email_found["password"]

            if bcrypt.checkpw(password.encode("utf-8"), passwordcheck):
                session["email"] = email_val
                return redirect(url_for("forumhome"))
            else:
                flash("Wrong Password")
                return render_template("home.html")
        else:
            flash("Email not found")
            return render_template("home.html")
    return render_template("home.html")

@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == "POST":
        user = request.form.get("username")
        email = request.form.get("email")
        available = request.form.get("available")
        learning = request.form.get("learning")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        bio = request.form.get("bio")
        profileimg = request.files.get("profileimg") 
        
        user_found = records.find_one({"username": user})
        email_found = records.find_one({"email": email})
        if not user:
            flash("Please enter your username")
            return render_template('register.html')
        if not email:
            flash("Please enter your email")
            return render_template('register.html')
        if not available:
            flash("Please enter your available language")
            return render_template('register.html')
        if not learning:
            flash("Please enter your learning language")
            return render_template('register.html')
        if not password1:
            flash("Please enter your password")
            return render_template('register.html')
        if not password2:
            flash("Please enter your password")
            return render_template('register.html')
        if not bio:
            flash("Please enter your bio")
            return render_template('register.html')
        if not profileimg:
            flash("Please upload your image")
            return render_template('register.html')
        if user_found:
            flash("There is already a user that exists by that username")
            return render_template('register.html')
        if email_found:
            flash("This email already exists in the database")
            return render_template('register.html')
        if password1 != password2:
            flash("Passwords should match!")
            return render_template('register.html')
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'username' : user,  
                          'email' : email, 
                          'available' : available,
                          'learning' : learning,
                          'password' : hashed,
                          'bio' : bio
                          }
            user_id = records.insert_one(user_input).inserted_id
            fs.put(profileimg, filename = 'profileimg', user_id = user_id) 

            return redirect(url_for('login'))
    return render_template('register.html')

db = client["forum"]  #use/create "forum" database
general = db.general  #use/create "general" collection
fstudygroups = db.fstudygroups  #use/create "fstudygroups" collection
english = db.english  #use/create "english" collection
korean = db.korean  #use/create "korean" collection
others = db.others  #use/create "others" collection
comments_gen = db.comments_gen  #use/create "comments_gen" collection
comments_fst = db.comments_fst  # use/create "comments_gen" collection
comments_eng = db.comments_eng  #use/create "comments_gen" collection
comments_kor = db.comments_kor  #use/create "comments_gen" collection
comments_oth = db.comments_oth  #use/create "comments_gen" collection
comments_mem = log_db.comments_mem  #use/create "comments_mem" collection

@app.route("/forum/index")
def forumhome():
    return render_template("forumhome.html")

@app.route("/forum/general")
def general_all():
    all_general = general.find()  #get all projects data
    all_general_list = list(all_general)  #convert the data into list

    return render_template("general.html", data = all_general_list)

@app.route("/forum/general/read/<id>")
def general_read(id):
    #convert from string to ObjectId:
    _id_converted = ObjectId(id)
    search_filter = {
        "_id": _id_converted
    }  #_id is key and _id_converted is the converted _id
    general_data = general.find_one(
        search_filter
    )  #get one project data matched with _id
    all_comments_gen = comments_gen.find({"postid": id})
    all_comments_gen_list = list(all_comments_gen)

    return render_template(
        "general-read.html", data = general_data, comments = all_comments_gen_list
    )

#only accessible if user is logged in, else redirects to login page
@app.route("/forum/general/addpost", methods = ["GET", "POST"])
def general_add():
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        title = request.form["title"]
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "title": title,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        general.insert_one(new_project_value)

        #redirect to projects admin page
        return redirect(url_for("general_all"))

    #else (not POST aka GET) then show the new input form
    return render_template("general-add.html")

@app.route("/forum/fstudygroups")
def fstudygroups_all():
    all_fstudygroups = fstudygroups.find()  #get all projects data
    all_fstudygroups_list = list(all_fstudygroups)  #convert the data into list

    return render_template("fstudygroups.html", data = all_fstudygroups_list)

@app.route("/forum/fstudygroups/read/<id>")
def fstudygroups_read(id):
    #convert from string to ObjectId:
    _id_converted = ObjectId(id)
    search_filter = {
        "_id": _id_converted
    }  #_id is key and _id_converted is the converted _id
    fstudygroups_data = fstudygroups.find_one(
        search_filter
    )  #get one project data matched with _id
    all_comments_fst = comments_fst.find({"postid": id})
    all_comments_fst_list = list(all_comments_fst)

    return render_template(
        "fstudygroups-read.html", data = fstudygroups_data, comments = all_comments_fst_list
    )

#only accessible if user is logged in, else redirects to login page
@app.route("/forum/fstudygroups/addpost", methods = ["GET", "POST"])
def fstudygroups_add():
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        title = request.form["title"]
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "title": title,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        fstudygroups.insert_one(new_project_value)

        #redirect to projects admin page
        return redirect(url_for("fstudygroups_all"))

    #else (not POST aka GET) then show the new input form
    return render_template("fstudygroups-add.html")

@app.route("/forum/english")
def english_all():
    all_english = english.find()  #get all projects data
    all_english_list = list(all_english)  #convert the data into list

    return render_template("english.html", data = all_english_list)

@app.route("/forum/english/read/<id>")
def english_read(id):
    #convert from string to ObjectId:
    _id_converted = ObjectId(id)
    search_filter = {
        "_id": _id_converted
    }  #_id is key and _id_converted is the converted _id
    english_data = english.find_one(
        search_filter
    )  #get one project data matched with _id
    all_comments_eng = comments_eng.find({"postid": id})
    all_comments_eng_list = list(all_comments_eng)

    return render_template(
        "english-read.html", data = english_data, comments = all_comments_eng_list
    )

#only accessible if user is logged in, else redirects to login page
@app.route("/forum/english/addpost", methods = ["GET", "POST"])
def english_add():
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        title = request.form["title"]
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "title": title,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        english.insert_one(new_project_value)

        #redirect to projects admin page
        return redirect(url_for("english_all"))

    #else (not POST aka GET) then show the new input form
    return render_template("english-add.html")

@app.route("/forum/korean")
def korean_all():
    all_korean = korean.find()  #get all projects data
    all_korean_list = list(all_korean)  #convert the data into list

    return render_template("korean.html", data = all_korean_list)

@app.route("/forum/korean/read/<id>")
def korean_read(id):
    #convert from string to ObjectId:
    _id_converted = ObjectId(id)
    search_filter = {
        "_id": _id_converted
    }  #_id is key and _id_converted is the converted _id
    korean_data = korean.find_one(
        search_filter
    )  #get one project data matched with _id
    all_comments_kor = comments_kor.find({"postid": id})
    all_comments_kor_list = list(all_comments_kor)

    return render_template(
        "general-read.html", data = korean_data, comments = all_comments_kor_list
    )

#only accessible if user is logged in, else redirects to login page
@app.route("/forum/korean/addpost", methods = ["GET", "POST"])
def korean_add():
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        title = request.form["title"]
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "title": title,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        korean.insert_one(new_project_value)

        #redirect to projects admin page
        return redirect(url_for("korean_all"))

    #else (not POST aka GET) then show the new input form
    return render_template("korean-add.html")

@app.route("/forum/others")
def others_all():
    all_others = others.find()  #get all projects data
    all_others_list = list(all_others)  #convert the data into list

    return render_template("others.html", data = all_others_list)

@app.route("/forum/others/read/<id>")
def others_read(id):
    #convert from string to ObjectId:
    _id_converted = ObjectId(id)
    search_filter = {
        "_id": _id_converted
    }  #_id is key and _id_converted is the converted _id
    others_data = others.find_one(
        search_filter
    )  #get one project data matched with _id
    all_comments_oth = comments_oth.find({"postid": id})
    all_comments_oth_list = list(all_comments_oth)

    return render_template(
        "others-read.html", data = others_data, comments = all_comments_oth_list
    )

#only accessible if user is logged in, else redirects to login page
@app.route("/forum/others/addpost", methods = ["GET", "POST"])
def others_add():
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        title = request.form["title"]
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "title": title,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        others.insert_one(new_project_value)

        #redirect to projects admin page
        return redirect(url_for("others_all"))

    #else (not POST aka GET) then show the new input form
    return render_template("others-add.html")

@app.route("/forum/general/comment/add/<id>", methods = ["POST"])
def comment_add_gen(id):
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        postid = id
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "postid": postid,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        comments_gen.insert_one(new_project_value)

        return redirect(url_for("general_read", id = postid))

@app.route("/forum/fstudygroups/comment/add/<id>", methods = ["POST"])
def comment_add_fst(id):
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        postid = id
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "postid": postid,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        comments_fst.insert_one(new_project_value)

        return redirect(url_for("fstudygroups_read", id = postid))

@app.route("/forum/english/comment/add/<id>", methods = ["POST"])
def comment_add_eng(id):
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        postid = id
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "postid": postid,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        comments_eng.insert_one(new_project_value)

        return redirect(url_for("english_read", id = postid))

@app.route("/forum/korean/comment/add/<id>", methods = ["POST"])
def comment_add_kor(id):
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        postid = id
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "postid": postid,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        comments_kor.insert_one(new_project_value)

        return redirect(url_for("korean_read", id = postid))
    
@app.route("/forum/others/comment/add/<id>", methods = ["POST"])
def comment_add_oth(id):
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        postid = id
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "postid": postid,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        comments_oth.insert_one(new_project_value)

        return redirect(url_for("others_read", id = postid))
    
rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code
    
@app.route("/messages", methods = ["POST", "GET"])
def chathome():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            flash("Please enter your username")
            return render_template("chathome.html", code = code, name = name)

        if join != False and not code:
            flash("Please enter a room code")
            return render_template("chathome.html", code = code, name = name)
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            flash("Room does not exist")
            return render_template("chathome.html", code = code, name = name)
        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))

    return render_template("chathome.html")

@app.route("/messages/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("chathome"))

    return render_template("room.html", code = room, messages = rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to = room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to = room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message" : "has left the room"}, to = room)
    print(f"{name} has left the room {room}")

#profile

@app.route("/profile")
def profile():
    if "email" in session:
        email = session["email"]
        user_info = records.find_one({"email": email})
        username = user_info["username"]
        available = user_info["available"]
        learning = user_info["learning"]
        bio = user_info["bio"]
        user_id = user_info["_id"]
        
        profileimg = fs.find_one({"user_id": user_id, "filename": "profileimg"})
        if profileimg:
            profileimg_url = url_for("image", filename=profileimg.filename)
        else:
            profileimg_url = None

        return render_template("profile.html", username=username, email=email, available=available,
                               learning=learning, bio=bio, profileimg=profileimg_url)
    else:
        return redirect(url_for('login'))

# Import necessary modules and packages

@app.route("/update-profile", methods=['GET', 'POST'])
def update_profile():
    if "email" in session:
        email = session["email"]
        user_info = records.find_one({"email": email})
        username = user_info["username"]
        available = user_info["available"]
        learning = user_info["learning"]
        bio = user_info["bio"]
        user_id = user_info["_id"]
        profileimg = fs.find_one({"metadata.user_id": user_id})

        if profileimg:
            profileimg_url = url_for("image", filename=profileimg.filename)
        else:
            profileimg_url = None

        if request.method == "POST":
            new_username = request.form.get("username")
            new_available = request.form.get("available")
            new_learning = request.form.get("learning")
            new_bio = request.form.get("bio")
            new_profileimg = request.files.get("profileimg")

            # 프로필 사진 업데이트
            if new_profileimg:
                # 이전 프로필 사진 삭제
                if profileimg:
                    fs.delete(profileimg._id)

                # 새로운 프로필 사진 저장
                profileimg_id = fs.put(new_profileimg, filename="profileimg", metadata={"user_id": user_id})
            else:
                profileimg_id = None

            # 이메일을 제외한 나머지 정보 업데이트
            records.update_one(
                {"email": email},
                {
                    "$set": {
                        "username": new_username,
                        "available": new_available,
                        "learning": new_learning,
                        "bio": new_bio
                    }
                }
            )

            # 프로필 업데이트 후 프로필 페이지로 리디렉션
            return redirect(url_for('profile'))

        return render_template("update-profile.html", username=username, email=email, available=available,
                               learning=learning, bio=bio, profileimg=profileimg_url)

    # 로그인되지 않은 경우 로그인 페이지로 리디렉션
    return redirect(url_for('login'))

@app.route("/memberprofile/<id>")
def memberprofile(id):
        #convert from string to ObjectId:
        _id_converted = ObjectId(id)
        search_filter = {
            "_id": _id_converted
        }  #_id is key and _id_converted is the converted _id
        member_data = records.find_one(
            search_filter
        )  #get one project data matched with _id
        username = member_data["username"]
        available = member_data["available"]
        learning = member_data["learning"]
        bio = member_data["bio"]
        user_id = member_data["_id"]
        profileimg = fs.find_one({"user_id" : user_id, "filename" : "profileimg"})
        if profileimg:
            profileimg_url = url_for("image", filename = profileimg.filename)
        else:
            profileimg_url = None
        all_comments_mem = comments_mem.find({"postid": id})
        all_comments_mem_list = list(all_comments_mem)

        return render_template("memberprofile.html", user_id = user_id, username = username, available = available, learning = learning, bio = bio, profileimg = profileimg_url, comments = all_comments_mem_list)

@app.route("/memberprofile/comment/add/<id>", methods = ["POST"])
def comment_mem(id):
    #handling a form is submitted via POST aka updating the project data
    if request.method == "POST":
        #get data from a submitted based on the 'name' in the input form
        postid = id
        nickname = request.form["nickname"]
        description = request.form["description"]

        #prepare new project data
        #{"key": new value }
        new_project_value = {
            "postid": postid,
            "nickname": nickname,
            "description": description,
            "date": datetime.now(),
        }

        #run the query to save one project data
        comments_mem.insert_one(new_project_value)

        return redirect(url_for("memberprofile", id = postid))
    
@app.route("/image/<filename>")
def image(filename):
    image_data = fs.get_last_version(filename = filename)
    if image_data:
        response = app.response_class(image_data.read(), mimetype = 'application/octet-stream')
        response.headers.set('Content-Disposition', 'attachement', filename = filename)
        return response
    else:
        return "Image not found"

@app.route("/searchmembers", methods=['GET', 'POST'])
def members():
    if request.method == 'POST':
        search_query = request.form.get('search_query')  # 검색어 가져오기
        if search_query:
            query = {"username": {"$regex": search_query, "$options": "i"}}  # 사용자 이름에 검색어가 포함된 멤버를 찾는 예시
            all_members = records.find(query)
        else:
            all_members = records.find()  # 검색어가 없으면 모든 멤버 정보를 데이터베이스에서 조회
    else:
        all_members = records.find()  # GET 요청이면 모든 멤버 정보를 데이터베이스에서 조회

    all_members_list = list(all_members)  # 조회된 정보를 리스트로 변환

    # Render the members.html template with the members data
    return render_template("members.html", data = all_members_list)  

#put the following code at the end of 'app.py' script
if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True) #debug is True, change host and port as needed
    socketio.run(app, debug = True)