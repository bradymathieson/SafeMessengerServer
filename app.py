"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from json import loads, load, dump
from threading import Lock

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')

DATA_STRUCTURE_LOCK = Lock()

###
# Routing for your application.
###

@app.route('/v1')
def home():
    """Render website's home page."""
    return "API instructions: (coming soon)"

@app.route('/v1/add_user', methods=["GET", "POST"])
def add():

    if request.method == "POST":

        # Import files from external JSONs
        user_data = dict()
        current_ips = dict()
        DATA_STRUCTURE_LOCK.acquire()
        with open("user_data.json") as json_data:
            user_data = load(json_data)
        with open("current_ips.json") as json_data:
            current_ips = load(json_data)
        DATA_STRUCTURE_LOCK.release()

        # Get POST data
        received_json = loads(request.data)

        # Make sure JSON message is complete!
        if "username" not in received_json or "ip" not in received_json or "port" not in received_json:
            return "Not enough info provided", 400

        username = received_json["username"]
        ip = received_json["ip"]
        port = int(received_json["port"])

        # Make sure username is not already in the system.
        if username in user_data:
            return "Username already taken", 400

        # Make sure that IP is not already in system
        # if ip in current_ips:
        #     return "IP already in session"

        # Make sure two IP/port pairs are not identical
        if port < 1000:
            port = 1000
        elif port > 9999:
            port = 9999
        while ip in current_ips and port in current_ips[ip]:
            port += 1
            if port > 9999:
                port = 1000

        # Add to data structures
        DATA_STRUCTURE_LOCK.acquire()
        user_data[username] = {
            "ip" : ip,
            "port" : port
        }
        if ip not in current_ips:
            current_ips[ip] = list()
        current_ips[ip].append(port)
        with open('user_data.json', 'w') as outfile:
            dump(user_data, outfile)
        with open('current_ips.json', 'w') as outfile:
            dump(current_ips, outfile)
        DATA_STRUCTURE_LOCK.release()

        return "Successfully added:\n" + str(username) + ", " + str(ip) + ", " + str(port), 200
    else:
        return render_template('404.html'), 404

@app.route('/v1/remove_user', methods=["GET", "POST"])
def remove():
    if request.method == "POST":

        # Import files from external JSONs
        user_data = dict()
        current_ips = dict()
        DATA_STRUCTURE_LOCK.acquire()
        with open("user_data.json") as json_data:
            user_data = load(json_data)
        with open("current_ips.json") as json_data:
            current_ips = load(json_data)
        DATA_STRUCTURE_LOCK.release()

        received_json = loads(request.data)

        # Make sure JSON message is complete!
        if "username" not in received_json or "ip" not in received_json or "port" not in received_json:
            return "Not enough info provided", 400

        username = received_json["username"]
        ip = received_json["ip"]
        port = int(received_json["port"])

        # Make sure username is not already in the system.
        if username not in user_data:
            return "Username not in system", 400

        if ip != user_data[username]["ip"]:
            return "Incorrect IP", 400

        if port != user_data[username]["port"]:
            return "Incorrect port", 400

        # Make sure that IP is not already in system
        # if ip in current_ips:
        #     return "IP already in session"

        # Add to data structures
        DATA_STRUCTURE_LOCK.acquire()
        del user_data[username]
        current_ips[ip].remove(port)
        if len(current_ips[ip]) == 0:
            del current_ips[ip]
        with open('user_data.json', 'w') as outfile:
            dump(user_data, outfile)
        with open('current_ips.json', 'w') as outfile:
            dump(current_ips, outfile)
        DATA_STRUCTURE_LOCK.release()

        return "Successfully deleted:\n" + str(username) + ", " + str(ip) + ", " + str(port), 200
    else:
        return render_template('404.html'), 404

@app.route('/v1/current_users', methods=["GET"])
def current_users():
    if request.method == "GET":
        user_data = dict()
        with open("user_data.json") as json_data:
            user_data = load(json_data)
        return jsonify(user_data), 200
    else:
        return render_template('404.html'), 404


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
