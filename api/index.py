from http.server import BaseHTTPRequestHandler
import json
import os
import statistics

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_POST(self):
        """Handle POST request to calculate metrics"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Parse request parameters
            regions = request_data.get('regions', [])
            threshold_ms = request_data.get('threshold_ms', 180)
            
            # Load telemetry data
            telemetry_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'telemetry.json')
            with open(telemetry_path, 'r') as f:
                telemetry_data = json.load(f)
            
            # Calculate metrics per region
            results = {}
            for region in regions:
                # Filter data for this region
                region_data = [entry for entry in telemetry_data if entry['region'] == region]
                
                if not region_data:
                    results[region] = {
                        'avg_latency': 0,
                        'p95_latency': 0,
                        'avg_uptime': 0,
                        'breaches': 0
                    }
                    continue
                
                # Extract latency and uptime values
                latencies = [entry['latency_ms'] for entry in region_data]
                uptimes = [entry.get('uptime_pct', entry.get('uptime', 0) * 100) for entry in region_data]
                
                # Calculate metrics
                avg_latency = statistics.mean(latencies)
                p95_latency = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 2 else latencies[0]
                avg_uptime = statistics.mean(uptimes)
                breaches = sum(1 for latency in latencies if latency > threshold_ms)
                
                results[region] = {
                    'avg_latency': avg_latency,
                    'p95_latency': p95_latency,
                    'avg_uptime': avg_uptime,
                    'breaches': breaches
                }
            
            # Send response with CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(results)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode('utf-8'))
