from flask_cors import CORS
from flask import Flask, jsonify
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/time')
def time_now():
  """ Retunt current time """
  current_time = datetime.datetime.now()
  formated_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
  return jsonify({'time':formated_time})

if __name__ == '__main__':
  app.run(debug=True)
  