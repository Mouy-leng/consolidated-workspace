#!/usr/bin/env python3
"""
JetBrains Integration Setup Script for GenX_FX
This script sets up connections between JetBrains IDEs and GitHub/GitLab/Gitpod
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class JetBrainsIntegration:
    def __init__(self):
        self.home_dir = Path.home()
        self.ssh_dir = self.home_dir / ".ssh"
        self.project_dir = Path(__file__).parent
        
    def setup_git_authentication(self, github_token=None):
        """Setup Git authentication with GitHub token"""
        print("🔧 Setting up Git authentication...")
        
        # Configure Git user (update these with your details)
        subprocess.run(["git", "config", "--global", "user.name", "GenX_FX_Admin"], 
                      cwd=self.project_dir, check=False)
        subprocess.run(["git", "config", "--global", "user.email", "admin@genx-fx.com"], 
                      cwd=self.project_dir, check=False)
        
        if github_token:
            # Store GitHub token for HTTPS authentication
            git_credentials = f"https://oauth2:{github_token}@github.com"
            subprocess.run(["git", "config", "--global", "credential.helper", "store"], 
                          check=False)
            
            # Create credentials file
            credentials_file = self.home_dir / ".git-credentials"
            with open(credentials_file, "w") as f:
                f.write(git_credentials + "\\n")
            
            print("✅ Git authentication configured with GitHub token")
        else:
            print("⚠️  GitHub token not provided. Manual configuration needed.")
            
    def setup_ssh_agent(self):
        """Setup and start SSH agent"""
        print("🔑 Setting up SSH agent...")
        
        try:
            # Start SSH agent (Windows)
            result = subprocess.run(["ssh-agent"], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("✅ SSH agent started")
                
                # Add the SSH key
                ssh_key_path = self.ssh_dir / "genx_fx_deploy"
                subprocess.run(["ssh-add", str(ssh_key_path)], check=False)
                print(f"✅ Added SSH key: {ssh_key_path}")
            else:
                print("⚠️  Could not start SSH agent automatically")
                
        except Exception as e:
            print(f"⚠️  SSH agent setup issue: {e}")
    
    def generate_jetbrains_config(self):
        """Generate JetBrains IDE configuration files"""
        print("🎨 Generating JetBrains IDE configurations...")
        
        # Create JetBrains config directory
        jetbrains_config_dir = self.project_dir / ".idea"
        jetbrains_config_dir.mkdir(exist_ok=True)
        
        # VCS configuration
        vcs_xml = jetbrains_config_dir / "vcs.xml"
        vcs_config = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="VcsDirectoryMappings">
    <mapping directory="" vcs="Git" />
  </component>
  <component name="GitSharedSettings">
    <option name="synchronizeBranchProtectionRules" value="false" />
  </component>
</project>'''
        
        with open(vcs_xml, "w") as f:
            f.write(vcs_config)
            
        # Workspace configuration
        workspace_xml = jetbrains_config_dir / "workspace.xml"
        workspace_config = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ChangeListManager">
    <list default="true" id="default" name="Changes" comment="">
      <change beforePath="" afterPath="" />
    </list>
  </component>
  <component name="ProjectViewState">
    <option name="hideEmptyMiddlePackages" value="true" />
    <option name="showLibraryContents" value="true" />
  </component>
  <component name="PropertiesComponent">
    <property name="RunOnceActivity.OpenProjectViewOnStart" value="true" />
    <property name="last_opened_file_path" value="$PROJECT_DIR$" />
  </component>
</project>'''
        
        with open(workspace_xml, "w") as f:
            f.write(workspace_config)
            
        print("✅ JetBrains IDE configuration files created")
    
    def setup_remote_development(self):
        """Setup remote development configurations"""
        print("🌐 Setting up remote development configurations...")
        
        # Create Gitpod configuration
        gitpod_yml = self.project_dir / ".gitpod.yml"
        if not gitpod_yml.exists():
            gitpod_config = '''# GitPod Configuration for GenX_FX
image:
  file: .gitpod.Dockerfile

ports:
  - port: 8000
    onOpen: open-browser
  - port: 5000
    onOpen: open-browser

tasks:
  - name: Setup Environment
    init: |
      echo "Setting up GenX_FX development environment..."
      pip install -r requirements.txt
      python setup.py develop
    command: |
      echo "GenX_FX development environment ready!"
      
vscode:
  extensions:
    - ms-python.python
    - ms-python.pylint
    - ms-python.black-formatter
    - ms-vscode.powershell
'''
            
            with open(gitpod_yml, "w") as f:
                f.write(gitpod_config)
                
        print("✅ Gitpod configuration created")
    
    def display_setup_instructions(self):
        """Display setup instructions for manual steps"""
        print("\\n" + "="*60)
        print("🚀 JETBRAINS INTEGRATION SETUP INSTRUCTIONS")
        print("="*60)
        
        print("\\n1. 📋 SSH PUBLIC KEY (Add to GitHub/GitLab):")
        print("-" * 50)
        ssh_pub_key = self.ssh_dir / "genx_fx_deploy.pub"
        if ssh_pub_key.exists():
            with open(ssh_pub_key, "r") as f:
                print(f.read().strip())
        
        print("\\n2. 🔑 GITHUB TOKEN SETUP:")
        print("-" * 30)
        print("• Go to GitHub Settings > Developer settings > Personal access tokens")
        print("• Create a new token with these scopes:")
        print("  - repo (full repository access)")
        print("  - workflow (update GitHub Action workflows)")
        print("  - admin:repo_hook (repository hooks)")
        print("• Copy the token and add it to your secret file")
        
        print("\\n3. 🎨 JETBRAINS IDE SETUP:")
        print("-" * 30)
        print("• Open your JetBrains IDE (IntelliJ IDEA, PyCharm, etc.)")
        print("• File > Open > Select this project folder")
        print("• Go to File > Settings > Version Control > Git")
        print("• Set SSH executable path and test connection")
        print("• Go to File > Settings > Version Control > GitHub")
        print("• Add your GitHub account using token authentication")
        
        print("\\n4. 🌐 GITPOD INTEGRATION:")
        print("-" * 30)
        print("• Install Gitpod browser extension")
        print("• Go to your GitHub repository")
        print("• Click 'Gitpod' button to open in cloud IDE")
        print("• Gitpod will use .gitpod.yml configuration")
        
        print("\\n5. 🔧 GITLAB INTEGRATION (if needed):")
        print("-" * 30)
        print("• Go to GitLab Settings > Access Tokens")
        print("• Create token with api, read_repository, write_repository scopes")
        print("• Add to JetBrains IDE: File > Settings > Version Control > GitLab")
        
        print("\\n6. 💰 COST OPTIMIZATION FEATURES:")
        print("-" * 30)
        print("• Use Gitpod with usage-based billing")
        print("• Configure auto-sleep for development environments")
        print("• Use JetBrains Gateway for remote development")
        print("• Enable code analysis and automated refactoring")
        
        print("\\n" + "="*60)
        print("🎯 Next steps: Add tokens to secret file and run setup again")
        print("="*60)
    
    def run_setup(self, github_token=None, gitlab_token=None, gitpod_token=None):
        """Run the complete setup process"""
        print("🚀 Starting JetBrains Integration Setup...")
        print(f"📁 Project Directory: {self.project_dir}")
        print(f"🏠 Home Directory: {self.home_dir}")
        
        # Setup steps
        self.setup_git_authentication(github_token)
        self.setup_ssh_agent()
        self.generate_jetbrains_config()
        self.setup_remote_development()
        
        # Display instructions
        self.display_setup_instructions()
        
        print("\\n✅ JetBrains integration setup completed!")
        return True

def load_tokens_from_file(token_file_path):
    """Load tokens from the secret file"""
    tokens = {}
    try:
        if os.path.exists(token_file_path):
            with open(token_file_path, 'r') as f:
                content = f.read().strip()
                if content and len(content) > 5:  # Basic validation
                    # Try to parse as JSON first
                    try:
                        tokens = json.loads(content)
                    except json.JSONDecodeError:
                        # Parse as simple key=value format
                        for line in content.split('\\n'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                tokens[key.strip()] = value.strip()
                    
        print(f"📄 Loaded {len(tokens)} tokens from secret file")
    except Exception as e:
        print(f"⚠️  Could not load tokens from {token_file_path}: {e}")
    
    return tokens

def main():
    """Main function"""
    print("GenX_FX JetBrains Integration Setup")
    print("=" * 40)
    
    # Initialize setup
    integration = JetBrainsIntegration()
    
    # Try to load tokens from secret file
    secret_file_path = r"E:\Code\\Dropbox\\OneDrive\\Desktop\\secret for Warp.txt"
    tokens = load_tokens_from_file(secret_file_path)
    
    # Extract tokens
    github_token = tokens.get('GITHUB_TOKEN') or tokens.get('github_token')
    gitlab_token = tokens.get('GITLAB_TOKEN') or tokens.get('gitlab_token')  
    gitpod_token = tokens.get('GITPOD_TOKEN') or tokens.get('gitpod_token')
    
    # Run setup
    success = integration.run_setup(
        github_token=github_token,
        gitlab_token=gitlab_token,
        gitpod_token=gitpod_token
    )
    
    if success:
        print("\\n🎉 Setup completed successfully!")
        print("💡 Remember to add your SSH public key to GitHub/GitLab")
        print("🔑 Update your secret file with the required tokens")
    else:
        print("\\n❌ Setup encountered issues")
        sys.exit(1)

if __name__ == "__main__":
    main()