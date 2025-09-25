# application/frontend/api/UserClient.py
import requests
import logging
from flask import session

logger = logging.getLogger(__name__)


class UserClient:
    @staticmethod
    def post_login(form):
        payload = {
            'username': form.username.data,
            'password': form.password.data
        }
        url = 'http://cuser-service:5001/api/user/login'
        logger.info("Sending login request for user '%s'", payload['username'])

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            d = response.json()
            logger.info("Response from user api: %s", d)

            api_key = d.get('api_key')
            if api_key:
                logger.info("Login successful, API key received")
                return api_key
            else:
                logger.warning("Login failed, no API key returned")
                return False

        except Exception as e:
            logger.exception("Login request failed")
            return False

    @staticmethod
    def get_user():
        headers = {
            'Authorization': 'Basic ' + session.get('user_api_key', '')
        }
        url = 'http://cuser-service:5001/api/user'
        logger.info("Fetching user info from %s", url)

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            user = response.json()
            logger.info("Fetched user info: %s", user)
            return user
        except Exception as e:
            logger.exception("Failed to fetch user info")
            return None

    @staticmethod
    def post_user_create(form):
        payload = {
            'email': form.email.data,
            'password': form.password.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'username': form.username.data
        }
        url = 'http://cuser-service:5001/api/user/create'
        logger.info("Creating user with payload: %s", payload)

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            user = response.json()
            logger.info("User created successfully: %s", user)
            return user
        except Exception as e:
            logger.exception("Failed to create user")
            return None

    @staticmethod
    def does_exist(username):
        url = f'http://cuser-service:5001/api/user/{username}/exists'
        logger.info("Checking if username '%s' exists", username)

        try:
            response = requests.get(url)
            exists = response.status_code == 200
            logger.info("Username '%s' exists: %s", username, exists)
            return exists
        except Exception as e:
            logger.exception("Failed to check username existence")
            return False
