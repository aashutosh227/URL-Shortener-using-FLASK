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
            f.save('urlshort/static/user_files/'+full_name)
            #f.save(url_for('static', filename= 'user_files/'+full_name))
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

@bp.route('/manage_codes')
def manage_code():
    return render_template('manage_codes.html')

#Function to visit the site by entering the short code
@bp.route('/visit', methods= ["GET","POST"])
def visit():
    if request.method =="POST" and os.path.exists('urls.json'):

        with open('urls.json') as url_file:
            urls = json.load(url_file)
            #Check if short code exists or not
            if(request.form['code'] not in urls.keys()):
                flash("Short code dosen't exist, Please make a new one! ")
                return redirect(url_for('urlshort.manage_code'))
            else:
                code = request.form['code']
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    #return redirect('urlshort/static/user_files/'+urls[code]['file'])
                    return redirect(url_for('static', filename= 'user_files/'+urls[code]['file']))
    else:
        return abort(404)

#Function to visit the site by entering the short code
@bp.route('/manage', methods= ["GET","POST"])
def manage():
    if request.method =="POST" and os.path.exists('urls.json'):

        with open('urls.json') as url_file:
            urls = json.load(url_file)
            #Check if short code exists or not
            if(request.form['code'] not in urls.keys()):
                flash("Short code dosen't exist, Please make a new one! ")
                return redirect(url_for('urlshort.manage_code'))
            else:
                code = request.form['code']
                if 'file' in urls[request.form['code']].keys():
                    return render_template('manage_file.html', 
                    code = request.form['code'], file_path=urls[request.form['code']]['file'][len(code):])
                elif 'url' in urls[request.form['code']].keys():
                    return render_template('manage_url.html', 
                    code = request.form['code'], url=urls[request.form['code']]['url'])
                else:
                    flash("Short code dosen't exist, Please make a new one! ")
                    return redirect(url_for('urlshort.manage_code'))
    else:
        return abort(404)

#Function to return URL/FILE info
@bp.route('/get_code_data')
def get_code_data(code, type):
    with open('urls.json') as url_file:
        urls = json.load(url_file)
        if type=="url":
            return urls[code]['url']
        else:
            return urls[code]['file'][len(code):]


#Function to delete code
@bp.route('/delete_file_code', methods=['GET','POST'])
def delete_file_code():
    if request.method == 'POST' and os.path.exists('urls.json'):
        with open('urls.json') as url_file:
            urls = json.load(url_file)

            if(request.form['code'] not in urls.keys()):
                flash("Short code dosen't exist")
                return redirect(url_for('urlshort.home'))
            else:
                if 'file' in urls[request.form['code']].keys() or 'url' in urls[request.form['code']].keys():
                    #Creating new copy of urls as we can't edit urls in read mode
                    urls_new = urls
                    #Deleting the key from the new copy created
                    urls_new.pop(request.form['code'])

                    with open('urls.json', 'w') as url_file:
                        #Write the new updated urls json to existing urls.json file in write mode
                        json.dump(urls_new,url_file)
                    
                    flash("Deleted Successfully")
                    return redirect(url_for('urlshort.home'))
                else:
                    flash("Already Deleted")
                    return redirect(url_for('urlshort.manage_code'))
    else:
        return abort(404)

@bp.route('/update_file', methods=['GET','POST'])
def update_file():
    if request.method == 'POST' and os.path.exists('urls.json'):
        with open('urls.json') as url_file:
            urls =json.load(url_file)
            code = request.form['code']
            try:
                os.remove('urlshort/static/user_files/'+urls[code]['file'])
            except OSError:
                pass
            
            urls_new = urls
            urls_new.pop(code)
            
            f = request.files['new_file'] #Key same as name attribute in html form
            full_name = code + secure_filename(f.filename)
            f.save('urlshort/static/user_files/'+full_name)
            #f.save(url_for('static', filename= 'user_files/'+full_name))
            urls_new[code] = {'file': full_name}

            with open('urls.json', 'w') as url_file:
                json.dump(urls_new,url_file)
                session[request.form['code']] = True
            
            flash("Updated Successfully")
            return redirect(url_for('urlshort.manage_code'))
    else:
        return abort(404)

@bp.route('/update_url', methods=['GET','POST'])
def update_url():
    if request.method == 'POST' and os.path.exists('urls.json'):
        with open('urls.json') as url_file:
            urls =json.load(url_file)
            urls_new = urls

            urls_new.pop(request.form['code'])
            urls_new[request.form['code']] = {'url': request.form['url']}

            with open('urls.json', 'w') as url_file:
                json.dump(urls_new, url_file)

                flash("Updated Successfully")
                return redirect(url_for('urlshort.manage_code'))
    else:
        return abort(404)