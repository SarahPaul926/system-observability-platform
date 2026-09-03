from flask import Flask,jsonify,render_template
from api.metrics import metrics_bp
from api.status import status_bp
from api.anomaly import anomaly_bp,set_model
from database.database import create_Table,create_index
from ai.ai_analytics import train_Model
from database.history import get_training_data

import time

create_Table()
create_index()

rawData=get_training_data()
model=train_Model(rawData)
set_model(model)

app=Flask(__name__,
          template_folder="web/templates",
          static_folder="web/static"
          )

app.register_blueprint(metrics_bp)
app.register_blueprint(status_bp)
app.register_blueprint(anomaly_bp)

# Server check
@app.route("/",methods=["GET"])

def home():
    return render_template("index.html")

# Error handling 
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success":False,
        "error":"RESOURCE_DOESNT_EXIST",
        "timestamp":time.time(),
        "message":"The requested endpoint does not exist"
    }),404

@app.errorhandler(500)
def page_crashed_error(error):
    return jsonify({
        "success":False,
        "error":"INTERNAL_SERVER_ERROR",
        "timestamp":time.time(),
        "message":"An unexpected internal server error occured"

    }),500

# CORS Policy ---> Not using CORS Policy beacuse using teh same SERVER !
#@app.after_request
#def apply_cors(response):
#    response.headers["Access-Control-Allow-Origin"]="*"
#    response.headers["Access-Control-Allow-Methods"]="GET,POST,OPTIONS"
#    response.headers["Access-Control-Allow-Headers"]="Content-Type,Authorization"

#    return response


if __name__=="__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )