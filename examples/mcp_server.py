"""
Holistic Google Ecosystem MCP Server
Multi-account support for Google Analytics, BigQuery, Search Console, and Tag Manager
Supports dynamic client switching and cross-account analytics
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from google.cloud import bigquery
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import cost control and client management
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auto_stop_cost_control import track_query_cost, check_server_should_run, check_budget_status
from client_manager import client_manager

# Check if server should run (auto-stop protection)
if not check_server_should_run():
    print("MCP Server blocked - budget limit reached")
    print("Use server-control.bat to reactivate when ready")
    sys.exit(1)

# Global configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')

# Cache for workspace IDs to avoid repeated API calls
_workspace_cache = {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("holistic-google-ecosystem")

# Initialize the MCP server
server = Server("holistic-google-ecosystem")

# Global clients (will be initialized)
bq_client = None
ga_client = None
search_console_service = None
tag_manager_service = None

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available Google ecosystem resources."""
    return [
        types.Resource(
            uri="bigquery://datasets",
            name="BigQuery Datasets",
            description="Available BigQuery datasets in your project",
            mimeType="application/json",
        ),
        types.Resource(
            uri="clients://configurations",
            name="Client Configurations", 
            description="All configured client accounts and properties",
            mimeType="application/json",
        ),
        types.Resource(
            uri="analytics://properties", 
            name="GA4 Properties",
            description="Available Google Analytics 4 properties across all clients",
            mimeType="application/json",
        ),
        types.Resource(
            uri="tagmanager://containers",
            name="GTM Containers",
            description="Available Google Tag Manager containers across all clients",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str:
    """Read specific Google ecosystem resources."""
    uri_str = str(uri)
    
    try:
        if uri_str == "bigquery://datasets":
            datasets = list(bq_client.list_datasets())
            return json.dumps([{
                "dataset_id": dataset.dataset_id,
                "full_name": f"{dataset.project}.{dataset.dataset_id}",
                "location": dataset.location
            } for dataset in datasets])
            
        elif uri_str == "clients://configurations":
            return json.dumps({
                "clients": client_manager.list_clients(),
                "active_client": client_manager.get_active_client_config(),
                "total_clients": len(client_manager.clients)
            })
            
        elif uri_str == "tagmanager://containers":
            accounts = tag_manager_service.accounts().list().execute()
            containers_list = []
            for account in accounts.get('account', []):
                containers = tag_manager_service.accounts().containers().list(
                    parent=account['path']
                ).execute()
                for container in containers.get('container', []):
                    containers_list.append({
                        "container_id": container['containerId'],
                        "name": container['name'],
                        "account_id": container['accountId'],
                        "path": container['path']
                    })
            return json.dumps(containers_list)
            
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
            
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return json.dumps({"error": str(e)})

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Google ecosystem tools."""
    return [
        # Client Management Tools
        types.Tool(
            name="list_clients",
            description="List all configured client accounts and their properties",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="set_active_client",
            description="Switch to a different client account for operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "Client ID to switch to"
                    }
                },
                "required": ["client_id"]
            }
        ),
        types.Tool(
            name="add_client",
            description="Add a new client configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "Unique identifier for the client"
                    },
                    "name": {
                        "type": "string",
                        "description": "Display name for the client"
                    },
                    "ga4_property_id": {
                        "type": "string",
                        "description": "GA4 property ID (format: properties/XXXXXXXXX)"
                    },
                    "gtm_container_id": {
                        "type": "string",
                        "description": "GTM container ID"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the client"
                    }
                },
                "required": ["client_id", "name"]
            }
        ),
        types.Tool(
            name="discover_accounts",
            description="Auto-discover available Google accounts, properties, and containers",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get_suggested_clients",
            description="Get suggested client configurations based on discovered accounts",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # BigQuery Tools
        types.Tool(
            name="query_bigquery",
            description="Execute SQL queries on BigQuery",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    },
                    "max_results": {
                        "type": "integer", 
                        "description": "Maximum number of results to return (default: 100)",
                        "default": 100
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use (uses active client if not specified)"
                    }
                },
                "required": ["sql_query"]
            }
        ),
        
        # Google Analytics Tools
        types.Tool(
            name="get_ga4_report",
            description="Get Google Analytics 4 report data for any property",
            inputSchema={
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "GA4 property ID (format: properties/XXXXXXXXX) - overrides client setting"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string", 
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "dimensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of dimensions (e.g., ['date', 'country'])"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of metrics (e.g., ['sessions', 'pageviews'])"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use (uses active client if not specified)"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        types.Tool(
            name="get_client_ga4_report",
            description="Get GA4 report for the currently active client",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string", 
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "dimensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of dimensions (e.g., ['date', 'country', 'pagePath'])",
                        "default": ["date"]
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of metrics (e.g., ['sessions', 'pageviews', 'users'])",
                        "default": ["sessions", "pageviews"]
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        
        # Google Tag Manager Tools - Complete Suite
        types.Tool(
            name="gtm_list_containers",
            description="List all Google Tag Manager containers accessible to your account",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="gtm_list_tags",
            description="List all tags in a GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path (e.g., 'accounts/123456/containers/123456') or use 'active' for active client"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path"]
            }
        ),
        types.Tool(
            name="gtm_create_tag",
            description="Create a new tag in GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "tag_name": {
                        "type": "string",
                        "description": "Name for the new tag"
                    },
                    "tag_type": {
                        "type": "string",
                        "description": "Tag type (e.g., 'gaawe' for GA4, 'html' for Custom HTML)",
                        "enum": ["gaawe", "html", "gtag", "sp", "gclidw", "cvt_template"]
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Tag configuration parameters (varies by tag type)"
                    },
                    "trigger_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of trigger IDs to attach to this tag"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "tag_name", "tag_type"]
            }
        ),
        types.Tool(
            name="gtm_list_triggers",
            description="List all triggers in a GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path"]
            }
        ),
        types.Tool(
            name="gtm_create_trigger",
            description="Create a new trigger in GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "trigger_name": {
                        "type": "string",
                        "description": "Name for the new trigger"
                    },
                    "trigger_type": {
                        "type": "string",
                        "description": "Trigger type (e.g., 'pageview', 'click', 'timer', 'custom')",
                        "enum": ["pageview", "domReady", "windowLoaded", "click", "linkClick", "jsError", "timer", "customEvent", "historyChange", "formSubmission", "scrollDepth"]
                    },
                    "filters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "parameter": {
                                    "type": "array",
                                    "items": {"type": "object"}
                                }
                            }
                        },
                        "description": "Trigger conditions/filters"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "trigger_name", "trigger_type"]
            }
        ),
        types.Tool(
            name="gtm_list_variables",
            description="List all variables in a GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path"]
            }
        ),
        types.Tool(
            name="gtm_create_variable",
            description="Create a new variable in GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "variable_name": {
                        "type": "string",
                        "description": "Name for the new variable"
                    },
                    "variable_type": {
                        "type": "string",
                        "description": "Variable type (e.g., 'c' for constant, 'jsm' for JavaScript, 'u' for URL)",
                        "enum": ["c", "jsm", "u", "e", "v", "dlv", "gtm", "remm", "smm", "ctv", "dbg"]
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Variable configuration parameters"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "variable_name", "variable_type"]
            }
        ),
        types.Tool(
            name="gtm_list_workspaces",
            description="List all workspaces in a GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path"]
            }
        ),
        types.Tool(
            name="gtm_publish_container",
            description="Publish/submit changes in a GTM workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "version_name": {
                        "type": "string",
                        "description": "Name for the published version"
                    },
                    "version_notes": {
                        "type": "string",
                        "description": "Optional notes for the version"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "version_name"]
            }
        ),
        types.Tool(
            name="gtm_list_versions",
            description="List all published versions of a GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path"]
            }
        ),
        types.Tool(
            name="gtm_enable_built_in_variable",
            description="Enable built-in variables in GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "variable_type": {
                        "type": "string",
                        "description": "Built-in variable type to enable",
                        "enum": ["pageUrl", "pageHostname", "pagePath", "referrer", "event", "clickElement", "clickClasses", "clickId", "clickTarget", "clickUrl", "clickText"]
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "variable_type"]
            }
        ),
        types.Tool(
            name="gtm_get_container_settings",
            description="Get container settings and consent configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path"]
            }
        ),
        
        # Enhanced GTM Management Tools - DELETE OPERATIONS
        types.Tool(
            name="gtm_delete_tag",
            description="Delete a tag from GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "tag_id": {
                        "type": "string",
                        "description": "Tag ID to delete"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "tag_id"]
            }
        ),
        types.Tool(
            name="gtm_delete_trigger",
            description="Delete a trigger from GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "trigger_id": {
                        "type": "string",
                        "description": "Trigger ID to delete"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "trigger_id"]
            }
        ),
        types.Tool(
            name="gtm_delete_variable",
            description="Delete a variable from GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "variable_id": {
                        "type": "string",
                        "description": "Variable ID to delete"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "variable_id"]
            }
        ),
        
        # Enhanced GTM Management Tools - UPDATE OPERATIONS
        types.Tool(
            name="gtm_update_tag",
            description="Update an existing tag in GTM container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_path": {
                        "type": "string",
                        "description": "GTM container path or 'active' for active client"
                    },
                    "tag_id": {
                        "type": "string",
                        "description": "Tag ID to update"
                    },
                    "tag_name": {
                        "type": "string",
                        "description": "New name for the tag (optional)"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Updated tag configuration parameters (optional)"
                    },
                    "trigger_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Updated list of trigger IDs (optional)"
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Enable or disable the tag (optional)"
                    },
                    "client_id": {
                        "type": "string",
                        "description": "Optional: specific client to use"
                    }
                },
                "required": ["container_path", "tag_id"]
            }
        ),
        
        # Cross-Platform Analysis Tools
        types.Tool(
            name="cross_client_analysis",
            description="Compare performance across multiple clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of client IDs to compare (uses all if not specified)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Metrics to compare",
                        "default": ["sessions", "pageviews", "users"]
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        types.Tool(
            name="generate_client_report",
            description="Generate a comprehensive report for a specific client",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "Client ID to generate report for (uses active client if not specified)"
                    },
                    "date_range": {
                        "type": "string",
                        "description": "Date range for analysis (e.g., 'last_7_days', 'last_30_days')"
                    },
                    "include_ga4": {
                        "type": "boolean",
                        "description": "Include Google Analytics data",
                        "default": True
                    },
                    "include_gtm": {
                        "type": "boolean",
                        "description": "Include Google Tag Manager configuration analysis",
                        "default": True
                    }
                },
                "required": ["date_range"]
            }
        ),
        
        # Enhanced Client Management Tools
        types.Tool(
            name="cleanup_duplicate_clients",
            description="Identify and show suggestions for cleaning up duplicate client configurations",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="auto_cleanup_duplicates",
            description="Automatically remove duplicate client configurations (keeps most complete ones)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="remove_client",
            description="Remove a specific client configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "Client ID to remove"
                    }
                },
                "required": ["client_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for Google ecosystem operations."""
    
    try:
        # Helper functions
        def get_client_config(client_id: str = None):
            """Get client configuration"""
            if client_id:
                return client_manager.get_client_config(client_id)
            return client_manager.get_active_client_config()
        
        def resolve_container_path(container_path_arg: str, client_config: dict = None):
            """Resolve container path to full numeric format"""
            if container_path_arg == "active":
                if not client_config:
                    client_config = client_manager.get_active_client_config()
                if client_config and client_config.get('gtm_container_path'):
                    return client_config['gtm_container_path']
                else:
                    raise ValueError("Active client has no GTM container configured")
            return container_path_arg
        
        async def resolve_active_container_path(client_id: str = None):
            """Resolve active client to container path"""
            client_config = get_client_config(client_id)
            if not client_config:
                raise ValueError("No active client set. Use 'set_active_client' first.")
            
            gtm_container_id = client_config.get('gtm_container_id')
            if not gtm_container_id:
                raise ValueError(f"Active client '{client_config['name']}' has no GTM container configured")
            
            # Find the full container path
            accounts = tag_manager_service.accounts().list().execute()
            for account in accounts.get('account', []):
                containers = tag_manager_service.accounts().containers().list(
                    parent=account['path']
                ).execute()
                for container in containers.get('container', []):
                    if container['containerId'] == gtm_container_id:
                        return container['path']
            
            raise ValueError(f"Container with ID {gtm_container_id} not found")
        
        async def resolve_gtm_workspace(container_path_arg: str, client_id: str = None):
            """Resolve container path and get default workspace path"""
            # Resolve container path if it's "active"
            if container_path_arg == "active":
                container_path = await resolve_active_container_path(client_id)
            else:
                container_path = container_path_arg
            
            # Get the workspace ID (use default workspace)
            workspaces = tag_manager_service.accounts().containers().workspaces().list(
                parent=container_path
            ).execute()
            
            workspace_path = None
            for workspace in workspaces.get('workspace', []):
                if workspace['name'] == 'Default Workspace':
                    workspace_path = workspace['path']
                    break
            
            if not workspace_path:
                # If no default workspace, use the first one
                workspace_path = workspaces['workspace'][0]['path'] if workspaces.get('workspace') else None
            
            if not workspace_path:
                raise ValueError("No workspace found in container")
            
            return container_path, workspace_path
        
        # Client Management Tools
        if name == "list_clients":
            clients = client_manager.list_clients()
            active_client = client_manager.get_active_client_config()
            
            result = {
                "status": "success",
                "clients": clients,
                "active_client": active_client,
                "total_clients": len(clients),
                "discovery_available": bool(client_manager.discovered_accounts)
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Enhanced GTM Management Tools - DELETE OPERATIONS
        elif name == "gtm_delete_tag":
            container_path = arguments["container_path"]
            tag_id = arguments["tag_id"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Construct the tag path
                tag_path = f"{workspace_path}/tags/{tag_id}"
                
                # Delete the tag
                tag_manager_service.accounts().containers().workspaces().tags().delete(
                    path=tag_path
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "tag_deleted",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "deleted_tag": {
                        "tag_id": tag_id,
                        "path": tag_path
                    },
                    "message": f"Tag '{tag_id}' deleted successfully from GTM"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "tag_id": tag_id
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_delete_trigger":
            container_path = arguments["container_path"]
            trigger_id = arguments["trigger_id"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Construct the trigger path
                trigger_path = f"{workspace_path}/triggers/{trigger_id}"
                
                # Delete the trigger
                tag_manager_service.accounts().containers().workspaces().triggers().delete(
                    path=trigger_path
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "trigger_deleted",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "deleted_trigger": {
                        "trigger_id": trigger_id,
                        "path": trigger_path
                    },
                    "message": f"Trigger '{trigger_id}' deleted successfully from GTM"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "trigger_id": trigger_id
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_delete_variable":
            container_path = arguments["container_path"]
            variable_id = arguments["variable_id"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Construct the variable path
                variable_path = f"{workspace_path}/variables/{variable_id}"
                
                # Delete the variable
                tag_manager_service.accounts().containers().workspaces().variables().delete(
                    path=variable_path
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "variable_deleted",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "deleted_variable": {
                        "variable_id": variable_id,
                        "path": variable_path
                    },
                    "message": f"Variable '{variable_id}' deleted successfully from GTM"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "variable_id": variable_id
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_update_tag":
            container_path = arguments["container_path"]
            tag_id = arguments["tag_id"]
            tag_name = arguments.get("tag_name")
            parameters = arguments.get("parameters", {})
            trigger_ids = arguments.get("trigger_ids")
            enabled = arguments.get("enabled")
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Construct the tag path
                tag_path = f"{workspace_path}/tags/{tag_id}"
                
                # First, get the current tag
                current_tag = tag_manager_service.accounts().containers().workspaces().tags().get(
                    path=tag_path
                ).execute()
                
                # Build update body with only provided fields
                update_body = {
                    'tagId': tag_id,
                    'name': tag_name if tag_name else current_tag['name'],
                    'type': current_tag['type'],  # Type cannot be changed
                    'parameter': current_tag.get('parameter', []),
                    'firingTriggerId': trigger_ids if trigger_ids is not None else current_tag.get('firingTriggerId', []),
                    'blockingTriggerId': current_tag.get('blockingTriggerId', []),
                    'paused': not enabled if enabled is not None else current_tag.get('paused', False)
                }
                
                # Update parameters if provided
                if parameters:
                    gtm_parameters = []
                    for key, value in parameters.items():
                        gtm_parameters.append({
                            'type': 'TEMPLATE',
                            'key': key,
                            'value': str(value)
                        })
                    update_body['parameter'] = gtm_parameters
                
                # Update the tag
                updated_tag = tag_manager_service.accounts().containers().workspaces().tags().update(
                    path=tag_path,
                    body=update_body
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "tag_updated",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "updated_tag": {
                        "tag_id": updated_tag['tagId'],
                        "name": updated_tag['name'],
                        "type": updated_tag['type'],
                        "path": updated_tag['path'],
                        "account_id": updated_tag['accountId'],
                        "container_id": updated_tag['containerId'],
                        "workspace_id": updated_tag['workspaceId'],
                        "paused": updated_tag.get('paused', False)
                    },
                    "changes_applied": {
                        "name_changed": tag_name is not None,
                        "parameters_changed": bool(parameters),
                        "triggers_changed": trigger_ids is not None,
                        "enabled_changed": enabled is not None
                    },
                    "message": f"Tag '{tag_id}' updated successfully in GTM"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "tag_id": tag_id
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "set_active_client":
            client_id = arguments["client_id"]
            
            try:
                config = client_manager.set_active_client(client_id)
                result = {
                    "status": "success",
                    "action": "client_switched",
                    "active_client": config,
                    "message": f"Switched to client: {config['name']}"
                }
            except ValueError as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "available_clients": [c['client_id'] for c in client_manager.list_clients()]
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "add_client":
            client_id = arguments["client_id"]
            client_config = {
                "name": arguments["name"],
                "ga4_property_id": arguments.get("ga4_property_id"),
                "gtm_container_id": arguments.get("gtm_container_id"),
                "description": arguments.get("description", "")
            }
            
            try:
                added_config = client_manager.add_client(client_id, client_config)
                result = {
                    "status": "success",
                    "action": "client_added",
                    "client": added_config,
                    "client_id": client_id
                }
            except ValueError as e:
                result = {
                    "status": "error",
                    "error": str(e)
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "discover_accounts":
            try:
                discovered = client_manager.discover_accounts(ga_client, tag_manager_service, bq_client)
                suggestions = client_manager.get_suggested_clients()
                
                result = {
                    "status": "success",
                    "action": "accounts_discovered",
                    "discovered": discovered,
                    "suggested_clients": suggestions,
                    "summary": {
                        "ga4_properties": len(discovered.get('ga4_properties', [])),
                        "gtm_containers": len(discovered['gtm_containers']),
                        "bigquery_projects": len(discovered['bigquery_projects']),
                        "suggestions": len(suggestions)
                    }
                }
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e)
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_suggested_clients":
            suggestions = client_manager.get_suggested_clients()
            
            result = {
                "status": "success",
                "suggested_clients": suggestions,
                "total_suggestions": len(suggestions),
                "message": "Use 'add_client' to create configurations from these suggestions"
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # BigQuery Tools
        elif name == "query_bigquery":
            sql_query = arguments["sql_query"]
            max_results = arguments.get("max_results", 100)
            client_id = arguments.get("client_id")
            
            query_job = bq_client.query(sql_query)
            results = query_job.result()
            
            # Track cost and auto-stop if budget exceeded
            cost_info = track_query_cost(query_job.total_bytes_processed)
            
            rows = []
            for i, row in enumerate(results):
                if i >= max_results:
                    break
                rows.append(dict(row))
            
            client_config = get_client_config(client_id)
            
            response = {
                "status": "success",
                "query": sql_query,
                "row_count": len(rows),
                "data": rows,
                "total_bytes_processed": query_job.total_bytes_processed,
                "job_id": query_job.job_id,
                "client_context": client_config['name'] if client_config else "No active client",
                "cost_info": {
                    "query_cost_eur": cost_info["cost_eur"],
                    "budget_status": cost_info["budget_status"],
                    "bytes_processed_gb": round((query_job.total_bytes_processed or 0) / (1024**3), 4),
                    "auto_stop_protection": "Server will auto-stop at €15 budget limit"
                }
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(response, indent=2, default=str)
            )]
        
        # Google Analytics Tools
        elif name == "get_ga4_report":
            property_id = arguments.get("property_id")
            start_date = arguments["start_date"]
            end_date = arguments["end_date"]
            dimensions = arguments.get("dimensions", ["date"])
            metrics = arguments.get("metrics", ["sessions", "pageviews"])
            client_id = arguments.get("client_id")
            
            # Use property_id from arguments or get from client config
            if not property_id:
                client_config = get_client_config(client_id)
                if client_config and client_config.get('ga4_property_id'):
                    property_id = client_config['ga4_property_id']
                else:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": "No GA4 property ID specified and no active client with GA4 property"})
                    )]
            
            request = RunReportRequest(
                property=property_id,
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=metric) for metric in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )
            
            response = ga_client.run_report(request=request)
            
            rows = []
            for row in response.rows:
                row_data = {}
                for i, dim in enumerate(dimensions):
                    row_data[dim] = row.dimension_values[i].value
                for i, metric in enumerate(metrics):
                    row_data[metric] = row.metric_values[i].value
                rows.append(row_data)
            
            client_config = get_client_config(client_id)
            
            result = {
                "status": "success",
                "property_id": property_id,
                "client_context": client_config['name'] if client_config else "Direct property access",
                "date_range": f"{start_date} to {end_date}",
                "dimensions": dimensions,
                "metrics": metrics,
                "row_count": len(rows),
                "data": rows
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_client_ga4_report":
            start_date = arguments["start_date"]
            end_date = arguments["end_date"]
            dimensions = arguments.get("dimensions", ["date"])
            metrics = arguments.get("metrics", ["sessions", "pageviews"])
            
            client_config = client_manager.get_active_client_config()
            if not client_config:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": "No active client set. Use 'set_active_client' first."})
                )]
            
            if not client_config.get('ga4_property_id'):
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Active client '{client_config['name']}' has no GA4 property configured"})
                )]
            
            property_id = client_config['ga4_property_id']
            
            request = RunReportRequest(
                property=property_id,
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=metric) for metric in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )
            
            response = ga_client.run_report(request=request)
            
            rows = []
            for row in response.rows:
                row_data = {}
                for i, dim in enumerate(dimensions):
                    row_data[dim] = row.dimension_values[i].value
                for i, metric in enumerate(metrics):
                    row_data[metric] = row.metric_values[i].value
                rows.append(row_data)
            
            result = {
                "status": "success",
                "property_id": property_id,
                "client_name": client_config['name'],
                "client_id": client_config['client_id'],
                "date_range": f"{start_date} to {end_date}",
                "dimensions": dimensions,
                "metrics": metrics,
                "row_count": len(rows),
                "data": rows
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # GTM Tools (simplified for space)
        elif name == "gtm_list_containers":
            accounts = tag_manager_service.accounts().list().execute()
            containers_list = []
            
            for account in accounts.get('account', []):
                containers = tag_manager_service.accounts().containers().list(
                    parent=account['path']
                ).execute()
                
                for container in containers.get('container', []):
                    # Check if this container is configured for any client
                    configured_client = None
                    for client_id, client_config in client_manager.clients.items():
                        if client_config.get('gtm_container_id') == container['containerId']:
                            configured_client = {
                                'client_id': client_id,
                                'client_name': client_config['name']
                            }
                            break
                    
                    containers_list.append({
                        "container_id": container['containerId'],
                        "name": container['name'],
                        "account_id": container['accountId'],
                        "account_name": account['name'],
                        "path": container['path'],
                        "public_id": container.get('publicId', ''),
                        "configured_client": configured_client
                    })
            
            result = {
                "status": "success",
                "containers": containers_list,
                "total_containers": len(containers_list)
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_list_tags":
            container_path = arguments["container_path"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path if it's "active"
                if container_path == "active":
                    client_config = get_client_config(client_id)
                    if not client_config:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({"error": "No active client set. Use 'set_active_client' first."})
                        )]
                    
                    # Find the container path from the GTM container ID
                    gtm_container_id = client_config.get('gtm_container_id')
                    if not gtm_container_id:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({"error": f"Active client '{client_config['name']}' has no GTM container configured"})
                        )]
                    
                    # Find the full container path
                    accounts = tag_manager_service.accounts().list().execute()
                    container_path = None
                    for account in accounts.get('account', []):
                        containers = tag_manager_service.accounts().containers().list(
                            parent=account['path']
                        ).execute()
                        for container in containers.get('container', []):
                            if container['containerId'] == gtm_container_id:
                                container_path = container['path']
                                break
                        if container_path:
                            break
                    
                    if not container_path:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({"error": f"Container with ID {gtm_container_id} not found"})
                        )]
                
                # Get the workspace ID (use default workspace)
                workspaces = tag_manager_service.accounts().containers().workspaces().list(
                    parent=container_path
                ).execute()
                
                workspace_path = None
                for workspace in workspaces.get('workspace', []):
                    if workspace['name'] == 'Default Workspace':
                        workspace_path = workspace['path']
                        break
                
                if not workspace_path:
                    # If no default workspace, use the first one
                    workspace_path = workspaces['workspace'][0]['path'] if workspaces.get('workspace') else None
                
                if not workspace_path:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": "No workspace found in container"})
                    )]
                
                # List tags in the workspace
                tags_response = tag_manager_service.accounts().containers().workspaces().tags().list(
                    parent=workspace_path
                ).execute()
                
                tags_list = []
                for tag in tags_response.get('tag', []):
                    tags_list.append({
                        "tag_id": tag['tagId'],
                        "name": tag['name'],
                        "type": tag['type'],
                        "firing_trigger_ids": tag.get('firingTriggerId', []),
                        "blocking_trigger_ids": tag.get('blockingTriggerId', []),
                        "parameters": tag.get('parameter', []),
                        "path": tag['path'],
                        "account_id": tag['accountId'],
                        "container_id": tag['containerId'],
                        "workspace_id": tag['workspaceId']
                    })
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "total_tags": len(tags_list),
                    "tags": tags_list
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_create_tag":
            container_path = arguments["container_path"]
            tag_name = arguments["tag_name"]
            tag_type = arguments["tag_type"]
            parameters = arguments.get("parameters", {})
            trigger_ids = arguments.get("trigger_ids", [])
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path if it's "active"
                if container_path == "active":
                    client_config = get_client_config(client_id)
                    if not client_config:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({"error": "No active client set. Use 'set_active_client' first."})
                        )]
                    
                    # Find the container path from the GTM container ID
                    gtm_container_id = client_config.get('gtm_container_id')
                    if not gtm_container_id:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({"error": f"Active client '{client_config['name']}' has no GTM container configured"})
                        )]
                    
                    # Find the full container path
                    accounts = tag_manager_service.accounts().list().execute()
                    container_path = None
                    for account in accounts.get('account', []):
                        containers = tag_manager_service.accounts().containers().list(
                            parent=account['path']
                        ).execute()
                        for container in containers.get('container', []):
                            if container['containerId'] == gtm_container_id:
                                container_path = container['path']
                                break
                        if container_path:
                            break
                    
                    if not container_path:
                        return [types.TextContent(
                            type="text",
                            text=json.dumps({"error": f"Container with ID {gtm_container_id} not found"})
                        )]
                
                # Get the workspace ID (use default workspace)
                workspaces = tag_manager_service.accounts().containers().workspaces().list(
                    parent=container_path
                ).execute()
                
                workspace_path = None
                for workspace in workspaces.get('workspace', []):
                    if workspace['name'] == 'Default Workspace':
                        workspace_path = workspace['path']
                        break
                
                if not workspace_path:
                    # If no default workspace, use the first one
                    workspace_path = workspaces['workspace'][0]['path'] if workspaces.get('workspace') else None
                
                if not workspace_path:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": "No workspace found in container"})
                    )]
                
                # Convert parameters dict to GTM parameter format
                gtm_parameters = []
                for key, value in parameters.items():
                    gtm_parameters.append({
                        'type': 'TEMPLATE',
                        'key': key,
                        'value': str(value)
                    })
                
                # Create the tag
                tag_body = {
                    'name': tag_name,
                    'type': tag_type,
                    'parameter': gtm_parameters,
                    'firingTriggerId': trigger_ids
                }
                
                # Create tag in GTM
                created_tag = tag_manager_service.accounts().containers().workspaces().tags().create(
                    parent=workspace_path,
                    body=tag_body
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "tag_created",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "created_tag": {
                        "tag_id": created_tag['tagId'],
                        "name": created_tag['name'],
                        "type": created_tag['type'],
                        "path": created_tag['path'],
                        "account_id": created_tag['accountId'],
                        "container_id": created_tag['containerId'],
                        "workspace_id": created_tag['workspaceId']
                    },
                    "message": f"Tag '{tag_name}' created successfully in GTM"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "tag_name": tag_name
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_list_triggers":
            container_path = arguments["container_path"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # List triggers in the workspace
                triggers_response = tag_manager_service.accounts().containers().workspaces().triggers().list(
                    parent=workspace_path
                ).execute()
                
                triggers_list = []
                for trigger in triggers_response.get('trigger', []):
                    triggers_list.append({
                        "trigger_id": trigger['triggerId'],
                        "name": trigger['name'],
                        "type": trigger['type'],
                        "filters": trigger.get('filter', []),
                        "path": trigger['path'],
                        "account_id": trigger['accountId'],
                        "container_id": trigger['containerId'],
                        "workspace_id": trigger['workspaceId']
                    })
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "total_triggers": len(triggers_list),
                    "triggers": triggers_list
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_create_trigger":
            container_path = arguments["container_path"]
            trigger_name = arguments["trigger_name"]
            trigger_type = arguments["trigger_type"]
            filters = arguments.get("filters", [])
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Create the trigger
                trigger_body = {
                    'name': trigger_name,
                    'type': trigger_type,
                    'filter': filters
                }
                
                # Create trigger in GTM
                created_trigger = tag_manager_service.accounts().containers().workspaces().triggers().create(
                    parent=workspace_path,
                    body=trigger_body
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "trigger_created",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "created_trigger": {
                        "trigger_id": created_trigger['triggerId'],
                        "name": created_trigger['name'],
                        "type": created_trigger['type'],
                        "path": created_trigger['path'],
                        "account_id": created_trigger['accountId'],
                        "container_id": created_trigger['containerId'],
                        "workspace_id": created_trigger['workspaceId']
                    },
                    "message": f"Trigger '{trigger_name}' created successfully in GTM"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "trigger_name": trigger_name
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_list_variables":
            container_path = arguments["container_path"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # List variables in the workspace
                variables_response = tag_manager_service.accounts().containers().workspaces().variables().list(
                    parent=workspace_path
                ).execute()
                
                variables_list = []
                for variable in variables_response.get('variable', []):
                    variables_list.append({
                        "variable_id": variable['variableId'],
                        "name": variable['name'],
                        "type": variable['type'],
                        "parameters": variable.get('parameter', []),
                        "path": variable['path'],
                        "account_id": variable['accountId'],
                        "container_id": variable['containerId'],
                        "workspace_id": variable['workspaceId']
                    })
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "total_variables": len(variables_list),
                    "variables": variables_list
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_create_variable":
            container_path = arguments["container_path"]
            variable_name = arguments["variable_name"]
            variable_type = arguments["variable_type"]
            parameters = arguments.get("parameters", {})
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Convert parameters dict to GTM parameter format
                gtm_parameters = []
                for key, value in parameters.items():
                    gtm_parameters.append({
                        'type': 'TEMPLATE',
                        'key': key,
                        'value': str(value)
                    })
                
                # Create the variable
                variable_body = {
                    'name': variable_name,
                    'type': variable_type,
                    'parameter': gtm_parameters
                }
                
                # Create variable in GTM
                created_variable = tag_manager_service.accounts().containers().workspaces().variables().create(
                    parent=workspace_path,
                    body=variable_body
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "variable_created",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "created_variable": {
                        "variable_id": created_variable['variableId'],
                        "name": created_variable['name'],
                        "type": created_variable['type'],
                        "path": created_variable['path'],
                        "account_id": created_variable['accountId'],
                        "container_id": created_variable['containerId'],
                        "workspace_id": created_variable['workspaceId']
                    },
                    "message": f"Variable '{variable_name}' created successfully in GTM"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "variable_name": variable_name
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_list_workspaces":
            container_path = arguments["container_path"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path if it's "active"
                if container_path == "active":
                    container_path = await resolve_active_container_path(client_id)
                
                # Get workspaces
                workspaces = tag_manager_service.accounts().containers().workspaces().list(
                    parent=container_path
                ).execute()
                
                workspaces_list = []
                for workspace in workspaces.get('workspace', []):
                    workspaces_list.append({
                        "workspace_id": workspace['workspaceId'],
                        "name": workspace['name'],
                        "description": workspace.get('description', ''),
                        "path": workspace['path'],
                        "account_id": workspace['accountId'],
                        "container_id": workspace['containerId']
                    })
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "container_path": container_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "total_workspaces": len(workspaces_list),
                    "workspaces": workspaces_list
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_publish_container":
            container_path = arguments["container_path"]
            version_name = arguments["version_name"]
            version_notes = arguments.get("version_notes", "")
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Create version from workspace
                version_body = {
                    'name': version_name,
                    'notes': version_notes
                }
                
                # Create version (publish)
                created_version = tag_manager_service.accounts().containers().workspaces().create_version(
                    parent=workspace_path,
                    body=version_body
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "container_published",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "published_version": {
                        "version_id": created_version['containerVersionId'],
                        "name": created_version['name'],
                        "notes": created_version.get('notes', ''),
                        "path": created_version['path'],
                        "account_id": created_version['accountId'],
                        "container_id": created_version['containerId']
                    },
                    "message": f"Container version '{version_name}' published successfully"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "version_name": version_name
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_list_versions":
            container_path = arguments["container_path"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path if it's "active"
                if container_path == "active":
                    container_path = await resolve_active_container_path(client_id)
                
                # Get versions
                versions = tag_manager_service.accounts().containers().versions().list(
                    parent=container_path
                ).execute()
                
                versions_list = []
                for version in versions.get('containerVersion', []):
                    versions_list.append({
                        "version_id": version['containerVersionId'],
                        "name": version.get('name', ''),
                        "notes": version.get('notes', ''),
                        "deleted": version.get('deleted', False),
                        "path": version['path'],
                        "account_id": version['accountId'],
                        "container_id": version['containerId']
                    })
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "container_path": container_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "total_versions": len(versions_list),
                    "versions": versions_list
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_enable_built_in_variable":
            container_path = arguments["container_path"]
            variable_type = arguments["variable_type"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path and get workspace
                container_path, workspace_path = await resolve_gtm_workspace(container_path, client_id)
                
                # Enable built-in variable
                enabled_variable = tag_manager_service.accounts().containers().workspaces().built_in_variables().create(
                    parent=workspace_path,
                    body={'type': [variable_type]}
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "action": "built_in_variable_enabled",
                    "container_path": container_path,
                    "workspace_path": workspace_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "enabled_variable": {
                        "type": variable_type,
                        "path": enabled_variable.get('path', ''),
                        "account_id": enabled_variable.get('accountId', ''),
                        "container_id": enabled_variable.get('containerId', ''),
                        "workspace_id": enabled_variable.get('workspaceId', '')
                    },
                    "message": f"Built-in variable '{variable_type}' enabled successfully"
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path,
                    "variable_type": variable_type
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "gtm_get_container_settings":
            container_path = arguments["container_path"]
            client_id = arguments.get("client_id")
            
            try:
                # Resolve container path if it's "active"
                if container_path == "active":
                    container_path = await resolve_active_container_path(client_id)
                
                # Get container details
                container = tag_manager_service.accounts().containers().get(
                    path=container_path
                ).execute()
                
                client_config = get_client_config(client_id)
                
                result = {
                    "status": "success",
                    "container_path": container_path,
                    "client_context": client_config['name'] if client_config else "Direct container access",
                    "container_settings": {
                        "container_id": container['containerId'],
                        "name": container['name'],
                        "public_id": container.get('publicId', ''),
                        "usage_context": container.get('usageContext', []),
                        "domain_name": container.get('domainName', []),
                        "notes": container.get('notes', ''),
                        "tag_manager_url": container.get('tagManagerUrl', ''),
                        "features": container.get('features', {})
                    }
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "container_path": container_path
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Cross-Platform Analysis
        elif name == "cross_client_analysis":
            client_ids = arguments.get("client_ids", list(client_manager.clients.keys()))
            start_date = arguments["start_date"]
            end_date = arguments["end_date"]
            metrics = arguments.get("metrics", ["sessions", "pageviews", "users"])
            
            analysis_results = []
            
            for client_id in client_ids:
                client_config = client_manager.get_client_config(client_id)
                if not client_config or not client_config.get('ga4_property_id'):
                    continue
                
                try:
                    request = RunReportRequest(
                        property=client_config['ga4_property_id'],
                        dimensions=[Dimension(name="date")],
                        metrics=[Metric(name=metric) for metric in metrics],
                        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                    )
                    
                    response = ga_client.run_report(request=request)
                    
                    # Aggregate metrics
                    totals = {metric: 0 for metric in metrics}
                    for row in response.rows:
                        for i, metric in enumerate(metrics):
                            totals[metric] += float(row.metric_values[i].value)
                    
                    analysis_results.append({
                        "client_id": client_id,
                        "client_name": client_config['name'],
                        "property_id": client_config['ga4_property_id'],
                        "totals": totals,
                        "data_available": True
                    })
                    
                except Exception as e:
                    analysis_results.append({
                        "client_id": client_id,
                        "client_name": client_config['name'],
                        "error": str(e),
                        "data_available": False
                    })
            
            result = {
                "status": "success",
                "analysis_type": "cross_client_comparison",
                "date_range": f"{start_date} to {end_date}",
                "metrics": metrics,
                "clients_analyzed": len(analysis_results),
                "results": analysis_results
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Enhanced Client Management Tools
        elif name == "cleanup_duplicate_clients":
            try:
                cleanup_suggestions = client_manager.cleanup_duplicate_clients()
                
                result = {
                    "status": "success",
                    "cleanup_suggestions": cleanup_suggestions,
                    "total_duplicates": len(cleanup_suggestions),
                    "message": "Use 'auto_cleanup_duplicates' to automatically remove duplicates" if cleanup_suggestions else "No duplicate clients found"
                }
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e)
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "auto_cleanup_duplicates":
            try:
                cleanup_result = client_manager.auto_cleanup_duplicates()
                result = {
                    "status": "success",
                    "cleanup_result": cleanup_result
                }
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e)
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "remove_client":
            client_id = arguments["client_id"]
            
            try:
                if client_manager.remove_client(client_id):
                    result = {
                        "status": "success",
                        "action": "client_removed",
                        "client_id": client_id,
                        "remaining_clients": len(client_manager.clients)
                    }
                else:
                    result = {
                        "status": "error",
                        "error": f"Client '{client_id}' not found",
                        "available_clients": [c['client_id'] for c in client_manager.list_clients()]
                    }
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e)
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "generate_client_report":
            client_id = arguments.get("client_id")
            date_range = arguments["date_range"]
            include_ga4 = arguments.get("include_ga4", True)
            include_gtm = arguments.get("include_gtm", True)
            
            try:
                # Get client configuration
                client_config = get_client_config(client_id)
                if not client_config:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": "No active client set. Use 'set_active_client' first."})
                    )]
                
                # Parse date range
                today = datetime.now()
                if date_range == "last_7_days":
                    start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
                    end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
                elif date_range == "last_30_days":
                    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
                    end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
                elif date_range == "last_90_days":
                    start_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
                    end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({"error": f"Unsupported date range: {date_range}. Use 'last_7_days', 'last_30_days', or 'last_90_days'"})
                    )]
                
                report_data = {
                    "client_info": {
                        "client_id": client_config['client_id'],
                        "name": client_config['name'],
                        "description": client_config.get('description', ''),
                        "ga4_property_id": client_config.get('ga4_property_id'),
                        "gtm_container_id": client_config.get('gtm_container_id')
                    },
                    "date_range": {
                        "range": date_range,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
                
                # GA4 Analysis
                if include_ga4 and client_config.get('ga4_property_id'):
                    try:
                        # Basic metrics
                        request = RunReportRequest(
                            property=client_config['ga4_property_id'],
                            dimensions=[Dimension(name="date")],
                            metrics=[
                                Metric(name="sessions"),
                                Metric(name="screenPageViews"),
                                Metric(name="activeUsers"),
                                Metric(name="bounceRate"),
                                Metric(name="averageSessionDuration")
                            ],
                            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                        )
                        
                        response = ga_client.run_report(request=request)
                        
                        # Process daily data
                        daily_data = []
                        totals = {"sessions": 0, "screenPageViews": 0, "activeUsers": 0}
                        
                        for row in response.rows:
                            row_data = {
                                "date": row.dimension_values[0].value,
                                "sessions": int(row.metric_values[0].value),
                                "pageviews": int(row.metric_values[1].value),
                                "users": int(row.metric_values[2].value),
                                "bounce_rate": float(row.metric_values[3].value),
                                "avg_session_duration": float(row.metric_values[4].value)
                            }
                            daily_data.append(row_data)
                            totals["sessions"] += row_data["sessions"]
                            totals["screenPageViews"] += row_data["pageviews"]
                            totals["activeUsers"] = max(totals["activeUsers"], row_data["users"])  # Users are unique
                        
                        # Top pages analysis
                        pages_request = RunReportRequest(
                            property=client_config['ga4_property_id'],
                            dimensions=[Dimension(name="pagePath")],
                            metrics=[Metric(name="screenPageViews"), Metric(name="sessions")],
                            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                            limit=10
                        )
                        
                        pages_response = ga_client.run_report(request=pages_request)
                        top_pages = []
                        for row in pages_response.rows:
                            top_pages.append({
                                "page": row.dimension_values[0].value,
                                "pageviews": int(row.metric_values[0].value),
                                "sessions": int(row.metric_values[1].value)
                            })
                        
                        report_data["ga4_analysis"] = {
                            "status": "success",
                            "totals": totals,
                            "daily_breakdown": daily_data,
                            "top_pages": top_pages,
                            "total_days": len(daily_data)
                        }
                        
                    except Exception as e:
                        report_data["ga4_analysis"] = {
                            "status": "error",
                            "error": str(e)
                        }
                else:
                    report_data["ga4_analysis"] = {
                        "status": "skipped",
                        "reason": "GA4 not included or no property configured"
                    }
                
                # GTM Analysis
                if include_gtm and client_config.get('gtm_container_id'):
                    try:
                        # Find container path
                        gtm_container_id = client_config['gtm_container_id']
                        accounts = tag_manager_service.accounts().list().execute()
                        container_path = None
                        
                        for account in accounts.get('account', []):
                            containers = tag_manager_service.accounts().containers().list(
                                parent=account['path']
                            ).execute()
                            for container in containers.get('container', []):
                                if container['containerId'] == gtm_container_id:
                                    container_path = container['path']
                                    break
                            if container_path:
                                break
                        
                        if container_path:
                            # Get workspace
                            workspaces = tag_manager_service.accounts().containers().workspaces().list(
                                parent=container_path
                            ).execute()
                            
                            workspace_path = None
                            for workspace in workspaces.get('workspace', []):
                                if workspace['name'] == 'Default Workspace':
                                    workspace_path = workspace['path']
                                    break
                            
                            if workspace_path:
                                # Get tags
                                tags_response = tag_manager_service.accounts().containers().workspaces().tags().list(
                                    parent=workspace_path
                                ).execute()
                                
                                # Get triggers
                                triggers_response = tag_manager_service.accounts().containers().workspaces().triggers().list(
                                    parent=workspace_path
                                ).execute()
                                
                                tag_summary = {}
                                for tag in tags_response.get('tag', []):
                                    tag_type = tag['type']
                                    if tag_type not in tag_summary:
                                        tag_summary[tag_type] = 0
                                    tag_summary[tag_type] += 1
                                
                                report_data["gtm_analysis"] = {
                                    "status": "success",
                                    "container_info": {
                                        "container_id": gtm_container_id,
                                        "path": container_path
                                    },
                                    "total_tags": len(tags_response.get('tag', [])),
                                    "total_triggers": len(triggers_response.get('trigger', [])),
                                    "tag_types_breakdown": tag_summary
                                }
                            else:
                                report_data["gtm_analysis"] = {
                                    "status": "error",
                                    "error": "No workspace found"
                                }
                        else:
                            report_data["gtm_analysis"] = {
                                "status": "error",
                                "error": f"Container {gtm_container_id} not found"
                            }
                        
                    except Exception as e:
                        report_data["gtm_analysis"] = {
                            "status": "error",
                            "error": str(e)
                        }
                else:
                    report_data["gtm_analysis"] = {
                        "status": "skipped",
                        "reason": "GTM not included or no container configured"
                    }
                
                result = {
                    "status": "success",
                    "report_type": "comprehensive_client_report",
                    "generated_at": datetime.now().isoformat(),
                    "report_data": report_data
                }
                
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "client_id": client_id,
                    "date_range": date_range
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]
            
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]

async def initialize_clients():
    """Initialize Google API clients."""
    global bq_client, ga_client, tag_manager_service
    
    try:
        # Initialize BigQuery client
        bq_client = bigquery.Client()
        logger.info("BigQuery client initialized")
        
        # Initialize Google Analytics client
        ga_client = BetaAnalyticsDataClient()
        logger.info("Google Analytics client initialized")
        
        # Initialize Google Tag Manager client
        tag_manager_service = build('tagmanager', 'v2')
        logger.info("Google Tag Manager client initialized")
        
        # Auto-discover accounts on startup
        logger.info("Auto-discovering accounts...")
        client_manager.discover_accounts(ga_client, tag_manager_service, bq_client)
        
    except Exception as e:
        logger.error(f"Error initializing clients: {e}")

async def main():
    """Main server function."""
    # Initialize Google API clients
    await initialize_clients()
    
    logger.info(f"Holistic Google Ecosystem MCP Server starting...")
    logger.info(f"Configured clients: {len(client_manager.clients)}")
    if client_manager.active_client:
        active_config = client_manager.get_active_client_config()
        logger.info(f"Active client: {active_config['name']}")
    
    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="holistic-google-ecosystem",
                server_version="3.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
