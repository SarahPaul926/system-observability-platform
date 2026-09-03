from flask import Blueprint, jsonify
import time

status_bp=Blueprint('status_bp',__name__,url_prefix='/api')

# System health check 
@status_bp.route("/health_status",methods=["GET"])
def get_statusUpdate():
    payload={"status":"HEALTHY","engine_epoch":time.time(),"upstream":"CONNECTED"}
    return jsonify(payload), 200