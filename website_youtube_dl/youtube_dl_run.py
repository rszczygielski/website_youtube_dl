from website_youtube_dl import create_app, socketio
from website_youtube_dl.config import DevelopmentConfig




if __name__ == "__main__":
    # tutaj doać konfigurację
    # argument parsera tutaj dodać
    app = create_app(DevelopmentConfig)
    socketio.run(app=app, host ="0.0.0.0")
