"""
Azure Minecraft Dashboard - Flask Application
Manages Azure VM and Minecraft Bedrock server lifecycle
"""

import os
import logging
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import subprocess

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Azure Configuration
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
AZURE_RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP')
AZURE_VM_NAME = os.getenv('AZURE_VM_NAME')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')

# Basic Auth Credentials
AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'password')

# Minecraft Configuration
MINECRAFT_SCREEN_NAME = os.getenv('MINECRAFT_SCREEN_NAME', 'minecraft')
MINECRAFT_STOP_DELAY = int(os.getenv('MINECRAFT_STOP_DELAY', '5'))


def check_auth(username, password):
    """Verify basic auth credentials."""
    return username == AUTH_USERNAME and password == AUTH_PASSWORD


def authenticate():
    """Send authentication challenge."""
    return jsonify({'message': 'Authentication required'}), 401, {
        'WWW-Authenticate': 'Basic realm="Minecraft Dashboard"'
    }


def require_auth(f):
    """Decorator to require basic authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated_function


def get_compute_client():
    """Initialize Azure Compute Management Client."""
    try:
        credential = ClientSecretCredential(
            tenant_id=AZURE_TENANT_ID,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET
        )
        return ComputeManagementClient(credential, AZURE_SUBSCRIPTION_ID)
    except Exception as e:
        logger.error(f"Failed to initialize Azure client: {e}")
        raise


def get_vm_status():
    """Get current VM status from Azure."""
    try:
        client = get_compute_client()
        vm = client.virtual_machines.get(AZURE_RESOURCE_GROUP, AZURE_VM_NAME)
        
        # Get instance view for power state
        instance_view = client.virtual_machines.instance_view(
            AZURE_RESOURCE_GROUP, AZURE_VM_NAME
        )
        
        # Parse power state from statuses
        power_state = 'Unknown'
        for status in instance_view.statuses:
            if status.code.startswith('PowerState/'):
                power_state = status.code.split('/')[-1]
                break
        
        return {
            'status': 'success',
            'power_state': power_state,
            'vm_name': AZURE_VM_NAME,
            'resource_group': AZURE_RESOURCE_GROUP
        }
    except Exception as e:
        logger.error(f"Error getting VM status: {e}")
        return {'status': 'error', 'message': str(e)}


def stop_minecraft_server():
    """Send stop command to Minecraft server via screen."""
    try:
        # Send stop command to screen session
        command = f"screen -S {MINECRAFT_SCREEN_NAME} -X stuff 'stop\\n'"
        subprocess.run(command, shell=True, check=True)
        logger.info("Minecraft stop command sent")
        
        # Wait for graceful shutdown
        import time
        time.sleep(MINECRAFT_STOP_DELAY)
        return True
    except Exception as e:
        logger.error(f"Failed to stop Minecraft server: {e}")
        return False


def start_vm():
    """Start the Azure Virtual Machine."""
    try:
        client = get_compute_client()
        operation = client.virtual_machines.begin_start(
            AZURE_RESOURCE_GROUP, AZURE_VM_NAME
        )
        operation.wait()
        logger.info(f"VM {AZURE_VM_NAME} started successfully")
        return {'status': 'success', 'message': 'VM start initiated'}
    except Exception as e:
        logger.error(f"Failed to start VM: {e}")
        return {'status': 'error', 'message': str(e)}


def stop_vm():
    """Stop the Azure Virtual Machine."""
    try:
        client = get_compute_client()
        operation = client.virtual_machines.begin_power_off(
            AZURE_RESOURCE_GROUP, AZURE_VM_NAME
        )
        operation.wait()
        logger.info(f"VM {AZURE_VM_NAME} stopped successfully")
        return {'status': 'success', 'message': 'VM stopped'}
    except Exception as e:
        logger.error(f"Failed to stop VM: {e}")
        return {'status': 'error', 'message': str(e)}


# Routes

@app.route('/')
@require_auth
def dashboard():
    """Serve the main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/status')
@require_auth
def api_status():
    """Get current VM status."""
    return jsonify(get_vm_status())


@app.route('/api/start', methods=['POST'])
@require_auth
def api_start():
    """Start the VM."""
    result = start_vm()
    return jsonify(result), 200 if result['status'] == 'success' else 400


@app.route('/api/stop', methods=['POST'])
@require_auth
def api_stop():
    """Stop the Minecraft server and VM."""
    # First, attempt to gracefully stop Minecraft
    minecraft_stopped = stop_minecraft_server()
    
    if minecraft_stopped:
        result = stop_vm()
        result['minecraft_stopped'] = True
    else:
        result = {
            'status': 'warning',
            'message': 'Minecraft stop command sent but VM shutdown skipped',
            'minecraft_stopped': False
        }
    
    return jsonify(result), 200 if result['status'] in ['success', 'warning'] else 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}")
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server - use production WSGI server in production
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
