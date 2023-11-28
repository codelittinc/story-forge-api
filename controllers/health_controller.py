from flask import jsonify, request, abort

def index_health():
    return {
        "status": "ok"
    }, 200
