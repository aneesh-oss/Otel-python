# application/frontend/api/ProductClient.py
import requests
import logging

logger = logging.getLogger(__name__)


class ProductClient:

    @staticmethod
    def get_products():
        url = 'http://cproduct-service:5002/api/products'
        logger.info("Fetching products from %s", url)

        try:
            response = requests.get(url)
            response.raise_for_status()
            products = response.json()
            logger.info("Fetched %d products", len(products.get('results', [])))
            return products
        except Exception as e:
            logger.exception("Failed to fetch products")
            return None

    @staticmethod
    def get_product(slug):
        url = f'http://cproduct-service:5002/api/product/{slug}'
        logger.info("Fetching product with slug '%s' from %s", slug, url)

        try:
            response = requests.get(url)
            response.raise_for_status()
            product = response.json()
            logger.info("Fetched product: %s", product)
            return product
        except Exception as e:
            logger.exception("Failed to fetch product with slug '%s'", slug)
            return None
