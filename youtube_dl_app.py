from  website_youtube_dl import create_app, socketio

app = create_app("test")

if __name__ == "__main__":
    socketio.run(app=app)
