"""
Multi-Client Google Ecosystem Manager
Handles dynamic switching between different Google accounts and properties
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("client-manager")

# GA4 Admin API for property discovery
try:
    from google.analytics.admin_v1alpha import AnalyticsAdminServiceClient
    from google.analytics.admin_v1alpha.types import ListAccountsRequest, ListPropertiesRequest
    GA4_ADMIN_AVAILABLE = True
except ImportError:
    GA4_ADMIN_AVAILABLE = False
    logger.warning("GA4 Admin API not available. Install: pip install google-analytics-admin>=0.21.0")

class ClientManager:
    """Manages multiple client configurations and account switching"""
    
    def __init__(self, config_file: str = "clients.json"):
        self.config_file = config_file
        self.clients = {}
        self.active_client = None
        self.discovered_accounts = {}
        self.load_clients()
    
    def load_clients(self):
        """Load client configurations from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.clients = data.get('clients', {})
                    self.active_client = data.get('active_client')
                    self.discovered_accounts = data.get('discovered_accounts', {})
                logger.info(f"Loaded {len(self.clients)} client configurations")
            except Exception as e:
                logger.error(f"Error loading client config: {e}")
                self.clients = {}
    
    def save_clients(self):
        """Save client configurations to file"""
        try:
            data = {
                'clients': self.clients,
                'active_client': self.active_client,
                'discovered_accounts': self.discovered_accounts,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.clients)} client configurations")
        except Exception as e:
            logger.error(f"Error saving client config: {e}")
    
    def add_client(self, client_id: str, client_config: Dict[str, Any]):
        """Add a new client configuration"""
        required_fields = ['name']
        for field in required_fields:
            if field not in client_config:
                raise ValueError(f"Missing required field: {field}")
        
        # Add metadata
        client_config['created_at'] = datetime.now().isoformat()
        client_config['last_accessed'] = None
        
        self.clients[client_id] = client_config
        self.save_clients()
        logger.info(f"Added client: {client_id} ({client_config['name']})")
        
        return client_config
    
    def remove_client(self, client_id: str):
        """Remove a client configuration"""
        if client_id in self.clients:
            client_name = self.clients[client_id].get('name', client_id)
            del self.clients[client_id]
            
            # Switch to another client if this was active
            if self.active_client == client_id:
                self.active_client = next(iter(self.clients.keys())) if self.clients else None
            
            self.save_clients()
            logger.info(f"Removed client: {client_id} ({client_name})")
            return True
        return False
    
    def set_active_client(self, client_id: str):
        """Switch to a different active client"""
        if client_id not in self.clients:
            raise ValueError(f"Client '{client_id}' not found")
        
        old_client = self.active_client
        self.active_client = client_id
        
        # Update last accessed time
        self.clients[client_id]['last_accessed'] = datetime.now().isoformat()
        
        self.save_clients()
        
        client_name = self.clients[client_id]['name']
        logger.info(f"Switched from '{old_client}' to '{client_id}' ({client_name})")
        
        return self.get_active_client_config()
    
    def get_active_client_config(self) -> Optional[Dict[str, Any]]:
        """Get the configuration for the currently active client"""
        if not self.active_client or self.active_client not in self.clients:
            return None
        
        config = self.clients[self.active_client].copy()
        config['client_id'] = self.active_client
        return config
    
    def get_client_config(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific client"""
        if client_id not in self.clients:
            return None
        
        config = self.clients[client_id].copy()
        config['client_id'] = client_id
        return config
    
    def list_clients(self) -> List[Dict[str, Any]]:
        """List all configured clients"""
        client_list = []
        for client_id, config in self.clients.items():
            client_info = {
                'client_id': client_id,
                'name': config['name'],
                'ga4_property_id': config.get('ga4_property_id'),
                'gtm_container_id': config.get('gtm_container_id'),
                'is_active': client_id == self.active_client,
                'created_at': config.get('created_at'),
                'last_accessed': config.get('last_accessed'),
                'status': 'active' if client_id == self.active_client else 'available'
            }
            client_list.append(client_info)
        
        return sorted(client_list, key=lambda x: x['last_accessed'] or '1970-01-01', reverse=True)
    
    def discover_ga4_properties(self):
        """Auto-discover GA4 properties using Analytics Admin API"""
        if not GA4_ADMIN_AVAILABLE:
            logger.warning("Cannot discover GA4 properties - Admin API not installed")
            return []
        
        discovered_properties = []
        
        try:
            # Initialize Analytics Admin client
            admin_client = AnalyticsAdminServiceClient()
            logger.info("Discovering GA4 properties...")
            
            # List all Analytics accounts
            accounts_request = ListAccountsRequest()
            accounts_response = admin_client.list_accounts(request=accounts_request)
            
            for account in accounts_response.accounts:
                logger.info(f"Scanning account: {account.display_name}")
                
                # List properties in each account
                properties_request = ListPropertiesRequest(parent=account.name)
                properties_response = admin_client.list_properties(request=properties_request)
                
                for property_obj in properties_response.properties:
                    # Extract property details
                    property_id = property_obj.name.split('/')[-1]  # Extract numeric ID
                    
                    property_info = {
                        'property_id': f"properties/{property_id}",
                        'property_name': property_obj.display_name,
                        'account_name': account.display_name,
                        'account_id': account.name.split('/')[-1],
                        'property_type': 'GA4',
                        'time_zone': property_obj.time_zone,
                        'currency_code': property_obj.currency_code,
                        'industry_category': property_obj.industry_category.name if property_obj.industry_category else 'Unknown'
                    }
                    
                    # Try to get measurement ID (data streams)
                    try:
                        data_streams = admin_client.list_data_streams(
                            parent=property_obj.name
                        )
                        
                        for stream in data_streams.data_streams:
                            if hasattr(stream, 'web_stream_data'):
                                property_info['measurement_id'] = stream.web_stream_data.measurement_id
                                property_info['stream_name'] = stream.display_name
                                break
                                
                    except Exception as e:
                        logger.warning(f"Could not get measurement ID for {property_obj.display_name}: {e}")
                        property_info['measurement_id'] = None
                    
                    discovered_properties.append(property_info)
                    logger.info(f"Found GA4 property: {property_obj.display_name} ({property_id})")
        
        except Exception as e:
            logger.error(f"Error discovering GA4 properties: {e}")
            
        return discovered_properties
    
    def discover_accounts(self, ga_client, tag_manager_service, bq_client):
        """Auto-discover available Google accounts and properties"""
        discovered = {
            'ga4_properties': [],
            'gtm_containers': [],
            'bigquery_projects': [],
            'discovery_timestamp': datetime.now().isoformat()
        }
        
        # Discover GA4 properties
        discovered['ga4_properties'] = self.discover_ga4_properties()
        
        try:
            # Discover GTM containers
            logger.info("Discovering GTM containers...")
            accounts = tag_manager_service.accounts().list().execute()
            
            for account in accounts.get('account', []):
                containers = tag_manager_service.accounts().containers().list(
                    parent=account['path']
                ).execute()
                
                for container in containers.get('container', []):
                    discovered['gtm_containers'].append({
                        'container_id': container['containerId'],
                        'name': container['name'],
                        'account_id': container['accountId'],
                        'account_name': account['name'],
                        'path': container['path'],
                        'usage_context': container.get('usageContext', [])
                    })
        
        except Exception as e:
            logger.error(f"Error discovering GTM containers: {e}")
        
        try:
            # Discover BigQuery projects
            logger.info("Discovering BigQuery datasets...")
            datasets = list(bq_client.list_datasets())
            projects_seen = set()
            for dataset in datasets:
                if dataset.project not in projects_seen:
                    discovered['bigquery_projects'].append({
                        'project_id': dataset.project,
                        'location': dataset.location
                    })
                    projects_seen.add(dataset.project)
        
        except Exception as e:
            logger.error(f"Error discovering BigQuery projects: {e}")
        
        self.discovered_accounts = discovered
        self.save_clients()
        
        logger.info(f"Discovery complete: {len(discovered['ga4_properties'])} GA4 properties, {len(discovered['gtm_containers'])} GTM containers, {len(discovered['bigquery_projects'])} BQ projects")
        return discovered
    
    def create_client_from_discovery(self, client_id: str, name: str, 
                                   ga4_property_id: str = None, 
                                   gtm_container_id: str = None) -> Dict[str, Any]:
        """Create a new client using discovered account information"""
        
        # Find matching GTM container
        gtm_config = {}
        if gtm_container_id:
            for container in self.discovered_accounts.get('gtm_containers', []):
                if container['container_id'] == gtm_container_id:
                    gtm_config = {
                        'gtm_container_id': container['container_id'],
                        'gtm_account_id': container['account_id'],
                        'gtm_container_path': container['path']
                    }
                    break
        
        client_config = {
            'name': name,
            'ga4_property_id': ga4_property_id,
            'description': f"Auto-created from discovery on {datetime.now().strftime('%Y-%m-%d')}",
            'auto_created': True,
            **gtm_config
        }
        
        return self.add_client(client_id, client_config)
    
    def get_suggested_clients(self) -> List[Dict[str, Any]]:
        """Get intelligent client suggestions by matching GA4 properties with GTM containers"""
        suggestions = []
        
        # Create measurement ID to property mapping
        measurement_to_property = {}
        for prop in self.discovered_accounts.get('ga4_properties', []):
            if prop.get('measurement_id'):
                measurement_to_property[prop['measurement_id']] = prop
        
        # Analyze GTM containers for GA4 connections
        for container in self.discovered_accounts.get('gtm_containers', []):
            client_id = f"auto_{container['container_id'].lower()}"
            if client_id in self.clients:
                continue  # Skip already configured clients
                
            suggestion = {
                'suggested_client_id': client_id,
                'name': container['name'],
                'gtm_container_id': container['container_id'],
                'gtm_container_path': container['path'],
                'account_name': container.get('account_name', 'Unknown'),
                'source': 'enhanced_discovery'
            }
            
            # Try to find linked GA4 properties by analyzing GTM tags
            # This would require GTM tag analysis - simplified for now
            # In practice, you'd use GTM API to analyze tags for measurement IDs
            
            # For now, suggest manual matching
            suggestion.update({
                'ga4_property_id': None,
                'auto_matched': False,
                'confidence': 'low',
                'note': 'Manual GA4 property assignment recommended. Check GTM tags for measurement IDs.'
            })
            
            suggestions.append(suggestion)
        
        # Add unmatched GA4 properties
        matched_properties = set()
        for suggestion in suggestions:
            if suggestion.get('ga4_property_id'):
                matched_properties.add(suggestion['ga4_property_id'])
        
        for prop in self.discovered_accounts.get('ga4_properties', []):
            if prop['property_id'] not in matched_properties:
                client_id = f"ga4_{prop['property_id'].split('/')[-1]}"
                if client_id not in self.clients:
                    suggestions.append({
                        'suggested_client_id': client_id,
                        'name': prop['property_name'],
                        'ga4_property_id': prop['property_id'],
                        'measurement_id': prop.get('measurement_id'),
                        'account_name': prop['account_name'],
                        'gtm_container_id': None,
                        'auto_matched': False,
                        'confidence': 'medium',
                        'source': 'ga4_only',
                        'note': 'GA4 property without detected GTM container.'
                    })
        
        return suggestions
    
    def cleanup_duplicate_clients(self) -> Dict[str, str]:
        """Identify and suggest cleanup for duplicate clients"""
        cleanup_suggestions = {}
        
        # Group clients by similar names
        name_groups = {}
        for client_id, config in self.clients.items():
            # Normalize name for comparison
            normalized_name = config['name'].lower().replace(' ', '_').replace('|', '_')
            if normalized_name not in name_groups:
                name_groups[normalized_name] = []
            name_groups[normalized_name].append((client_id, config))
        
        # Identify duplicates
        for group_name, clients in name_groups.items():
            if len(clients) > 1:
                # Sort by completeness: GA4 + GTM > GA4 only > GTM only > neither
                clients.sort(key=lambda x: (
                    bool(x[1].get('ga4_property_id')),
                    bool(x[1].get('gtm_container_id')),
                    x[1].get('created_at', '')
                ), reverse=True)
                
                # Keep the most complete one, suggest removing others
                primary_client = clients[0]
                for client_id, config in clients[1:]:
                    reason = []
                    if not config.get('ga4_property_id'):
                        reason.append('no GA4')
                    if not config.get('gtm_container_id'):
                        reason.append('no GTM')
                    
                    cleanup_suggestions[client_id] = {
                        'action': 'remove',
                        'reason': f"Duplicate of {primary_client[0]} ({', '.join(reason) if reason else 'less complete'})",
                        'primary_client': primary_client[0],
                        'primary_name': primary_client[1]['name']
                    }
        
        return cleanup_suggestions
    
    def auto_cleanup_duplicates(self) -> Dict[str, Any]:
        """Automatically remove duplicate clients (keeping the most complete ones)"""
        cleanup_suggestions = self.cleanup_duplicate_clients()
        
        if not cleanup_suggestions:
            return {'status': 'no_duplicates', 'message': 'No duplicate clients found'}
        
        removed_clients = []
        for client_id, suggestion in cleanup_suggestions.items():
            if self.remove_client(client_id):
                removed_clients.append({
                    'client_id': client_id,
                    'reason': suggestion['reason']
                })
        
        return {
            'status': 'completed',
            'removed_clients': removed_clients,
            'total_removed': len(removed_clients),
            'remaining_clients': len(self.clients)
        }

# Global client manager instance
client_manager = ClientManager()
