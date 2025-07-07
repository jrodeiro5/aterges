"""
AI Orchestrator for Aterges Platform
Handles tool calling workflow with Google Gemini and data agents
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import asyncio

# Google Vertex AI imports
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part
from vertexai.generative_models import FinishReason
import vertexai.preview.generative_models as generative_models

# Import our agents
from agents.base_agent import BaseAgent
from agents.google_analytics_agent import GoogleAnalyticsAgent

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Core AI Orchestrator for Aterges Platform
    Manages the conversation flow between user, LLM, and data agents
    """
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize the AI Orchestrator"""
        self.project_id = project_id
        self.location = location
        self.model_name = "gemini-2.5-flash"  # Updated to available model for new projects
        
        # Initialize Vertex AI with proper credentials
        self._initialize_vertex_ai()
        
        # Initialize the model
        self.model = GenerativeModel(self.model_name)
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Create tools for function calling
        self.tools = self._create_tools()
        
        logger.info(f"AI Orchestrator initialized with {len(self.agents)} agents")
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with proper service account credentials"""
        import os
        from google.oauth2 import service_account
        from config import settings
        
        try:
            # Check if we're running in Cloud Run (workload identity environment)
            is_cloud_run = os.environ.get('K_SERVICE') is not None
            
            if is_cloud_run:
                # Use default credentials from workload identity in Cloud Run
                vertexai.init(project=self.project_id, location=self.location)
                logger.info("Vertex AI initialized with workload identity (Cloud Run)")
            else:
                # Local development - use service account file
                service_account_file = settings.google_application_credentials
                
                if service_account_file and os.path.exists(service_account_file):
                    # Load credentials from service account file
                    credentials = service_account.Credentials.from_service_account_file(
                        service_account_file,
                        scopes=['https://www.googleapis.com/auth/cloud-platform']
                    )
                    
                    # Initialize Vertex AI with explicit credentials
                    vertexai.init(
                        project=self.project_id, 
                        location=self.location,
                        credentials=credentials
                    )
                    logger.info(f"Vertex AI initialized with service account: {service_account_file}")
                else:
                    # Fallback to default credentials
                    vertexai.init(project=self.project_id, location=self.location)
                    logger.warning("Vertex AI initialized with default credentials (may fail without ADC)")
                    
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            # Still try to initialize without credentials as fallback
            vertexai.init(project=self.project_id, location=self.location)
    
    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all available agents"""
        agents = {}
        
        # Google Analytics Agent
        try:
            ga_agent = GoogleAnalyticsAgent()
            agents['google_analytics'] = ga_agent
            logger.info("Google Analytics Agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Analytics Agent: {e}")
        
        return agents
    
    def _create_tools(self) -> List[Tool]:
        """Create Vertex AI tools from available agents"""
        function_declarations = []
        
        try:
            # Google Analytics Agent functions
            if 'google_analytics' in self.agents:
                # Get GA4 report
                function_declarations.append(
                    FunctionDeclaration(
                        name="get_ga4_report",
                        description="Get Google Analytics 4 data for website metrics like sessions, pageviews, users, etc.",
                        parameters={
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
                                    "description": "List of dimensions like ['date', 'country', 'pagePath']"
                                },
                                "metrics": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of metrics like ['sessions', 'pageviews', 'users']"
                                }
                            },
                            "required": ["start_date", "end_date"]
                        }
                    )
                )
                
                # Get top pages
                function_declarations.append(
                    FunctionDeclaration(
                        name="get_top_pages",
                        description="Get the most popular pages from Google Analytics",
                        parameters={
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
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of top pages to return (default: 10)"
                                }
                            },
                            "required": ["start_date", "end_date"]
                        }
                    )
                )
                
                # Get traffic sources
                function_declarations.append(
                    FunctionDeclaration(
                        name="get_traffic_sources",
                        description="Get traffic source data from Google Analytics (organic, direct, referral, etc.)",
                        parameters={
                            "type": "object",
                            "properties": {
                                "start_date": {
                                    "type": "string",
                                    "description": "Start date in YYYY-MM-DD format"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "End date in YYYY-MM-DD format"
                                }
                            },
                            "required": ["start_date", "end_date"]
                        }
                    )
                )
            
            # Create tools if we have function declarations
            if function_declarations:
                tools = [Tool(function_declarations=function_declarations)]
                logger.info(f"Successfully created {len(function_declarations)} function declarations in {len(tools)} tool(s)")
            else:
                tools = []
                logger.warning("No function declarations created - no agents available")
            
            return tools
            
        except Exception as e:
            logger.error(f"Error creating tools: {e}")
            return []
    
    def _parse_date_reference(self, user_query: str) -> tuple[str, str]:
        """Parse natural language date references into start_date and end_date"""
        today = datetime.now()
        
        # Common date patterns
        query_lower = user_query.lower()
        
        if "today" in query_lower:
            date = today.strftime("%Y-%m-%d")
            return date, date
        elif "yesterday" in query_lower:
            date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            return date, date
        elif "last week" in query_lower or "past week" in query_lower:
            end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            return start_date, end_date
        elif "last month" in query_lower or "past month" in query_lower:
            end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            return start_date, end_date
        elif "last 7 days" in query_lower:
            end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            return start_date, end_date
        elif "last 30 days" in query_lower:
            end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            return start_date, end_date
        else:
            # Default to last 7 days
            end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            return start_date, end_date
    
    async def _execute_function_call(self, function_call) -> Dict[str, Any]:
        """Execute a function call from the AI model"""
        try:
            # Add null check for function_call
            if not function_call:
                logger.error("Function call is None")
                return {"error": "Invalid function call - function_call is None"}
            
            # Check if function_call has name attribute
            if not hasattr(function_call, 'name'):
                logger.error(f"Function call missing 'name' attribute: {type(function_call)}")
                return {"error": "Invalid function call - missing 'name' attribute"}
            
            function_name = function_call.name
            function_args = {}
            
            # Parse function arguments with error handling
            if hasattr(function_call, 'args') and function_call.args:
                for key, value in function_call.args.items():
                    function_args[key] = value
            
            logger.info(f"Executing function: {function_name} with args: {function_args}")
            
            # CRITICAL FIX: Override AI-generated dates with properly parsed dates
            if function_name in ["get_ga4_report", "get_top_pages", "get_traffic_sources"]:
                # Check if the AI used old/incorrect dates
                start_date = function_args.get('start_date')
                end_date = function_args.get('end_date')
                
                # If dates are from 2023 or 2024, override with current dates
                if start_date and (start_date.startswith('2023') or start_date.startswith('2024')):
                    logger.warning(f"AI generated old date {start_date}, overriding with current dates")
                    # Use yesterday for single-day queries, last 7 days for ranges
                    if start_date == end_date:
                        # Single day query - use yesterday
                        from datetime import datetime, timedelta
                        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                        function_args['start_date'] = yesterday
                        function_args['end_date'] = yesterday
                        logger.info(f"Override to yesterday: {yesterday}")
                    else:
                        # Range query - use last 7 days
                        from datetime import datetime, timedelta
                        end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                        function_args['start_date'] = start_date
                        function_args['end_date'] = end_date
                        logger.info(f"Override to last 7 days: {start_date} to {end_date}")
            
            # Route function calls to appropriate agents
            if function_name == "get_ga4_report":
                if 'google_analytics' not in self.agents:
                    return {"error": "Google Analytics agent not available"}
                
                return await self.agents['google_analytics'].get_ga4_report(
                    start_date=function_args.get('start_date'),
                    end_date=function_args.get('end_date'),
                    dimensions=function_args.get('dimensions', ['date']),
                    metrics=function_args.get('metrics', ['sessions', 'pageviews'])
                )
            
            elif function_name == "get_top_pages":
                if 'google_analytics' not in self.agents:
                    return {"error": "Google Analytics agent not available"}
                
                return await self.agents['google_analytics'].get_top_pages(
                    start_date=function_args.get('start_date'),
                    end_date=function_args.get('end_date'),
                    limit=function_args.get('limit', 10)
                )
            
            elif function_name == "get_traffic_sources":
                if 'google_analytics' not in self.agents:
                    return {"error": "Google Analytics agent not available"}
                
                return await self.agents['google_analytics'].get_traffic_sources(
                    start_date=function_args.get('start_date'),
                    end_date=function_args.get('end_date')
                )
            
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except AttributeError as e:
            logger.error(f"AttributeError in function call execution: {e}")
            logger.error(f"Function call object type: {type(function_call)}")
            logger.error(f"Function call object attributes: {dir(function_call) if function_call else 'None'}")
            return {"error": f"Function call attribute error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error executing function call: {e}")
            return {"error": f"Function execution failed: {str(e)}"}
    
    async def process_query(self, user_query: str, user_context: Dict[str, Any] = None) -> str:
        """
        Process a user query using the AI orchestrator
        
        Args:
            user_query: The user's natural language query
            user_context: Additional context about the user (email, preferences, etc.)
            
        Returns:
            AI-generated response string
        """
        try:
            # Create system prompt
            system_prompt = self._create_system_prompt(user_context)
            
            # Start the conversation with response validation disabled
            chat = self.model.start_chat(response_validation=False)
            
            # Send the system prompt first
            response = chat.send_message(
                system_prompt + "\n\nUser Query: " + user_query,
                tools=self.tools
            )
            
            # Handle function calls if any
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                # Check if response contains function calls
                has_function_calls = False
                if (response.candidates and response.candidates[0].content and 
                    response.candidates[0].content.parts):
                    has_function_calls = any(
                        hasattr(part, 'function_call') for part in response.candidates[0].content.parts
                    )
                
                if not has_function_calls:
                    break
                iteration += 1
                logger.info(f"Processing function calls (iteration {iteration})")
                
                # Execute all function calls
                function_responses = []
                
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        result = await self._execute_function_call(part.function_call)
                        function_responses.append(
                            Part.from_function_response(
                                name=part.function_call.name,
                                response=result
                            )
                        )
                
                # Send function results back to the model
                if function_responses:
                    response = chat.send_message(function_responses)
            
            # Get the final response text
            if response.candidates and response.candidates[0].content.parts:
                final_response = response.candidates[0].content.parts[0].text
                logger.info("Query processing completed successfully")
                return final_response
            else:
                logger.warning("No response content generated")
                return "I apologize, but I couldn't generate a response to your query. Please try rephrasing your question."
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I encountered an error while processing your query: {str(e)}. Please try again or contact support if the issue persists."
    
    def _create_system_prompt(self, user_context: Dict[str, Any] = None) -> str:
        """Create a system prompt for the AI model"""
        
        user_email = user_context.get('email', 'User') if user_context else 'User'
        
        system_prompt = f"""You are Aterges AI, an intelligent assistant specializing in marketing analytics and business intelligence.

User Context:
- User: {user_email}
- Platform: Aterges AI Platform
- Capabilities: Google Analytics 4 data analysis, website performance insights

Your Role:
- Help users understand their website and marketing performance
- Provide clear, actionable insights from Google Analytics data
- Answer questions about traffic, user behavior, and content performance
- Use available tools to fetch real data when needed

IMPORTANT FUNCTION CALLING INSTRUCTIONS:
- When you need analytics data, ONLY use the provided function tools
- DO NOT write or execute Python code directly
- DO NOT use imports like 'from datetime import date'
- Use the structured function calls: get_ga4_report, get_top_pages, get_traffic_sources
- For date ranges, use YYYY-MM-DD format in function parameters

Guidelines:
1. Always use real data from the available function tools when possible
2. Provide clear, concise answers with specific numbers and insights
3. If you need to fetch data, automatically determine appropriate date ranges from the user's question
4. Format responses in a friendly, professional manner
5. Include actionable recommendations when relevant
6. If data is unavailable, explain why and suggest alternatives

Available Function Tools:
- get_ga4_report: Get general Google Analytics data with custom dimensions and metrics
- get_top_pages: Get most popular pages from your website
- get_traffic_sources: Get traffic source breakdown (organic, direct, referral, etc.)

Example: If user asks "How many users yesterday?", call get_ga4_report with yesterday's date and users metric.

Remember: You can access real Google Analytics data for this user. Use the function tools proactively to provide data-driven insights."""

        return system_prompt
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        # Count total function declarations across all tools
        tools_count = 0
        if self.tools:
            for tool in self.tools:
                if hasattr(tool, 'function_declarations') and tool.function_declarations:
                    tools_count += len(tool.function_declarations)
        
        status = {
            "orchestrator": {
                "model": self.model_name,
                "project_id": self.project_id,
                "location": self.location,
                "agents_count": len(self.agents),
                "tools_count": tools_count,
                "tools_available": len(self.tools) > 0
            },
            "agents": {}
        }
        
        for agent_name, agent in self.agents.items():
            status["agents"][agent_name] = agent.get_status()
        
        return status
