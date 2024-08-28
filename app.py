from flask import Flask, jsonify, request, render_template, url_for, redirect, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
# import requests

app = Flask(__name__, static_url_path='/static')
CORS(app)
app.secret_key = '50M3tH1nG_53cR3T'

def loadProduct():
    # with open('products.json','r', encoding='utf-8') as files:
    #     return json.load(files)
    file = open('products.json','r',encoding='utf-8')
    return json.load(file)

def writeProduct(products):
    file = open('products.json','w',encoding='utf-8')
    json.dump(products,file,indent=4)

def load_users():
    with open('users.json','r', encoding='utf-8') as files:
        return json.load(files)
    
def load_admin():
    with open('admin.json','r', encoding='utf-8') as files:
        return json.load(files)
    
def write_users(users):
    with open('users.json','w', encoding='utf-8') as files:
        json.dump(users, files, indent=4)



@app.route("/api/products",methods=['GET'])
def prod():
    data = loadProduct()
    return jsonify(data)

@app.route("/api/products",methods=['POST'])
def createProd():
    new_product = request.form.to_dict()

    data = loadProduct()
    maxid = max(product["id"] for product in data) if data else 0
    new_product["id"] = maxid+1

    data.append(new_product)
    writeProduct(data)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(new_product), 201
    else:
        return redirect(url_for('admin'))

@app.route("/api/products/<int:pid>",methods=['GET'])
def getProductById(pid):
    products = loadProduct()
    prod = None

    for p in products:
        if p['id'] == pid:
            prod = p
            break
    return jsonify(prod) if prod else jsonify({"error":"product not found"}),404

@app.route("/api/products/<int:pid>",methods=['PUT'])
def updateProductById(pid):
    products = loadProduct()
    prod = None

    for p in products:
        if p['id'] == pid:
            prod = p
            break

    if prod:
        updated_prod = request.json
        prod.update(updated_prod)
        writeProduct(products)
        return jsonify(updated_prod)

    else: 
        return jsonify({"error":"product not found"}),404

@app.route("/api/products/<int:pid>",methods=['DELETE'])
def deleteProductById(pid):
    products = loadProduct()

    updatedList = list(filter(lambda p: p["id"] != pid, products))
    if len(updatedList) == len(products):
        return jsonify({"error":"product not found"}),404

    writeProduct(updatedList)
    return "Deleted Successfully!",204 if updatedList else 404


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/products")
def products():
    with open('products.json', 'r') as f:
        products = json.load(f)
    return render_template('products.html', products=products)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        user = next((user for user in users if user['username'] == username), None)
        if user and check_password_hash(user['password'],password):
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password!',401
    return render_template('login.html')

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method == 'POST':
        new_user = {
            'id': str(uuid.uuid1()),
            'username': request.form['username'],
            'email': request.form['email'],
            'password': generate_password_hash(request.form['password'])
        }
        users = load_users()

        if any(user['username'] == new_user['username'] for user in users):
            flash('Usern already exist!','error')
            return redirect(url_for('register'))
        users.append(new_user)
        write_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

@app.route("/admin_login",methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        admin_username = request.form['username']
        password = request.form['password']
        users = load_admin()

        user = next((user for user in users if user['username'] == admin_username and user['password'] == password), None)
        if user :
            session['admin_username'] = user['username']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password!',401
    return render_template('admin_login.html')
    

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/edit")
def edit_products():
    # return render_template('admin.html')
    return render_template('admin_edit.html')

@app.route("/delete")
def delete_products():
    with open('products.json', 'r') as f:
        products = json.load(f)
    return render_template('admin_delete.html', products=products)

app.run(debug=True,port=5000,host='0.0.0.0')