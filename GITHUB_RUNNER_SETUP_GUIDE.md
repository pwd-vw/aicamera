# GitHub Actions Runner Setup Guide for LPR Server

This guide will help you configure this machine (`lprserver.tail605477.ts.net`) as a GitHub Actions runner to automatically trigger deployments to your edge devices when you push to the main branch.

## Prerequisites

1. **GitHub Personal Access Token** with these permissions:
   - `repo` (Full control of private repositories)
   - `admin:org` (Full control of organizations and teams)
   - `workflow` (Update GitHub Action workflows)

2. **Repository Access**: Ensure you have admin access to `popwandee/aicamera`

## Step 1: Generate GitHub Personal Access Token

1. Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "LPR Server Runner Token"
4. Select these scopes:
   - `repo` (Full control of private repositories)
   - `admin:org` (Full control of organizations and teams)
   - `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

## Step 2: Configure GitHub Repository Variables

In your GitHub repository (`popwandee/aicamera`):

1. Go to Settings → Secrets and variables → Actions
2. Add these **Variables** (not secrets):
   - `ENABLE_SERVER_DEPLOYMENT` = `true`
   - `ENABLE_EDGE_DEPLOYMENT` = `true`

3. Add these **Secrets**:
   - `SSH_PRIVATE_KEY` = Your SSH private key for connecting to edge devices
   - `SERVER_USER` = `lpruser` (or your server username)
   - `EDGE_USER` = `camuser` (or your edge device username)

## Step 3: Run the Setup Script

```bash
# Make the script executable
chmod +x scripts/setup-github-runner.sh

# Run the setup script
./scripts/setup-github-runner.sh
```

When prompted, enter:
- **Repository**: `popwandee/aicamera`
- **GitHub Token**: The token you generated in Step 1
- **Runner Name**: `lprserver-runner`
- **Labels**: `self-hosted,linux,lpr-server`

## Step 4: Verify Runner Setup

```bash
# Check runner status
github-runner-status

# Check runner logs
github-runner-logs

# Check if runner is online in GitHub
# Go to: https://github.com/popwandee/aicamera/settings/actions/runners
```

## Step 5: Test the Workflow

1. Make a small change to your code
2. Push to the main branch:
   ```bash
   git add .
   git commit -m "Test deployment workflow"
   git push origin main
   ```
3. Check the workflow execution at: https://github.com/popwandee/aicamera/actions

## Step 6: Monitor Deployments

The workflow will automatically:
1. Build and test your code
2. Deploy to LPR Server (`lprserver.tail605477.ts.net`)
3. Deploy to all edge devices:
   - `aicamera1.tail605477.ts.net`
   - `aicamera2.tail605477.ts.net`
   - `aicamera3.tail605477.ts.net`
   - `aicamera4.tail605477.ts.net`
   - `aicamera5.tail605477.ts.net`

## Management Commands

After setup, you can use these commands:

```bash
# Check runner status
github-runner-status

# Restart runner
github-runner-restart

# View logs
github-runner-logs

# Update runner (with new token)
github-runner-update <new-token>
```

## Troubleshooting

### Runner Not Starting
```bash
# Check service status
sudo systemctl status github-runner

# Check logs
sudo journalctl -u github-runner -f

# Restart service
sudo systemctl restart github-runner
```

### Permission Issues
```bash
# Fix permissions
sudo chown -R github-runner:github-runner /opt/github-runner
sudo chmod +x /opt/github-runner/*.sh
```

### Token Issues
If you get "Not Found" errors, your token may have expired or lacks permissions:
1. Generate a new token with the required permissions
2. Update the runner: `github-runner-update <new-token>`

## Security Notes

1. Keep your GitHub token secure
2. The runner runs as a dedicated user (`github-runner`)
3. SSH keys are stored securely in GitHub secrets
4. All deployments use Tailscale for secure communication

## Network Configuration

Your setup uses Tailscale for secure communication:
- **Domain**: `tail605477.ts.net`
- **LPR Server**: `lprserver.tail605477.ts.net`
- **Edge Devices**: `aicamera1-5.tail605477.ts.net`

All deployments happen over the secure Tailscale network.

## Next Steps

Once the runner is set up:

1. **Test a deployment**: Make a small change and push to main
2. **Monitor the first deployment**: Check logs and service status
3. **Verify all edge devices**: Ensure all 5 cameras receive updates
4. **Set up monitoring**: Consider setting up alerts for failed deployments

## Support

If you encounter issues:
1. Check the runner logs: `github-runner-logs`
2. Check GitHub Actions logs: https://github.com/popwandee/aicamera/actions
3. Verify SSH connectivity to edge devices
4. Check Tailscale network status
