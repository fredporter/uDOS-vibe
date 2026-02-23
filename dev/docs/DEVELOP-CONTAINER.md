# Developing uDOS Containers

Containers are isolated application environments that package code with their dependencies. This guide covers creating, testing, and distributing container definitions for uDOS.

---

## What is a Container?

A uDOS container is:

- ✅ **Self-contained environment** with its own dependencies
- ✅ **Portable** across different systems
- ✅ **Versioned** with clear specifications
- ✅ **Integrable** with uDOS services

**Examples:** Web servers, databases, development environments, tools

---

## Quick Start

### 1. Create Container Directory

```bash
cd dev
mkdir my-container
cd my-container
```

### 2. Create Container Definition

Create `container.json`:

```json
{
  "name": "my-container",
  "version": "1.0.0",
  "description": "My custom container",
  "author": "Your Name",
  "license": "MIT",
  "type": "container",
  "base": {
    "image": "python:3.11-alpine",
    "platform": "linux/amd64"
  },
  "dependencies": {
    "system": ["git", "curl"],
    "python": ["flask", "requests"]
  },
  "lifecycle": {
    "setup": "scripts/setup.sh",
    "start": "scripts/start.sh",
    "stop": "scripts/stop.sh",
    "health": "scripts/health.sh"
  },
  "ports": [
    {"container": 5000, "host": 5000, "protocol": "tcp"}
  ],
  "volumes": [
    {"container": "/app/data", "host": "./data"}
  ],
  "environment": {
    "APP_ENV": "production",
    "LOG_LEVEL": "info"
  }
}
```

### 3. Create Lifecycle Scripts

Create `scripts/setup.sh`:

```bash
#!/bin/bash
# Container setup (run once)

echo "Setting up container..."

# Install dependencies
pip install -r requirements.txt

# Initialize data
mkdir -p /app/data

echo "Setup complete"
```

Create `scripts/start.sh`:

```bash
#!/bin/bash
# Start the container service

echo "Starting application..."

# Run the app
python app.py
```

Create `scripts/health.sh`:

```bash
#!/bin/bash
# Health check

curl -f http://localhost:5000/health || exit 1
```

### 4. Add Application Code

Create `app.py`:

```python
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def hello():
    return jsonify({"message": "Hello from my container!"}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

Create `requirements.txt`:

```
flask==3.0.0
requests==2.31.0
```

---

## Container Structure

```
dev/my-container/
├── container.json      # Container definition (required)
├── app.py             # Main application code
├── requirements.txt   # Python dependencies
├── scripts/           # Lifecycle scripts
│   ├── setup.sh       # One-time setup
│   ├── start.sh       # Start service
│   ├── stop.sh        # Stop service
│   └── health.sh      # Health check
├── config/            # Configuration files
│   └── default.conf
├── data/              # Data directory (gitignored)
├── logs/              # Log directory (gitignored)
├── tests/             # Tests
│   └── test_app.py
└── README.md          # Documentation
```

---

## Container Definition Schema

```json
{
  "name": "string (required)",
  "version": "semver (required)",
  "description": "string (required)",
  "author": "string (optional)",
  "license": "string (optional)",
  "type": "container",
  
  "base": {
    "image": "docker_image:tag",
    "platform": "linux/amd64 | linux/arm64"
  },
  
  "dependencies": {
    "system": ["package1", "package2"],
    "python": ["package1>=1.0.0"],
    "node": ["package1@1.0.0"]
  },
  
  "lifecycle": {
    "setup": "path/to/setup.sh",
    "start": "path/to/start.sh",
    "stop": "path/to/stop.sh",
    "health": "path/to/health.sh",
    "backup": "path/to/backup.sh",
    "restore": "path/to/restore.sh"
  },
  
  "ports": [
    {
      "container": 8080,
      "host": 8080,
      "protocol": "tcp|udp"
    }
  ],
  
  "volumes": [
    {
      "container": "/app/data",
      "host": "./data",
      "readonly": false
    }
  ],
  
  "environment": {
    "KEY": "value"
  },
  
  "secrets": [
    "API_KEY",
    "DATABASE_URL"
  ],
  
  "resources": {
    "cpu": "1.0",
    "memory": "512M",
    "storage": "1G"
  }
}
```

---

## Lifecycle Hooks

### Setup Hook (`setup.sh`)

**When called:** Once, when container is first created  
**Purpose:** Install dependencies, initialize data

```bash
#!/bin/bash
set -e

echo "Installing dependencies..."
apk add --no-cache git curl

echo "Setting up Python environment..."
pip install -r requirements.txt

echo "Initializing database..."
python scripts/init_db.py

echo "Setup complete"
```

### Start Hook (`start.sh`)

**When called:** Every time container starts  
**Purpose:** Start the main service

```bash
#!/bin/bash
set -e

echo "Starting service..."

# Validate config
if [ ! -f /app/config/app.conf ]; then
    echo "Config not found, using defaults"
    cp /app/config/default.conf /app/config/app.conf
fi

# Start the app
exec python app.py
```

**Important:** Use `exec` for the main process so signals are handled correctly.

### Stop Hook (`stop.sh`)

**When called:** When container is stopping  
**Purpose:** Graceful shutdown

```bash
#!/bin/bash
set -e

echo "Stopping service..."

# Send shutdown signal
if [ -f /app/app.pid ]; then
    kill -TERM $(cat /app/app.pid)
    
    # Wait for shutdown
    for i in {1..30}; do
        if ! kill -0 $(cat /app/app.pid) 2>/dev/null; then
            echo "Service stopped"
            exit 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    kill -KILL $(cat /app/app.pid) 2>/dev/null || true
fi

echo "Stop complete"
```

### Health Hook (`health.sh`)

**When called:** Periodically to check container health  
**Purpose:** Report service status

```bash
#!/bin/bash

# Check if service is running
if ! pgrep -f "python app.py" > /dev/null; then
    echo "Service not running"
    exit 1
fi

# Check HTTP endpoint
curl -sf http://localhost:5000/health > /dev/null || exit 1

# Check disk space
USED=$(df /app/data | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$USED" -gt 90 ]; then
    echo "Disk space critical: ${USED}%"
    exit 1
fi

echo "Healthy"
exit 0
```

---

## Testing Your Container

### 1. Local Testing

```bash
# Build and run locally
cd dev/my-container

# Run setup
bash scripts/setup.sh

# Start service
bash scripts/start.sh &

# Test health
bash scripts/health.sh

# Test functionality
curl http://localhost:5000/
```

### 2. Integration with uDOS

```bash
# From uDOS root
python -m core.containers.manager install dev/my-container

# Start the container
python -m core.containers.manager start my-container

# Check status
python -m core.containers.manager status my-container

# View logs
python -m core.containers.manager logs my-container

# Stop
python -m core.containers.manager stop my-container
```

### 3. Unit Tests

Create `tests/test_app.py`:

```python
import unittest
from app import app

class TestMyContainer(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
    
    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_hello(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)

if __name__ == '__main__':
    unittest.main()
```

Run tests:

```bash
python -m pytest tests/
```

---

## Common Patterns

### Web Service Container

```json
{
  "name": "web-service",
  "base": {"image": "python:3.11-alpine"},
  "dependencies": {
    "python": ["flask", "gunicorn"]
  },
  "ports": [{"container": 8000, "host": 8000}],
  "lifecycle": {
    "start": "gunicorn -b 0.0.0.0:8000 app:app"
  }
}
```

### Background Worker Container

```json
{
  "name": "worker",
  "base": {"image": "python:3.11-alpine"},
  "dependencies": {
    "python": ["celery", "redis"]
  },
  "environment": {
    "REDIS_URL": "redis://localhost:6379/0"
  },
  "lifecycle": {
    "start": "celery -A tasks worker --loglevel=info"
  }
}
```

### Database Container

```json
{
  "name": "postgres",
  "base": {"image": "postgres:16-alpine"},
  "ports": [{"container": 5432, "host": 5432}],
  "volumes": [
    {"container": "/var/lib/postgresql/data", "host": "./pgdata"}
  ],
  "secrets": ["POSTGRES_PASSWORD"],
  "lifecycle": {
    "health": "pg_isready -U postgres"
  }
}
```

---

## Distribution

### 1. Package Your Container

```bash
cd dev
tar -czf my-container-1.0.0.tar.gz my-container/
```

### 2. Create Documentation

Ensure your `README.md` includes:

- **Description** — What the container does
- **Requirements** — System dependencies
- **Installation** — How to install
- **Configuration** — Environment variables, secrets
- **Usage** — How to run and interact
- **Troubleshooting** — Common issues

### 3. Distribution Options

- **GitHub Release:** Tag and publish
- **Container Registry:** Push to Docker Hub or similar
- **uDOS Catalog:** Submit if available
- **Direct Share:** Provide archive for manual installation

---

## Best Practices

✅ **Use Alpine base** — Smaller, faster images  
✅ **Handle signals** — Use `exec` in start scripts  
✅ **Health checks** — Always provide health hook  
✅ **Log to stdout** — Don't write logs to files  
✅ **Fail fast** — Use `set -e` in shell scripts  
✅ **Document secrets** — List required environment variables  
✅ **Test thoroughly** — Unit + integration tests  

❌ **Don't store state** — Use volumes for persistence  
❌ **Don't hardcode URLs** — Use environment variables  
❌ **Don't run as root** — Create and use app user  
❌ **Don't bundle secrets** — Inject at runtime  

---

## Next Steps

✅ **Review examples:** `/dev/examples/containers/`  
✅ **Build an extension:** [DEVELOP-EXTENSION.md](DEVELOP-EXTENSION.md)  
✅ **Read scaffold guide:** [SCAFFOLD-STRUCTURE.md](SCAFFOLD-STRUCTURE.md)  

---

**Back to:** [Wiki home](README.md)
