from app import app, db, bcrypt
from flask import url_for, render_template, redirect, request, jsonify, make_response, send_file, send_from_directory, abort, safe_join, session, flash
from datetime import datetime
from models import User
from tasks import *
import os, secrets
from app import r
from app import q

@app.route('/')
def home():
    #abort(500)
    return render_template("/public/home.html")

@app.template_filter()
def clean_date(date):
    return datetime.strftime(date,"%y-%m-%d")

@app.template_filter()
def clean_time(time):
    return datetime.strftime(time, "%H:%M:%S")
    
#Try differnt objects to display using jinja template
langs = ['Python', 'Java','C', 'C++']
student_info = {
                "first_name" : "Raghav",
                "last_name"  : "Chadda",
                "age"  : 12,
                "class" :"7th Grade",
                "nationality" : "Indian",
                "hobbies": "Arts and Crafts"
               }
age = 30

class TestJinja():
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.email = "{}@gmail.com".format(self.first_name)
    
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)
            

@app.route("/jinja_templating")
def jinja_template():

    test_jinja = TestJinja(student_info['first_name'], student_info['last_name'])    
    return render_template("/public/jinja.html", 
                            langs=langs, 
                            student_info=student_info,
                            test_jinja = test_jinja,
                            age = age,
                            date = datetime.utcnow()
                            )

@app.route('/about')
def about():
    return render_template('/public/about.html')

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        req = request.form
        db.create_all()
        if req.get('password') == "":
            flash("Password cannot be blank", 'danger')
            return render_template("public/register.html")
        if len(req.get('password')) <10 :
            flash("Password must contain atleast 10 characters", "danger")
            return render_template("public/register.html")
        if req.get('password') != req.get('confirm_password'):
            flash("Password and Confirm_password must match", "danger")
            return render_template("public/register.html")
        password_hash = bcrypt.generate_password_hash(req.get("password")).decode('utf-8')
        user = User(username=req.get('username') , email=req.get('email'), password=password_hash)
        db_username = User.query.filter_by(username=user.username).first()
        if req.get('username') == "":
            flash("Please enter username, cant be blank", "danger")
            return render_template("public/register.html")
        if len(req.get('username')) < 8:
            flash("Username must contain atleast eight characters", "danger")
            return render_template("public/register.html")
        if db_username:
            flash("username already exist", "warning")
        else:
            db.session.add(user)
            db.session.commit()
            flash(f"User {req.get('username')} registered succesfully", "success")
            return render_template('public/login.html')
    return render_template('/public/register.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':
       req = request.form
       user = User.query.filter_by(email=req.get('email')).first()
       if user is not None:
            if req.get('email') == user.email and bcrypt.check_password_hash(user.password, req.get('password')):
                flash(f"Welcome {user.username}", "success")
                session['user_id'] = user.id
                session['role'] = "Admin"
                print(session.get('user_id'))
                return render_template("public/home.html", session=session)
            else:
                flash("Please check the username and password", "danger")
       else:
            flash(f"User does not exist with email {req.get('email')}", "warning")
    return render_template("public/login.html")

@app.route('/logout')
def logout():
    if session:
        session.pop('user_id', None)
        session.pop('role', None)
    return render_template("public/home.html")

UserNames = {
                "Gandhi":{
                            "name"  :"MK Gandhi",
                            "Date_Of_Birth" : "02-OCT-1869",
                            "Place_Of_Birth" : "India, Gujarat",
                            "AKA" : "Father of Indian Nation"
                          },
                "Hitler": { 

                            "name" : "Adolf Hitler",
                            "Date_Of_Birth":"20-APR-1889",
                            "Place_Of_Birth":"Austria",
                            "AKA" : "NAZI"
                          }

            }
    
@app.route("/profile/<username>")
def public_profile(username):
    
    user = None
    if username in UserNames:
       user = UserNames[username]

    return render_template("/public/profile.html",username=username,  user=user)

@app.route("/multiple/<foo>/<bar>/<baz>")
def multiple(foo, bar, baz):
    return f"foo is {foo}, bar is {bar}, baz is {baz}"

@app.route("/json", methods=["GET","POST"])
def json():
    if request.is_json:
        req = request.get_json()
        response = {
        
                    "msg":"JSON RECEIVED",
                    "name":req.get("name")
                    }
        res = make_response(jsonify(response), 200)
        return res
    else:
        return make_response(jsonify({"msg": "JSON NOT RECEIVED"}), 400)

@app.route("/guestbook", methods=['POST'])
def guestbook():
    return render_template("public/guestbook.html")

@app.route("/guestbook/create-entry", methods=["POST"])
def guestbook_entry():
    req = request.get_json()
    response = make_response(jsonify({"message" : req['message'], "name":req['name']}) ,200)
    return response


@app.route("/query")
def query():
    if request.args:
        args = request.args
        if "test" in args:
            print(f"test : {args.get('test')}")
        if "bar" in args:
            print(f"bar : {args.get('bar')}")
    return "No query string received", 200

def allowed_images(filename):
    if not "." in filename:
        return False
    allowed_extension = filename.rsplit(".")[-1]
    if allowed_extension.upper() in app.config["ALLOWED_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/upload-image", methods=['GET','POST'])
def upload_image():
    if request.method == 'POST':
        image = request.files['image']

        if image.filename == " ":
            return redirect(request.url)

        if allowed_images(image.filename):
            if int(request.cookies['filesize']) < int(app.config['MAX_FILE_SIZE']):
                image.save(os.path.join(app.config['IMAGE_UPLOADS'], image.filename))
                print("Image Saved")
                print(request.cookies['filesize'])
                return redirect(request.url)
            else:
                print(f"Image size {request.cookies['filesize']}exceeds max allowed size {app.config['MAX_FILE_SIZE']}")
                return redirect(request.url)
        else:
            print("Image Extension not allowed")
            return redirect(request.url)
            
        return redirect(request.url)
    return render_template("/public/upload_image.html")
    

@app.route("/get_image/<image_name>")
def send_files(image_name):
    try:
        file_extension = image_name.rsplit(".")[-1].upper()
        if file_extension in ['PNG','JPEG','JPG','GIF']:
            return send_from_directory(app.config['CLIENT_IMAGES'], filename=image_name,as_attachment=True)
        elif file_extension == "PDF":
            return send_from_directory(app.config['CLIENT_PDF'], filename=image_name,as_attachment=True)
        elif file_extension == "CSV":
            return send_from_directory(app.config['CLIENT_CSV'], filename=image_name,as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route("/get_report/<path:file_path>")
def client_reports(file_path):
    safe_path = safe_join(app.config['CLIENT_CSV'], file_path)
    try:
        return send_file(safe_path, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route("/download")
def download_files():
    image_name = "BC.CSV"
    return render_template("/public/download.html", image_name="BC.csv")


'''
set_cookie(
    key,
    value='',
    max_age=None,
    expires=None,
    path='/',
    domain=None,
    secure=False,
    httponly=False,
    samesite=None
)
'''
@app.route("/cookies")
def cookies():
    response = make_response("Cookies", 200)
    response.set_cookie(
        "flavour",
        value="chocolate chip",
        max_age=10,
        path=request.path)
    print(request.cookies)
    return response


#HTTP MEthods

inventory = {

        "Fruits": {
            
            "apple" : 10,
            "orange": 20
        },
        "Electronics": {

            "mouse" : 10,
            "keyboard": 20
        },
        "Textiles": {
            "shirts" : 20,
            "pants"  : 30
        }
    
}
@app.route('/get-text')
def get_text():
    return "Get HTTP Method"

@app.route("/inventory/<collection>", methods=['GET', 'POST'])
def inventory_collection(collection):
    req = request.form
    if request.method == 'POST':
        if req.get('collection') == "":
            flash(f"Please provide collection name", "danger")
            return render_template('public/collection.html', collection=inventory)
        if req.get('products') == "":
            flash(f"Please provide product name", "danger")
            return render_template('public/collection.html', collection=inventory)
            
        if req.get('collection') is not None:
            if req.get('collection') not in inventory:
                inventory[req.get('collection')] ={}
                inventory[req.get('collection')][req.get('products')] = req.get('quantity')

                return render_template('public/collection.html', collection=inventory)
    return render_template('public/collection.html', collection=inventory)


@app.route('/post-request/<collection>', methods=['GET','POST', 'PUT', 'PATCH'])
def post_request(collection):
    
    if request.method == 'POST':
        req = request.get_json()
        if collection in inventory:
            return req
        else:
            inventory.update({collection : req})
            return make_response(jsonify(inventory), 200)
    if request.method == 'PUT':
        req = request.get_json()

    if request.method == 'PATCH':
        req = request.get_json()

    return req


@app.route('/put-request/<collection>', methods=['PUT'])
def put_request(collection):
    
    if request.method == 'PUT':
        req =  request.get_json()
        if collection in inventory:
            inventory.update({collection : req })
            return make_response(jsonify(inventory), 200)

@app.route('/patch-request/<collection>', methods=['PATCH'])
def patch_request(collection):
    
    if request.method == 'PATCH':
        req =  request.get_json()
        if collection in inventory:
            for item, quantity in req.items():
                inventory[collection][item] = quantity
            return make_response(jsonify(inventory), 200)
#        else:
#            inventory[collection] = req
#            return make_response(jsonify(inventory), 201)
    return make_response(jsonify({collection : "Collection not found in the inventory"}))


#To Implement Delete Request


@app.route("/tasks")
def bakground_tasks():
    
    if request.args.get("n"):
        job = q.enqueue(tasks.background_task, request.args.get('n'))
        return f" Task {job.id} added to the queue at {job.enqueued_at} {job.result}"

    return "No value for count provided"

@app.route("/added_tasks", methods=['GET','POST'])
def tasks():
    req = request.form
    if req:
        url=req.get('url')
        task=q.enqueue(count_words, url)
        jobs = q.jobs
        q_len = len(q)
        message = f"Task queued at {task.enqueued_at.strftime('%a, %d %b %Y %H:%M:%S')}. {q_len} jobs queued"
    return render_template("public/tasks.html", jobs=jobs, message=message)


### RESIZE IMAGES ##
@app.route("/upload_resized_images", methods=['GET', 'POST'])
def resized_images():
    if request.method == 'POST':
        image = request.files['image']
        image_dir_name = secrets.token_hex(16)
        os.mkdir(os.path.join(app.config['IMAGE_UPLOADS'], image_dir_name))
        image.save(os.path.join(app.config['IMAGE_UPLOADS'], image_dir_name, image.filename))
        image_dir = os.path.join(app.config['IMAGE_UPLOADS'], image_dir_name)
        jobs = q.enqueue(image_task, image_dir, image.filename)
        flash("Image Uploaded and sent for resizing", "success")
        message = f"/image/{image_dir_name}/{image.filename.split('.')[0]}"
    return render_template("public/upload_resize_img.html")

