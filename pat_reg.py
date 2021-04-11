from flask import Flask, render_template, request
from dbconnect import connection
from passlib.hash import md5_crypt

app = Flask(__name__)

cur,conn = connection()

@app.route('/patient_register')
def patient_reg():
    return render_template('patient_reg.html')

if __name__ == "__main__":
    app.run(debug=True)
