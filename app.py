from backend import create_app
from dotenv import load_dotenv

load_dotenv(override=True)


def deploy_app():
    app = create_app()
    return app


app = deploy_app()

if __name__ == "__main__":
    app.run()
