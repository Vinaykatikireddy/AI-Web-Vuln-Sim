# Deployment Guide

This guide provides instructions for deploying the AI-Powered Web Application Attack Simulation Platform in various environments.

## Prerequisites

Before deploying, ensure you have the following:

- Docker and Docker Compose installed
- A server with at least 4GB RAM and 2 CPU cores
- A domain name (optional)
- SSL certificates (optional but recommended)
- Administrative access to the server

## Deployment Options

### 1. Local Development Environment

For development and testing purposes, use the provided `docker-compose.yml` file:

```bash
cd /path/to/attack-simulation-platform
# Create the .env file from the example

cp backend/.env.example backend/.env
# Edit the .env file with appropriate values
nano backend/.env

# Start the application
sudo docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api

### 2. Production Deployment on a Single Server

For a production deployment on a single server:

1. **Update Configuration Files**

   Update the `backend/.env` file with production values:
   ```bash
   # Database configuration
   DATABASE_URL=postgresql://produser:strongpassword@localhost:5432/attack_simulation
   
   # JWT configuration
   SECRET_KEY=your-production-super-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   # AI Configuration
   AI_API_KEY=your-production-ai-api-key
   
   ```

2. **Set Up SSL Certificates**

   Create a directory for SSL certificates:
   ```bash
   mkdir -p ~/ssl
   
   # Place your SSL certificates in this directory
   # Add your .crt and .key files
   ```

3. **Update Nginx Configuration**

   Update `docker/nginx/nginx.conf` to include SSL configuration:
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /etc/nginx/ssl/fullchain.pem;
       ssl_certificate_key /etc/nginx/ssl/privkey.pem;
       
       # Security headers
       add_header Strict-Transport-Security "max-age=63072000" always;
       add_header X-Frame-Options "SAMEORIGIN";
       add_header X-Content-Type-Options "nosniff";
       add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://your-domain.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:;";
       
       # Proxy requests to backend API
       location /api/ {
           proxy_pass http://backend:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 300;
       }
       
       # Serve frontend
       location / {
           proxy_pass http://frontend;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   
   # Redirect HTTP to HTTPS
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   ```

4. **Deploy with Docker Compose**

   ```bash
   cd /path/to/attack-simulation-platform
   sudo docker-compose up -d
   ```

5. **Verify Deployment**

   Check that all containers are running:
   ```bash
   sudo docker-compose ps
   ```

   Test the application:
   ```bash
   curl -k https://your-domain.com/health
   ```

### 3. Cloud Deployment (AWS, GCP, Azure)

For cloud deployment, we recommend using a managed Kubernetes service:

#### AWS EKS (Elastic Kubernetes Service)

1. **Create EKS Cluster**
   ```bash
   # Using eksctl
   eksctl create cluster --name attack-simulation --region us-west-2 --nodes 3
   ```

2. **Deploy Helm Charts** (if available) or Kubernetes manifests

   Create `k8s/` directory with deployment manifests:
   - `postgres-deployment.yaml`
   - `redis-deployment.yaml`
   - `backend-deployment.yaml`
   - `frontend-deployment.yaml`
   - `nginx-deployment.yaml`
   - `ingress.yaml`

3. **Apply Deployments**
   ```bash
   kubectl apply -f k8s/
   ```

4. **Set up Load Balancer**
   ```bash
   # Create a LoadBalancer service for Nginx
   kubectl expose deployment nginx-deployment --type=LoadBalancer --name=nginx-lb --port=80 --target-port=80
   ```

5. **Set up Ingress** (for SSL termination)
   ```bash
   # Create an Ingress resource
   kubectl apply -f ingress.yaml
   ```

#### Google Cloud GKE (Google Kubernetes Engine)

Similar to EKS, but with GKE-specific commands:

```bash
# Create GKE cluster
gcloud container clusters create attack-simulation --zone=us-central1-a --num-nodes=3

# Configure kubectl
gcloud container clusters get-credentials attack-simulation --zone=us-central1-a

# Deploy using kubectl
kubectl apply -f k8s/
```

### 4. Container Registry Integration

For CI/CD pipelines, set up a container registry:

#### Docker Hub

1. **Build and push images**:
   ```bash
   # Build backend image
   docker build -t your-username/attack-simulation-backend:latest backend/
   
   # Push to Docker Hub
   docker push your-username/attack-simulation-backend:latest
   
   # Build frontend image
   docker build -t your-username/attack-simulation-frontend:latest frontend/
   
   # Push to Docker Hub
   docker push your-username/attack-simulation-frontend:latest
   ```

2. **Update docker-compose.yml to use images**:
   ```yaml
   backend:
     image: your-username/attack-simulation-backend:latest
   
   frontend:
     image: your-username/attack-simulation-frontend:latest
   ```

#### AWS ECR (Elastic Container Registry)

1. **Create ECR repository**:
   ```bash
   aws ecr create-repository --repository-name attack-simulation-backend
   aws ecr create-repository --repository-name attack-simulation-frontend
   ```

2. **Authenticate Docker**:
   ```bash
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-west-2.amazonaws.com
   ```

3. **Build and push images**:
   ```bash
   # Backend
   docker build -t your-account-id.dkr.ecr.us-west-2.amazonaws.com/attack-simulation-backend:latest backend/
   docker push your-account-id.dkr.ecr.us-west-2.amazonaws.com/attack-simulation-backend:latest
   
   # Frontend
   docker build -t your-account-id.dkr.ecr.us-west-2.amazonaws.com/attack-simulation-frontend:latest frontend/
   docker push your-account-id.dkr.ecr.us-west-2.amazonaws.com/attack-simulation-frontend:latest
   ```

## Backup Strategy

Regular backups are essential for production deployments:

### Database Backups

```bash
# PostgreSQL backup
pg_dump -h localhost -U user -d attack_simulation > attack_simulation_$(date +%Y%m%d_%H%M%S).sql

# Redis backup (AOF file)
cp /var/lib/redis/dump.rdb /backups/redis_dump_$(date +%Y%m%d_%H%M%S).rdb

# Schedule with cron (daily at 2:30 AM)
30 2 * * * pg_dump -h localhost -U user -d attack_simulation > /backups/attack_simulation_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

### File System Backups

```bash
# Backup all critical files and configurations

tar -czf /backups/attack-simulation-$(date +%Y%m%d_%H%M%S).tar.gz \
  /path/to/attack-simulation-platform/backend/ \
  /path/to/attack-simulation-platform/frontend/ \
  /path/to/attack-simulation-platform/docker/
```

## Monitoring and Alerting

Set up monitoring to ensure system health:

### Basic Monitoring

```bash
# Check container status
sudo docker-compose ps

# Check logs
sudo docker-compose logs backend

# Check if service is responding
curl http://localhost:8000/health
```

### Prometheus and Grafana (Recommended)

1. **Deploy Prometheus**:
   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'backend'
       static_configs:
         - targets: ['backend:8000']
     - job_name: 'nginx'
       static_configs:
         - targets: ['nginx:80']
   ```

2. **Deploy Grafana**:
   ```yaml
   # grafana-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: grafana
   spec:
     replicas: 1
     template:
       spec:
         containers:
         - name: grafana
           image: grafana/grafana:latest
           ports:
           - containerPort: 3000
   ```

3. **Set up alerts** for:
   - Container restarts
   - High CPU/memory usage
   - HTTP 5xx errors
   - Database connection failures

## Security Hardening

### Network Security

- Limit network exposure
- Use network policies to restrict container communication
- Only expose necessary ports to the internet

### Container Security

- Run containers as non-root users
- Use read-only filesystems where possible
- Limit container capabilities
- Scan images for vulnerabilities

### Application Security

- Use HTTPS for all connections
- Set secure headers
- Implement rate limiting
- Use strong password policies
- Regularly update dependencies

## Maintenance

### Updates

1. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

2. **Rebuild images**:
   ```bash
   docker-compose build
   ```

3. **Restart containers**:
   ```bash
   docker-compose down && docker-compose up -d
   ```

### Log Rotation

Configure log rotation to prevent disk space exhaustion:

```bash
# Edit /etc/logrotate.d/docker
/path/to/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

### Database Maintenance

```bash
# Clean up old data (keep last 6 months)
psql -h localhost -U user -d attack_simulation -c "DELETE FROM logs WHERE timestamp < NOW() - INTERVAL '6 months';"

# Vacuum database
psql -h localhost -U user -d attack_simulation -c "VACUUM ANALYZE;"
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Containers won't start | Check `docker-compose logs` for error messages |
| Database connection failed | Verify credentials and network connectivity |
| Frontend not loading | Check browser console for JavaScript errors |
| API returns 500 errors | Check backend logs for stack traces |
| SSL certificate errors | Ensure certificates are in the right location and permissions are correct |

### Debugging Steps

1. **Check container status**:
   ```bash
   docker-compose ps
   ```

2. **Inspect specific container logs**:
   ```bash
   docker-compose logs backend
   ```

3. **Test database connectivity**:
   ```bash
   psql -h localhost -U user -d attack_simulation
   ```

4. **Test API endpoints**:
   ```bash
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/api/auth/register \
        -H "Content-Type: application/json" \
        -d '{"username":"test","email":"test@example.com","password":"password123"}'
   ```

5. **Test frontend connectivity**:
   ```bash
   curl http://localhost:3000
   ```

## Recovery Procedures

### System Recovery

1. **Stop all containers**:
   ```bash
   docker-compose stop
   ```

2. **Restore database**:
   ```bash
   psql -h localhost -U user -d attack_simulation < attack_simulation_YYYYMMDD_HHMMSS.sql
   ```

3. **Restore files**:
   ```bash
   tar -xzf /backups/attack-simulation-YYYYMMDD_HHMMSS.tar.gz -C /
   ```

4. **Restart containers**:
   ```bash
   docker-compose up -d
   ```

### Data Recovery

For data recovery scenarios:

1. **Check backups**:
   ```bash
   ls -la /backups/
   ```

2. **Verify backup integrity**:
   ```bash
   # For PostgreSQL
   head -n 10 attack_simulation_*.sql
   
   # For Redis
   redis-cli --rdb dump.rdb
   ```

3. **Execute recovery** using the appropriate procedure for your specific backup type

## Support

For additional support with deployment:

- Check our [documentation](https://github.com/your-username/attack-simulation-platform/blob/main/docs/)
- Join our community forum
- Report issues on GitHub
- Contact support@attack-simulation-platform.com

Remember: This is an educational platform designed for secure testing environments. Never use it to attack third-party systems or production environments.