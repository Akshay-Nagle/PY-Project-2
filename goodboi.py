import coreLogic
import os      # For File Manipulations like get paths, rename
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import shutil
import csv
import openpyxl
from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment, Border, Font, NamedStyle, Side
import os

path = os.getcwd()
app=Flask(__name__, static_folder=coreLogic.baseDir)
app.secret_key = "secret key" # for encrypting the session

#It will allow below 4MB contents only, you can change it
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

# Make directory if "uploads" folder not exists
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['csv', 'png', 'jpeg', 'jpg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
   return render_template('upload.html')

@app.route('/', methods=['GET','POST'])
def file():
   if request.method == 'POST':
      rfm = request.form
      #print("============")
      #print(rfm)
      #print("-----------------")
      # print(request.files['sign'])
      # print("============")
      if 'files[]' not in request.files:
          flash('No file part')
          return redirect(request.url)

      files = request.files.getlist('files[]')
      if 'sign' in request.files and 'application/octet-stream' not in request.files:
         print(request.files['sign'])
         cPath =(os.path.join(app.config['UPLOAD_FOLDER'], "sign.png"))
         request.files['sign'].save(cPath)
         #print(f"saved to:{cPath}")
      if 'seal' in request.files and 'application/octet-stream' not in request.files:
         #print(request.files['seal'])
         cPath =(os.path.join(app.config['UPLOAD_FOLDER'], "seal.png"))
         request.files['seal'].save(cPath)
         #print(f"saved to:{cPath}")
         
      for file in files:
         #print(file)
         #print("________________--8")
         if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #print(file)
            #print("***********8")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      #flash('File(s) successfully uploaded')


      if "range" in rfm:
         print("yyyyyyyyyy")
         if "First" in rfm:
            fst = rfm['First']
            #print(fst)
            coreLogic.prepMs(rfm['First'])
            flash('Transcript generated between given range')
         else:
            flash("Enter valid range for RollNos!")

      if "transcript" in rfm:
         coreLogic.prepMs("", all=True)
         flash('All Transcript generated')

   return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
