from flask import Blueprint,jsonify,request
from ai.ai_analytics import predict_live
anomaly_bp=Blueprint('anomaly_bp', __name__, url_prefix='/ai/anomaly')
model=None

def set_model(trained_model):
    global model
    model=trained_model

def get_model():
    return model

@anomaly_bp.route("/status",methods=["POST"])
def process_live_inference():
    data=request.get_json()
    live_vector=[
        data["cpu_usage"],
        data["ram_percent"],
        data["disk_usage"],
        data["network_sent"],
        data["network_received"]
    ]
    prediction=predict_live(model,live_vector)
    return jsonify({
        "anomaly_flag":prediction
    }),200


