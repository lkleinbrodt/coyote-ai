from backend import create_app
from dotenv import load_dotenv
from backend.config import DevelopmentConfig, ProductionConfig, TestingConfig
import os

load_dotenv(override=True)


def deploy_app():
    config_map = {
        "dev": DevelopmentConfig,
        "prod": ProductionConfig,
        "test": TestingConfig,
    }

    env = os.environ.get("ENV", "dev")
    app = create_app(config_map[env]())
    return app


app = deploy_app()

if __name__ == "__main__":
    app.run()
