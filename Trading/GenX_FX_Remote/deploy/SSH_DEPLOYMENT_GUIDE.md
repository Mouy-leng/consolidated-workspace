# Deploying the FastAPI Application with SSH

This guide outlines the process of deploying the GenX FX FastAPI application to a virtual private server (VPS) using SSH, without Docker. This approach gives you more control over the environment.

## Table of Contents

1.  [Prerequisites](#prerequisites)
2.  [Server Setup](#server-setup)
3.  [Code Deployment](#code-deployment)
4.  [Application Setup](#application-setup)
5.  [Running the Application with Gunicorn](#running-the-application-with-gunicorn)
6.  [Setting up Nginx as a Reverse Proxy](#setting-up-nginx-as-a-reverse-proxy)
7.  [Process Management with systemd](#process-management-with-systemd)

---

## 1. Prerequisites

Before you begin, you will need:

*   A VPS running a recent version of Ubuntu (e.g., 20.04 or 22.04).
*   A user with `sudo` privileges.
*   An SSH key pair for secure login.

## 2. Server Setup

First, connect to your server via SSH. Then, update the system and install the necessary packages.

```bash
# Connect to your server
ssh your_user@your_server_ip

# Update package lists and upgrade packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Python, pip, and venv
# This project uses Python 3.9+
sudo apt-get install -y python3.9 python3.9-venv python3-pip git

# Verify installations
python3.9 --version
pip3 --version
```

## 3. Code Deployment

Next, clone the project repository from GitHub to your server.

```bash
# Navigate to your home directory
cd ~

# Clone the repository
# Note: This uses the HTTPS URL. For a private repository, you would
# need to add your server's SSH key to your GitHub account.
git clone https://github.com/Mouy-leng/GenX_FX.git

# Navigate into the project directory
cd GenX_FX
```

## 4. Application Setup

Now, set up a virtual environment for the application and install the required dependencies.

```bash
# Create a virtual environment
python3.9 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Now your shell prompt should be prefixed with (venv).

# Upgrade pip
pip install --upgrade pip

# Install the project dependencies
pip install -r requirements.txt

# Install Gunicorn, a production-grade WSGI server
pip install gunicorn
```

## 5. Running the Application with Gunicorn

With the dependencies installed, you can now run the FastAPI application using Gunicorn. Gunicorn will manage the Uvicorn workers to handle requests.

```bash
# Make sure you are in the GenX_FX directory and the virtual environment is active.

# The command to start Gunicorn:
# -w 4: Use 4 worker processes. Adjust based on your server's CPU cores.
# -k uvicorn.workers.UvicornWorker: Use Uvicorn for the worker class.
# api.main:app: The path to your FastAPI application instance.
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
```

Your API should now be running. You can test this by opening a new terminal, SSHing into your server, and running `curl http://localhost:8000`.

However, this process will stop when you close your terminal. For a production setup, you should run Gunicorn as a service, which is covered in the `systemd` section.

## 6. Setting up Nginx as a Reverse Proxy

A reverse proxy like Nginx sits in front of your application and forwards client requests to it. This is useful for load balancing, SSL termination, and serving static files.

### Step 1: Install Nginx

```bash
sudo apt-get install -y nginx
```

### Step 2: Create an Nginx Configuration File

Create a new Nginx configuration file for your application.

```bash
sudo nano /etc/nginx/sites-available/genx_fx
```

Paste the following configuration into the file. Replace `your_domain_or_ip` with your server's domain name or IP address.

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 3: Enable the Configuration

Link your new configuration file to the `sites-enabled` directory to activate it.

```bash
sudo ln -s /etc/nginx/sites-available/genx_fx /etc/nginx/sites-enabled/
```

### Step 4: Test and Restart Nginx

Test your Nginx configuration for syntax errors and then restart the service.

```bash
sudo nginx -t
sudo systemctl restart nginx
```

Now, you should be able to access your application by navigating to `http://your_domain_or_ip` in your browser.

## 7. Process Management with systemd

To ensure your application runs continuously, even after a reboot, you should run Gunicorn as a `systemd` service.

### Step 1: Create a systemd Service File

Create a new service file for your application.

```bash
sudo nano /etc/systemd/system/genx_fx.service
```

Paste the following configuration into the file. Remember to replace `your_user` with your actual username on the server.

```ini
[Unit]
Description=Gunicorn instance to serve GenX FX
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/home/your_user/GenX_FX
Environment="PATH=/home/your_user/GenX_FX/venv/bin"
ExecStart=/home/your_user/GenX_FX/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

### Step 2: Start and Enable the Service

Now, start the service and enable it to start on boot.

```bash
sudo systemctl start genx_fx
sudo systemctl enable genx_fx
```

### Step 3: Check the Status

You can check the status of the service to make sure it's running correctly.

```bash
sudo systemctl status genx_fx
```

Congratulations! Your GenX FX FastAPI application is now deployed and running as a service on your server.
