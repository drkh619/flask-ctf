from flask import Flask, jsonify, request, render_template, url_for
import json
# import requests

app = Flask(__name__, static_url_path='/static')

def loadProduct():
    # with open('products.json','r', encoding='utf-8') as files:
    #     return json.load(files)
    file = open('products.json','r',encoding='utf-8')
    return json.load(file)

def writeProduct(products):
    file = open('products.json','w',encoding='utf-8')
    json.dump(products,file,indent=4)




@app.route("/api/products",methods=['GET'])
def prod():
    data = loadProduct()
    return jsonify(data)

@app.route("/api/products",methods=['POST'])
def createProd():
    new_product = request.json

    data = loadProduct()
    maxid = max(product["id"] for product in data) if data else 0
    new_product["id"] = maxid+1

    data.append(new_product)
    writeProduct(data)

    return jsonify(new_product), 201

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
    return render_template('products.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/login")
def admin():
    # return render_template('admin.html')
    return 'login'

@app.route("/register")
def admin():
    # return render_template('admin.html')
    return 'register'

@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/edit")
def edit_products():
    # return render_template('admin.html')
    return render_template('admin_edit.html')

@app.route("/delete")
def delete_products():
    # return render_template('de.html')
    return 'delete'

app.run(debug=True)