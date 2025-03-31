from website_youtube_dl import create_app, socketio
from website_youtube_dl.config import DevelopmentConfig


app = create_app(DevelopmentConfig)


def main():
    socketio.run(app=app, host ="0.0.0.0")


if __name__ == "__main__":
    main()
