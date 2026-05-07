# 🎮 SETUP GUIDE FOR BEGINNERS

This guide is super simple! Follow each step carefully.

## Step 1: Install Python (if you don't have it)

1. Go to https://www.python.org/downloads/
2. Click the big download button
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH"
5. Click "Install Now"

## Step 2: Download This Project

1. Go to the GitHub repository
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to a folder (like `C:\Users\YourName\Desktop\minecraft-dashboard`)

## Step 3: Open Command Line in Your Project Folder

**On Windows:**
- Open the folder where you extracted the project
- Right-click in the empty space
- Click "Open in Terminal" (or "Open PowerShell window here")

**On Mac/Linux:**
- Open Terminal
- Type: `cd /path/to/minecraft-dashboard`

## Step 4: Create a Virtual Environment

Copy and paste this command:

```bash
python -m venv venv
```

Then run:

**On Windows:**
```bash
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
source venv/bin/activate
```

If it works, you'll see `(venv)` at the start of each line in your terminal.

## Step 5: Install Requirements

Copy and paste:

```bash
pip install -r requirements.txt
```

Wait for it to finish. This downloads the code libraries you need.

## Step 6: Get Your Azure Information

You need 6 pieces of information from Azure. Follow these steps exactly:

### Get Subscription ID:
1. Go to https://portal.azure.com/
2. Search for "Subscriptions" at the top
3. Copy your Subscription ID somewhere safe

### Get Resource Group and VM Name:
1. Search for "Virtual Machines"
2. Find your Minecraft server VM
3. Write down:
   - **VM Name** (the name of your machine)
   - **Resource Group** (shown next to the VM name)

### Create a Service Principal (This gives the dashboard permission to control your VM):

1. Install Azure CLI from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
2. Open a new terminal/command prompt
3. Type: `az login` and log in with your Azure account
4. Copy this command and replace the parts in `{brackets}`:

```bash
az ad sp create-for-rbac --name "MinecraftDashboard" --role "Virtual Machine Contributor" --scopes /subscriptions/{your-subscription-id}/resourceGroups/{your-resource-group-name}
```

**Example** (with fake values):
```bash
az ad sp create-for-rbac --name "MinecraftDashboard" --role "Virtual Machine Contributor" --scopes /subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/my-minecraft-rg
```

5. You'll get output that looks like this:
```json
{
  "appId": "abc123...",
  "displayName": "MinecraftDashboard",
  "password": "xyz789...",
  "tenant": "def456..."
}
```

**Save these values!** You'll need them next.

## Step 7: Create the .env File

1. In your project folder, find `.env.example`
2. Make a copy and rename it to `.env`
3. Open `.env` with a text editor (Notepad is fine)
4. Fill in the values from the previous steps:

```env
AZURE_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789012
AZURE_RESOURCE_GROUP=my-minecraft-rg
AZURE_VM_NAME=minecraft-bedrock-vm
AZURE_CLIENT_ID=abc123...
AZURE_CLIENT_SECRET=xyz789...
AZURE_TENANT_ID=def456...
MINECRAFT_SCREEN_NAME=minecraft
AUTH_USERNAME=admin
AUTH_PASSWORD=mypassword123
```

**Change these:**
- `AUTH_USERNAME` - your login username (default: admin)
- `AUTH_PASSWORD` - your login password (change from "mypassword123")

## Step 8: Start the Dashboard

In your terminal (with `(venv)` showing), type:

```bash
python app.py
```

You should see:
```
Running on http://127.0.0.1:5000
```

## Step 9: Open the Dashboard

1. Open your web browser
2. Go to: `http://localhost:5000`
3. Log in with your username and password from `.env`

Done! 🎉

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
- Make sure you ran `pip install -r requirements.txt`
- Make sure `(venv)` is showing in your terminal

### "Unauthorized 401" when logging in
- Check your `AUTH_USERNAME` and `AUTH_PASSWORD` in `.env`
- Make sure there are no extra spaces

### "Azure connection failed"
- Double-check all the values from Step 6 are correct in `.env`
- Make sure you didn't paste extra spaces or quotes

### Still stuck?
- Read the error message carefully
- Copy the error and Google it
- Check that you followed each step exactly

---

## Next Steps

Once it's working:
1. Click "Start Server" to turn on your VM
2. Click "Stop Server" to shut it down safely
3. The status updates every 10 seconds automatically

**Have fun!** 🎮
