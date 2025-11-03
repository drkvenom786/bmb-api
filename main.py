from flask import Flask, jsonify, request
import threading
import time
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ----------------- Security Configuration -----------------
VALID_API_KEYS = {
    "SMS-BOMBER-API-KEY-2024-VENOM-786": True,
    "BACKUP-KEY-2024-SECURE-ACCESS": True
}

# ----------------- Security Middleware -----------------
@app.before_request
def authenticate():
    client_ip = request.remote_addr
    
    # Check API Key (mandatory)
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in VALID_API_KEYS:
        logger.warning(f"🔑 INVALID API KEY from {client_ip}")
        return jsonify({"error": "Invalid API Key"}), 401
    
    logger.info(f"✅ Authenticated request from {client_ip}")

# ----------------- Safe Import Helper -----------------
def safe_import(module_name, func_name):
    try:
        mod = __import__(module_name)
        return getattr(mod, func_name)
    except Exception:
        # fallback dummy function if module not found
        def dummy(mobile_no):
            logger.info(f"{func_name} skipped (module {module_name}.py not found)")
        return dummy

# ----------------- Import All API Modules -----------------
run_apis1 = safe_import("apis1", "run_apis1")
run_apis2 = safe_import("apis2", "run_apis2")
run_apis3 = safe_import("apis3", "run_apis3")
run_apis4 = safe_import("apis4", "run_apis4")
run_apis5 = safe_import("apis5", "run_apis5")
run_apis6 = safe_import("apis6", "run_apis6")
run_apis7 = safe_import("apis7", "run_apis7")
run_apis8 = safe_import("apis8", "run_apis8")
run_apis9 = safe_import("apis9", "run_apis9")
run_apis10 = safe_import("apis10", "run_apis10")

all_apis = [
    run_apis1, run_apis2, run_apis3, run_apis4, run_apis5,
    run_apis6, run_apis7, run_apis8, run_apis9, run_apis10
]

# ----------------- Request Validation -----------------
def validate_mobile_number(mobile_no):
    """Validate mobile number format"""
    if not mobile_no or not isinstance(mobile_no, str):
        return False
    # Basic validation - 10 digits
    return mobile_no.isdigit() and len(mobile_no) == 10

# ----------------- Flask Routes -----------------
@app.route('/num=<mobile_no>', methods=['GET'])
def trigger_apis(mobile_no):
    # Validate mobile number
    if not validate_mobile_number(mobile_no):
        return jsonify({
            "error": "Invalid mobile number format. Must be 10 digits."
        }), 400
    
    client_ip = request.remote_addr
    api_key = request.headers.get('X-API-Key', 'Unknown')
    
    logger.info(f"🚀 Bombing started for {mobile_no} from {client_ip} (API Key: {api_key[:8]}...)")

    # Run each API in separate thread
    def run_api(api_func, number):
        try:
            api_func(number)
            logger.debug(f"API {api_func.__name__} executed successfully for {number}")
        except Exception as e:
            logger.error(f"Error in {api_func.__name__}: {e}")

    for api_func in all_apis:
        threading.Thread(target=run_api, args=(api_func, mobile_no), daemon=True).start()

    return jsonify({
        "status": "Bombing Start",
        "mobile": mobile_no,
        "apis_triggered": len(all_apis),
        "timestamp": time.time()
    })

@app.route('/status', methods=['GET'])
def status():
    """API status endpoint"""
    active_apis = sum(1 for api in all_apis if not api.__name__.startswith('dummy'))
    
    return jsonify({
        "status": "API is running",
        "active_apis": active_apis,
        "total_apis": len(all_apis),
        "security": {
            "api_key_auth": "ENABLED",
            "ip_whitelisting": "DISABLED",
            "rate_limiting": "DISABLED",
            "unlimited_bombing": "ENABLED"
        }
    })

@app.route('/security')
def security_info():
    """Security configuration info"""
    return jsonify({
        "api_keys_configured": len(VALID_API_KEYS),
        "security_level": "API_KEY_ONLY",
        "protection": "API Key Authentication Only",
        "rate_limiting": "DISABLED",
        "ip_restrictions": "DISABLED"
    })

@app.route('/')
def home():
    return jsonify({
        "message": "SMS Bombing API - SECURED",
        "usage": "GET /num=<mobile_number> with X-API-Key header",
        "security": "API Key Authentication Only - No IP Restrictions",
        "endpoints": {
            "bombing": "/num=<mobile_number>",
            "status": "/status",
            "security_info": "/security"
        }
    })

# ----------------- Additional Security Headers -----------------
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Server'] = 'Secure-Bombing-API'
    return response

# ----------------- Error Handlers -----------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized - Invalid API key"}), 401

if __name__ == '__main__':
    print("=" * 60)
    print("🛡️  SECURE SMS Bombing API Starting...")
    print(f"🔑 API Keys: {len(VALID_API_KEYS)} configured")
    print(f"🛡️  Security: API Key Authentication Only")
    print(f"📈 Active APIs: {sum(1 for api in all_apis if not api.__name__.startswith('dummy'))}/{len(all_apis)}")
    print("=" * 60)
    print("🚀 READY: Anyone with API key can access this API!")
    print("=" * 60)
    
    # Get port from environment variable (for Railway/Render) or use default
    port = int(os.environ.get('PORT', 7887))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
