# Railway Deployment Guide

This guide will help you deploy your Secre API to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. Git repository (GitHub, GitLab, or Bitbucket)
3. Your project code pushed to the repository

## Step 1: Prepare Your Repository

Your repository is already configured with the necessary Railway files:
- `railway.json` - Railway configuration
- `Procfile` - Process definition
- `.railwayignore` - Files to exclude from deployment

## Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Choose "Deploy from GitHub repo" (or your Git provider)
4. Select your `secre_api` repository
5. Railway will automatically detect it's a Python project

## Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL database
4. Note the `DATABASE_URL` that Railway provides (you'll need this)

## Step 4: Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add these environment variables:

### Required Variables:
```
API_V1_PREFIX=/v1
PROJECT_NAME=Secre API
VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### Security Variables (IMPORTANT - Change these!):
```
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MASTER_API_KEY=your-master-api-key-change-this-in-production
```

### Database:
- Railway automatically provides `DATABASE_URL` - no need to set this manually

## Step 5: Deploy

1. Railway will automatically start building and deploying your project
2. The build process will:
   - Install Python dependencies from `requirements.txt`
   - Build the Docker image
   - Deploy to Railway's infrastructure

## Step 6: Run Database Migrations

After deployment, you need to run the database migrations:

1. Go to your project dashboard
2. Click on your service
3. Go to the "Deployments" tab
4. Click on the latest deployment
5. Go to the "Logs" tab
6. Click "Open Shell" or use the Railway CLI

Run these commands in the shell:
```bash
# Run migrations
alembic upgrade head

# Seed lookup data (optional)
python -c "
from backend.app.db.session import sync_engine
from backend.scripts.init_db import seed_lookup_data
seed_lookup_data(sync_engine)
"
```

## Step 7: Test Your Deployment

1. Railway will provide you with a URL like `https://your-app-name.railway.app`
2. Test the health endpoint: `https://your-app-name.railway.app/health`
3. Test the API docs: `https://your-app-name.railway.app/docs`

## Step 8: Create Your First Tenant and API Key

Use the Railway shell or Railway CLI to create a tenant and API key:

```bash
python -c "
from backend.scripts.create_tenant_and_apikey import create_tenant_and_apikey
tenant_id, api_key = create_tenant_and_apikey('Your Tenant Name')
print(f'Tenant ID: {tenant_id}')
print(f'API Key: {api_key}')
"
```

## Railway CLI (Optional but Recommended)

Install the Railway CLI for easier management:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# View logs
railway logs

# Open shell
railway shell

# Deploy
railway up
```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes (auto-provided) |
| `API_V1_PREFIX` | API version prefix | `/v1` | No |
| `PROJECT_NAME` | Application name | `Secre API` | No |
| `VERSION` | Application version | `1.0.0` | No |
| `ENVIRONMENT` | Environment name | `production` | No |
| `DEBUG` | Debug mode | `false` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `ALGORITHM` | JWT algorithm | `HS256` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` | No |
| `MASTER_API_KEY` | Master API key | - | Yes |

## Troubleshooting

### Common Issues:

1. **Build fails**: Check the build logs in Railway dashboard
2. **Database connection fails**: Verify `DATABASE_URL` is set correctly
3. **Migrations fail**: Run migrations manually in Railway shell
4. **API not responding**: Check if the service is running and healthy

### Useful Commands:

```bash
# Check service status
railway status

# View logs
railway logs --follow

# Open shell
railway shell

# Restart service
railway restart
```

## Security Notes

1. **Change all default secrets** before going to production
2. **Use strong, unique API keys** for each tenant
3. **Enable HTTPS** (Railway provides this automatically)
4. **Monitor your logs** for any suspicious activity
5. **Regularly rotate your secrets**

## Next Steps

1. Set up monitoring and alerting
2. Configure custom domain (optional)
3. Set up automated backups for your database
4. Implement proper logging and monitoring
5. Consider setting up staging environment

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your project logs are available in the Railway dashboard
