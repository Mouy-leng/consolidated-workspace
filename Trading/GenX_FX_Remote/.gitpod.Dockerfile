FROM gitpod/workspace-full

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js and dependencies for the frontend
COPY package.json package-lock.json ./
RUN nvm install 20 && nvm use 20 && npm install

# Copy the rest of the application code
COPY . .
