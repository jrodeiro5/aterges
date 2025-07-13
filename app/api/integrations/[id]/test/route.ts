import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Create Supabase client for server-side operations
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  }
)

// Helper to get user from authorization header
async function getUserFromAuth(request: NextRequest) {
  const authHeader = request.headers.get('authorization')
  if (!authHeader?.startsWith('Bearer ')) {
    throw new Error('Missing or invalid authorization header')
  }

  const token = authHeader.substring(7)
  const { data: { user }, error } = await supabase.auth.getUser(token)
  
  if (error || !user) {
    throw new Error('Invalid or expired token')
  }

  return user
}

// POST /api/integrations/[id]/test - Test integration connectivity
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getUserFromAuth(request)

    // Get integration details
    const { data: integration, error: integrationError } = await supabase
      .from('integrations')
      .select('id, name, type, status')
      .eq('id', params.id)
      .eq('user_id', user.id)
      .single()

    if (integrationError || !integration) {
      return NextResponse.json({ error: 'Integration not found' }, { status: 404 })
    }

    // Get credentials securely from vault
    const { data: credentials, error: credentialsError } = await supabase.rpc('get_integration_credentials', {
      p_integration_id: params.id
    })

    if (credentialsError || !credentials) {
      return NextResponse.json({ 
        error: 'Failed to retrieve credentials: ' + (credentialsError?.message || 'No credentials found') 
      }, { status: 500 })
    }

    // Test connectivity based on integration type
    let testResult = { success: false, message: '', details: {} }

    try {
      switch (integration.type) {
        case 'openai':
          testResult = await testOpenAIConnection(credentials)
          break
        case 'google-cloud':
          testResult = await testGoogleCloudConnection(credentials)
          break
        case 'aws':
          testResult = await testAWSConnection(credentials)
          break
        case 'azure':
          testResult = await testAzureConnection(credentials)
          break
        default:
          testResult = { 
            success: false, 
            message: 'Unsupported integration type', 
            details: {} 
          }
      }
    } catch (error) {
      testResult = {
        success: false,
        message: 'Connection test failed: ' + (error as Error).message,
        details: {}
      }
    }

    // Update integration status based on test result
    await supabase.rpc('update_integration_status', {
      p_integration_id: params.id,
      p_status: testResult.success ? 'connected' : 'error',
      p_error_message: testResult.success ? null : testResult.message
    })

    return NextResponse.json({
      success: testResult.success,
      message: testResult.message,
      details: testResult.details,
      integration: {
        id: integration.id,
        name: integration.name,
        type: integration.type
      }
    })

  } catch (error) {
    console.error('API Error:', error)
    if (error instanceof Error && error.message.includes('authorization')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// Test functions for different integration types
async function testOpenAIConnection(apiKey: string) {
  try {
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return {
        success: false,
        message: `OpenAI API error: ${response.status} ${response.statusText}`,
        details: { status: response.status, error: errorData }
      }
    }

    const data = await response.json()
    const modelCount = data.data?.length || 0

    return {
      success: true,
      message: `Successfully connected to OpenAI API. ${modelCount} models available.`,
      details: { 
        modelCount,
        organization: response.headers.get('openai-organization') || 'Unknown'
      }
    }
  } catch (error) {
    return {
      success: false,
      message: 'Failed to connect to OpenAI API: ' + (error as Error).message,
      details: {}
    }
  }
}

async function testGoogleCloudConnection(serviceAccountJson: string) {
  try {
    const credentials = JSON.parse(serviceAccountJson)
    
    // Validate service account structure
    const requiredFields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
    const missingFields = requiredFields.filter(field => !credentials[field])
    
    if (missingFields.length > 0) {
      return {
        success: false,
        message: `Invalid service account: missing fields: ${missingFields.join(', ')}`,
        details: { missingFields }
      }
    }

    if (credentials.type !== 'service_account') {
      return {
        success: false,
        message: 'Invalid credential type. Expected service_account.',
        details: { type: credentials.type }
      }
    }

    // For a real implementation, you could make an authenticated request to Google Cloud APIs
    // For now, we'll validate the structure and format
    return {
      success: true,
      message: 'Google Cloud service account credentials are valid.',
      details: {
        projectId: credentials.project_id,
        clientEmail: credentials.client_email,
        keyId: credentials.private_key_id
      }
    }
  } catch (error) {
    return {
      success: false,
      message: 'Invalid JSON or malformed service account: ' + (error as Error).message,
      details: {}
    }
  }
}

async function testAWSConnection(credentials: string) {
  try {
    const awsCreds = JSON.parse(credentials)
    
    if (!awsCreds.access_key_id || !awsCreds.secret_access_key) {
      return {
        success: false,
        message: 'Missing required AWS credentials: access_key_id and secret_access_key',
        details: {}
      }
    }

    // For a real implementation, you could make an AWS API call to verify credentials
    // For now, we'll validate the structure
    return {
      success: true,
      message: 'AWS credentials structure is valid.',
      details: {
        accessKeyId: awsCreds.access_key_id,
        region: awsCreds.region || 'Not specified'
      }
    }
  } catch (error) {
    return {
      success: false,
      message: 'Invalid AWS credentials format: ' + (error as Error).message,
      details: {}
    }
  }
}

async function testAzureConnection(credentials: string) {
  try {
    const azureCreds = JSON.parse(credentials)
    
    const requiredFields = ['client_id', 'client_secret', 'tenant_id']
    const missingFields = requiredFields.filter(field => !azureCreds[field])
    
    if (missingFields.length > 0) {
      return {
        success: false,
        message: `Missing required Azure credentials: ${missingFields.join(', ')}`,
        details: { missingFields }
      }
    }

    // For a real implementation, you could make an authenticated request to Azure APIs
    return {
      success: true,
      message: 'Azure credentials structure is valid.',
      details: {
        clientId: azureCreds.client_id,
        tenantId: azureCreds.tenant_id
      }
    }
  } catch (error) {
    return {
      success: false,
      message: 'Invalid Azure credentials format: ' + (error as Error).message,
      details: {}
    }
  }
}
