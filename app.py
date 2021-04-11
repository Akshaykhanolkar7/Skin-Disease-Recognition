from flask import (Flask, session,flash, json, jsonify, redirect, render_template, request, url_for)
from PIL import Image
import werkzeug
from os import walk
import tensorflow as tf
from werkzeug.utils import secure_filename
from tensorflow import keras
from tensorflow.keras.models import Sequential, load_model
from keras.preprocessing import image, sequence
from dbconnect import connection
from passlib.hash import md5_crypt
import os
import pickle
import threading
import webbrowser
from timeit import default_timer as timer
import glob
import cv2
import numpy as np
import werkzeug
import pat_reg

app = Flask(__name__)
input_img_path = 'static/images/input_img.jpg'
app.secret_key = 'key123'
cur,conn = connection()

input_img_path = 'static/images/input_img.jpg'
model = load_model('static/weather_model.h5')

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/user_panel')
def user_panel():
    return render_template('user_panel.html')

@app.route('/doctor')
def doc():
    return render_template('Doctors.html')

@app.route('/aboutus')
def abt():
    return render_template('about.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/patient_register')
def patient_reg():
    return render_template('patient_reg.html')
    
@app.route('/patient_login')
def patient_log():
    return render_template('login.html')

@app.route('/scan')
def firstpage():
    return render_template('index.html')

@app.route('/register',methods=["GET","POST"]) 
def register():

    try:
        rname = request.form['name']
        remail = request.form['email']
        entered_pass = request.form['password']
        print(rname,remail)
        y=cur.execute("INSERT INTO patient (name,email,password) VALUES (%s,%s,%s)",(rname,remail,entered_pass))
        conn.commit()
        return render_template("index1.html")
        # return render_template('patient_reg.html')
    except Exception as e:
        return(str(e))

@app.route('/login',methods=["GET","POST"]) 
def login():
    try:
        email = request.form['email']
        session['email'] = email
        password = request.form['password']
        sql = ("select * from patient where email = %s")
        p = (email,)
        cur.execute(sql,p)
        data = cur.fetchall()[0]
        patient_id = data[0]
        name = data[1]
        session['name'] = name
        print(patient_id,name)
        return render_template("user_panel.html",patient_id = patient_id, name = session['name'])
    except Exception as e:
        return(str(e))    

@app.route('/filldata',methods=["POST","GET"])
def filldata():
    age = request.form['age']
    bgroup = request.form['bgroup']
    sql2 =("UPDATE patient SET age = '%s',blood_group = '%s' WHERE email = '%s'" %(age,bgroup,session['email']))
    cur.execute(sql2)
    conn.commit()
    return render_template("login.html")

# def getinfo(lpin):
#     cur, conn = connection()
#     sql = ("select * from doctor where pin = %s") #address phone
#     p = (lpin,)
#     cur.execute(sql,p)
#     doc_id = cur.fetchall()[0][0]
#     name = cur.fetchall()[0][1]
#     return doc_id, name
# graph = tf.compat.v1.get_default_graph()
# global graph
#     with graph.as_default():

def getclass(image_path):
    class_name = ['Benign','Malignant']
    start = timer()
    img = image.load_img(image_path, target_size=(150, 150)) #(150, 150, 3)
    img_tensor = image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0) #(1, 150, 150, 3) 1 is because you pass only 1 image as an input and not multiple
    img_tensor /= 255. #(1, 150, 150, 1)
    pred = model.predict(img_tensor)
    end = timer()
    classes = np.argmax(pred) 
    return str(round(pred[0][0]*100,2))+'%', str(round(pred[0][1]*100,2))+'%', class_name[classes], str(round(end-start,2))+' seconds'


@app.route("/process_img",methods=["GET", "POST"])
def objectdetection():
    file_name = request.form['file_name']
    file = request.files.getlist('files[]')[0]
    inputimg = Image.open(file).convert('RGB')
    img = np.array(inputimg)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    cv2.imwrite(input_img_path,img) # save img
    ben_acc, mal_acc, output, time= getclass(input_img_path)  # predict
    print(ben_acc, mal_acc, output, time)
    result = ''
    if(output == ben_acc):
        result = 'no'
    else:
        result = 'yes'
    sql2 =("UPDATE patient SET detected = '%s' WHERE email = '%s'" %(result,session['email']))
    cur.execute(sql2)
    conn.commit()
    return jsonify({'ben_acc': ben_acc, 'mal_acc':mal_acc, 'output':output, 'time':time})  

# @app.route('/logintry',methods=["GET","POST"])
# def logintry():
#     try:
#         #print(md5_crypt.hash('modi'))
#         cur, conn = connection()
#         lpin = request.form['pin']
#         entered_pass = request.form['password']
#         sql = ("select password from doctor where pin = %s")
#         p = (lpin,)
#         cur.execute(sql,p)
#         data = cur.fetchall()[0]
#         print(data[0])
#         if md5_crypt.verify(entered_pass,data[0]):
#             doc_id, name = getinfo(lpin)
#             return "Success" #return render_template
#         else:
#             return "false"
#     except Exception as e:
#         return(str(e))
    
@app.route('/patient_login')
def pat_login():
    return render_template('login.html',title='login')

if __name__ == "__main__":
    app.run(debug=True)

    