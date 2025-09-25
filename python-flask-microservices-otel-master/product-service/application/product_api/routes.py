# application/product_api/routes.py
import logging
from flask import jsonify, request
from . import product_api_blueprint
from .. import db
from ..models import Product

# Setup logger
logger = logging.getLogger(__name__)


@product_api_blueprint.route('/api/products', methods=['GET'])
def products():
    logger.info("Fetching all products")
    items = [row.to_json() for row in Product.query.all()]
    logger.info("Fetched %d products", len(items))
    return jsonify({'results': items})


@product_api_blueprint.route('/api/product/create', methods=['POST'])
def post_create():
    logger.info("Received request to create product: %s", request.form.to_dict())

    try:
        name = request.form['name']
        slug = request.form['slug']
        image = request.form['image']
        price = request.form['price']

        item = Product(name=name, slug=slug, image=image, price=price)

        db.session.add(item)
        db.session.commit()

        logger.info("Product created successfully: %s", item.to_json())
        return jsonify({'message': 'Product added', 'product': item.to_json()})

    except Exception as e:
        logger.exception("Failed to create product")
        return jsonify({'message': 'Error creating product', 'error': str(e)}), 500


@product_api_blueprint.route('/api/product/<slug>', methods=['GET'])
def product(slug):
    logger.info("Fetching product with slug: %s", slug)
    item = Product.query.filter_by(slug=slug).first()

    if item is not None:
        logger.info("Product found: %s", item.to_json())
        return jsonify({'result': item.to_json()})
    else:
        logger.warning("Product with slug '%s' not found", slug)
        return jsonify({'message': 'Cannot find product'}), 404
