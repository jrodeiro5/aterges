# Supabase MCP Server Setup Guide

## Overview
This guide helps you set up the Supabase MCP server for better database management in Claude Desktop.

## Configuration Details

### Project Reference
- **Your Project Ref**: `zsmnqwjeeknohsumhmlx` (extracted from your Supabase URL)
- **Your Supabase URL**: `https://zsmnqwjeeknohsumhmlx.supabase.co`
- **Platform**: Windows (using `cmd /c npx` format)

### Steps to Complete Setup

1. **Ensure Node.js and NPX are in PATH**:
   ```cmd
   # Check if npm is available
   npm config get prefix
   
   # If npm is not found, add Node.js to PATH
   # Replace <path-to-node> with the actual path from npm config get prefix
   setx PATH "%PATH%;<path-to-node>"
   ```

2. **Get Supabase Personal Access Token**:
   - Visit: https://supabase.com/dashboard/account/tokens
   - Click "Generate new token"
   - Name: "MCP Server Access"
   - Permissions: Read-only recommended for safety
   - Copy the generated token

3. **Update Claude Desktop Configuration**:
   - Open: `%APPDATA%\Claude\claude_desktop_config.json`
   - Copy the contents of `claude_desktop_config_with_supabase.json`
   - Replace `YOUR_PERSONAL_ACCESS_TOKEN_HERE` with your actual token
   - **Note**: This configuration is Windows-specific (uses `cmd /c npx`)

4. **Restart Claude Desktop**:
   - Close Claude Desktop completely
   - Reopen to load the new MCP server configuration

## Configuration File Location
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

## What This Enables

With the Supabase MCP server, you'll be able to:
- Query your database directly from Claude
- Inspect table schemas
- View data without leaving the conversation
- Get insights into your database structure
- Monitor database health and performance

## Security Notes

- The `--read-only` flag ensures no accidental writes
- Use minimal permissions on your access token
- Keep your access token secure and don't commit it to version control

## Usage Examples

Once configured, you can ask Claude to:
- "Show me the structure of my profiles table"
- "How many users are registered in my database?"
- "What's the schema for my conversations table?"
- "Check if there are any recent integrations added"

## Troubleshooting

- **Token Issues**: Regenerate token if authentication fails
- **Connection Issues**: Verify project-ref matches your Supabase URL
- **Permission Issues**: Ensure token has sufficient read permissions
