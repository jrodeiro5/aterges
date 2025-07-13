// Integration service for secure API key management with Supabase Vault
import { supabase } from './supabase'

export interface Integration {
  id: string
  name: string
  type: 'google-cloud' | 'aws' | 'azure' | 'openai'
  status: 'connected' | 'error' | 'pending' | 'disabled'
  is_active: boolean
  config: Record<string, any>
  last_used_at?: string
  error_message?: string
  created_at: string
  updated_at: string
}

export interface CreateIntegrationRequest {
  name: string
  type: Integration['type']
  credentials: string
  config?: Record<string, any>
}

export interface UpdateIntegrationRequest {
  name?: string
  credentials?: string
  config?: Record<string, any>
  is_active?: boolean
}

export interface TestResult {
  success: boolean
  message: string
  details: Record<string, any>
  integration?: {
    id: string
    name: string
    type: string
  }
}

class IntegrationsService {
  private baseUrl = '/api/integrations'

  // Get authentication headers from Supabase session
  private async getAuthHeaders(): Promise<HeadersInit> {
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session?.access_token) {
      throw new Error('User not authenticated')
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`
    }
  }

  async getIntegrations(): Promise<Integration[]> {
    try {
      const headers = await this.getAuthHeaders()
      
      const response = await fetch(this.baseUrl, {
        method: 'GET',
        headers
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.error || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.integrations || []
    } catch (error) {
      console.error('Error fetching integrations:', error)
      throw error
    }
  }

  async createIntegration(request: CreateIntegrationRequest): Promise<{ id: string; message: string }> {
    try {
      const headers = await this.getAuthHeaders()
      
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.error || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error creating integration:', error)
      throw error
    }
  }

  async getIntegration(id: string): Promise<Integration> {
    try {
      const headers = await this.getAuthHeaders()
      
      const response = await fetch(`${this.baseUrl}/${id}`, {
        method: 'GET',
        headers
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.error || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.integration
    } catch (error) {
      console.error('Error fetching integration:', error)
      throw error
    }
  }

  async updateIntegration(id: string, request: UpdateIntegrationRequest): Promise<void> {
    try {
      const headers = await this.getAuthHeaders()
      
      const response = await fetch(`${this.baseUrl}/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.error || `HTTP error! status: ${response.status}`)
      }
    } catch (error) {
      console.error('Error updating integration:', error)
      throw error
    }
  }

  async deleteIntegration(id: string): Promise<void> {
    try {
      const headers = await this.getAuthHeaders()
      
      const response = await fetch(`${this.baseUrl}/${id}`, {
        method: 'DELETE',
        headers
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.error || `HTTP error! status: ${response.status}`)
      }
    } catch (error) {
      console.error('Error deleting integration:', error)
      throw error
    }
  }

  async testIntegration(id: string): Promise<TestResult> {
    try {
      const headers = await this.getAuthHeaders()
      
      const response = await fetch(`${this.baseUrl}/${id}/test`, {
        method: 'POST',
        headers
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.error || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error testing integration:', error)
      throw error
    }
  }

  // Helper methods for integration type information
  getIntegrationTypeInfo(type: Integration['type']) {
    const types = {
      'google-cloud': {
        name: 'Google Cloud',
        description: 'Conecta tu proyecto de Google Cloud para acceder a APIs de IA',
        color: 'bg-blue-500',
        credentialsPlaceholder: 'Pega aquí el contenido completo de tu archivo service-account.json...',
        credentialsLabel: 'Contenido del archivo service-account.json',
        docsUrl: 'https://cloud.google.com/docs/authentication/getting-started'
      },
      'openai': {
        name: 'OpenAI',
        description: 'Usa tu propia API key de OpenAI para modelos GPT',
        color: 'bg-green-500',
        credentialsPlaceholder: 'sk-...',
        credentialsLabel: 'API Key de OpenAI',
        docsUrl: 'https://platform.openai.com/docs/quickstart'
      },
      'aws': {
        name: 'Amazon Web Services',
        description: 'Integra servicios de AWS como Bedrock y SageMaker',
        color: 'bg-orange-500',
        credentialsPlaceholder: '{"access_key_id": "...", "secret_access_key": "...", "region": "us-east-1"}',
        credentialsLabel: 'Credenciales AWS JSON',
        docsUrl: 'https://docs.aws.amazon.com/general/latest/gr/aws-security-credentials.html'
      },
      'azure': {
        name: 'Microsoft Azure',
        description: 'Conecta con Azure OpenAI Service y Cognitive Services',
        color: 'bg-blue-600',
        credentialsPlaceholder: '{"client_id": "...", "client_secret": "...", "tenant_id": "..."}',
        credentialsLabel: 'Credenciales Azure JSON',
        docsUrl: 'https://docs.microsoft.com/en-us/azure/cognitive-services/authentication'
      }
    }

    return types[type]
  }

  getStatusIcon(status: Integration['status']) {
    const icons = {
      connected: { icon: 'CheckCircle', className: 'h-4 w-4 text-green-500' },
      error: { icon: 'AlertCircle', className: 'h-4 w-4 text-red-500' },
      pending: { icon: 'Clock', className: 'h-4 w-4 text-yellow-500' },
      disabled: { icon: 'XCircle', className: 'h-4 w-4 text-gray-500' }
    }

    return icons[status] || icons.pending
  }

  getStatusText(status: Integration['status']) {
    const texts = {
      connected: 'Conectado',
      error: 'Error',
      pending: 'Verificando',
      disabled: 'Deshabilitado'
    }

    return texts[status] || 'Desconocido'
  }

  getStatusColor(status: Integration['status']) {
    const colors = {
      connected: 'text-green-600 bg-green-50 border-green-200',
      error: 'text-red-600 bg-red-50 border-red-200',
      pending: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      disabled: 'text-gray-600 bg-gray-50 border-gray-200'
    }

    return colors[status] || colors.pending
  }

  // Validate credentials format before sending to API
  validateCredentials(type: Integration['type'], credentials: string): { valid: boolean; error?: string } {
    try {
      switch (type) {
        case 'openai':
          if (!credentials.startsWith('sk-')) {
            return { valid: false, error: 'OpenAI API keys should start with "sk-"' }
          }
          if (credentials.length < 20) {
            return { valid: false, error: 'OpenAI API key appears to be too short' }
          }
          break

        case 'google-cloud':
          const gcpCreds = JSON.parse(credentials)
          const requiredGcpFields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
          const missingGcpFields = requiredGcpFields.filter(field => !gcpCreds[field])
          
          if (missingGcpFields.length > 0) {
            return { valid: false, error: `Missing required fields: ${missingGcpFields.join(', ')}` }
          }
          
          if (gcpCreds.type !== 'service_account') {
            return { valid: false, error: 'Expected service_account type in JSON' }
          }
          break

        case 'aws':
          const awsCreds = JSON.parse(credentials)
          if (!awsCreds.access_key_id || !awsCreds.secret_access_key) {
            return { valid: false, error: 'Missing access_key_id or secret_access_key' }
          }
          break

        case 'azure':
          const azureCreds = JSON.parse(credentials)
          const requiredAzureFields = ['client_id', 'client_secret', 'tenant_id']
          const missingAzureFields = requiredAzureFields.filter(field => !azureCreds[field])
          
          if (missingAzureFields.length > 0) {
            return { valid: false, error: `Missing required fields: ${missingAzureFields.join(', ')}` }
          }
          break

        default:
          return { valid: false, error: 'Unsupported integration type' }
      }

      return { valid: true }
    } catch (error) {
      if (type !== 'openai') {
        return { valid: false, error: 'Invalid JSON format' }
      }
      return { valid: false, error: 'Invalid credentials format' }
    }
  }

  // Get example credentials for documentation
  getExampleCredentials(type: Integration['type']): string {
    const examples = {
      'openai': 'sk-1234567890abcdef1234567890abcdef12345678',
      'google-cloud': JSON.stringify({
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
        "client_email": "service-account@your-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
      }, null, 2),
      'aws': JSON.stringify({
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1"
      }, null, 2),
      'azure': JSON.stringify({
        "client_id": "12345678-1234-1234-1234-123456789012",
        "client_secret": "your-client-secret",
        "tenant_id": "87654321-4321-4321-4321-210987654321"
      }, null, 2)
    }

    return examples[type] || ''
  }
}

export const integrationsService = new IntegrationsService()
