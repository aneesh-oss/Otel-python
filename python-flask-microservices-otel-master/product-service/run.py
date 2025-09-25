# run.py
import logging
from application import create_app, db
from application import models
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    logger.info("Starting Product API service on port 5002")
    app.run(host='0.0.0.0', port=5002)
