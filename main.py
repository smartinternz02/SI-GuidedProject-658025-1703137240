import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from flask import Flask, request, render_template, redirect, url_for
from cloudant.client import Cloudant

model = load_model(r'updated-xception-diabetic-retinopathy.h5')

from cloudant.client import Cloudant

client = Cloudant.iam('a70abfee-c790-4fc3-a8ea-717c40a01d86-bluemix', 'ChsIS6C8jNrFfC89nI60AVvF8Oq62qu2w9qISux8xvfg',
                      connect=True)

my_database = client.create_database('my_database')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login.html')
def login():
    return render_template('login.html')


@app.route('/afterlogin', methods=['POST'])
def afterlogin():
    user = request.form['id']
    passw = request.form['password']
    print(user, passw)
    query = {'_id': {'$eq': user}}
    docs = my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if (len(docs.all()) == 0):
        return render_template('login.html', pred="The username is not found.")
    else:
        if ((user == docs[0][0]['_id'] and passw == docs[0][0]['psw'])):
            return redirect(url_for('prediction'))
        else:
            print('Invalid User')


@app.route('/index.html')
def home():
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/afterreq', methods=['POST'])
def afterreq():
    x = [x for x in request.form.values()]
    print((x))
    data = {'_id': x[1], 'name': x[0], 'psw': x[2], 'check': x[3]}
    print(data)
    query = {'_id': {'$eq': data['_id']}}
    docs = my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if (len(docs.all()) == 0):
        url = my_database.create_document(data)
        return render_template('register.html', pred="registration Successful, please login using your details")
    else:
        return render_template('register.html', pred="you are already a member, please login using your details")


@app.route('/prediction.html')
def prediction():
    return render_template('prediction.html')


@app.route('/res', methods=['GET', 'POST'])
def res():
    if (request.method == "POST" or request.method== "GET") :
        print(request.files)
        f = request.files['image']
        basepath = os.path.dirname(__file__)
        filepath = os.path.join(basepath, 'uploads', f.filename)
        f.save(filepath)
        img = image.load_img(filepath, target_size=(299, 299))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        img_data = preprocess_input(x)
        prediction = np.argmax(model.predict(img_data), axis=1)
        index = ['No Diabetic Retinopathy', 'MILD DR', 'Moderate DR', 'Severe DR', 'Proliferative DR']
        result = str(index[prediction[0]])
        print(result)
        return render_template('prediction.html', prediction=result)


@app.route('/logout')
def logout():
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True)
