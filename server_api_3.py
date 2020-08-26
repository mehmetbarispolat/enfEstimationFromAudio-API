from flask import Flask, render_template, request, send_from_directory, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
from pytube import YouTube, Stream
import logging

UPLOAD_FOLDER = '/home/baris/Projects/stajprojesiGit/static/enfEstimationFromAudio_docker/testVideo'
IMAGE_FOLDER = '/home/baris/Projects/stajprojesiGit/static/enfEstimationFromAudio_docker/output'
CMD = 'docker run -v /home/baris/Projects/stajprojesiGit/static/enfEstimationFromAudio_docker:/codeDir -v /home/baris/Projects/stajprojesiGit/static/enfEstimationFromAudio_docker:/testDir estimate-enf-from-audio-content /codeDir/testScript.sh'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER



@app.route('/')
def index():
	return render_template('upload.html')

@app.route('/youtube')
def youtube():
	return render_template('youtube.html')
###############
### FILE UPLOAD
###############
@app.route('/', methods = ['GET', 'POST'])
def uploaded_file():
	if request.method == 'POST':
		f = request.files['file']
		if f.filename == '':
			return render_template('display.html')

		filename = secure_filename(f.filename)
		print(filename)
		extension_file= os.path.splitext(filename)[1]
		splitfilename = os.path.splitext(filename)[0]
		print("before extension: "+extension_file)
		print("isim:"+ splitfilename)
		print(len(extension_file))

		if(len(extension_file) > 4):
			filename = splitfilename + ".mp4"

		destination = "/".join([app.config['UPLOAD_FOLDER'], filename])
		print(filename)
		f.save(destination)
		return  redirect(url_for("runDocker",filename = filename))
	elif request.method == 'GET':
		return render_template("404.html")

###############
### YOUTUBE
###############
@app.route('/youtube', methods = ['GET','POST'])
def youtube_file():
	if request.method == 'POST':
		url = request.form["url"]
		if url == '':
			return render_template('display.html')
		yt = YouTube(url)
		print(url)
		print("downloading")
		print(yt.title)
		sfilename = secure_filename(yt.title)
		tmp = sfilename.split('.')
		print(tmp)
		fn = ''
		for i in tmp:
			fn = fn + i
		print(fn)
		yt.streams.filter(file_extension='mp4', res = '360p').first().download(output_path = app.config['UPLOAD_FOLDER'], filename = fn)
		print("downloaded")
		filename = fn +".mp4"
		print(filename)
		return redirect(url_for('runDocker',filename = filename))

###############
### DOCKER RUN
##############
@app.route('/docker_run/<filename>')
def runDocker(filename):
	print("command starting")
	os.system(CMD+" "+filename)
	tmpFilename = os.path.splitext(filename)[0]
	print(tmpFilename)
	filename = tmpFilename + ".png"
	print(filename)
	print("komut bitti.")
	return redirect(url_for("display_image",filename=filename))

######################
### DISPLAY ENF OUTPUT
######################
@app.route('/display/<filename>')
def display_image(filename):
	print("display'e girdim.")
	return render_template('display.html', filename = filename)
###############
##ERROR HANDLER
###############
@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
	logging.basicConfig(filename="500.log",level=logging.DEBUG,format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s %(funcName)s %(module)s")
	return 'Please go file upload first and then go youtube, estimate url',500


if __name__ == '__main__':
   app.run(host='0.0.0.0', port = 80)

