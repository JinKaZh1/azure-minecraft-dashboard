# Azure Minecraft Bedrock Dashboard

A lightweight Flask web dashboard to manage an Azure Virtual Machine running a Minecraft Bedrock server. Control power state and gracefully shutdown the server with a clean, mobile-responsive interface.

## Features

✅ **Power Management**: START and STOP Azure VMs directly from the dashboard
✅ **Graceful Shutdown**: Safely stops the Minecraft server before powering off the VM
✅ **Basic Authentication**: Simple login protection (configurable username/password)
✅ **Real-time Status**: Auto-refreshing server status indicator
✅ **Mobile-Responsive**: Works seamlessly on desktop, tablet, and mobile devices
✅ **Bootstrap UI**: Clean, modern interface with dark mode support

## Prerequisites

- Python 3.8+ installed on your system
- An Azure subscription with an existing Minecraft Bedrock server VM
- Azure Service Principal credentials (see setup instructions below)
- The Minecraft server running in a Linux `screen` session

## Installation

### 1. Clone or download this repository

```bash
git clone <repository-url>
cd azure-minecraft-dashboard
```

### 2. Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Individual packages:**
```bash
pip install Flask==3.0.0
pip install azure-identity==1.14.0
pip install azure-mgmt-compute==33.1.0
pip install python-dotenv==1.0.0
pip install requests==2.31.0
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your Azure credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
AZURE_SUBSCRIPTION_ID=your-subscription-id-here
AZURE_RESOURCE_GROUP=your-resource-group-name
AZURE_VM_NAME=your-vm-name
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
MINECRAFT_SCREEN_NAME=minecraft  # Name of your screen session
AUTH_USERNAME=admin
AUTH_PASSWORD=your-secure-password
```

## Azure Service Principal Setup

To allow the dashboard to control your VM, you need to create an Azure Service Principal and grant it permissions.

### Step 1: Create a Service Principal

```bash
# Login to Azure
az login

# Create a Service Principal
az ad sp create-for-rbac --name "MinecraftDashboard" --role "Virtual Machine Contributor" \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group-name}
```

This will output:
```json
{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "displayName": "MinecraftDashboard",
  "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### Step 2: Extract credentials

From the output above, populate your `.env` file:
- `AZURE_CLIENT_ID` = `appId`
- `AZURE_CLIENT_SECRET` = `password`
- `AZURE_TENANT_ID` = `tenant`
- `AZURE_SUBSCRIPTION_ID` = Your subscription ID (visible in Azure Portal)

### Step 3: Verify permissions

The Service Principal needs these roles:
- **Virtual Machine Contributor** (or **Contributor**)
- Assigned to the resource group containing your VM

## Running the Application

### Development Mode

```bash
export FLASK_ENV=development  # Linux/Mac
# or
set FLASK_ENV=development  # Windows

python app.py
```

The dashboard will be available at `http://localhost:5000`

### Production Mode (Recommended)

Use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use uWSGI:

```bash
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

## Accessing the Dashboard

1. Open your browser to `http://localhost:5000` (or your server's IP)
2. Log in with the credentials from your `.env` file
3. Use the "Start" button to boot the VM
4. Use the "Stop" button to gracefully shutdown Minecraft and power off the VM

**Note**: The status auto-refreshes every 10 seconds.

## Configuration

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `AZURE_SUBSCRIPTION_ID` | Your Azure subscription ID | ✅ Yes |
| `AZURE_RESOURCE_GROUP` | Resource group containing the VM | ✅ Yes |
| `AZURE_VM_NAME` | Name of the Minecraft VM | ✅ Yes |
| `AZURE_CLIENT_ID` | Service Principal client ID | ✅ Yes |
| `AZURE_CLIENT_SECRET` | Service Principal client secret | ✅ Yes |
| `AZURE_TENANT_ID` | Azure tenant ID | ✅ Yes |
| `MINECRAFT_SCREEN_NAME` | Linux screen session name | ⭕ Optional (default: "minecraft") |
| `MINECRAFT_STOP_DELAY` | Seconds to wait before powering off VM | ⭕ Optional (default: 5) |
| `AUTH_USERNAME` | Dashboard login username | ⭕ Optional (default: "admin") |
| `AUTH_PASSWORD` | Dashboard login password | ⭕ Optional (default: "password") |
| `SECRET_KEY` | Flask session secret key | ⭕ Optional (auto-generated) |

## Security Considerations

⚠️ **Important Security Notes:**

1. **Change the default credentials** - Update `AUTH_USERNAME` and `AUTH_PASSWORD` in `.env`
2. **Use HTTPS in production** - Deploy behind a reverse proxy (nginx, Apache) with SSL/TLS
3. **Protect your `.env` file** - Never commit it to version control
4. **Use strong passwords** - Avoid simple credentials
5. **Rotate credentials regularly** - Regenerate your Service Principal password periodically
6. **Limit Service Principal permissions** - Use the "Virtual Machine Contributor" role, not "Owner"
7. **Consider IP whitelisting** - Restrict access to known IPs if possible

## Troubleshooting

### Authentication Errors

**Error**: "401 Unauthorized"
- Verify `AUTH_USERNAME` and `AUTH_PASSWORD` match your `.env` file
- Check that Basic Auth is being sent correctly

### Azure Connection Errors

**Error**: "Failed to initialize Azure client" or "Invalid credentials"
- Verify all Azure credentials in `.env` are correct
- Ensure the Service Principal has "Virtual Machine Contributor" role
- Run `az ad sp show --id <client-id>` to verify the SP exists

### VM Status Not Updating

**Error**: Status shows "Unknown"
- Check network connectivity to Azure APIs
- Verify firewall isn't blocking outbound HTTPS connections

### Minecraft Stop Command Not Working

**Issue**: VM doesn't power off after clicking Stop
- Verify `MINECRAFT_SCREEN_NAME` matches your actual screen session name
- Check the Minecraft server is running: `screen -list`
- Increase `MINECRAFT_STOP_DELAY` if needed

## Deployment Options

### Systemd Service (Ubuntu/Debian)

Create `/etc/systemd/system/minecraft-dashboard.service`:

```ini
[Unit]
Description=Azure Minecraft Dashboard
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/user/azure-minecraft-dashboard
Environment="PATH=/home/user/azure-minecraft-dashboard/venv/bin"
ExecStart=/home/user/azure-minecraft-dashboard/venv/bin/gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable minecraft-dashboard
sudo systemctl start minecraft-dashboard
```

## API Reference

All endpoints require Basic Authentication.

### GET `/api/status`
Returns current VM power state.

### POST `/api/start`
Starts the VM.

### POST `/api/stop`
Stops the Minecraft server and powers off the VM.

## License

This project is provided as-is for personal use.

---

**Happy gaming!** 🎮
