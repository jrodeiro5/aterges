# Supabase MCP Server Configurations

## Windows Configuration
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
        "SUPABASE_ACCESS_TOKEN": "YOUR_PERSONAL_ACCESS_TOKEN_HERE"
      }
    }
  }
}
```

## macOS/Linux Configuration
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--read-only",
        "--project-ref=zsmnqwjeeknohsumhmlx"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "YOUR_PERSONAL_ACCESS_TOKEN_HERE"
      }
    }
  }
}
```

## Key Differences

- **Windows**: Uses `"command": "cmd"` with `"/c", "npx"` in args
- **macOS/Linux**: Uses `"command": "npx"` directly

## Project Details
- **Project Ref**: `zsmnqwjeeknohsumhmlx`
- **Supabase URL**: `https://zsmnqwjeeknohsumhmlx.supabase.co`
