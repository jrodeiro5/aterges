# Complete Supabase MCP Setup for Windows

## Quick Setup Commands

### 1. Check Node.js PATH
```cmd
npm config get prefix
```
**Example output**: `C:\Users\jrodeiro\AppData\Roaming\npm`

### 2. Add to PATH (if needed)
```cmd
setx PATH "%PATH%;C:\Users\jrodeiro\AppData\Roaming\npm"
```
*Replace with your actual npm prefix path*

### 3. Get Your Supabase Token
Visit: https://supabase.com/dashboard/account/tokens
- Generate new token
- Copy the token value

### 4. Edit Claude Desktop Config
**File Location**: `%APPDATA%\Claude\claude_desktop_config.json`

**To open directly**:
```cmd
notepad %APPDATA%\Claude\claude_desktop_config.json
```

### 5. Configuration Template
```json
{
  "mcpServers": {
    "supabase": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--read-only",
        "--project-ref=zsmnqwjeeknohsumhmlx"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "YOUR_ACTUAL_TOKEN_HERE"
      }
    }
  }
}
```

### 6. Replace Values
- Replace `YOUR_ACTUAL_TOKEN_HERE` with your Supabase personal access token
- The project-ref `zsmnqwjeeknohsumhmlx` is already correct for your project

### 7. Restart Claude Desktop
- Close Claude Desktop completely
- Reopen to activate the Supabase MCP server

## Verification
Once configured, you should be able to ask:
- "Show me my Supabase database tables"
- "What's the structure of my profiles table?"
- "How many users are in my database?"

## Troubleshooting
- **NPX not found**: Ensure Node.js is in PATH
- **Token errors**: Verify token permissions and validity
- **Connection issues**: Check project-ref matches your Supabase URL
