from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
import json
import os.path
from werkzeug.utils import secure_filename

bp = Blueprint('urlshort',__name__)

@bp.route('/')
def home():
    #return render_template('home.html', name="Aashutosh")
    return render_template('home.html', codes=session.keys())

#@app.route('/your-url')
#def your_url():
#   return render_template('your_url.html', code = request.args['code'])

#Note: Route Only allows GET Request. So we have to explicitly specify the POST  request.
@bp.route('/your-url', methods= ["GET","POST"])
def your_url():
    if request.method== "POST":
        urls={}
        #Checking If a JSON File for urls already exists.
        if os.path.exists('urls.json'):
            with open('urls.json') as url_file:
                urls=json.load(url_file)     

        #Checking If a key entered already exists in the json files If yes then return to home  
        if(request.form['code'] in urls.keys()):
            flash("Short name already taken. Choose another")
            return redirect(url_for('urlshort.home'))

        #Check if File or URL is inputted
        if 'url' in request.form.keys(): #key list is same as list of name attribute value for form inputs
            #For URL 
            urls[request.form['code']] = {'url':request.form['url']}
        else:   #For File
            f=request.files['file'] #Key same as name attribute in html form
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save('/home/aashutosh/Desktop/url_shortener/urlshort/static/user_files/'+full_name)
            urls[request.form['code']] = {'file': full_name}

        with open('urls.json', 'w') as url_file:
            json.dump(urls, url_file)
            #Adding the code to current session info 
            session[request.form['code']] = True

        return render_template('your_url.html', code = request.form['code'])
    else:
        #return redirect('/')  #Redirect to home page.
        return redirect(url_for('urlshort.home'))


#Functionality to redirect to desired page for each code.
@bp.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('urls.json'):
        with open('urls.json') as url_file:
            urls=json.load(url_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename= 'user_files/'+urls[code]['file']))
        
    return abort(404) #If invalid user request 

@bp.errorhandler(404) #Catch the 404 error and execute following code
def page_not_found(error):
    return render_template('page_not_found.html'), 404

#Session API- displays user session info in form of JSON
@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))
