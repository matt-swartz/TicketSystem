# import flask and sql
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import secrets


# initialize the app
app = Flask(__name__)

# configure the SQL
connection = pymysql.connect(
    host='127.0.0.1',
    port=8889,
    user='root',
    password='root',
    db='TicketSystem',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
# secret key setup
secret = secrets.token_urlsafe(32)
app.secret_key = secret

# home page routing
@app.route('/')
@app.route('/index.html')
@app.route('/logout.html')
def hello():
    return render_template('index.html')
#
# CUSTOMER FUNCTIONS
#

# our customer login routing
@app.route('/customerlogin.html')
def customerlogin():
    return render_template('customerlogin.html')
# customer home page
@app.route('/CustomerPage.html')
def customerHome():
    username = session['username']
    cursor = connection.cursor()
    # this is our query for our future flights
    query = 'SELECT flight_number, depart_month, depart_day, depart_year, depart_hr, depart_min FROM has NATURAL JOIN customer_purchase WHERE email = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    # this is our query for our previous flights
    query2 = 'SELECT flight_number, depart_month, depart_day, depart_year, depart_hr, depart_min, comment, rating FROM rates WHERE email = %s'
    cursor.execute(query2, username)
    data2 = cursor.fetchall()
    cursor.close()
    return render_template('CustomerPage.html', username=username, posts=data, posts2 = data2)
# customer purchasing a ticket
@app.route('/custPurchase', methods=['GET', 'POST'])
def custPurchase():
    username = session['username']
    depart_loc = request.form['From:']
    depart_month = request.form['departuremonth']
    depart_day = request.form['departureday']
    depart_year = request.form['departureyear']
    arrive_loc = request.form['To:']
    return_month = request.form['returnmonth']
    return_day = request.form['returnday']
    return_year = request.form['returnyear']
    # check there is a flight on this departure date
    cursor = connection.cursor()
    query = 'SELECT * FROM departs WHERE name = %s and depart_month = %s and depart_day = %s and depart_year = %s'
    cursor.execute(query, depart_loc, depart_month, depart_day, depart_year)
    data = cursor.fetchone()
    query2 = 'SELECT * FROM arrives WHERE name = %s and arrive_month = %s and arrive_day = %s and arrive_year = %s'
    cursor.execute(query2, arrive_loc, depart_month, depart_day, depart_year)
    data2 = cursor.fetchone()
    # check there is a flight on the return date
    query3 = 'SELECT * FROM departs WHERE name = %s and depart_month = %s and depart_day = %s and depart_year = %s'
    cursor.execute(query3,  arrive_loc, return_month, return_day, return_year)
    data3 = cursor.fetchone()
    query4 = 'SELECT * FROM arrives WHERE name = %s and arrive_month = %s and arrive_day = %s and arrive_year = %s'
    cursor.execute(query4, depart_loc, return_month, return_day, return_year)
    data4 = cursor.fetchone()

    cursor.close()
    error = None
    # if the flight exists and only one-way
    if data and data2 and not data3 and not data4:
        ins = 'INSERT INTO customer_purchase VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, ('00005', username, '600', '1', '1', '2021', '1', '0', 'VISA', '4345454343', 'Matt', '1/1/2021'))
        connection.commit()
        return redirect(url_for('customerHome'))
    # the two way flight
    elif data and data2 and data3 and data4:
        ins = 'INSERT INTO customer_purchase VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, ('00005', username, '600', '1', '1', '2021', '1', '0', 'VISA', '4345454343', 'Matt', '1/1/2021'))
        connection.commit()
        return redirect(url_for('customerHome'))
    else:
        error = 'No Ticket Exists'
        return render_template('CustomerPage.html', error=error)
# authenticating the customer
@app.route('/loginAuthCust', methods=['GET', 'POST'])
def loginAuthCust():
    # get user info
    username = request.form['username']
    password = request.form['password']
    # cursor for sending queries
    cursor = connection.cursor()
    # execute said query
    query = 'SELECT * FROM customer WHERE email = %s and password = %s'
    cursor.execute(query, (username, password))
    # store the result
    data = cursor.fetchone()
    # close the cursor as we are done with it
    cursor.close()
    error = None
    # if the customer login is valid
    if data:
        session['username'] = username
        return redirect(url_for('customerHome'))
    # if login is invalid
    else:
        error = 'Invalid Username or Password'
        return render_template('customerlogin.html', error=error)
# our booking agent login routing
@app.route('/register.html')
def registerPage():
    return render_template('register.html')
# register a customer
@app.route('/registerCust', methods=['GET', 'POST'])
def registerCust():
    # get info from the forms
    firstname = request.form['First Name']
    lastname = request.form['Last Name']
    dob = request.form['Date of Birth']
    phone_number = request.form['Phone Number']
    building_no = request.form['Building Number']
    street = request.form['Street']
    city = request.form['City']
    state = request.form['State']
    passport_no = request.form['Passport Number']
    expiration_day = request.form['Expiration Day']
    expiration_month = request.form['Expiration Month']
    expiration_year = request.form['Expiration Year']
    country = request.form['Country']
    username = request.form['username']
    password = request.form['password']

    # cursor for sending queries
    cursor = connection.cursor()
    # execute query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, username)
    # store the result in a variable
    data = cursor.fetchone()
    error = None
    if (data):
        # if this user is already registered
        error = 'This user already exists.'
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (
            username,
            password,
            firstname + ' ' + lastname,
            building_no,
            street,
            city,
            state,
            phone_number,
            passport_no,
            expiration_day,
            expiration_month,
            expiration_year,
            country,
            dob
        ))
        connection.commit()
        cursor.close()
        return render_template('index.html')

#
# BOOKING AGENT FUNCTIONS
#

# our booking agent login routing
@app.route('/bookingagentlogin.html')
def bookingagentlogin():
    return render_template('bookingagentlogin.html')
# authenticating the booking agent login
@app.route('/loginAuthAgent', methods=['GET', 'POST'])
def loginAuthAgent():
    # get user info
    username = request.form['username']
    password = request.form['password']
    agent_id = request.form['ID']
    # cursor for sending queries
    cursor = connection.cursor()
    # execute said query
    query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s and id = %s'
    cursor.execute(query, (username, password, agent_id))
    # store the result
    data = cursor.fetchone()
    # close the cursor as we are done with it
    cursor.close()
    error = None
    # if the customer login is valid
    if data:
        session['username'] = username
        return redirect(url_for('hello'))
    # if login is invalid
    else:
        error = 'Invalid Username or Password or ID'
        return render_template('bookingagentlogin.html', error=error)
# our booking agent login routing
@app.route('/AgentRegister.html')
def agentRegisterPage():
    return render_template('AgentRegister.html')
# register a booking agent
@app.route('/registerAgent', methods=['GET', 'POST'])
def registerAgent():
    # get info from the forms
    username = request.form['Email']
    password = request.form['password']
    agent_id = request.form['ID']

    # cursor for sending queries
    cursor = connection.cursor()
    # execute query
    query = 'SELECT * FROM booking_agent WHERE email = %s'
    cursor.execute(query, username)
    # store the result in a variable
    data = cursor.fetchone()
    error = None
    if (data):
        # if this user is already registered
        error = 'This agent already exists.'
        return render_template('AgentRegister.html', error=error)
    else:
        ins = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
        cursor.execute(ins, (username, password, agent_id))
        connection.commit()
        cursor.close()
        return render_template('index.html')
# booking agent home page
@app.route('/bookingagenthome.html')
def agentHome():
    username = session['username']
    cursor = connection.cursor()
    # this is our query for our booking agent flights
    query = 'SELECT cust_email, flight_number, depart_month, depart_day, depart_year, depart_hr, depart_min FROM has NATURAL JOIN purchase WHERE agent_email = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('bookingagenthome.html', username=username, posts=data)
# booking agent purchasing a ticket
@app.route('/agentPurchase', methods=['GET', 'POST'])
def agentPurchase():
    username = session['username']
    depart_loc = request.form['From:']
    depart_month = request.form['departuremonth']
    depart_day = request.form['departureday']
    depart_year = request.form['departureyear']
    arrive_loc = request.form['To:']
    return_month = request.form['returnmonth']
    return_day = request.form['returnday']
    return_year = request.form['returnyear']
    # check there is a flight on this departure date
    cursor = connection.cursor()
    query = 'SELECT * FROM departs WHERE name = %s and depart_month = %s and depart_day = %s and depart_year = %s'
    cursor.execute(query, depart_loc, depart_month, depart_day, depart_year)
    data = cursor.fetchone()
    query2 = 'SELECT * FROM arrives WHERE name = %s and arrive_month = %s and arrive_day = %s and arrive_year = %s'
    cursor.execute(query2, arrive_loc, depart_month, depart_day, depart_year)
    data2 = cursor.fetchone()
    # check there is a flight on the return date
    query3 = 'SELECT * FROM departs WHERE name = %s and depart_month = %s and depart_day = %s and depart_year = %s'
    cursor.execute(query3, arrive_loc, return_month, return_day, return_year)
    data3 = cursor.fetchone()
    query4 = 'SELECT * FROM arrives WHERE name = %s and arrive_month = %s and arrive_day = %s and arrive_year = %s'
    cursor.execute(query4, depart_loc, return_month, return_day, return_year)
    data4 = cursor.fetchone()

    cursor.close()
    error = None
    # if the flight exists and only one-way
    if data and data2 and not data3 and not data4:
        ins = 'INSERT INTO purchase VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins,
                       ('00005', username, '600', '1', '1', '2021', '1', '0', 'VISA', '4345454343', 'Matt', '1/1/2021'))
        connection.commit()
        return redirect(url_for('customerHome'))
    # the two way flight
    elif data and data2 and data3 and data4:
        ins = 'INSERT INTO purchase VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins,
                       ('00005', username, '600', '1', '1', '2021', '1', '0', 'VISA', '4345454343', 'Matt', '1/1/2021'))
        connection.commit()
        return redirect(url_for('customerHome'))
    else:
        error = 'No Ticket Exists'
        return render_template('CustomerPage.html', error=error)

#
# AIRLINE STAFF FUNCTIONS
#

# home page for airline staff
@app.route('/AirlineStaffHome.html')
def airlineHome():
    return render_template('AirlineStaffHome.html')

# our airline login routing
@app.route('/AirlineLogin.html')
def airlinelogin():
    return render_template('AirlineLogin.html')
# authenticating the airline worker login
@app.route('/loginAuthAirline', methods=['GET', 'POST'])
def loginAuthAirline():
    # get user info
    username = request.form['username']
    password = request.form['password']
    # cursor for sending queries
    cursor = connection.cursor()
    # execute said query
    query = 'SELECT * FROM staff WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    # store the result
    data = cursor.fetchone()
    # close the cursor as we are done with it
    cursor.close()
    error = None
    # if the customer login is valid
    if data:
        session['username'] = username
        return redirect(url_for('airlineHome'))
    # if login is invalid
    else:
        error = 'Invalid Username or Password or ID'
        return render_template('AirlineLogin.html', error=error)
# our booking agent login routing
@app.route('/AirlineRegister.html')
def airlineRegisterPage():
    return render_template('AirlineRegister.html')
# register a airline
@app.route('/registerAirline', methods=['GET', 'POST'])
def registerAirline():
    # get info from the forms
    username = request.form['choose a username']
    password = request.form['password']
    phone_number = request.form['Phone Number']

    # cursor for sending queries
    cursor = connection.cursor()
    # execute query
    query = 'SELECT * FROM staff WHERE username = %s'
    cursor.execute(query, username)
    # store the result in a variable
    data = cursor.fetchone()
    error = None
    if (data):
        # if this user is already registered
        error = 'This staff member already exists.'
        return render_template('AirlineRegister.html', error=error)
    else:
        ins = 'INSERT INTO staff VALUES(%s, %s, %s)'
        cursor.execute(ins, (username, password, phone_number))
        connection.commit()
        cursor.close()
        return render_template('index.html')
# staff can view flights
@app.route('/viewFlights', methods=['GET', 'POST'])
def viewFlights():
    username = session['username']
    cursor = connection.cursor()
    # this is our query for our future flights
    query = 'SELECT flight_number, depart_month, depart_day, depart_year, depart_hr, depart_min FROM works_for NATURAL JOIN operates WHERE username = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('CustomerPage.html', username=username, posts=data)
# adding flights to the database
@app.route('/addFlights', methods=['GET', 'POST'])
def addFlights():
    # our flight variables
    flight_num = request.form['Flight Num']
    depart_month = request.form['departuremonth']
    depart_day = request.form['departureday']
    depart_year = request.form['departureyear']
    depart_hr = request.form['departurehr']
    depart_min = request.form['departuremin']
    arrive_month = request.form['arrivemonth']
    arrive_day = request.form['arriveday']
    arrive_year = request.form['arriveyear']
    arrive_hr = request.form['arrivehr']
    arrive_min = request.form['arrivemin']
    base_price = request.form['base price']
    status = 'ON TIME'
    # operates variables
    airline = request.form['Airline']
    # uses variables
    plane_id = request.form['Plane ID']
    # arrives and departs variables
    depart_airport = request.form['Departed Airport']
    arrive_airport = request.form['Arrival Airport']
    # inserting all info into the database
    cursor = connection.cursor()
    # add to flight
    ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(ins, (flight_num, depart_month, depart_day, depart_year, depart_hr, depart_min, arrive_month, arrive_day, arrive_year, arrive_hr, arrive_min, base_price, status))
    connection.commit()
    # add to operates
    ins2 = 'INSERT INTO operates VALUES(%s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(ins2, (airline, flight_num, depart_month, depart_day, depart_year, depart_hr, depart_min))
    connection.commit()
    cursor.close()
    # add to uses
    ins3 = 'INSERT INTO operates VALUES(%s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(ins3, (plane_id, flight_num, depart_month, depart_day, depart_year, depart_hr, depart_min))
    connection.commit()
    cursor.close()
    # add to arrives
    ins4 = 'INSERT INTO arrives VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(ins4, (arrive_airport, depart_month, depart_day, depart_year, depart_hr, depart_min, arrive_month, arrive_day, arrive_year,arrive_hr, arrive_min))
    connection.commit()
    # add to departs
    ins5 = 'INSERT INTO departs VALUES(%s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(ins5, (depart_airport, flight_num, depart_month, depart_day, depart_year, depart_hr, depart_min))
    connection.commit()
    cursor.close()
    return redirect(url_for('airlineHome'))

# adding an airplane to the database
@app.route('/addAirplane', methods=['GET', 'POST'])
def addPlane():
    # airplane variables
    airplane_id = request.form['Airplane ID']
    seats = request.form['Seats']
    # own variables
    airline_name = request.form['Airline']

    # adding to airplane
    cursor = connection.cursor()
    ins = 'INSERT INTO airplane VALUES(%s, %s)'
    cursor.execute(ins, (airplane_id, seats))
    connection.commit()
    # adding to own
    ins2 = 'INSERT INTO own VALUES(%s, %s)'
    cursor.execute(ins, (airplane_id, airline_name))
    connection.commit()
    cursor.close()
    return redirect(url_for('airlineHome'))
# adding an airport to the database
@app.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
    # airport variables
    airport_name = request.form['Airport Name']
    city = request.form['City Name']

    # adding to airplane
    cursor = connection.cursor()
    ins = 'INSERT INTO airport VALUES(%s, %s)'
    cursor.execute(ins, (airport_name, city))
    connection.commit()
    cursor.close()
    return redirect(url_for('airlineHome'))
# viewing flight ratings
@app.route('/viewRatings', methods=['GET', 'POST'])
def viewRatings():
    # this is our query for our ratings
    cursor = connection.cursor()
    query = 'SELECT * FROM rates'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('CustomerPage.html', posts=data)

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=False)
