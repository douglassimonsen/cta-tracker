import flask
import flask_cors
import datetime

class CustomJSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%dT%H:%M:%S")
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return flask.json.JSONEncoder.default(self, obj)


app = flask.Flask(__name__)

app.json_encoder = CustomJSONEncoder  # needed to correctly pass datetimes

flask_cors.CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'  # necessary for POST requests, see https://stackoverflow.com/a/57735363/6465644
