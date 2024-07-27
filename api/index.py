import random
import requests
from flask import Flask, request, redirect
from cachetools import TTLCache
from urllib.parse import urlparse, urlunparse

app = Flask(__name__)

# List of backend servers
servers = [
    'https://server1.oilnwine.live',
    'https://server2.oilnwine.live',
    'https://server3.oilnwine.live',
    'https://server4.oilnwine.live'
]

# Cache for server status with a TTL of 30 seconds
server_status_cache = TTLCache(maxsize=100, ttl=30)

def is_server_up(server):
    if server in server_status_cache:
        return server_status_cache[server]
    try:
        response = requests.get(server + "/login", timeout=5)
        is_up = response.status_code == 200
    except requests.RequestException:
        is_up = False
    server_status_cache[server] = is_up
    return is_up

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def load_balancer(path):
    # Filter servers that are up
    available_servers = [server for server in servers if is_server_up(server)]
    
    if not available_servers:
        return "No servers are currently available.", 503

    # Randomly select from available servers
    selected_server = random.choice(available_servers)
    
    # Extract the query string
    query_string = request.query_string.decode('utf-8')
    
    # Build the new URL with the selected server, path, and query string
    new_url = f"{selected_server}/{path}"
    if query_string:
        new_url = f"{new_url}?{query_string}"
    
    # Forward the request to the selected server
    return redirect(new_url, code=307)
