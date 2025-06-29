# Phase 1 Development Guide: AI Orchestrator

**Complete roadmap for implementing the AI-powered conversational interface**

---

## 🎯 **Phase 1 Objective**

Transform the current placeholder chat system into a fully functional AI-powered interface that can:
- Process natural language queries about Google Analytics data
- Use Google Vertex AI (Gemini) for intelligent response generation
- Implement the first data agent (GoogleAnalyticsAgent)
- Provide real, actionable insights through conversation

---

## 📋 **Phase 1 Deliverables Checklist**

### **🔧 Infrastructure Setup**
- [ ] Google Cloud Project configuration
- [ ] Vertex AI API enablement
- [ ] Service account creation and permissions
- [ ] Google Analytics Data API access
- [ ] Backend deployment to Google Cloud Run

### **🤖 AI Orchestrator Implementation**
- [ ] Create `backend/ai/orchestrator.py`
- [ ] Implement Gemini model integration
- [ ] Build tool calling workflow
- [ ] Add conversation state management
- [ ] Error handling and fallbacks

### **📊 Google Analytics Agent**
- [ ] Create `backend/agents/google_analytics_agent.py`
- [ ] Implement GA4 data retrieval methods
- [ ] Add query parameter validation
- [ ] Handle API rate limiting and errors
- [ ] Return structured data for AI synthesis

### **🔗 API Integration**
- [ ] Update `/api/query` endpoint for real AI processing
- [ ] Add conversation persistence to database
- [ ] Implement streaming responses (optional)
- [ ] Add usage tracking and monitoring

### **🎨 Frontend Enhancements**
- [ ] Update chat interface for real-time responses
- [ ] Add loading states for AI processing
- [ ] Implement error handling for AI failures
- [ ] Add conversation history UI

---

## 🚀 **Step-by-Step Implementation Plan**

### **Step 1: Google Cloud Setup (30 minutes)**

#### **1.1 Create Google Cloud Project**
```bash
# Install Google Cloud CLI if not already installed
# Visit: https://cloud.google.com/sdk/docs/install

# Create new project
gcloud projects create aterges-ai-platform --name="Aterges AI Platform"

# Set as default project
gcloud config set project aterges-ai-platform

# Get project ID for later use
gcloud config get-value project
```

#### **1.2 Enable Required APIs**
```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Google Analytics Data API
gcloud services enable analyticsdata.googleapis.com

# Enable Cloud Run API (for deployment)
gcloud services enable run.googleapis.com

# Enable Cloud Build API (for CI/CD)
gcloud services enable cloudbuild.googleapis.com
```

#### **1.3 Create Service Account**
```bash
# Create service account for Aterges backend
gcloud iam service-accounts create aterges-backend \
    --display-name="Aterges Backend Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding aterges-ai-platform \
    --member="serviceAccount:aterges-backend@aterges-ai-platform.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding aterges-ai-platform \
    --member="serviceAccount:aterges-backend@aterges-ai-platform.iam.gserviceaccount.com" \
    --role="roles/analyticsdata.viewer"

# Create and download service account key
gcloud iam service-accounts keys create aterges-service-account.json \
    --iam-account=aterges-backend@aterges-ai-platform.iam.gserviceaccount.com
```

### **Step 2: AI Orchestrator Implementation (2-3 hours)**

#### **2.1 Create AI Module Structure**
```bash
cd backend
mkdir ai
mkdir agents

# Create AI module files
touch ai/__init__.py
touch ai/orchestrator.py
touch ai/models.py
touch ai/tool_calling.py

# Create agents module files
touch agents/__init__.py
touch agents/base_agent.py
touch agents/google_analytics_agent.py
```

#### **2.2 Implement Base AI Orchestrator**

Create `backend/ai/orchestrator.py`:
```python
import json
import logging
from typing import Dict, Any, List, Optional
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import vertexai
from vertexai.generative_models import GenerativeModel

from ..agents.google_analytics_agent import GoogleAnalyticsAgent
from ..database.database import Database

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize the AI Orchestrator with Vertex AI."""
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize Gemini model
        self.model = GenerativeModel("gemini-1.5-pro")
        
        # Initialize available agents
        self.agents = {
            "google_analytics": GoogleAnalyticsAgent()
        }
        
        logger.info("AI Orchestrator initialized successfully")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for the AI model."""
        return [
            {
                "name": "query_google_analytics",
                "description": "Query Google Analytics 4 data for website traffic, user behavior, and performance metrics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "GA4 metrics to retrieve (e.g., 'sessions', 'pageviews', 'users')"
                        },
                        "dimensions": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "GA4 dimensions to group by (e.g., 'date', 'pagePath', 'country')"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string", 
                            "description": "End date in YYYY-MM-DD format"
                        }
                    },
                    "required": ["metrics", "start_date", "end_date"]
                }
            }
        ]

    async def process_query(self, user_query: str, user_id: str) -> str:
        """Process a user query using AI and available tools."""
        try:
            # Create system prompt with available tools
            system_prompt = self._create_system_prompt()
            
            # Prepare the conversation
            full_prompt = f"{system_prompt}\n\nUser Query: {user_query}"
            
            # Get AI response
            response = self.model.generate_content(full_prompt)
            
            # Check if AI wants to use tools
            if self._wants_to_use_tools(response.text):
                tool_response = await self._execute_tools(response.text, user_id)
                
                # Send tool results back to AI for synthesis
                synthesis_prompt = f"""
                Original user query: {user_query}
                
                Tool execution results: {tool_response}
                
                Please provide a clear, human-readable answer to the user's question based on this data.
                Be specific, actionable, and highlight key insights.
                """
                
                final_response = self.model.generate_content(synthesis_prompt)
                return final_response.text
            else:
                return response.text
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I apologize, but I encountered an error processing your request. Please try again or rephrase your question."

    def _create_system_prompt(self) -> str:
        """Create system prompt with tool descriptions."""
        tools_description = json.dumps(self.get_available_tools(), indent=2)
        
        return f"""
        You are Aterges AI, an intelligent assistant for marketing and web analytics data.
        You help users understand their website performance through natural conversation.
        
        Available tools:
        {tools_description}
        
        Guidelines:
        1. Use tools when users ask about specific data or metrics
        2. If you use a tool, respond with: TOOL_CALL: [tool_name] [parameters]
        3. Always provide actionable insights, not just raw data
        4. Be conversational and helpful
        5. If you can't help with something, suggest alternatives
        
        Examples of queries that need tools:
        - "Show me my top pages last week"
        - "How many users did I have yesterday?"
        - "What's my traffic trend this month?"
        """

    def _wants_to_use_tools(self, response: str) -> bool:
        """Check if AI response indicates tool usage."""
        return "TOOL_CALL:" in response

    async def _execute_tools(self, ai_response: str, user_id: str) -> str:
        """Execute tools based on AI response."""
        # Simple parsing for demo - in production, use more robust parsing
        if "TOOL_CALL: query_google_analytics" in ai_response:
            # Extract parameters (simplified parsing)
            # In production, implement proper JSON parsing
            agent = self.agents["google_analytics"]
            
            # Default parameters for demo
            result = await agent.query_ga4(
                metrics=["sessions", "pageviews", "users"],
                dimensions=["date"],
                start_date="2024-06-21",
                end_date="2024-06-28"
            )
            
            return json.dumps(result)
        
        return "No tool execution performed"
```

#### **2.3 Create Base Agent Class**

Create `backend/agents/base_agent.py`:
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """Base class for all data agents."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the agent's main functionality."""
        pass
        
    def validate_parameters(self, required_params: list, provided_params: dict) -> bool:
        """Validate that all required parameters are provided."""
        return all(param in provided_params for param in required_params)
```

### **Step 3: Google Analytics Agent (1-2 hours)**

#### **3.1 Update Requirements**
Add to `backend/requirements.txt`:
```
google-analytics-data>=0.18.0
google-cloud-aiplatform>=1.74.0
vertexai>=1.0.0
```

#### **3.2 Implement Google Analytics Agent**

Create `backend/agents/google_analytics_agent.py`:
```python
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    Dimension,
    Metric,
    DateRange
)

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class GoogleAnalyticsAgent(BaseAgent):
    """Agent for querying Google Analytics 4 data."""
    
    def __init__(self, property_id: str = None):
        super().__init__()
        self.property_id = property_id or "properties/YOUR_GA4_PROPERTY_ID"
        self.client = BetaAnalyticsDataClient()
        logger.info(f"GoogleAnalyticsAgent initialized for property: {self.property_id}")

    async def query_ga4(
        self, 
        metrics: List[str], 
        dimensions: List[str] = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Query Google Analytics 4 data.
        
        Args:
            metrics: List of GA4 metrics (e.g., ['sessions', 'pageviews'])
            dimensions: List of GA4 dimensions (e.g., ['date', 'pagePath'])
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of rows to return
            
        Returns:
            Dictionary containing the query results
        """
        try:
            # Set default date range if not provided
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
                
            # Set default dimensions if not provided
            if not dimensions:
                dimensions = ["date"]

            # Create the request
            request = RunReportRequest(
                property=self.property_id,
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=metric) for metric in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                limit=limit
            )

            # Execute the request
            response = self.client.run_report(request=request)
            
            # Process the response
            results = self._process_response(response, metrics, dimensions)
            
            logger.info(f"Successfully retrieved {len(results.get('rows', []))} rows from GA4")
            return results
            
        except Exception as e:
            logger.error(f"Error querying GA4: {e}")
            return {
                "error": str(e),
                "metrics": metrics,
                "dimensions": dimensions,
                "date_range": f"{start_date} to {end_date}"
            }

    def _process_response(self, response, metrics: List[str], dimensions: List[str]) -> Dict[str, Any]:
        """Process GA4 API response into a structured format."""
        
        # Extract headers
        dimension_headers = [header.name for header in response.dimension_headers]
        metric_headers = [header.name for header in response.metric_headers]
        
        # Extract data rows
        rows = []
        for row in response.rows:
            row_data = {}
            
            # Add dimension values
            for i, dimension_value in enumerate(row.dimension_values):
                row_data[dimension_headers[i]] = dimension_value.value
                
            # Add metric values
            for i, metric_value in enumerate(row.metric_values):
                row_data[metric_headers[i]] = metric_value.value
                
            rows.append(row_data)
        
        # Calculate totals
        totals = {}
        if response.totals:
            for i, total in enumerate(response.totals[0].metric_values):
                totals[metric_headers[i]] = total.value
        
        return {
            "rows": rows,
            "totals": totals,
            "row_count": len(rows),
            "metrics": metrics,
            "dimensions": dimensions,
            "query_info": {
                "property_id": self.property_id,
                "data_collected": True
            }
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute method required by BaseAgent."""
        return await self.query_ga4(**kwargs)
```

### **Step 4: Update Main API (30 minutes)**

#### **4.1 Update main.py**

Replace the placeholder `/api/query` endpoint in `backend/main.py`:

```python
from ai.orchestrator import AIOrchestrator

# Add this after the other imports
import os

# Initialize AI Orchestrator (add this after app creation)
ai_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global auth_service, database, ai_orchestrator
    
    # Startup
    logger.info("Starting Aterges AI Backend...")
    
    # Initialize database
    database = Database()
    await database.connect()
    
    # Initialize auth service
    auth_service = AuthService(database)
    
    # Initialize AI Orchestrator for Phase 1
    if settings.google_cloud_project:
        try:
            ai_orchestrator = AIOrchestrator(
                project_id=settings.google_cloud_project
            )
            logger.info("AI Orchestrator initialized successfully")
        except Exception as e:
            logger.warning(f"AI Orchestrator initialization failed: {e}")
            logger.info("Running in Phase 0 mode (placeholder responses)")
    
    logger.info("Backend initialization complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend...")
    if database:
        await database.disconnect()

# Update the chat endpoint
@app.post("/api/query")
async def query_ai(
    query_data: dict,
    current_user = Depends(get_current_user)
):
    """Process AI query with real AI integration in Phase 1."""
    prompt = query_data.get("prompt", "")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        if ai_orchestrator:
            # Phase 1: Real AI processing
            response = await ai_orchestrator.process_query(prompt, current_user["id"])
        else:
            # Phase 0: Placeholder response
            response = f"Hello {current_user.get('email', 'User')}! This is a placeholder response for: '{prompt}'. The AI Orchestrator will be implemented in Phase 1 with Google Gemini integration."
        
        # TODO: Save conversation to database
        # await save_conversation(current_user["id"], prompt, response)
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error processing AI query: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Sorry, I encountered an error processing your request. Please try again."
        )
```

### **Step 5: Environment Configuration (15 minutes)**

#### **5.1 Update .env file**

Add these variables to `backend/.env`:
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=aterges-ai-platform
GOOGLE_APPLICATION_CREDENTIALS=./aterges-service-account.json

# Google Analytics (replace with your GA4 property ID)
GA4_PROPERTY_ID=properties/123456789
```

#### **5.2 Update config.py**

Add to `backend/config.py`:
```python
# Google Cloud Configuration
google_cloud_project: str = ""
google_application_credentials: str = ""
ga4_property_id: str = ""
```

### **Step 6: Testing & Validation (30 minutes)**

#### **6.1 Test Local Setup**
```bash
# Test configuration
python test-config.py

# Install new dependencies
pip install -r requirements.txt

# Start server
python main.py
```

#### **6.2 Test AI Integration**
Use the API docs at http://localhost:8000/docs to test:

1. **Authentication:** Login to get JWT token
2. **AI Query:** Send POST to `/api/query` with:
   ```json
   {
     "prompt": "Show me my website traffic for the last week"
   }
   ```

### **Step 7: Deploy to Production (45 minutes)**

#### **7.1 Update GitHub Secrets**
Add these secrets to your GitHub repository:
- `GCP_PROJECT_ID`: `aterges-ai-platform`
- `GCP_SA_KEY`: Contents of `aterges-service-account.json`
- `GA4_PROPERTY_ID`: Your Google Analytics property ID

#### **7.2 Deploy Backend**
```bash
# Commit all changes
git add .
git commit -m "feat: implement Phase 1 AI Orchestrator with Google Analytics agent"

# Push to trigger deployment
git push origin main
```

#### **7.3 Update Vercel Environment**
Update `NEXT_PUBLIC_API_BASE_URL` on Vercel to your deployed backend URL.

---

## ✅ **Phase 1 Success Criteria**

When Phase 1 is complete, users should be able to:

1. **Ask natural questions** like:
   - "What were my top 5 pages yesterday?"
   - "How many users did I have last week?"
   - "Show me my traffic trends this month"

2. **Receive intelligent responses** that:
   - Use real Google Analytics data
   - Provide actionable insights
   - Are written in natural language

3. **Have conversations saved** to the database for history

---

## 📊 **Expected Timeline**

- **Setup & Configuration:** 1 hour
- **AI Orchestrator Development:** 3 hours  
- **Google Analytics Agent:** 2 hours
- **Integration & Testing:** 1 hour
- **Deployment:** 1 hour

**Total: ~8 hours of focused development**

---

## 🎯 **Next Steps After Phase 1**

Once Phase 1 is working:

1. **Add more agents** (Search Console, Tag Manager)
2. **Improve conversation UI** (streaming, copy buttons)
3. **Add conversation history** management
4. **Implement account settings** and BYOK integration
5. **Add more sophisticated AI workflows**

---

**Ready to build the future of conversational analytics! 🚀**

*This is where Aterges transforms from a solid foundation into a truly intelligent platform.*
