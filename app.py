from flask import Flask,render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_session import Session
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import pickle

# app = Flask(__name__,template_folder="template")          

app = Flask(__name__)
app.secret_key = 'prakriti_assessment'
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///prakriti.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

rSession = sessionmaker(bind=db.engine)
rsession = rSession()

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Models
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    kapha_per = db.Column(db.Integer, default=0)
    vata_per = db.Column(db.Integer, default=0)
    pitta_per = db.Column(db.Integer, default=0)
    dosha = db.Column(db.String(100), default="Not defined")
    city = db.Column(db.String(100), nullable=False)
    date_status = db.Column(db.DateTime, default=date.today())
    
    def __repr__(self) -> str:
        return f"{self.user_id} {self.user_name} {self.email} {self.password} {self.kapha_per} {self.vata_per} {self.pitta_per} {self.dosha} {self.city} {self.date_status}"
    
class MyChats(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    query = db.Column(db.String(500), nullable=False)
    response = db.Column(db.String(500), nullable=False)
    date_status = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"{self.chat_id} {self.user_id} {self.query} {self.response} {self.date_status}"

class Questions(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    weightage = db.Column(db.Integer, nullable=False)
    dosha_type = db.Column(db.String(100), nullable=False)
    
    def __repr__(self) -> str:
        return f"{self.question_id} {self.question} {self.answer} {self.weightage} {self.dosha_type}"
    
class Doctors(db.Model):
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.String(100), nullable=False)
    specialist = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(500), nullable=False)
    
    def __repr__(self) -> str:
        return f"{self.doctor_id} {self.name} {self.email} {self.mobile_no} {self.specialist} {self.city} {self.address} {self.location}"
    
class Contactus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    comments = db.Column(db.String(500), nullable=False)
    date_status = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"{self.id} {self.name} {self.email} {self.subject} {self.comments} {self.date_status}"
    
class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    mobie_no = db.Column(db.String(100), nullable=False)    
    date_status = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"{self.admin_id} {self.email} {self.password} {self.mobie_no} {self.date_status}"

class Diet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dosha_type = db.Column(db.String(100), nullable=False)
    diet = db.Column(db.String(500), nullable=False)
    date_status = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return f"{self.id} {self.diet} {self.dosha_type} {self.date_status}"

class Lifestyle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dosha_type = db.Column(db.String(100), nullable=False)
    lifestyle_heading = db.Column(db.String(500), nullable=False)
    lifestyle_description = db.Column(db.String(500), nullable=False)
    date_status = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return f"{self.id} {self.lifestyle_heading} {self.dosha_type} {self.lifestyle_description} {self.date_status}"

class Yoga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dosha_type = db.Column(db.String(100), nullable=False)
    yoga_heading = db.Column(db.String(500), nullable=False)
    yoga_description = db.Column(db.String(500), nullable=False)
    date_status = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return f"{self.id} {self.yoga_heading} {self.dosha_type} {self.yoga_description} {self.date_status}"


# home page
@app.route('/')
def hello_world():    
    msg = ""
    return render_template('index.html', msg=msg)

@app.route('/contactusindex', methods = ['GET', 'POST'])
def contactusindex():
    msg = ""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        comments = request.form['message']        
        data = Contactus(name=name, email=email, subject=subject, comments=comments)
        db.session.add(data)
        db.session.commit()
        return render_template('index.html', msg=msg)    

@app.route('/register', methods = ['GET', 'POST'])
def register():
    gmsg = ""
    bmsg = ""
    if request.method == 'POST':
        fname = request.form['firstName']
        lname = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        cpass = request.form['cpass']
        city = request.form['city']
        name = fname + " " + lname
        
        check = Users.query.filter_by(email=email).first()
        if check:
            bmsg = "This email is already registered"
            return render_template('register.html', gmsg=gmsg, bmsg=bmsg)
        if password == cpass:
            hashed_password = generate_password_hash(password)
            data = Users(user_name=name, email=email, password=hashed_password, city=city)
            db.session.add(data)
            db.session.commit()
            gmsg = "User registration is successful"
            return render_template('register.html', gmsg=gmsg, bmsg=bmsg)            
        else:
            bmsg = "Password didn't match"
            return render_template('register.html', gmsg=gmsg, bmsg=bmsg)
        
    return render_template('register.html', gmsg=gmsg, bmsg=bmsg)

@app.route('/adminregistration', methods = ['GET', 'POST'])
def adminregistration():
    gmsg = ""
    bmsg = ""
    if request.method == 'POST':
        fname = request.form['firstName']
        lname = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        cpass = request.form['cpass']
        mobile_no = request.form['mobile_no']
        name = fname + " " + lname

        check = Admin.query.filter_by(email=email).first()
        if check:
            bmsg = "This email is already registered"
            return render_template('admin_registration.html', gmsg=gmsg, bmsg=bmsg)
        if password == cpass:
            data = Admin(admin_name=name, email=email, password=password, mobie_no=mobile_no)
            db.session.add(data)
            db.session.commit()
            gmsg = "Registration successgul"
            return render_template('admin_registration.html', gmsg=gmsg, bmsg=bmsg)
        else:
            bmsg = "Password didn't match"
            return render_template('admin_registration.html', gmsg=gmsg, bmsg=bmsg)
        
    return render_template('admin_registration.html', gmsg=gmsg, bmsg=bmsg)

@app.route('/adminlogin', methods = ['GET', 'POST'])
def adminlogin():
    msg = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        data = Admin.query.filter_by(email=email, password=password).first()
        if data:
            session["email"] = request.form.get("email")
            # print("User email: ")
            # print(session.get('email'))
            return redirect(url_for('admin'))   
        else:
            msg = "Email or password is incorrect"       
            return render_template('admin_login.html', msg=msg)   
    return render_template('admin_login.html', msg=msg)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        data = Users.query.filter_by(email=email).first()
        if data:
            hashed_password = data.password
            if check_password_hash(hashed_password, password):
                session["email"] = request.form.get("email")
                # print("User email: ")
                # print(session.get('email'))
                return redirect(url_for('userdashboard'))   
        else:
            msg = "Email or password is incorrect"       
            return render_template('login.html', msg=msg)   
    return render_template('login.html', msg=msg)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# admin side
@app.route('/admin')
def admin():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        users_count = Users.query.count()
        questions_count = Questions.query.count()
        doctors_count = Doctors.query.count()
        contactus_count = Contactus.query.count()
        return render_template('admin.html', users_count=users_count, questions_count=questions_count, doctors_count=doctors_count, contactus_count=contactus_count, name=name, mail=mail)

@app.route('/RegisterUser', methods = ['GET', 'POST'])
def RegisterUser():  
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Users.query.all()  
        return render_template('RegisterUser.html', data=data, name=name, mail=mail)

@app.route('/userdetails/<int:user_id>', methods = ['GET', 'POST'])
def userdetails(user_id):  
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        print("user_id: ", user_id)  
        data = Users.query.filter_by(user_id=user_id).first()  
        print(data.user_name)
        return render_template('userdetails.html', data=data, mail=mail, name=name)
    
@app.route('/userdelete/<int:user_id>', methods = ['GET', 'POST'] )
def userdelete(user_id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
        data = Users.query.filter_by(user_id=user_id).first()
        db.session.delete(data)
        db.session.commit()   
        return redirect("/RegisterUser")

@app.route('/QuestionsPanel', methods = ['GET', 'POST'])
def QuestionsPanel():
    if not session.get("email"):  
        return redirect('/login') 
    else:   
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Questions.query.all() 
        return render_template('QuestionsPanel.html', data=data, name=name, mail=mail)

@app.route('/addquestion', methods = ['GET', 'POST'])
def addquestion():
    if not session.get("email"):  
        return redirect('/login') 
    else:    
        msg = ""    
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        if request.method == 'POST':
            question = request.form['question']
            answer = request.form['answer']
            weightage = request.form['weightage']
            dosha_type = request.form['dosha_type']
            data = Questions(question=question, answer=answer, weightage=weightage, dosha_type=dosha_type)
            db.session.add(data)
            db.session.commit()
            msg = "Question added successfully"
            print("success")        
            return render_template('addquestion.html', name=name, mail=mail, msg=msg)
        return render_template('addquestion.html', name=name, mail=mail, msg=msg)

@app.route('/updatequestion/<int:question_id>',methods = ['GET', 'POST'])
def updatequestion(question_id): 
    if not session.get("email"):  
        return redirect('/login') 
    else:      
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email 
        if request.method == "POST":
            question = request.form['question']
            answer = request.form['answer']        
            weightage = request.form['weightage'] 
            dosha_type = request.form['dosha_type']             
            quest = Questions.query.filter_by(question_id=question_id).first() 
            quest.question = question
            quest.answer = answer
            quest.weightage = weightage
            quest.dosha_type = dosha_type
            db.session.add(quest)
            db.session.commit()        
            return redirect("/QuestionsPanel")
        quest = Questions.query.filter_by(question_id=question_id).first() 
        return render_template("updatequestion.html", quest=quest, name=name, mail=mail)    

@app.route('/deletequestion/<int:question_id>')
def deletequestion(question_id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
        quest = Questions.query.filter_by(question_id=question_id).first()    
        db.session.delete(quest)
        db.session.commit()   
        return redirect("/QuestionsPanel")

@app.route('/Doctorslist', methods = ['GET', 'POST'] )
def Doctorslist():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Doctors.query.all()
        return render_template('Doctorslist.html', data=data, name=name, mail=mail)

@app.route('/add_doctor', methods = ['GET', 'POST'])
def add_doctor():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        msg = ""
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            mobile = request.form['mobile']
            speciality = request.form['specialist']
            city = request.form['city']
            address = request.form['address']
            location = request.form['location']

            data = Doctors(name=name, email=email, mobile_no=mobile, specialist=speciality, city=city, address=address, location=location)
            db.session.add(data)
            db.session.commit()
            msg = "Doctor added successfully..!"
            return render_template('add_doctor.html', msg=msg, name=name, mail=mail)
        return render_template('add_doctor.html', msg=msg, name=name, mail=mail)

@app.route('/updatedoctor/<int:doctor_id>', methods = ['GET', 'POST'] )
def updatedoctor(doctor_id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Doctors.query.filter_by(doctor_id=doctor_id).first()
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            mobile = request.form['mobile']
            speciality = request.form['specialist']
            city = request.form['city']
            address = request.form['address']
            location = request.form['location']
    # data = Doctors(name=name, email=email, mobile_no=mobile, specialist=speciality, city=city, address=address, location=location)
            data = Doctors.query.filter_by(doctor_id=doctor_id).first()
            data.name = name
            data.email = email
            data.mobile_no = mobile
            data.specialist = speciality
            data.city = city
            data.address = address
            data.location = location
            db.session.add(data)
            db.session.commit()  
            return redirect("/Doctorslist")
        return render_template('update_doctor.html', data=data, name=name, mail=mail)

@app.route('/deletedoctor/<int:doctor_id>', methods = ['GET', 'POST'] )
def deletedoctor(doctor_id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
        data = Doctors.query.filter_by(doctor_id=doctor_id).first()
        db.session.delete(data)
        db.session.commit()   
        return redirect("/Doctorslist")

@app.route('/adminmap/<int:doctor_id>', methods = ['GET', 'POST'])
def adminmap(doctor_id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Doctors.query.filter_by(doctor_id=doctor_id).first()
        location = data.location
        return render_template('admin_map.html', location=location, name=name, mail=mail)

@app.route('/ContactUs', methods = ['GET', 'POST'])
def ContactUs():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Contactus.query.all()
        return render_template('ContactUs.html', data=data, name=name, mail=mail)

@app.route('/viewsugesstionPanel', methods = ['GET', 'POST'])
def viewsugesstionPanel():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        dosha_type = "Kapha"
        diet_data = Diet.query.filter_by(dosha_type=dosha_type).all()
        lifestyle_data = Lifestyle.query.filter_by(dosha_type=dosha_type).all()
        yoga_data = Yoga.query.filter_by(dosha_type=dosha_type).all()
        return render_template('Suggestions_View.html', diet_data=diet_data, lifestyle_data=lifestyle_data, yoga_data=yoga_data, typ=dosha_type, name=name, mail=mail)

@app.route('/viewpittasugesstionPanel', methods = ['GET', 'POST'])
def viewpittasugesstionPanel():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        dosha_type = "Pitta"
        diet_data = Diet.query.filter_by(dosha_type=dosha_type).all()
        lifestyle_data = Lifestyle.query.filter_by(dosha_type=dosha_type).all()
        yoga_data = Yoga.query.filter_by(dosha_type=dosha_type).all()
        return render_template('Suggestions_View.html', diet_data=diet_data, lifestyle_data=lifestyle_data, yoga_data=yoga_data, typ=dosha_type, name=name, mail=mail)

@app.route('/viewvatasugesstionPanel', methods = ['GET', 'POST'])
def viewvatasugesstionPanel():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        dosha_type = "Vata"
        diet_data = Diet.query.filter_by(dosha_type=dosha_type).all()
        lifestyle_data = Lifestyle.query.filter_by(dosha_type=dosha_type).all()
        yoga_data = Yoga.query.filter_by(dosha_type=dosha_type).all()
        return render_template('Suggestions_View.html', diet_data=diet_data, lifestyle_data=lifestyle_data, yoga_data=yoga_data, typ=dosha_type, name=name, mail=mail)

@app.route('/update_diet/<int:id>', methods = ['GET', 'POST'])
def update_diet(id):  
    if not session.get("email"):  
        return redirect('/login') 
    else:  
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Diet.query.filter_by(id=id).first()  
        if request.method == "POST":
            dosha_type = request.form['dosha_type']
            diet = request.form['diet']

            data = Diet.query.filter_by(id=id).first()
            data.dosha_type = dosha_type
            data.diet = diet
            db.session.add(data)
            db.session.commit()        
            if dosha_type == "Kapha":
                return redirect("/viewsugesstionPanel")
            elif dosha_type == "Pitta":
                return redirect("/viewpittasugesstionPanel")
            else:
                return redirect("/viewvatasugesstionPanel")
        return render_template('SuggestionsDiet_update.html', data=data, name=name, mail=mail)
    
@app.route('/update_lifestyle/<int:id>', methods = ['GET', 'POST'])
def update_lifestyle(id):  
    if not session.get("email"):  
        return redirect('/login') 
    else:  
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Lifestyle.query.filter_by(id=id).first()  
        if request.method == "POST":
            dosha_type = request.form['dosha_type']
            lifestyle_heading = request.form['lifestyle_heading']
            lifestyle_description = request.form['lifestyle_description']

            data = Lifestyle.query.filter_by(id=id).first()
            data.dosha_type = dosha_type
            data.lifestyle_heading = lifestyle_heading
            data.lifestyle_description = lifestyle_description
            db.session.add(data)
            db.session.commit()        
            if dosha_type == "Kapha":
                return redirect("/viewsugesstionPanel")
            elif dosha_type == "Pitta":
                return redirect("/viewpittasugesstionPanel")
            else:
                return redirect("/viewvatasugesstionPanel")
        return render_template('SuggestionsLifestyle_update.html', data=data, name=name, mail=mail)
    
@app.route('/update_yoga/<int:id>', methods = ['GET', 'POST'])
def update_yoga(id):  
    if not session.get("email"):  
        return redirect('/login') 
    else:  
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        data = Yoga.query.filter_by(id=id).first()  
        if request.method == "POST":
            dosha_type = request.form['dosha_type']
            yoga_heading = request.form['yoga_heading']
            yoga_description = request.form['yoga_description']

            data = Yoga.query.filter_by(id=id).first()
            data.dosha_type = dosha_type
            data.yoga_heading = yoga_heading
            data.yoga_description = yoga_description
            db.session.add(data)
            db.session.commit()        
            if dosha_type == "Kapha":
                return redirect("/viewsugesstionPanel")
            elif dosha_type == "Pitta":
                return redirect("/viewpittasugesstionPanel")
            else:
                return redirect("/viewvatasugesstionPanel")
        return render_template('SuggestionsYoga_update.html', data=data, name=name, mail=mail)
    
@app.route('/deletediet/<dosha_type>/<int:id>', methods = ['GET', 'POST'])
def deletediet(dosha_type, id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
        # dosha_type = "Kapha"
        if dosha_type == "Kapha":
            data = Diet.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewsugesstionPanel")
        
        if dosha_type == "Pitta":
            data = Diet.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewpittasugesstionPanel")
        
        if dosha_type == "Vata":
            data = Diet.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewvatasugesstionPanel")    

@app.route('/deletelifestyle/<dosha_type>/<int:id>', methods = ['GET', 'POST'])
def deletelifestyle(dosha_type, id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
    # dosha_type = "Kapha"
        if dosha_type == "Kapha":
            data = Lifestyle.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewsugesstionPanel")
        
        if dosha_type == "Pitta":
            data = Lifestyle.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewpittasugesstionPanel")
        
        if dosha_type == "Vata":
            data = Lifestyle.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewvatasugesstionPanel")    

@app.route('/deleteyoga/<dosha_type>/<int:id>', methods = ['GET', 'POST'])
def deleteyoga(dosha_type, id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
    # dosha_type = "Kapha"
        if dosha_type == "Kapha":
            data = Yoga.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewsugesstionPanel")
        
        if dosha_type == "Pitta":
            data = Yoga.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewpittasugesstionPanel")
        
        if dosha_type == "Vata":
            data = Yoga.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()   
            return redirect("/viewvatasugesstionPanel")    

@app.route('/SugesstionPanel')
def SugesstionPanel():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        d = ""
        l = ""
        y = ""
        return render_template('SugesstionPanel.html', d=d, l=l, y=y, name=name, mail=mail)

@app.route('/dietsuggestion', methods = ['GET', 'POST'])
def dietsuggestion():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        d = ""
        l = ""
        y = ""
        if request.method == 'POST':
            dosha_type = request.form['dosha_type']
            diet = request.form['diet']

            data = Diet(dosha_type=dosha_type, diet=diet)
            db.session.add(data)
            db.session.commit()
            d = "Diet suggestion added successfully"
            return render_template('SugesstionPanel.html', d=d, l=l, y=y)
        return render_template('SugesstionPanel.html', d=d, l=l, y=y, name=name, mail=mail)

@app.route('/lifestylesuggestion', methods = ['GET', 'POST'])
def lifestylesuggestion():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        d = ""
        l = ""
        y = ""
        if request.method == 'POST':
            dosha_type = request.form['dosha_type']
            lifestyle_heading = request.form['lifestyle_heading']
            lifestyle_description = request.form['lifestyle_description']

            data = Lifestyle(dosha_type=dosha_type,lifestyle_heading=lifestyle_heading, lifestyle_description=lifestyle_description)
            db.session.add(data)
            db.session.commit()
            l = "Lifestyle suggestion added successfully"
            return render_template('SugesstionPanel.html', d=d, l=l, y=y)
        return render_template('SugesstionPanel.html', d=d, l=l, y=y, name=name, mail=mail)

@app.route('/yogasuggestion', methods = ['GET', 'POST'])
def yogasuggestion():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')
        data = Admin.query.filter_by(email=email).first()
        name = data.admin_name   
        mail = data.email
        d = ""
        l = ""
        y = ""
        if request.method == 'POST':
            dosha_type = request.form['dosha_type']
            yoga_heading = request.form['yoga_heading']
            yoga_description = request.form['yoga_description']

            data = Yoga(dosha_type=dosha_type, yoga_heading=yoga_heading, yoga_description=yoga_description)
            db.session.add(data)
            db.session.commit()
            y = "Yoga suggestion added successfully"
            return render_template('SugesstionPanel.html', d=d, l=l, y=y)
        return render_template('SugesstionPanel.html', d=d, l=l, y=y, name=name, mail=mail)

@app.route('/adminlogout', methods = ['GET', 'POST'])
def adminlogout():
    # print(session.get('email'))
    session["email"] = None
    # print("User email : ")
    # print(session.get('email'))
    return redirect("/")



# Users
@app.route('/userdashboard')
def userdashboard():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get("email")
        data = Users.query.filter_by(email=email).first()
        name = data.user_name        
        kapha = "Attempted"
        vata = "Attempted"
        pitta = "Attempted"
        email = session.get('email')  
        data = Users.query.filter_by(email=email).first()        
        dosha = data.dosha
        if data.kapha_per == 0:
            kapha = "Not Attempted"
        if data.vata_per == 0:
            vata = "Not Attempted"
        if data.pitta_per == 0:
            pitta = "Not Attempted"
    return render_template('user_dashboard.html', kapha=kapha, vata=vata, pitta=pitta, dosha=dosha, email=email, name=name)

@app.route('/userchatbot', methods = ['GET', 'POST'])
def userchatbot():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        # chat = Chats.query.all()
        email = session.get("email")
        data = Users.query.filter_by(email=email).first()
        user_id = data.user_id
        name = data.user_name
        print(user_id)
        chats = rsession.query(MyChats).filter_by(user_id=user_id).all()
        if request.method == 'POST':
            email = session.get("email")
            data = Users.query.filter_by(email=email).first()
            user_id = data.user_id
            print(user_id)
            query = request.form['query']
            print(query)
            response = bot(query)
            print(response)
            data = MyChats(user_id=user_id, query=query, response=response)
            db.session.add(data)
            db.session.commit()
            if response == "Okay...Lets start the quiz..!":  
                email = session.get("email")
                user_data = Users.query.filter_by(email=email).first()              
                if user_data.kapha_per != 0:
                    return redirect(url_for('afterbot'))
                else:
                    dosha_type = "Kapha"
                    quest = Questions.query.filter_by(dosha_type=dosha_type).all()
                    # chats = rsession.query(MyChats).all()
                    chats = rsession.query(MyChats).filter_by(user_id=user_id).all()
                    return render_template('user_chatbot.html', chats=chats, quest=quest, dosha_type=dosha_type, name=name, email=email)
            print("user_id :", user_id)
            # chats = rsession.query(MyChats).all()
            chats = rsession.query(MyChats).filter_by(user_id=user_id).all()
            return render_template('user_chatbot.html', chats=chats, name=name, email=email)
        return render_template('user_chatbot.html', chats=chats, name=name, email=email)
        # return render_template('user_chatbot.html')

@app.route('/questionans/<string:dosha_type>', methods = ['GET', 'POST'])
def questionans(dosha_type):
    if not session.get("email"):  
        return redirect('/login') 
    else:    
        print("Dosha type :",dosha_type)
        question = Questions.query.filter_by(dosha_type=dosha_type).all()  
        if request.method == "POST":
            if dosha_type == "Kapha":
                kapha_result = 0
                kapha_total = 0
                # kapha_percentage = 0
                for quest in question:
                    quest_id = str(quest.question_id)
                    print("Question id : " + quest_id)
                    select = request.form[quest_id]   
                    print("Selected id : "+ select)
                    correct = quest.answer
                    if select == correct:
                        kapha_result = kapha_result + quest.weightage 
                        print(quest.weightage)
                    else:
                        print("0")
                    kapha_total = kapha_total + quest.weightage
                print("Total =", kapha_total)
                print("Result : ", kapha_result)
                kapha_percentage = kapha_result / kapha_total * 100
                print("Kapha Percentage :", kapha_percentage)
                email = session.get('email')
                user_data = Users.query.filter_by(email=email).first()
                user_data.kapha_per = kapha_percentage
                db.session.commit()

            if dosha_type == "Pitta":      
                pitta_total = 0
                pitta_result = 0
                for quest in question:
                    quest_id = str(quest.question_id)
                    print("Question id : " + quest_id)
                    select = request.form[quest_id]   
                    print("Selected id : "+ select)
                    correct = quest.answer
                    if select == correct:
                        pitta_result = pitta_result + quest.weightage 
                        print(quest.weightage)
                    else:
                        print("0")
                    pitta_total = pitta_total + quest.weightage
                print("Total =", pitta_total)
                print("Result : ", pitta_result)
                pitta_percentage = pitta_result / pitta_total * 100
                print("Pitta Percentage :", pitta_percentage)
                email = session.get('email')
                user_data = Users.query.filter_by(email=email).first()
                user_data.pitta_per = pitta_percentage
                db.session.commit()

            if dosha_type == "Vata":    
                vata_total = 0  
                vata_result = 0
                for quest in question:
                    quest_id = str(quest.question_id)
                    print("Question id : " + quest_id)
                    select = request.form[quest_id]   
                    print("Selected id : "+ select)
                    correct = quest.answer
                    if select == correct:
                        vata_result = vata_result + quest.weightage 
                        print(quest.weightage)
                    else:
                        print("0")
                    vata_total = vata_total + quest.weightage
                print("Total =", vata_total)
                print("Result : ", vata_result)
                vata_percentage = vata_result / vata_total * 100
                print("Vata Percentage :", vata_percentage)

                email = session.get('email')
                user_data = Users.query.filter_by(email=email).first()
                user_data.vata_per = vata_percentage            
                db.session.commit()    

                #changes
                prediction = predict_prakriti(user_data.kapha_per, user_data.pitta_per, user_data.vata_per)
                if prediction == 'Kapha':
                    user_data.dosha = "Kapha"                    
                    db.session.commit()   
                    print("Dosha : ", user_data.dosha)
                    return redirect(url_for('usersuggestions'))
                if prediction == 'Pitta':
                    user_data.dosha = "Pitta"
                    db.session.commit()   
                    print("Dosha : ", user_data.dosha)
                    return redirect(url_for('usersuggestions'))
                if prediction == 'Vata':
                    user_data.dosha = "Vata"
                    db.session.commit()   
                    print("Dosha : ", user_data.dosha)
                    return redirect(url_for('usersuggestions')) 
                #end changes
                                               
            return redirect(url_for('afterbot'))
        
def predict_prakriti(kapha_per, pitta_per, vata_per):
    with open("Prakriti_model.pkl", "rb") as file:
        model = pickle.load(file)    

    prediction = model.predict([[kapha_per,pitta_per,vata_per]])
    print(prediction)
    print(type(prediction))
    if 'Kapha' in prediction:
        print("Kapha")
        return "Kapha"
    if 'Pitta' in prediction:
        print("Pitta")
        return "Pitta"
    if 'Vata' in prediction:
        print("Vata")
        return "Vata"
            
@app.route('/afterbot', methods = ['GET', 'POST'])
def afterbot():   
    # globals.i += 1
    email = session.get('email')
    user_data = Users.query.filter_by(email=email).first() 
    email = session.get("email")
    u_data = Users.query.filter_by(email=email).first()
    user_id = u_data.user_id   
    print("User id : ", user_id)
    print("Pitta per : ", user_data.pitta_per)
    name = user_data.user_name
    if user_data.pitta_per == 0:    
        data = MyChats(user_id=user_id, query="", response="Thank you for attempting the 1st part of quiz. \nKindly attempt the 2nd part of quiz as well to determine your prakriti..!")
        db.session.add(data)
        db.session.commit()
        # chats = rsession.query(MyChats).all() 
        chats = rsession.query(MyChats).filter_by(user_id=user_id).all()
        dosha_type = "Pitta"
        quest = Questions.query.filter_by(dosha_type=dosha_type).all()
        return render_template("user_chatbot.html", chats=chats, quest=quest, dosha_type=dosha_type, name=name, email=email) 
        # newly added up
    
    if user_data.vata_per == 0:
        data = MyChats(user_id=user_id, query="", response="Thank you for attempting the 2nd part of quiz. \nKindly attempt the last part of quiz as well to determine your prakriti..!")
        db.session.add(data)
        db.session.commit()
        # chats = rsession.query(MyChats).all()
        chats = rsession.query(MyChats).filter_by(user_id=user_id).all()
        # newly added down
        dosha_type = "Vata"
        quest = Questions.query.filter_by(dosha_type=dosha_type).all()
        return render_template("user_chatbot.html", chats=chats, quest=quest, dosha_type=dosha_type, name=name, email=email) 
        # newly added up
       
@app.route('/userdoctorslist', methods = ['GET', 'POST'])
def userdoctorslist():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')   
        user = Users.query.filter_by(email=email).first()
        city = user.city    
        name = user.user_name
        data = Doctors.query.filter_by(city=city).all()
        return render_template('user_doctorslist.html', data=data, name=name, email=email)

@app.route('/usermap/<int:doctor_id>', methods = ['GET', 'POST'])
def usermap(doctor_id):
    if not session.get("email"):  
        return redirect('/login') 
    else:
        email = session.get('email')   
        user = Users.query.filter_by(email=email).first()           
        name = user.user_name
        data = Doctors.query.filter_by(doctor_id=doctor_id).first()
        location = data.location
        return render_template('user_map.html', location=location, name=name, email=email)

@app.route('/usersuggestions')
def usersuggestions():
    if not session.get("email"):  
        return redirect('/login') 
    else:
        msg = ""                        
        email = session.get('email')
        user_data = Users.query.filter_by(email=email).first()
        name = user_data.user_name        
        if user_data.dosha == "Not defined":
            msg = "You need to attempt all sections to know your prakriti and know suggestions based on your prakriti"
            return render_template('user_suggestions.html', msg=msg, name=name, email=email)
        else:
            return redirect(url_for('userdoshasuggestions'))       

@app.route('/userdoshasuggestions', methods = ['GET', 'POST'])
def userdoshasuggestions():
    msg = ""
    email = session.get('email')
    user_data = Users.query.filter_by(email=email).first()
    name = user_data.user_name
    if user_data.dosha == "Vata":        
        dosha_type = "Vata"
        msg = "You have Vata body prakrti. To keep your dosha balanced here are some suggestions given below."
        diet_data = Diet.query.filter_by(dosha_type=dosha_type).all()
        lifestyle_data = Lifestyle.query.filter_by(dosha_type=dosha_type).all()
        yoga_data = Yoga.query.filter_by(dosha_type=dosha_type).all()
        return render_template('user_dosha_suggestions.html', diet_data=diet_data, lifestyle_data=lifestyle_data, yoga_data=yoga_data, msg=msg, name=name, email=email)
    
    if user_data.dosha == "Kapha":
        dosha_type = "Kapha"
        msg = "You have Kapha body prakrti. To keep your dosha balanced here are some suggestions given below."
        diet_data = Diet.query.filter_by(dosha_type=dosha_type).all()
        lifestyle_data = Lifestyle.query.filter_by(dosha_type=dosha_type).all()
        yoga_data = Yoga.query.filter_by(dosha_type=dosha_type).all()
        return render_template('user_dosha_suggestions.html', diet_data=diet_data, lifestyle_data=lifestyle_data, yoga_data=yoga_data, msg=msg, name=name, email=email)
    
    if user_data.dosha == "Pitta":
        dosha_type = "Pitta"
        msg = "You have Pitta body prakrti. To keep your dosha balanced here are some suggestions given below."
        diet_data = Diet.query.filter_by(dosha_type=dosha_type).all()
        lifestyle_data = Lifestyle.query.filter_by(dosha_type=dosha_type).all()
        yoga_data = Yoga.query.filter_by(dosha_type=dosha_type).all()
        return render_template('user_dosha_suggestions.html', diet_data=diet_data, lifestyle_data=lifestyle_data, yoga_data=yoga_data, msg=msg, name=name, email=email)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    # print(session.get('email'))
    session["email"] = None
    # print("User email : ")
    # print(session.get('email'))
    return redirect("/")

@app.route('/clearchat/<int:chat_id>', methods = ['GET', 'POST'] )
def clearchat(chat_id):
    if not session.get("email"):  
        return redirect('/login') 
    else:        
        # email = session.get('email')
        # user_data = Users.query.filter_by(email=email).first()
        # user_id = user_data.user_id        
        # chats = rsession.query(MyChats).filter_by(user_id=user_id).all()
        # try:            
        #     for c in chats:
        #         db.session.delete(c)    
        #     print("Successfully deleted")
        # except:
        #     print("Something error occured")
        # db.session.commit()  
        chats = rsession.query(MyChats).filter_by(chat_id=chat_id).first()
        db.session.delete(chats)
        db.session.commit()
        return redirect(url_for('userchatbot'))

def bot(query):    
    greetings = ["hi","hii","hello"]
    end = ["bye","exit"]
    reply = ["i am fine", "fine", "great"]
    start_quiz = ['start the quiz', 'start quiz', 'lets start the quiz', "let's start the quiz"]
    pitta_quiz = ["yes", "yes please","yes start"]
    user = []
    bot = []     
    user.append(query)
    query = query.lower()        
    if query in greetings:                
        response = "Hello..! How are you..?"               
        bot.append(response)
    elif query in reply:               
        response = "Awesome..! Any question for me..?"        
        bot.append(response)
    elif query in end:            
        response = "Bye"
        bot.append(response)     
    elif query in start_quiz:            
        response = "Okay...Lets start the quiz..!"
        bot.append(response)   
    elif query in pitta_quiz:            
        response = "Okay...Lets start with the further quiz..!"
        bot.append(response)   
    elif query == "what is ayurveda?" or query == "what is ayurveda":            
        response = "Ayurveda is an ancient system of medicine originating from India, focusing on holistic health and well-being through a balance of body, mind, and spirit"
        bot.append(response) 

    elif query == "what is prakrti in ayurveda?" or query == "what is prakrti in ayurveda":  
        response = "Prakrti refers to an individual's unique constitution or inherent balance of the three doshas: Vata, Pitta, and Kapha"
        bot.append(response)

    elif query == "what are the characteristics of vata prakrti?" or query == "what are the characteristics of vata prakrti":  
        response = "Vata Prakrti individuals tend to be creative, energetic, and enthusiastic. They may experience fluctuations in energy levels, dry skin, and irregular digestion"
        bot.append(response)                
    
    elif query == "how can i identify if i have a pitta prakrti?" or query == "how can i identify if i have a pitta prakrti":  
        response = "Pitta Prakrti individuals are usually passionate, determined, and have strong digestion. They may have a moderate build, sharp intellect, and be prone to issues like acidity and inflammation"
        bot.append(response) 

    elif query == "can you explain the qualities of kapha prakrti?" or query == "can you explain the qualities of kapha prakrti":  
        response = "Kapha Prakrti individuals are typically calm, nurturing, and have strong endurance. They may have a sturdy build, smooth skin, and be prone to issues like sluggish digestion and weight gain"
        bot.append(response) 

    elif query == "what factors influence a person's prakrti?" or query == "what factors influence a person's prakrti":  
        response = "Prakrti is influenced by genetics, prenatal factors, diet, lifestyle, environment, and emotional experiences"
        bot.append(response)

    elif query == "is it possible to have a combination of prakrtis?" or query == "is it possible to have a combination of prakrtis":  
        response = "Yes, it's common for individuals to have a dominant Prakrti with influences from one or both of the other doshas"
        bot.append(response)

    elif query == "how does ayurveda determine an individual's prakrti?" or query == "how does ayurveda determine an individual's prakrti":  
        response = "Ayurveda assesses Prakrti through physical, mental, and emotional characteristics, as well as by analyzing factors like digestion, sleep patterns, and reaction to stress"
        bot.append(response)

    elif query == "are there specific foods recommended for each prakrti type?" or query == "are there specific foods recommended for each prakrti type":  
        response = "Yes, Ayurveda recommends dietary choices based on an individual's Prakrti to maintain balance and prevent imbalances"
        bot.append(response)  

    elif query == "can you provide examples of lifestyle recommendations based on prakrti?" or query == "can you provide examples of lifestyle recommendations based on prakrti":  
        response = "Lifestyle recommendations may include daily routines, exercise regimens, and stress management techniques tailored to an individual's Prakrti"
        bot.append(response)
    # 10 questions complete

    elif query == "how does one balance their prakrti if it's out of balance?" or query == "how does one balance their prakrti if it's out of balance":  
        response = "Balancing Prakrti involves adopting lifestyle changes, dietary modifications, herbal remedies, and therapeutic practices to pacify aggravated doshas"
        bot.append(response)  

    elif query == "can emotional tendencies be linked to a person's prakrti?" or query == "can emotional tendencies be linked to a person's prakrti":  
        response = "Yes, Ayurveda associates specific emotional traits with each dosha. For example, Vata individuals may experience anxiety, Pitta individuals may have anger issues, and Kapha individuals may struggle with attachment"
        bot.append(response)  

    elif query == "are there any specific exercises or yoga poses suitable for each prakrti?" or query == "are there any specific exercises or yoga poses suitable for each prakrti":  
        response = "Yes, Ayurveda recommends yoga practices and exercises tailored to an individual's Prakrti to promote balance and well-being"
        bot.append(response)  

    elif query == "how does seasonal change affect prakrti?" or query == "how does seasonal change affect prakrti":  
        response = "Seasonal changes can influence Prakrti by aggravating certain doshas. Ayurveda advises adjusting diet, lifestyle, and self-care practices accordingly to maintain balance"
        bot.append(response) 

    elif query == "can meditation help balance prakrti?" or query == "can meditation help balance prakrti":  
        response = "Yes, meditation is beneficial for balancing Prakrti by calming the mind, reducing stress, and promoting inner harmony"
        bot.append(response) 
    # 15 questions completed

    elif query == "what are the primary qualities associated with vata dosha?" or query == "what are the primary qualities associated with vata dosha":  
        response = "The primary qualities of Vata dosha include dry, light, cold, rough, subtle, and mobile"
        bot.append(response)

    elif query == "how does vata imbalance manifest in the body and mind?" or query == "how does vata imbalance manifest in the body and mind":  
        response = "Imbalanced Vata can lead to symptoms such as anxiety, insomnia, dry skin, constipation, and erratic digestion"
        bot.append(response)

    elif query == "what are the main qualities of pitta dosha?" or query == "what are the main qualities of pitta dosha":  
        response = "Pitta dosha is characterized by qualities such as hot, sharp, oily, light, liquid, and spreading"
        bot.append(response)

    elif query == "what health issues may arise from pitta imbalance?" or query == "what health issues may arise from pitta imbalance":  
        response = "Imbalanced Pitta can result in conditions like acidity, inflammation, skin rashes, ulcers, and irritability"
        bot.append(response)  

    elif query == "describe the qualities of kapha dosha" or query == "describe the qualities of kapha dosha":  
        response = "Kapha dosha is characterized by qualities such as heavy, slow, cool, oily, smooth, and stable"
        bot.append(response) 
    # 20 questions completed

    elif query == "what are common signs of kapha imbalance?" or query == "what are common signs of kapha imbalance":  
        response = "Imbalanced Kapha may lead to symptoms like lethargy, weight gain, congestion, sluggish metabolism, and attachment"
        bot.append(response) 

    elif query == "can climate and weather affect prakrti?" or query == "can climate and weather affect prakrti":  
        response = "Yes, changes in climate and weather can influence Prakrti by aggravating or pacifying doshas"
        bot.append(response)

    elif query == "how does ayurveda approach treating prakrti imbalances?" or query == "how does ayurveda approach treating prakrti imbalances":  
        response = "Ayurveda employs personalized treatments, including dietary adjustments, herbal remedies, lifestyle modifications, and therapeutic practices to restore balance"
        bot.append(response) 

    elif query == "are there specific herbs recommended for balancing vata dosha?" or query == "are there specific herbs recommended for balancing vata dosha":  
        response = "Yes, herbs such as ashwagandha, ginger, licorice, and sesame oil are beneficial for pacifying Vata dosha"
        bot.append(response) 

    elif query == "what dietary guidelines should pitta individuals follow?" or query == "what dietary guidelines should pitta individuals follow":  
        response = "Pitta individuals should favor cooling, hydrating foods like leafy greens, sweet fruits, whole grains, and dairy in moderation"
        bot.append(response) 
    # 25 questions completed

    elif query == "which yoga poses are beneficial for reducing kapha imbalance?" or query == "which yoga poses are beneficial for reducing kapha imbalance":  
        response = "Yoga poses that stimulate circulation and energize the body, such as Sun Salutations (Surya Namaskar) and backbends, are helpful for balancing Kapha"
        bot.append(response)

    elif query == "can aromatherapy be used to balance prakrti?" or query == "can aromatherapy be used to balance prakrti":  
        response = "Yes, aromatherapy with essential oils like lavender, peppermint, and eucalyptus can help balance doshas and promote well-being"
        bot.append(response)

    elif query == "what role does digestion play in determining prakrti?" or query == "what role does digestion play in determining prakrti":  
        response = "Digestion is crucial in Ayurveda as it influences the formation of tissues (dhatus) and the production of energy (agni), which are key factors in determining Prakrti"
        bot.append(response)

    elif query == "how does ayurveda view the mind-body connection in relation to prakrti?" or query == "how does ayurveda view the mind-body connection in relation to prakrti":  
        response = "Ayurveda emphasizes the interconnectedness of the mind and body, recognizing that mental and emotional factors can influence physical health and Prakrti"
        bot.append(response)

    elif query == "can prakrti change over time?" or query == "can prakrti change over time":  
        response = "While one's fundamental Prakrti remains stable throughout life, external factors like diet, lifestyle, and environment can temporarily influence dosha imbalances"
        bot.append(response)
    # 30 questions completed

    elif query == "what role does sleep play in maintaining prakrti balance?" or query == "what role does sleep play in maintaining prakrti balance":  
        response = "Sufficient, restful sleep is essential for balancing doshas and rejuvenating the body and mind according to Ayurveda"
        bot.append(response)

    elif query == "how does ayurveda classify foods based on their taste (rasa) and effect on doshas?" or query == "how does ayurveda classify foods based on their taste (rasa) and effect on doshas":  
        response = "Ayurveda categorizes foods into six tastes (rasas) - sweet, sour, salty, bitter, pungent, and astringent - each with its unique effects on doshas"
        bot.append(response) 

    elif query == "are there specific pranayama (breathing) techniques recommended for each prakrti?" or query == "are there specific pranayama (breathing) techniques recommended for each prakrti":  
        response = "Yes, pranayama techniques like Nadi Shodhana (alternate nostril breathing), Kapalabhati (skull shining breath), and Bhramari (humming bee breath) can be tailored to balance individual doshas"
        bot.append(response) 

    elif query == "can ayurvedic oils and massage therapies help balance prakrti?" or query == "can ayurvedic oils and massage therapies help balance prakrti":  
        response = "Yes, Ayurvedic oils and massage therapies like Abhyanga (self-massage) and Shirodhara (oil pouring on the forehead) are beneficial for balancing doshas and promoting relaxation"
        bot.append(response) 
    
    elif query == "what role does stress management play in preventing prakrti imbalances?" or query == "what role does stress management play in preventing prakrti imbalances":  
        response = "Effective stress management techniques, including meditation, mindfulness, and yoga, are essential for maintaining Prakrti balance and overall well-being"
        bot.append(response) 
    # 35 questions completed
    else:
        response = "I am unable to understand your question."            
    return response

if __name__ == "__main__" :
    app.run(debug=True,port=8001)