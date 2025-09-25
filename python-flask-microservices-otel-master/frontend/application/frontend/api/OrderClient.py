# application/frontend/api/OrderClient.py
from flask import session
import requests
import logging

logger = logging.getLogger(__name__)


class OrderClient:

    @staticmethod
    def get_order():
        url = 'http://corder-service:5003/api/order'
        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        logger.info("Fetching current order from %s", url)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            order = response.json()
            logger.info("Fetched order: %s", order)
            return order
        except Exception as e:
            logger.exception("Failed to fetch current order")
            return None

    @staticmethod
    def post_add_to_cart(product_id, qty=1):
        url = 'http://corder-service:5003/api/order/add-item'
        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        payload = {
            'product_id': product_id,
            'qty': qty
        }
        logger.info("Adding product_id=%s qty=%s to cart via %s", product_id, qty, url)

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()
            order = response.json()
            logger.info("Updated order after adding item: %s", order)
            return order
        except Exception as e:
            logger.exception("Failed to add product_id=%s to cart", product_id)
            return None

    @staticmethod
    def post_checkout():
        url = 'http://corder-service:5003/api/order/checkout'
        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        logger.info("Checking out order via %s", url)

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            order = response.json()
            logger.info("Checkout successful: %s", order)
            return order
        except Exception as e:
            logger.exception("Checkout failed")
            return None

    @staticmethod
    def get_order_from_session():
        default_order = {
            'items': {},
            'total': 0,
        }
        order = session.get('order', default_order)
        logger.debug("Retrieved order from session: %s", order)
        return order
