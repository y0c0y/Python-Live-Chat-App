from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

import bcrypt

from pymongo import MongoClient  #import the pymongo
from bson.objectid import ObjectId #import this to convert ObjectID from string to its datatype in MongoDB
from datetime import datetime  #datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

#login
client = MongoClient("mongodb://localhost:27017/")  #connect on the "localhost" host and port 27017
log_db = client["users"]
records = log_db.users

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
        #profileimg = request.form.get("profileimg")
        
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
        #if not profileimg:
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
                          #'profileimg' : profileimg
                          }
            records.insert_one(user_input)
   
            return render_template('home.html')
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

#put the following code at the end of 'app.py' script
if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 5000, debug = True) #debug is True, change host and port as needed
    socketio.run(app, debug=True)