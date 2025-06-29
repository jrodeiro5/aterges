import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application
    app_name: str = "Aterges AI Backend"
    debug: bool = False
    port: int = 8000  # Default port for local development
    
    # Database (Supabase)
    supabase_url: str
    supabase_key: str
    database_url: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Google Cloud (Phase 1 - AI Configuration)
    # These must be configured with your dedicated Aterges Google Cloud project
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    google_application_credentials: str = ""
    
    # Google Analytics (Phase 1)
    # Must be configured with your Aterges-specific GA4 property
    ga4_property_id: str = ""
    
    # API Configuration - CORS origins as comma-separated string
    cors_origins: str = "http://localhost:3000,https://aterges.vercel.app,https://aterges-m7uy49hpk-javier-rodeiros-projects.vercel.app"
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'  # Ignore extra environment variables
    )
    
    def get_cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def validate_google_cloud_config(self) -> bool:
        """Validate that Google Cloud configuration is properly set.
        In Cloud Run, credentials are provided automatically via service account.
        """
        if not self.google_cloud_project:
            return False
        
        # In Cloud Run or Google Cloud environments, credentials are automatic
        # Check for Cloud Run environment variable
        if os.environ.get('K_SERVICE'):  # Cloud Run environment
            return True
        
        # For local development, check for credentials file
        if not self.google_application_credentials:
            return False
        if not os.path.exists(self.google_application_credentials):
            return False
        return True

settings = Settings()
