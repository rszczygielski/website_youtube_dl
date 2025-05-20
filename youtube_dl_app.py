from website_youtube_dl import create_app, socketio
from website_youtube_dl.config import DevelopmentConfig
import argparse
import json
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the YouTube DL Flask app.")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host to run the app on (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000,
                        help="Port to run the app on (default: 5000)")
    parser.add_argument("--debug", action="store_true",
                        help="Run app in debug mode")
    parser.add_argument("--config-dir", default=None,
                        help="Custom config directory for site_config_dir")
    parser.add_argument("--logger-config", default=None,
                        help="Path to a JSON logger config file")
    args = parser.parse_args()

    logger_config = None
    if args.logger_config and os.path.exists(args.logger_config):
        with open(args.logger_config, "r") as f:
            logger_config = json.load(f)

    app = create_app(DevelopmentConfig,
                     config_dir=args.config_dir, logger_config=logger_config)
    socketio.run(app=app, host=args.host, port=args.port, debug=args.debug)
