"""
Google Analytics Agent for Aterges Platform
Handles Google Analytics 4 data retrieval and analysis
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Google Analytics imports
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class GoogleAnalyticsAgent(BaseAgent):
    """
    Google Analytics 4 Data Agent
    Provides comprehensive GA4 data retrieval and analysis capabilities
    """
    
    def __init__(self):
        """Initialize the Google Analytics Agent"""
        super().__init__(
            agent_name="Google Analytics Agent",
            agent_description="Retrieves and analyzes Google Analytics 4 data for website performance insights"
        )
        
        # GA4 client will be initialized in _initialize()
        self.ga_client = None
        self.default_property_id = None
    
    def _initialize(self):
        """Initialize Google Analytics client and credentials"""
        # Import settings here to avoid circular imports
        from config import settings
        import json
        import tempfile
        
        # Get credentials and property ID from settings
        service_account_file = settings.google_application_credentials
        self.default_property_id = settings.ga4_property_id
        
        if not service_account_file:
            raise ValueError(
                "Google service account credentials not found. "
                "Please set GOOGLE_APPLICATION_CREDENTIALS environment variable "
                "to point to your Aterges service account JSON file."
            )
        
        # Handle both file path (local) and JSON content (Vercel)
        credentials = None
        try:
            if service_account_file.startswith('{'):
                # JSON content (Vercel deployment)
                service_account_info = json.loads(service_account_file)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
                logger.info("Google Analytics client initialized with service account JSON content")
            else:
                # File path (local development)
                if not os.path.exists(service_account_file):
                    raise ValueError(
                        f"Service account file not found at: {service_account_file}. "
                        "Please ensure the file exists and the path is correct."
                    )
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=['https://www.googleapis.com/auth/analytics.readonly']
                )
                logger.info(f"Google Analytics client initialized with service account file: {service_account_file}")
            
            self.ga_client = BetaAnalyticsDataClient(credentials=credentials)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in service account credentials: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Analytics client: {str(e)}")
        
        if not self.default_property_id:
            logger.warning(
                "No GA4_PROPERTY_ID set in environment variables. "
                "You'll need to provide property_id parameter for each request."
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check by testing GA4 API connection"""
        try:
            if not self.ga_client:
                return {"status": "error", "message": "GA4 client not initialized"}
            
            if not self.default_property_id:
                return {
                    "status": "warning", 
                    "message": "No default GA4 property configured",
                    "note": "Set GA4_PROPERTY_ID environment variable"
                }
            
            # Try a simple API call
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            request = RunReportRequest(
                property=self.default_property_id,
                dimensions=[Dimension(name="date")],
                metrics=[Metric(name="sessions")],
                date_ranges=[DateRange(start_date=yesterday, end_date=yesterday)],
                limit=1
            )
            
            response = self.ga_client.run_report(request=request)
            
            return {
                "status": "healthy",
                "message": "GA4 connection working",
                "property_id": self.default_property_id,
                "test_data_points": len(response.rows)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"GA4 connection failed: {str(e)}",
                "property_id": self.default_property_id
            }
    
    async def get_ga4_report(self, 
                           start_date: str, 
                           end_date: str,
                           dimensions: List[str] = None,
                           metrics: List[str] = None,
                           property_id: str = None) -> Dict[str, Any]:
        """
        Get a comprehensive GA4 report
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            dimensions: List of dimensions (default: ['date'])
            metrics: List of metrics (default: ['sessions', 'pageviews'])
            property_id: GA4 property ID (uses default if not provided)
        """
        try:
            if not self.ga_client:
                return self._handle_error("get_ga4_report", Exception("GA4 client not initialized"))
            
            # Use defaults if not provided
            if dimensions is None:
                dimensions = ['date']
            if metrics is None:
                metrics = ['sessions', 'screenPageViews']
            if property_id is None:
                property_id = self.default_property_id
            
            if not property_id:
                return self._handle_error("get_ga4_report", Exception(
                    "No GA4 property ID available. Set GA4_PROPERTY_ID environment variable or provide property_id parameter."
                ))
            
            # Create the request
            request = RunReportRequest(
                property=property_id,
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=metric) for metric in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )
            
            # Execute the request
            response = self.ga_client.run_report(request=request)
            
            # Process the response
            rows = []
            for row in response.rows:
                row_data = {}
                
                # Add dimensions
                for i, dim in enumerate(dimensions):
                    row_data[dim] = row.dimension_values[i].value
                
                # Add metrics
                for i, metric in enumerate(metrics):
                    try:
                        value = float(row.metric_values[i].value)
                        row_data[metric] = int(value) if value.is_integer() else value
                    except (ValueError, AttributeError):
                        row_data[metric] = row.metric_values[i].value
                
                rows.append(row_data)
            
            # Calculate totals
            totals = {}
            for metric in metrics:
                total = sum(row.get(metric, 0) for row in rows if isinstance(row.get(metric), (int, float)))
                totals[metric] = total
            
            result = {
                "property_id": property_id,
                "date_range": f"{start_date} to {end_date}",
                "dimensions": dimensions,
                "metrics": metrics,
                "row_count": len(rows),
                "data": rows,
                "totals": totals
            }
            
            return self._format_success_response(result, "get_ga4_report")
            
        except Exception as e:
            return self._handle_error("get_ga4_report", e)
    
    async def get_top_pages(self, 
                          start_date: str, 
                          end_date: str,
                          limit: int = 10,
                          property_id: str = None) -> Dict[str, Any]:
        """
        Get top performing pages from GA4
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Number of top pages to return
            property_id: GA4 property ID (uses default if not provided)
        """
        try:
            if not self.ga_client:
                return self._handle_error("get_top_pages", Exception("GA4 client not initialized"))
            
            if property_id is None:
                property_id = self.default_property_id
            
            if not property_id:
                return self._handle_error("get_top_pages", Exception(
                    "No GA4 property ID available. Set GA4_PROPERTY_ID environment variable or provide property_id parameter."
                ))
            
            # Create the request for top pages
            request = RunReportRequest(
                property=property_id,
                dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="sessions"),
                    Metric(name="activeUsers")
                ],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                order_bys=[{"metric": {"metric_name": "screenPageViews"}, "desc": True}],
                limit=limit
            )
            
            response = self.ga_client.run_report(request=request)
            
            # Process the response
            pages = []
            for row in response.rows:
                page_data = {
                    "page_path": row.dimension_values[0].value,
                    "page_title": row.dimension_values[1].value,
                    "pageviews": int(row.metric_values[0].value),
                    "sessions": int(row.metric_values[1].value),
                    "users": int(row.metric_values[2].value)
                }
                pages.append(page_data)
            
            result = {
                "property_id": property_id,
                "date_range": f"{start_date} to {end_date}",
                "limit": limit,
                "total_pages": len(pages),
                "pages": pages
            }
            
            return self._format_success_response(result, "get_top_pages")
            
        except Exception as e:
            return self._handle_error("get_top_pages", e)
    
    async def get_traffic_sources(self, 
                                start_date: str, 
                                end_date: str,
                                property_id: str = None) -> Dict[str, Any]:
        """
        Get traffic sources breakdown from GA4
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            property_id: GA4 property ID (uses default if not provided)
        """
        try:
            if not self.ga_client:
                return self._handle_error("get_traffic_sources", Exception("GA4 client not initialized"))
            
            if property_id is None:
                property_id = self.default_property_id
            
            if not property_id:
                return self._handle_error("get_traffic_sources", Exception(
                    "No GA4 property ID available. Set GA4_PROPERTY_ID environment variable or provide property_id parameter."
                ))
            
            # Create the request for traffic sources
            request = RunReportRequest(
                property=property_id,
                dimensions=[
                    Dimension(name="sessionDefaultChannelGroup"),
                    Dimension(name="sessionSource"),
                    Dimension(name="sessionMedium")
                ],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="activeUsers"),
                    Metric(name="bounceRate")
                ],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                order_bys=[{"metric": {"metric_name": "sessions"}, "desc": True}]
            )
            
            response = self.ga_client.run_report(request=request)
            
            # Process the response
            sources = []
            total_sessions = 0
            
            for row in response.rows:
                sessions = int(row.metric_values[0].value)
                total_sessions += sessions
                
                source_data = {
                    "channel_group": row.dimension_values[0].value,
                    "source": row.dimension_values[1].value,
                    "medium": row.dimension_values[2].value,
                    "sessions": sessions,
                    "users": int(row.metric_values[1].value),
                    "bounce_rate": round(float(row.metric_values[2].value), 2)
                }
                sources.append(source_data)
            
            # Add percentage calculations
            for source in sources:
                source["percentage"] = round((source["sessions"] / total_sessions * 100), 1) if total_sessions > 0 else 0
            
            result = {
                "property_id": property_id,
                "date_range": f"{start_date} to {end_date}",
                "total_sessions": total_sessions,
                "total_sources": len(sources),
                "sources": sources
            }
            
            return self._format_success_response(result, "get_traffic_sources")
            
        except Exception as e:
            return self._handle_error("get_traffic_sources", e)
    
    async def get_real_time_data(self, property_id: str = None) -> Dict[str, Any]:
        """
        Get real-time analytics data (last 30 minutes)
        
        Args:
            property_id: GA4 property ID (uses default if not provided)
        """
        try:
            if not self.ga_client:
                return self._handle_error("get_real_time_data", Exception("GA4 client not initialized"))
            
            if property_id is None:
                property_id = self.default_property_id
            
            if not property_id:
                return self._handle_error("get_real_time_data", Exception(
                    "No GA4 property ID available. Set GA4_PROPERTY_ID environment variable or provide property_id parameter."
                ))
            
            # Note: Real-time reporting API is different from the standard reporting API
            # For now, we'll return recent data from the standard API
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            
            request = RunReportRequest(
                property=property_id,
                dimensions=[Dimension(name="date")],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="screenPageViews")
                ],
                date_ranges=[DateRange(start_date=yesterday, end_date=today)],
            )
            
            response = self.ga_client.run_report(request=request)
            
            # Process recent activity
            recent_data = []
            for row in response.rows:
                date = row.dimension_values[0].value
                active_users = int(row.metric_values[0].value)
                pageviews = int(row.metric_values[1].value)
                
                recent_data.append({
                    "date": date,
                    "active_users": active_users,
                    "pageviews": pageviews
                })
            
            result = {
                "property_id": property_id,
                "note": "Recent activity data (real-time API not yet implemented)",
                "data": recent_data
            }
            
            return self._format_success_response(result, "get_real_time_data")
            
        except Exception as e:
            return self._handle_error("get_real_time_data", e)
