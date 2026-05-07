/**
 * Azure Minecraft Dashboard - Frontend Script
 * Handles UI interactions and API communication
 */

// Configuration
const STATUS_CHECK_INTERVAL = 10000; // 10 seconds
const API_BASE = '/api';

// State management
let statusCheckTimer;
let isOperationInProgress = false;

/**
 * Initialize the dashboard on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    statusCheckTimer = setInterval(fetchStatus, STATUS_CHECK_INTERVAL);
});

/**
 * Fetch current server status from API
 */
async function fetchStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        
        if (response.status === 401) {
            showMessage('Authentication required. Please refresh and log in again.', 'danger');
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        updateStatusUI(data);
    } catch (error) {
        console.error('Error fetching status:', error);
        updateStatusUI({ status: 'error', message: 'Failed to fetch status' });
    }
}

/**
 * Update the UI based on server status
 */
function updateStatusUI(data) {
    const statusText = document.getElementById('statusText');
    const vmStatus = document.getElementById('vmStatus');
    const vmName = document.getElementById('vmName');
    const statusIndicator = document.querySelector('.status-indicator');
    const statusSpinner = document.getElementById('statusSpinner');
    
    if (data.status === 'error') {
        statusText.textContent = 'Error: ' + (data.message || 'Unknown error');
        statusIndicator.classList.remove('online', 'offline');
        vmStatus.textContent = 'Error';
        vmStatus.className = 'badge bg-danger';
        statusSpinner.style.display = 'none';
        return;
    }

    // Update power state
    const powerState = data.power_state || 'Unknown';
    const isOnline = powerState.toLowerCase() === 'running';
    
    statusText.textContent = isOnline ? '🟢 Server Online' : '🔴 Server Offline';
    statusIndicator.classList.remove('online', 'offline');
    statusIndicator.classList.add(isOnline ? 'online' : 'offline');
    
    // Update badge
    vmStatus.textContent = powerState;
    vmStatus.className = isOnline ? 'badge bg-success' : 'badge bg-danger';
    
    // Update VM name
    vmName.textContent = data.vm_name || 'Unknown';
    
    // Hide spinner
    statusSpinner.style.display = 'none';
    
    // Update button states
    updateButtonStates(isOnline);
}

/**
 * Enable/disable buttons based on server state
 */
function updateButtonStates(isOnline) {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    if (isOperationInProgress) {
        startBtn.disabled = true;
        stopBtn.disabled = true;
    } else {
        startBtn.disabled = isOnline;
        stopBtn.disabled = !isOnline;
    }
}

/**
 * Start the server
 */
async function startServer() {
    if (isOperationInProgress) return;
    
    isOperationInProgress = true;
    const startBtn = document.getElementById('startBtn');
    const startSpinner = document.getElementById('startSpinner');
    
    startBtn.disabled = true;
    startSpinner.style.display = 'inline-block';
    
    try {
        const response = await fetch(`${API_BASE}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            showMessage('Authentication required. Please refresh and log in again.', 'danger');
            return;
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            showMessage('✅ Server start initiated. It may take a few moments to boot...', 'success');
            // Refresh status after a delay
            setTimeout(fetchStatus, 5000);
        } else {
            showMessage('❌ Error starting server: ' + (data.message || 'Unknown error'), 'danger');
        }
    } catch (error) {
        console.error('Error starting server:', error);
        showMessage('❌ Failed to start server. Check console for details.', 'danger');
    } finally {
        isOperationInProgress = false;
        startBtn.disabled = false;
        startSpinner.style.display = 'none';
        fetchStatus();
    }
}

/**
 * Stop the server
 */
async function stopServer() {
    if (isOperationInProgress) return;
    
    // Confirmation dialog
    if (!confirm('Are you sure you want to stop the Minecraft server and shutdown the VM? This may cause data loss if players are connected.')) {
        return;
    }
    
    isOperationInProgress = true;
    const stopBtn = document.getElementById('stopBtn');
    const stopSpinner = document.getElementById('stopSpinner');
    
    stopBtn.disabled = true;
    stopSpinner.style.display = 'inline-block';
    
    try {
        const response = await fetch(`${API_BASE}/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            showMessage('Authentication required. Please refresh and log in again.', 'danger');
            return;
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            showMessage('✅ Server stopped successfully. VM is shutting down...', 'success');
        } else if (data.status === 'warning') {
            showMessage('⚠️ ' + (data.message || 'Server stop completed with warnings'), 'warning');
        } else {
            showMessage('❌ Error stopping server: ' + (data.message || 'Unknown error'), 'danger');
        }
        
        // Refresh status after a delay
        setTimeout(fetchStatus, 3000);
    } catch (error) {
        console.error('Error stopping server:', error);
        showMessage('❌ Failed to stop server. Check console for details.', 'danger');
    } finally {
        isOperationInProgress = false;
        stopBtn.disabled = false;
        stopSpinner.style.display = 'none';
        fetchStatus();
    }
}

/**
 * Display a message to the user
 */
function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('actionMessage');
    messageDiv.textContent = message;
    messageDiv.className = `alert alert-${type}`;
    messageDiv.style.display = 'block';
    
    // Auto-hide after 8 seconds (unless it's an error)
    const duration = type === 'danger' ? 12000 : 8000;
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, duration);
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    clearInterval(statusCheckTimer);
});
