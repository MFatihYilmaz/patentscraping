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
    summary_words=request.args.get('words')

    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    # Bu fonksiyon 3 parametre aliyor default deger bos string
    #Sadece baslik varsa mainfunc(title=query) seklinde digerlerinide ayni sekil yollayabilirsiniz 
    if startDate !=None and endDate != None:
        response = mainfunc(title=query,sum=summary_words,start_date=startDate,end_date=endDate)
    else:
        response = mainfunc(title=query)

    return response
if __name__ == '__main__':
    app.run(debug=True)

