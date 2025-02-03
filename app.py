from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'  


@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/schemes', methods=['GET'])
def get_schemes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    cursor.execute("SELECT scheme_id, scheme_name, scheme_type, launch_date FROM schemes")
    schemes = cursor.fetchall()
    
    print(schemes)  

    cursor.close()
    conn.close()
    
    
    return render_template('dashboard.html', schemes=schemes)

@app.route('/announcements', methods=['GET', 'POST'])
def announcements():
    if request.method == 'POST':
        announcement_message = request.form['announcement_message']  
        conn = get_db_connection()
        cursor = conn.cursor()

        
        cursor.execute("SELECT announcement_message, announcement_date FROM announcements ORDER BY announcement_date DESC")
        announcements=cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        flash("Announcement submitted successfully!", "success")

    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    cursor.execute("SELECT announcement_id, announcement_message, announcement_date FROM announcements ORDER BY announcement_date DESC")
    announcements = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('announcements.html', announcements=announcements)



@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        customer_id = session.get('customer_id')  
        feedback_message = request.form['feedback_message']  

        if customer_id:  
            conn = get_db_connection()
            cursor = conn.cursor()

            
            cursor.execute("INSERT INTO feedback (customer_id, feedback_message, created_date) VALUES (%s, %s, NOW())", 
                           (customer_id, feedback_message))
            conn.commit()
            cursor.close()
            conn.close()

            flash("Feedback submitted successfully!", "success")
        else:
            flash("Please log in to submit feedback.", "danger")
            return redirect(url_for('login'))

    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    if 'customer_id' in session:
        customer_id = session['customer_id']
        cursor.execute("SELECT feedback_message, created_date FROM feedback WHERE customer_id = %s ORDER BY created_date DESC", 
                       (customer_id,))
        feedbacks = cursor.fetchall()  
    else:
        feedbacks = []

    cursor.close()
    conn.close()

    return render_template('feedback.html', feedbacks=feedbacks)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Customers WHERE email=%s", (email,))
        customer = cursor.fetchone()
        
        if customer:
            
            if password == customer[4]:  
                session['customer_id'] = customer[0]  
                return redirect(url_for('customer_dashboard'))  
            else:
                flash("Invalid password. Please try again.", "danger")
                return redirect(url_for('login'))  
        else:
            flash("Email not found. Please register.", "danger")
            return redirect(url_for('login'))  
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  
        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'danger')
            return redirect('/register')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customers (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))  

    return render_template('register.html')  

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    scheme_id = request.form['scheme_id']
    flash('Successfully subscribed to the scheme!', 'success')
    return redirect(url_for('dashboard.html'))

@app.route('/customer_dashboard')
def customer_dashboard():
    if 'customer_id' in session:
        customer_id = session['customer_id']

        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        
        cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))
        customer = cursor.fetchone()

        
        cursor.execute("SELECT * FROM transactions WHERE customer_id=%s", (customer_id,))
        transactions = cursor.fetchall()

        
        cursor.execute("""
        SELECT cs.scheme_id, s.scheme_name, s.scheme_type, cs.customer_id, cs.subscription_date, cs.status
        FROM customer_scheme cs
        JOIN schemes s ON cs.scheme_id = s.scheme_id
        WHERE cs.customer_id = %s
        """, (customer_id,))
        customer_scheme = cursor.fetchall()

        
        cursor.execute("SELECT * FROM funds WHERE fund_manager = (SELECT customer_name FROM customers WHERE customer_id = %s)", (customer_id,))
        funds = cursor.fetchall()

        cursor.close()
        conn.close()

        
        return render_template('customer_dashboard.html', 
                               customer=customer, 
                               transactions=transactions,
                               customer_scheme=customer_scheme,
                               funds=funds)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('customer_id', None)  
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))  

if __name__ == '__main__':
    app.run(port=5001)
