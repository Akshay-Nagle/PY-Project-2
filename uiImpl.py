import coreLogic
import os      # For File Manipulations like get paths, rename
from flask import Flask, flash, request, redirect, render_template, send_file
from werkzeug.utils import secure_filename
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
transcripts_DIR = os.path.join(path, 'transcriptsIITP')

# Make directory if "uploads" folder not exists
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
os.mkdir(UPLOAD_FOLDER)

if os.path.exists(transcripts_DIR):
    shutil.rmtree(transcripts_DIR)
os.mkdir(transcripts_DIR)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['csv', 'png', 'jpeg', 'jpg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
   return render_template('upload.html')

@app.route('/download', methods=['GET', 'POST'])
def push_file():
   resp = coreLogic.prepareTranscriptsArchive()
   if resp:
      file_path = os.path.join(os.getcwd(), "transcripts.zip")
      return send_file(file_path, as_attachment=True)
   else:
      flash("Generate Transcripts First")
      return redirect("/")

@app.route('/', methods=['GET','POST'])
def file():
   if request.method == 'POST':
      finfo = False
      rejForm = 'application/octet-stream' 
      rfm = request.form
      print("============")
      print(rfm)
      print("-----------------")
      if 'files[]' not in request.files:
          flash('No file part')
          return redirect(request.url)

      files = request.files.getlist('files[]')
      rfSign = request.files['sign']
      rfSeal = str(request.files['seal'])
      print("+++++++")
      print(files)
      print(str(rfSign))
      print(str(rfSeal))
      print("++++++++")
      if 'sign' in request.files and 'application/octet-stream' not in str(rfSign):
         print(f"{request.files['sign']} || {type(request.files['sign'])}")
         request.files['sign'].save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(request.files['sign'].filename)))
         print(f"Saving attempt: {os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(request.files['sign'].filename))}")
      if 'seal' in request.files and 'application/octet-stream' not in str(rfSeal):
         print(f"{request.files['seal']} || {type(request.files['seal'])}")
         request.files['seal'].save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(request.files['seal'].filename)))
         print(f"Saving attempt: {os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(request.files['seal'].filename))}")
         # print(f"saved to:{cPath}")
      if rejForm not in str(files):
         if len(files) == 3:
            for file in files :
               print(f"{file} || {type(file)}")
               print("________________--8")
               if file and allowed_file(file.filename):
                  filename = secure_filename(file.filename)
                  print(file)
                  print("***********8")
                  file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File(s) successfully uploaded')
         else: 
            finfo = True
            flash("Please input all the required files!")
            return redirect('/')
      elif not finfo:
         flash("Please input all the required files!")
         return redirect('/')

      if "range" in rfm and not finfo:
         print("yyyyyyyyyy")
         if rejForm not in str(files):
            if "First" in rfm:
               fst = rfm['First']
               print(fst)
               resp, tlst = coreLogic.prepMs(rfm['First'])
               if resp:
                  flash('Transcripts generated in specified range')
                  if len(tlst) > 0:
                     flash(f"Roll Nos: {tlst} do not exist!")
               else:
                  flash("Enter valid range for RollNos!")
            else:
               flash("Enter valid range for RollNos!")
         elif not finfo:
            flash("Please upload all the required files!")

      if "transcript" in rfm:
         if rejForm not in str(files):
            resp, tlst = coreLogic.prepMs("", all=True)
            if resp:
               flash('All Transcript generated')
               if len(tlst) > 0:
                  flash(f"Roll Nos: {tlst} do not exist!")
         else:
            if not finfo:
               flash('Please upload all the required files')
   return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
