# application/order_api/routes.py
import logging
from flask import jsonify, request, make_response
from . import order_api_blueprint
from .. import db
from ..models import Order, OrderItem
from .api.UserClient import UserClient

# Logger for this module (OTel auto-instrumentation will inject trace/span IDs)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@order_api_blueprint.route("/api/orders", methods=["GET"])
def orders():
    logger.info("Fetching all orders")
    items = [row.to_json() for row in Order.query.all()]
    return jsonify(items)


@order_api_blueprint.route("/api/order/add-item", methods=["POST"])
def order_add_item():
    api_key = request.headers.get("Authorization")
    logger.info("Adding item to order", extra={"api_key": api_key})

    response = UserClient.get_user(api_key)
    if not response:
        logger.warning("Unauthorized add-item attempt")
        return make_response(jsonify({"message": "Not logged in"}), 401)

    user = response["result"]
    p_id = int(request.form["product_id"])
    qty = int(request.form["qty"])
    u_id = int(user["id"])

    known_order = Order.query.filter_by(user_id=u_id, is_open=1).first()

    if known_order is None:
        logger.info("Creating new order", extra={"user_id": u_id})
        known_order = Order()
        known_order.is_open = True
        known_order.user_id = u_id
        known_order.items.append(OrderItem(p_id, qty))
    else:
        logger.info("Updating existing order", extra={"order_id": known_order.id, "user_id": u_id})
        found = False
        for item in known_order.items:
            if item.product_id == p_id:
                found = True
                item.quantity += qty
                logger.info("Incremented quantity", extra={"product_id": p_id, "new_qty": item.quantity})
        if not found:
            known_order.items.append(OrderItem(p_id, qty))
            logger.info("Added new item", extra={"product_id": p_id, "qty": qty})

    db.session.add(known_order)
    db.session.commit()
    logger.info("Order updated successfully", extra={"order_id": known_order.id})
    return jsonify({"result": known_order.to_json()})


@order_api_blueprint.route("/api/order", methods=["GET"])
def order():
    api_key = request.headers.get("Authorization")
    logger.info("Fetching open order", extra={"api_key": api_key})

    response = UserClient.get_user(api_key)
    if not response:
        logger.warning("Unauthorized order fetch attempt")
        return make_response(jsonify({"message": "Not logged in"}), 401)

    user = response["result"]
    open_order = Order.query.filter_by(user_id=user["id"], is_open=1).first()

    if open_order is None:
        logger.info("No open order found", extra={"user_id": user["id"]})
        return jsonify({"message": "No order found"})
    else:
        logger.info("Open order retrieved", extra={"order_id": open_order.id, "user_id": user["id"]})
        return jsonify({"result": open_order.to_json()})


@order_api_blueprint.route("/api/order/checkout", methods=["POST"])
def checkout():
    api_key = request.headers.get("Authorization")
    logger.info("Checkout initiated", extra={"api_key": api_key})

    response = UserClient.get_user(api_key)
    if not response:
        logger.warning("Unauthorized checkout attempt")
        return make_response(jsonify({"message": "Not logged in"}), 401)

    user = response["result"]
    order_model = Order.query.filter_by(user_id=user["id"], is_open=1).first()

    if order_model is None:
        logger.warning("Checkout attempted without open order", extra={"user_id": user["id"]})
        return make_response(jsonify({"message": "No open order"}), 400)

    order_model.is_open = 0
    db.session.add(order_model)
    db.session.commit()

    logger.info("Checkout completed", extra={"order_id": order_model.id, "user_id": user["id"]})
    return jsonify({"result": order_model.to_json()})
