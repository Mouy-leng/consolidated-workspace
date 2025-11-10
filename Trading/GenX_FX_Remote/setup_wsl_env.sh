#!/bin/bash
# GenX_FX WSL Environment Setup

export GENX_PROJECT_ROOT=/mnt/c/Users/lengk/GenX_FX_Remote
export GENX_ENVIRONMENT=dev
export GENX_WSL_MODE=true

# Add to .bashrc if not already present
if ! grep -q "GENX_PROJECT_ROOT" ~/.bashrc; then
    echo "# GenX_FX Environment" >> ~/.bashrc
    echo "export GENX_PROJECT_ROOT=/mnt/c/Users/lengk/GenX_FX_Remote" >> ~/.bashrc  
    echo "export GENX_ENVIRONMENT=dev" >> ~/.bashrc
    echo "export GENX_WSL_MODE=true" >> ~/.bashrc
    echo "cd ~/genx_fx" >> ~/.bashrc
fi

# Install Python dependencies in WSL if needed
if command -v python3 >/dev/null 2>&1; then
    cd ~/genx_fx
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --user
    fi
fi

echo "WSL environment setup complete"
