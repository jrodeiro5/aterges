# Examples Directory

This directory contains example configuration files for the Aterges platform. **NEVER commit real credentials to git!**

## Files

### `google-ecosystem-service-account.example.json`
Example Google Cloud service account credentials file. To use:
1. Copy this file to `google-ecosystem-service-account.json`
2. Replace all placeholder values with your real Google Cloud credentials
3. The real file is ignored by git for security

### `example_MCP_config_Claude_Desktop.example.json`
Example MCP (Model Context Protocol) configuration for Claude Desktop. To use:
1. Copy this file to `example_MCP_config_Claude_Desktop.json` 
2. Replace placeholder values:
   - `YOUR_USERNAME` with your actual Windows username
   - `ghp_YOUR_GITHUB_TOKEN_HERE` with your GitHub Personal Access Token
   - `fc-YOUR_FIRECRAWL_API_KEY_HERE` with your Firecrawl API key
   - `your-google-cloud-project-id` with your Google Cloud project ID
3. The real file is ignored by git for security

## Security Note

All files ending in `.example.json` are safe templates. Files with real credentials are automatically ignored by git through `.gitignore` patterns.

**Never commit files containing:**
- API keys
- Private keys  
- Personal access tokens
- Service account credentials
- Database passwords
- Any other sensitive information