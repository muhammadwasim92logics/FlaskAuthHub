from flask import Flask, request, redirect, url_for, render_template, send_file, url_for,session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets 
max_attempts = 3

app = Flask(__name__)
app.secret_key = '@malik'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)   # session end after 3 minutes
# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///my.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Avoid unnecessary warning

# Initialize database
db = SQLAlchemy(app)

# Define the file model
class USER(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    fname=db.Column(db.String(40),nullable=True)
    lname=db.Column(db.String(40),nullable=True)
    email = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(20), nullable=True)  # Store file content as binary
    gander = db.Column(db.String(20),nullable=True)

# Route to the main page with the upload form
@app.route('/')
def index1():
    return render_template('base.html')

@app.route('/email')
def send_mail():
    return render_template("email.html")

@app.route('/send', methods=['POST'])
def send():
    email=request.form['email']
    massage=request.form['message']
    # Use environment variables for sensitive data
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'waseemhanif0018@gmail.com')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'iwuc bovs zdwk harj')  # App password or OAuth token
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

    def send_email():
        # List of recipients
        recipient_emails = [f'{email}' ]   # ['wasim.92logics@gmail.com' ]
        
        subject = 'This is Flask Testing E-Mail'
        body = f'{massage}'

        # Create the email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ', '.join(recipient_emails)  # Join all recipients with commas

        try:
            # Send the email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Log in to the email server
                server.sendmail(EMAIL_ADDRESS, recipient_emails, msg.as_string())  # Send the email
                print('Email sent successfully!')
        except Exception as e:
            print(f'Error: {e}')
            

    send_email()
    return render_template('email.html')  # Corrected to render the template


@app.route('/act', methods=["POST"])
def index2():
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['email']
    results = USER.query.filter(USER.email.ilike(f'{email}')).all()
    if results:
        print("Email Already Exist")
        return render_template ("error.html")
    password =request.form['password']
    gander =request.form['gender']
    add__new_user=USER(fname=fname, lname=lname, email=email, password=password, gander=gander)
    db.session.add(add__new_user)
    db.session.commit()
    return render_template('base.html')


@app.route('/delete', methods=['POST'])
def delete():
    try:
        email = request.form.get('email')  # Use a clear variable name
    except:
        return redirect(url_for("login"))

    delete_user = USER.query.filter_by(email=email).first()
    
    if delete_user:
        db.session.delete(delete_user)
        db.session.commit()
        flash(f"User with email {email} deleted successfully.", "success")  # Flashing success message
    else:
        flash(f"User with email {email} not found.", "error")  # Flashing error message

    return redirect(url_for("key"))  # Redirect instead of rendering directly



@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == "POST":
        update_sno = request.form.get('email')
        user_updated = USER.query.filter_by(email=update_sno).first()
        
        if not user_updated:
            return render_template("update.html", error="User Not Found")

        # Get values, but keep old values if new ones are empty
        fname = request.form.get('fname') or user_updated.fname
        lname = request.form.get('lname') or user_updated.lname
        email = request.form.get('email') or user_updated.email
        password = request.form.get('password') or user_updated.password
        gender = request.form.get('gender') or user_updated.gander  # Corrected typo

        user_updated.fname = fname
        user_updated.lname = lname
        user_updated.email = email
        user_updated.password = password
        user_updated.gander = gender
        
        db.session.commit()

        return render_template("update.html", updated=user_updated, success="Updated Information")

    return render_template("child.html", updated=None, error="User Not Updated")


from datetime import datetime, timezone

@app.route("/show", methods=["POST", "GET"])
def key():  
    now = datetime.now(timezone.utc)  # Ensure all timestamps are timezone-aware

    # Check if session exists and reset if expired
    if "attempt_timestamp" in session:
        attempt_time = datetime.fromisoformat(session["attempt_timestamp"])  # Convert stored string to datetime
        elapsed_time = (now - attempt_time).total_seconds()

        if elapsed_time > 60:  # 1 minutes = 60 seconds
            session["attempt_count"] = 0  # Reset attempt count
            session.pop("attempt_timestamp", None)

    session["attempt_count"] = session.get("attempt_count", 0)  

    if session["attempt_count"] >= max_attempts:
        return render_template("key.html", error="You are blocked from accessing data Try Again after few Mintes")

    # if request.method == "POST":
    key = request.form.get("key")
    if session.get("access_data") or key == "1122":
        session["access_data"] = True
        session.pop("attempt_count", None)  # Reset on success
        session.pop("attempt_timestamp", None)  # Clear timestamp
        show_all_users = USER.query.all()
        messages = get_flashed_messages(with_categories=True)
        return render_template("child.html", users=show_all_users, messages=messages)

    session["attempt_count"] += 1  # Increment attempt count
    session["attempt_timestamp"] = now.isoformat()  # Store timestamp as string

    return render_template("key.html", error="Please Enter a Valid Key to Access Data")


@app.route('/searchuser')
def searchuser():
    return render_template ("search.html")
    
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/search', methods=["POST"])
def search():
    serach_id=request.form['search']
    results = USER.query.filter(USER.email.ilike(f'{serach_id}')).first()
    if results:
     return render_template("search.html", result=results, found=True)
    else:
        return render_template ("search.html")
    
   #   Function of Send E-Mail
def send_verification_email(email):
        # Use environment variables for sensitive data
        EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'waseemhanif0018@gmail.com')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'iwuc bovs zdwk harj')  # App password or OAuth token
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587
        # Generate a verification code
        email_verification_code = secrets.token_hex(3)
        session["email_verification_code"] = email_verification_code

        subject = 'Your Email Verification Code'
        body = f'''
                <html>
                    <body style="background-color: #f4f4f4; padding: 20px; text-align: center;">
                        <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); display: inline-block;">
                            <h2 style="color: #333;">Email Verification</h2>
                            <p style="font-size: 18px; color: #555;">
                                Your Verification Code is:  
                                <strong style="font-size: 22px; color: #d9534f;">{email_verification_code}</strong>
                            </p>
                        </div>
                    </body>
                </html>
            '''


        # Create the email
        msg = MIMEMultipart()  # Corrected
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email  # Sending to only one recipient
        msg.attach(MIMEText(body, 'html'))  # Use 'html' instead of 'plain' for formatting

        try:
            # Send the email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Log in to the email server
                server.sendmail(EMAIL_ADDRESS, email, msg.as_string())  # Send the email
                print('Email sent successfully!')
        except Exception as e:
            print(f'Error: {e}') 

     
@app.route('/verification_email/<email>')
def verification_email(email):
    print("E-MAIL:", email)  # Debugging purpose
    session["email"]=email
    results = USER.query.filter(USER.email.ilike(f'{email}')).first()
    if results:
        send_verification_email(email)
        return render_template("cord.html")  # Show forget password page
    else:
        return render_template("login.html", error="This E-Mail Not exist")

@app.route('/v_cord', methods=["POST"])
def v_cord():
    get_cord=request.form.get("cord")
    email_varifcation_cord = session.get('email_verification_code', None)
    if get_cord == email_varifcation_cord:
        return render_template("forget.html", massage="E-Mail Varifed Success")
    else:
        return render_template("login.html", error="Varifcation Cord Not Match")
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email=request.form['email']
        password=request.form['password']
        information=USER.query.filter_by(email=email, password=password).first()
        results = USER.query.filter(USER.email.ilike(f'{email}')).first()
        # Validate login credentials
        if results:
            if information :  
                session['logged_in'] = True
                return redirect(url_for('home'))  # Redirect to home page
            else:
                return render_template('login.html', error="Invalid log-In Information")
        else:
            return render_template('login.html', error="Invalid E-Mail ")


    return  render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session and log the user out
    session.pop('access_data', None)
    session.pop('logged_in', None)  # Remove 'logged_in' from the session
    flash("You have are logged out at This Time")  # Add a category to the flash message for styling
    return redirect(url_for('login'))  # Redirect to the login page after logging out


@app.route('/home')
def home():
    if 'logged_in' not in session:
        flash("You can't access the Home page without logging in.")
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template("Home.html")

@app.route("/f_password1")
def f_password1():
    return render_template("forget.html")

@app.route("/f_password", methods=["POST", "GET"])
def f_password():
    if request.method == "POST":
        password = request.form.get('password')
        email = session.get('email', None)
        print("Email:", email)
        user_email = USER.query.filter_by(email=email).first()
        if user_email:
            user_email.password = password  # Update the user's password
        
            db.session.commit()  # Save the changes
            flash("Password updated successfully!")
            return redirect(url_for("login"))
        else:
            return render_template("forget.html", error="This Email Not Exist, Please Register First, Are Use Correct E-Mail For log-In")


if __name__ == "__main__":
    app.run(debug=True)
