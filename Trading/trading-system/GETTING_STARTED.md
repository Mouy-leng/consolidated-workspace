# 🚀 Getting Started with Your Trading System

This guide provides a step-by-step roadmap to set up, run, and manage your trading system.

## Prerequisites

Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v20.0.0 or higher)
- [npm](https://www.npmjs.com/) (v10.0.0 or higher)
- Windows PowerShell

---

## 🗺️ Roadmap: Step-by-Step Guide

Here is the path to get your system up and running:

### **Step 1: Configure Your Environment**

Your system uses environment variables to manage sensitive information and configurations.

1.  **Create a `.env` file** in the root directory: `c:\Users\lengk\.config\trading-system\.env`.
2.  **Add the following variables** to the `.env` file. You will need to fill in the values based on your AWS, VPS, and other service credentials.

    ```bash
    # AWS Credentials
    AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
    AWS_REGION=YOUR_AWS_REGION

    # VPS (Virtual Private Server) Connection Details
    VPS_HOST=YOUR_VPS_IP_OR_HOSTNAME
    VPS_USER=YOUR_VPS_USERNAME
    VPS_PASSWORD=YOUR_VPS_PASSWORD

    # Microservice Configuration
    PORT=3000
    LOG_LEVEL=info

    # Add any other necessary variables for your trading APIs (e.g., Gemini, AMP)
    GEMINI_API_KEY=YOUR_GEMINI_KEY
    GEMINI_API_SECRET=YOUR_GEMINI_SECRET
    ```

### **Step 2: Install Microservice Dependencies**

The core of your system is a Node.js microservice. You need to install its dependencies.

1.  Open a terminal or PowerShell.
2.  Navigate to the microservice directory:
    ```powershell
    cd c:\Users\lengk\.config\trading-system\trading-microservice
    ```
3.  Run the installation command:
    ```powershell
    npm install
    ```

### **Step 3: Run the Trading System**

Now you can start the system components.

1.  **Load Environment Variables**: Open a new PowerShell window and run `load-env.ps1`. This script loads the variables from your `.env` file into your current session.
    ```powershell
    .\load-env.ps1
    ```
2.  **Start the Microservice**: In the same PowerShell window, start the microservice. It will run in the background.
    ```powershell
    # Navigate to the microservice directory if you aren't already there
    cd c:\Users\lengk\.config\trading-system\trading-microservice

    # Start the server
    npm start
    ```
    You should see output indicating the server is running on the configured port (e.g., `Server running on port 3000`).

### **Step 4: Manage and Monitor Your Devices**

With the system running, you can use the provided PowerShell tools to manage your trading devices.

-   **Device Manager (`device-manager.ps1`)**: Use this for discovering, registering, and synchronizing local devices (e.g., MT5 terminals, USB hardware).
    ```powershell
    # Example: Discover and register all devices
    .\device-manager.ps1 -Action Discover
    .\device-manager.ps1 -Action Register
    ```
-   **Device CLI (`device-cli.ps1`)**: Use this for command-line operations like checking status or forcing a sync.
    ```powershell
    # Example: Get the status of all devices
    .\device-cli.ps1 -Command Get-DeviceStatus

    # Example: Force a sync for a specific device
    .\device-cli.ps1 -Command Sync-Device -DeviceID "DEVICE_ID_HERE"
    ```

---

## ⚙️ System Workflow

Here is a simple text-based graph illustrating how the components work together:

```
+--------------------------+
|   PowerShell Scripts     |
| (device-manager.ps1,     |
|  device-cli.ps1)         |
+-------------+------------+
              |
              |
              v
+-------------+------------+      +------------------------+
|  Trading Microservice    |<---->|   Device Plugins       |
|  (Node.js / Express)     |      |   (mt5-plugin.js,      |
|                          |      |    api-plugin.js)      |
+-------------+------------+      +------------------------+
              |
              |
              v
+-------------+------------+
|      Cloud Services      |
|      (AWS / VPS)         |
+--------------------------+
```

---

## 📋 API Endpoints Quick Reference

The microservice provides the following REST API endpoints for management:

-   `GET /api/v1/devices`: List all registered devices.
-   `GET /api/v1/devices/sync-status`: Get the synchronization status of all devices.
-   `POST /api/v1/devices/register`: Register a new device.
-   `POST /api/v1/devices/:id/sync`: Trigger a synchronization for a specific device.
-   `POST /api/v1/devices/sync-all`: Trigger a synchronization for all devices.
-   `DELETE /api/v1/devices/:id`: Remove a device.

This guide should provide a clear path to getting your trading system operational.
