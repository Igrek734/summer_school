import os

from flask import Flask, jsonify, abort, make_response, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/igork/PycharmProjects/Rest/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
products = []


@app.route('/product', methods=['POST'])
def create_product():
    if not request.json or not 'name' or not 'description' in request.json:
        abort(400)
    product = {
        'id': len(products) + 1,
        'name': request.json['name'],
        'description': request.json['description'],
        'icon': request.json.get('icon', '')
    }
    products.append(product)
    return jsonify(product), 201


@app.route('/product/<int:product_id>/image', methods=['POST'])
def load_icon(product_id):
    if len(products) < product_id or product_id < 0:
        abort(404)
    icon = request.files['icon']
    if icon:
        filename = secure_filename(icon.filename)
        icon.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        app.logger.debug('Icon uploaded: %s', filename)
        products[product_id - 1]['icon'] = filename
        return jsonify(products[product_id - 1])
    else:
        abort(400)

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    if len(products) < product_id or product_id < 0:
        abort(404)
    return jsonify(products[product_id - 1])


@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_product_icon(product_id):
    if len(products) < product_id or product_id < 0:
        abort(404)
    filename=products[product_id - 1]['icon']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            abort(404)
    except FileNotFoundError:
        abort(404)



@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if len(products) < product_id or product_id < 0:
        abort(404)
    if not request.json:
        abort(400)

    products[product_id - 1]['name'] = request.json.get('name', products[product_id - 1]['name'])
    products[product_id - 1]['description'] = request.json.get('description', products[product_id - 1]['description'])
    return jsonify(products[product_id - 1])


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if len(products) < product_id or product_id < 0:
        abort(404)
    products.remove(products[product_id - 1])
    return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


if __name__ == '__main__':
    app.run(debug=True)
