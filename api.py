from flask import Flask, jsonify, request
import nest_asyncio
from scraping import *
from flask_cors import CORS
nest_asyncio.apply()

# Create Flask application
app = Flask(__name__)
CORS(app)
@app.route('/api/patent', methods=['GET'])
async def get_relationel_patent():
    query = request.args.get('q')
    date = request.args.get('date')
    response = mainfunc(query)

    return response
if __name__ == '__main__':
    app.run(debug=True)

