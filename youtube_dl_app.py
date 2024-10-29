from website_youtube_dl import create_app, socketio
from website_youtube_dl.config import DevelopmentConfig


app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    socketio.run(app=app, host="0.0.0.0")
