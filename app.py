from flask import Flask, jsonify, request, render_template, url_for, redirect, session, flash, Response, abort
import markdown
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import uuid
import json
# import requests

app = Flask(__name__, static_url_path='/static')
CORS(app)
app.secret_key = '50M3tH1nG_53cR3T'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)



def loadProduct():
    # with open('./data/products.json','r', encoding='utf-8') as files:
    #     return json.load(files)   
    file = open('./data/products.json','r',encoding='utf-8')
    return json.load(file)

def writeProduct(products):
    file = open('./data/products.json','w',encoding='utf-8')
    json.dump(products,file,indent=4)

def load_users():
    with open('./data/users.json','r', encoding='utf-8') as files:
        return json.load(files)
    
def load_admin():
    with open('admin.json','r', encoding='utf-8') as files:
        return json.load(files)
    
def write_users(users):
    with open('./data/users.json','w', encoding='utf-8') as files:
        json.dump(users, files, indent=4)

def load_cart():
    with open('./data/cart.json','r', encoding='utf-8') as files:
        return json.load(files)

def write_cart(cart_item):
    with open('./data/cart.json','w', encoding='utf-8') as files:
        json.dump(cart_item, files, indent=4)

def load_rating():
    with open('./data/rating.json','r', encoding='utf-8') as files:
        return json.load(files)

def write_rating(cart_item):
    with open('./data/rating.json','w', encoding='utf-8') as files:
        json.dump(cart_item, files, indent=4)

def load_files(filename):
    try:
        with open(file=filename, mode='r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Return a custom message if the file does not exist
        return "notfound"



@app.route("/api/products",methods=['GET'])
def prod():
    data = loadProduct()
    return jsonify(data)

@app.route("/api/products",methods=['POST'])
def createProd():
    if 'admin_username' not in session:
        return abort(403)

    new_product = request.form.to_dict()
    new_product['price'] = float(new_product['price'])

    data = loadProduct()
    maxid = max(product["id"] for product in data) if data else 0
    new_product["id"] = maxid+1

    data.append(new_product)
    writeProduct(data)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(new_product), 201
    else:
        flash('Product created successfully!','message')
        return render_template('admin.html')

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
        if request.is_json:
            updated_prod = request.get_json()
        else:
            updated_prod = request.form.to_dict()
        
        updated_prod['price'] = float(updated_prod['price'])
        prod.update(updated_prod)
        writeProduct(products)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(updated_prod)
        else:
            # flash('Product updated successfully','message')
            return render_template('product_edit.html', product=prod)

    else: 
        return jsonify({"error":"product not found"}),404

@app.route("/api/products/<int:pid>",methods=['DELETE'])
def deleteProductById(pid):
    if 'admin_username' not in session:
        return abort(403)

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
    with open('./data/products.json', 'r') as f:
        products = json.load(f)
    return render_template('products.html', products=products)

@app.route("/product/<int:pid>")
def product_details(pid):
    products = loadProduct()
    prod = None

    for p in products:
        if p['id'] == pid:
            prod = p
            break
    
    if prod:
        return render_template('product_details.html', product=prod)
    else:
        return 404 

@app.route("/about")
def about():
    
    fname = request.args.get('file')
    if not fname:
        content = load_files('about.md')
        html_content = markdown.markdown(content)
        # Handle missing filename (e.g., return a default message)
        return render_template('about.html', markdown_content=html_content)
    content = load_files(fname)
    if content == 'notfound':
        abort (404)
    html_content = markdown.markdown(content)
    return render_template('about.html',markdown_content=html_content)

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        rating = load_rating()
        

        user = next((user for user in users if user['username'] == username), None)
        if user and check_password_hash(user['password'],password):
            session['username'] = user['username']
            session['uid'] = user['id']
            user_rating = rating.get(user['id'])
            if user_rating:
                session['rate'] = len(user_rating)

            session.permanent = True #session expiry

            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!','error')
            return render_template('login.html')
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
            flash('User already exist!','error')
            return render_template(url_for('register'))
        users.append(new_user)
        write_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('username',None)
    session.pop('uid',None)
    session.pop('rate',None)
    return redirect(url_for('login'))

#here
@app.route("/api/cart/add/<int:pid>", methods=['POST'])
def add_product_to_cart(pid):
    if 'username' not in session:
        # flash('Please log in to add products to your cart!', 'error')
        # return redirect(url_for('product_details',pid=pid))
        return Response(status=204)
    
    user_id = session['uid']
    products = loadProduct()
    product = next((p for p in products if p['id'] == pid), None)
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('products'))

    cart = load_cart()

    if not isinstance(cart, dict):
        cart = {} 

    # If user has no cart yet, initialize it
    if user_id not in cart:
        cart[user_id] = []

    # Check if the product is already in the user's cart
    cart_item = next((item for item in cart[user_id] if item['id'] == pid), None)
    
    if cart_item:
        # If the product is already in the cart, increase the quantity
        cart_item['quantity'] += request.form.get('quantity', 1, type=int)
    else:
        # Add new product to the cart
        cart_item = {
            "id": product['id'],
            "name": product['title'],
            "price": product['price'],
            "image": product['image'], 
            "quantity": request.form.get('quantity', 1, type=int)
        }
        cart[user_id].append(cart_item)

    write_cart(cart)
    # flash('Product added to cart successfully!', 'message')
    return redirect(url_for('cart'))

@app.route("/api/cart/delete/<int:item_id>", methods=['POST'])
def remove_cart(item_id):
    if 'uid' not in session:
        return redirect(url_for('products'))
    
    user_id = session['uid']
    cart = load_cart()
    user_cart = cart.get(user_id)

    updated_cart = [item for item in user_cart if item['id'] != item_id]
    if len(updated_cart) == len(user_cart):
        return jsonify({"error": "Product not found in your cart"}), 404
        
    cart[user_id] = updated_cart

    write_cart(cart)
    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    if 'uid' not in session:
        flash('Please log in to view your cart!', 'error')
        return redirect(url_for('login'))

    user_id = session['uid']
    cart = load_cart()

    cart_items = cart.get(user_id, [])
    total = sum(item.get('price', 0) * item.get('quantity', 0) for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

#to here

@app.route("/api/checkout",methods=['POST'])
def checkout():
    if 'uid' not in session:
        flash('Please log in to view your cart!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['uid']
    cart = load_cart()
    user_cart = cart.get(user_id)

    if not user_cart:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('products'))
    
    # Load the current ratings from the file
    ratings = load_rating() 

    item_ids = [item['id'] for item in user_cart]

    if user_id in ratings:
        ratings[user_id].extend(item_ids)  # Append new items to the user's existing list
    else:
        ratings[user_id] = item_ids  # Create a new entry for the user if it doesn't exist

    # Save the updated ratings to the file
    write_rating(ratings)
    user_rating = ratings.get(user_id)
    if user_rating:
        session['rate'] = len(user_rating)
    
    cart[user_id] = []
    write_cart(cart)

    return redirect(url_for('rating')) # TODO Add product rating and redirect there with the
# TODO rating should take id's that user ordered and give a valid rating or no rating at all. It should send a PUT req to
# the edit endpoint and add rating and count!


# TODO We need to store this file to rating.json instead of session. Becuase session gets popped if not handled correctly or leak maybe found
@app.route("/rate", methods=['GET', 'POST'])
def rating():
    if 'uid' not in session:
        flash("Please login to rate products.")
        return render_template('login.html')

    user_id = session['uid']
    rating = load_rating()
    user_rating = rating.get(user_id)

    if not user_rating:
        return redirect(url_for('cart'))

    products = loadProduct()
    item_id = user_rating
    rated_products = [product for product in products if product['id'] in item_id]

    if request.method == 'POST':
        product_rating = request.form.to_dict()

        # Load the entire product.json file
        products = loadProduct()

        # Loop through form data to update product ratings
        for key, value in product_rating.items():
            if key.startswith("rating_"):
                product_id = key.split("_")[1]  # Extract the product ID
                new_rating = int(value)  # Convert rating value from string to integer

                # Find the product with this ID in the products list
                for product in products:
                    if str(product['id']) == product_id:
                        # Update the product rating
                        old_rating = product['rating']['rate']
                        old_count = product['rating']['count']

                        # Calculate the new rating
                        total_rating = old_rating * old_count
                        new_total = total_rating + new_rating
                        new_count = old_count + 1
                        new_rate = new_total / new_count

                        # Update the product in the loaded product list
                        product['rating']['rate'] = round(new_rate, 1)
                        product['rating']['count'] = new_count
                        break  # Stop the loop once the product is found

        # Write the updated product list back to product.json
        writeProduct(products)  # Pass the full product list to be written back

        # Clear user's rating from rating.json
        rating[user_id] = []
        write_rating(rating)

        # Remove the 'rate' session key after rating is submitted
        session.pop('rate', None)

        flash("Thanks for your rating")
        return redirect(url_for('home'))

    return render_template('rating.html', products=rated_products)


@app.route("/admin_login",methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        admin_username = request.form['username']
        password = request.form['password']
        users = load_admin()

        user = next((user for user in users if user['username'] == admin_username and user['password'] == password), None)
        if user :
            session['admin_username'] = user['username']
            session.permanent = True

            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password!','error')
            return render_template('admin_login.html')
    return render_template('admin_login.html')

@app.route("/admin_logout")
def admin_logout():
    session.pop('admin_username',None)
    return redirect(url_for('admin_login'))
    

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/edit")
def edit_products():
    with open('./data/products.json','r') as f:
        products = json.load(f)
    return render_template('admin_edit.html', products=products)

@app.route("/edit/<int:pid>")
def product_edit(pid):
    products = loadProduct()
    prod = None

    for p in products:
        if p['id'] == pid:
            prod = p
            break
    
    if prod:
        return render_template('product_edit.html', product=prod)
    else:
        return 404 

@app.route("/delete")
def delete_products():
    with open('./data/products.json', 'r') as f:
        products = json.load(f)
    return render_template('admin_delete.html', products=products)

app.run(debug=True,port=5000,host='0.0.0.0')