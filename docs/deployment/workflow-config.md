# Workflow Configuration Guide

This document explains how to enable/disable CI/CD workflows during development and production.

## 🚫 **Disable All Workflows (Development)**

### Method 1: GitHub Settings (Recommended)
1. Go to your repository → **Settings** → **Actions** → **General**
2. Under "Actions permissions", select **"Disable actions"**
3. Click **Save**

### Method 2: Repository Variables
1. Go to **Settings** → **Secrets and variables** → **Actions** → **Variables**
2. Add variable: `ENABLE_CI` = `false`
3. Add variable: `ENABLE_EDGE_DEPLOYMENT` = `false`

## ✅ **Enable Workflows (Production)**

### Method 1: GitHub Settings
1. Go to **Settings** → **Actions** → **General**
2. Under "Actions permissions", select **"Allow all actions and reusable workflows"**
3. Click **Save**

### Method 2: Repository Variables
1. Go to **Settings** → **Secrets and variables** → **Actions** → **Variables**
2. Set `ENABLE_CI` = `true`
3. Set `ENABLE_EDGE_DEPLOYMENT` = `true`

## 🔧 **Individual Workflow Control**

### CI/CD Pipeline (`ci.yml`)
- **Variable**: `ENABLE_CI`
- **Values**: `true` (enabled) / `false` (disabled)
- **Default**: `true` (enabled if not set)

### Edge Deployment (`edge-deploy.yml`)
- **Variable**: `ENABLE_EDGE_DEPLOYMENT`
- **Values**: `true` (enabled) / `false` (disabled)
- **Default**: `false` (disabled if not set)

## 🎯 **Development Workflow**

### Phase 1: Development (Workflows Disabled)
```bash
# Workflows are disabled
git push origin main  # No CI/CD runs
```

### Phase 2: Testing (Selective Enable)
```bash
# Enable only CI testing
ENABLE_CI=true
ENABLE_EDGE_DEPLOYMENT=false

git push origin main  # Only tests run, no deployment
```

### Phase 3: Production (Full Enable)
```bash
# Enable everything
ENABLE_CI=true
ENABLE_EDGE_DEPLOYMENT=true

git push origin main  # Full CI/CD pipeline runs
```

## 🚀 **Manual Triggers**

### Manual Edge Deployment
1. Go to **Actions** → **Edge Deployment**
2. Click **"Run workflow"**
3. Check **"Force deployment"** to bypass environment check
4. Click **"Run workflow"**

### Manual CI/CD
1. Go to **Actions** → **CI/CD Pipeline**
2. Click **"Run workflow"**
3. Click **"Run workflow"**

## 📋 **Quick Commands**

### Check Current Status
```bash
# Check if workflows are enabled
curl -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/popwandee/aicamera/actions/variables"
```

### Disable All (Development)
```bash
# Set variables to disable workflows
gh variable set ENABLE_CI --body "false"
gh variable set ENABLE_EDGE_DEPLOYMENT --body "false"
```

### Enable All (Production)
```bash
# Set variables to enable workflows
gh variable set ENABLE_CI --body "true"
gh variable set ENABLE_EDGE_DEPLOYMENT --body "true"
```

## 🔒 **Security Notes**

- **Repository Variables** are visible to all collaborators
- **Secrets** are encrypted and hidden
- Use **Secrets** for sensitive data (SSH keys, passwords)
- Use **Variables** for configuration flags

## 📊 **Workflow Status**

| Workflow | Variable | Development | Production |
|----------|----------|-------------|------------|
| CI/CD Pipeline | `ENABLE_CI` | ❌ Disabled | ✅ Enabled |
| Edge Deployment | `ENABLE_EDGE_DEPLOYMENT` | ❌ Disabled | ✅ Enabled |
| Version Management | None | ✅ Always enabled | ✅ Always enabled |
