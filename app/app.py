from flask import Flask, request
from logging_hook import init_logger, flask_request_hook, log_event  # import hook functions

app = Flask(__name__)

# Initialize the logger (will create logs/events.log by default)
init_logger()

# Log every incoming HTTP request automatically
@app.before_request
def before_request():
    flask_request_hook(request)

@app.route('/')
def hello():
    # Log a custom event when this route is called
    log_event("hello_page_viewed", {"message": "Hello from Docker and Flask!"})
    return "Hello from Docker and Flask!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
