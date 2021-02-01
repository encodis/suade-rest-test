from flask import Flask

from queries import query_summary


app = Flask(__name__)

@app.route('/summary/<date>')
def summary(date):
    
    result = query_summary(date)
    
    return result, 200
