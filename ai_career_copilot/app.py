import flask as fl
from db import Base ,engine ,SessionLocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json

app = fl.Flask(__name__)
app.secret_key = "secret123"

Base.metadata.create_all(bind = engine)

# Home Page (Base Route) ------
@app.route('/')
def home():
    if "user" in fl.session:
        return fl.redirect("/dashboard")
    else:
        return fl.redirect("/login")

# Signup Route ------
@app.route('/signup' , methods = ['GET' , 'POST'])
def signup():
    db = SessionLocal()

    if fl.request.method == 'POST':
        email = fl.request.form.get("email")
        password = fl.request.form.get("password")

        existing_user = db.query(models.User).filter_by(email = email).first()
        if existing_user:
            return "User already exists"
        
        user = models.User(email = email , password = password)
        db.add(user)
        db.commit()
    
    return fl.render_template('signup.html')

# Login Route -------
@app.route('/login' , methods = ['GET' , 'POST'])
def login():
    db = SessionLocal()

    if fl.request.method == 'POST':
        email = fl.request.form.get("email")
        password = fl.request.form.get("password")

        user = db.query(models.User).filter_by(email = email , password = password).first()
        
        if user:
            fl.session["user"] = user.email
            return fl.redirect("/dashboard")
        else:
            return "Invalid Credentials"
        
    return fl.render_template("login.html")
        
# Dashboard Route -------
@app.route('/dashboard' , methods = ["GET" , "POST"])
def dashboard():
    if "user" not in fl.session:
        return fl.redirect("/login") 

    result = None

    if fl.request.method == "POST":
        user_goal = fl.request.form.get("role")
        resume_text = fl.request.form.get("resume")
        
        file = fl.request.files.get("file")
        
        # Essential File Handling
        if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as ex:
                    result = {"error": f"PDF Error -> {str(ex)}"}
        
            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + '\n'
                    resume_text = text
                except Exception as ex:
                    result = {"error": f"Docx Error -> {str(ex)}"}
        
        # Herein we basically use OLLAMA Qwen 8b for pur analysis of the Resume
        if resume_text and user_goal:
            try:
                result = analyze_resume(resume_text , user_goal)
                
                # save to db 
                db = SessionLocal()
                user = db.query(models.User).filter_by(email = fl.session["user"]).first()

                report = models.Reports(
                    user_id = user.id,
                    resume_text = resume_text,
                    result = json.dumps(result)
                )

                db.add(report)
                db.commit()
            
            except Exception as ex:
                result = {"error": f"AI+ error -> {str(ex)}"}
        
        return fl.render_template(
            "dashboard.html",
            user = fl.session["user"],
            result = result
        )

# History Route ---------
@app.route("/history")
def history():
    if "user" not in fl.session:
        return fl.redirect("/login")
    
    db = SessionLocal()
    user = db.query(models.User).filter_by(email = fl.session["user"]).first()

    reports = db.query(models.Reports).filter_by(user_id = user.id).all()
    
    # JSON String Converted here
    passed_report = []
    for r in reports:
        try:
            result = json.loads(r.result)
        except:
            result = []

        passed_report.append({
            "resume": r.resume_text,
            "result": result
        })

    return fl.render_template(
        "history.html",
        report = passed_report,

    )

# Logout -------
@app.route('/logout')
def logout():
    fl.session.pop("user", None)
    return fl.redirect("/login")

if __name__ == '__main__':
    app.run(debug = True)