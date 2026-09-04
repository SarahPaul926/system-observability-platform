'''
Create a blueprint in a separate module.
Define routes inside that blueprint.
Register the blueprint in the main application.

'''

from flask import Blueprint,jsonify
from flask import request
from core.serializer import TelemetrySeralize
from database.database import save_metric
from database.analytics import system_analysis
from database.profiling import profiling_Time
from database.maintenance import delete_OldData
from ai.ai_analytics import predict_live,diagnose_system,ai_summary
from ai.process_info import get_process,system_snapshot
from ai.LLM_reasoning import analyze_incident 
from api.anomaly import get_model
from database.history import getHistory
import time
import threading

ai_investigation_running = False
ai_lock = threading.Lock()
ai_latest_result=None

latest_metric = None
latest_anomaly = 0
latest_summary = None
latest_issues = []
connection_time=None

# Creating  a blueprint Instance
metrics_bp = Blueprint('metrics_bp', __name__, url_prefix='/api/metrics')

@metrics_bp.route("/telemetry",methods=["POST"]) 
def receive_telemetry():
    start=time.time()
    global ai_investigation_running
    global ai_latest_result
    global latest_metric
    global latest_anomaly
    global latest_summary
    global latest_issues
    global connection_time
    try:
        print("1. Capturing telemetry")
        connection_time=time.time()
        metric_payload=request.get_json()
        if not metric_payload:
            return jsonify({
                "success":False,
                "error":"No Telemetry data received"
                }),400
        print("2. Telemetry captured")
        serialized_meterics=TelemetrySeralize.convert_data(metric_payload)
        print("3. Metrics serialized")
        live_vector=[
            serialized_meterics['cpu']['cpu_usage'],
            serialized_meterics['ram']['percent'],
            serialized_meterics['disk']['disk_usage'],
            serialized_meterics['network_activity']['network_sent'],
            serialized_meterics['network_activity']['network_received']
        ]
        anomaly=predict_live(get_model(),live_vector)
        print("4. Anomaly:", anomaly)
        issues=diagnose_system(serialized_meterics)
        print("5. Issues diagnosed")
        summary=ai_summary(anomaly,issues)
        print("6. Summary created")
        save_metric(serialized_meterics,anomaly)
        print("7. Metric saved")
        latest_metric = serialized_meterics
        latest_anomaly= anomaly
        latest_summary = summary
        latest_issues = issues
        if anomaly == -1:
            print("8. ANOMALY DETECTED → Getting processes")
            with ai_lock:
                if not ai_investigation_running:
                    ai_investigation_running = True
                    ai_latest_result = None
                    print("9. Starting background AI investigation")
                    thread=threading.Thread(target=run_ai,args=(serialized_meterics,anomaly,issues),name="AI-Investigation")
                    thread.start()
                else:
                    print("9. AI investigation already running")
        else:
            print("8. System normal")
        return jsonify({
            "success":True,
            "time_taken":round((time.time()-start)*1000,2),
            "metric":serialized_meterics,
            "anomaly":anomaly,
            "summary":summary,
            "issues":issues,
            "database":"Done"
            }), 200
    except Exception as e:
            return jsonify({
                        "success":False,
                        "error":str(e)
                        }), 500

def run_ai(meteric,anomaly,issues):
    global ai_investigation_running
    global ai_latest_result
    try:
        print("Background Ai starting")
        process=get_process()
        incident=system_snapshot(meteric,anomaly,issues,process)
        ai_analysis=analyze_incident(incident)
        with ai_lock:
            ai_latest_result=ai_analysis
        print("Background AI Result stored")
    except Exception as e:
        print("BACKGROUND AI ERROR:", e)
    finally:
        with ai_lock:
            ai_investigation_running = False
        print("BACKGROUND AI investigation finished")

@metrics_bp.route("/ai",methods=["GET"])
def get_ai():
    with ai_lock:
        if ai_investigation_running:
            return jsonify({
                "ai": {
                    "summary":
                        "Anomaly detected. AI investigation is running....",
                    "root_cause":
                        "Investigation in progress.",
                    "contributors": [],
                    "recommendations": [],
                    "confidence": 0.0
                },
                "status":"running",
                "success":True
            }),200

        if ai_latest_result is not None:
            return jsonify({
                "status":"complete",
                "success":True,
                "ai":ai_latest_result
            }),200
        
        return jsonify({
                "ai": {
                    "summary":
                        "System is healthy. No anomaly detected.",
                    "root_cause":
                        "No investigation required.",
                    "contributors": [],
                    "recommendations": [],
                    "confidence": 1.0
                },
                "success":True,
                "status":"healthy"
        })

@metrics_bp.route("/live",methods=["GET"])
def get_metrics():
    start=time.time()
    try:
        if latest_metric is None:
            return jsonify({
                "success":False,
                "connection":False,
                "message":"No Telemetry received from the agent."
            }),404
        if time.time()-connection_time > 15:
            return jsonify({
                "success":False,
                "connection":False,
                "message":"No recent activities."
            }),404
        
        return jsonify({
            "success":True,
            "time_taken":round((time.time()-start)*1000,2),
            "metric":latest_metric,
            "anomaly":latest_anomaly,
            "summary":latest_summary,
            "issues":latest_issues,
            "connection":True,
            "database":"Done"
            }), 200

    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e)
                    }), 500

@metrics_bp.route("/summary",methods=["GET"])
def meterics_summary():
    try:
        systemData=system_analysis()
        return jsonify({
            "success":True,
            "summary":systemData
        })
    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e),
                    "analysis":"Something went wrong!"
                    }), 500

@metrics_bp.route("/history",methods=["GET"])
def meterics_history():
    try:
        start=time.time()
        start_time=float(request.args.get("start"))
        end_time=float(request.args.get("end"))
        page=int(request.args.get("page",1))
        limit=int(request.args.get("limit",20))
        offset=(page-1)*limit
        data=getHistory(start_time,end_time,limit,offset)
        duration=time.time()-start
        return jsonify({
            "success":True,
            "history":data,
            "page":page,
            "limit":limit,
            "count":len(data),
            "duration":duration
        }),200
    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e),
                    "analysis":"hey i am wrong!"
                    }), 500
    
@metrics_bp.route("/profile",methods=["GET"])
def get_profiling_time():
    try:
        result=profiling_Time()
        return jsonify({
            "success":True,
            "results":result
        })
    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e),
                    "analysis":"Something went wrong!"
                    }),500

@metrics_bp.route("/cleanup",methods=["GET"])
def delete_Rows():
    try:
        result=delete_OldData()
        return jsonify({
            "success":True,
            "results":result
        }),200
    except Exception as e:
        return jsonify({
                    "success":False,
                    "error":str(e),
                    }),500



