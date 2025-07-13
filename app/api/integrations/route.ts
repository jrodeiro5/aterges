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

// GET /api/integrations - List user's integrations
export async function GET(request: NextRequest) {
  try {
    const user = await getUserFromAuth(request)

    // Get user's integrations (without credentials for security)
    const { data: integrations, error } = await supabase
      .from('integrations')
      .select(`
        id,
        name,
        type,
        status,
        is_active,
        config,
        last_used_at,
        error_message,
        created_at,
        updated_at
      `)
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching integrations:', error)
      return NextResponse.json({ error: 'Failed to fetch integrations' }, { status: 500 })
    }

    return NextResponse.json({ integrations })
  } catch (error) {
    console.error('API Error:', error)
    if (error instanceof Error && error.message.includes('authorization')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// POST /api/integrations - Create new integration with secure credential storage
export async function POST(request: NextRequest) {
  try {
    const user = await getUserFromAuth(request)
    const body = await request.json()
    const { name, type, credentials, config = {} } = body

    // Validate required fields
    if (!name || !type || !credentials) {
      return NextResponse.json({ 
        error: 'Name, type, and credentials are required' 
      }, { status: 400 })
    }

    // Validate integration type
    const validTypes = ['google-cloud', 'openai', 'aws', 'azure']
    if (!validTypes.includes(type)) {
      return NextResponse.json({ 
        error: 'Invalid integration type' 
      }, { status: 400 })
    }

    // Create integration with vault storage using service role
    const { data, error } = await supabase.rpc('create_integration_with_vault', {
      p_name: name,
      p_type: type,
      p_credentials: credentials,
      p_config: config
    })

    if (error) {
      console.error('Error creating integration:', error)
      return NextResponse.json({ 
        error: 'Failed to create integration: ' + error.message 
      }, { status: 500 })
    }

    // Verify the credentials in the background
    // This will update the status to 'connected' or 'error'
    verifyIntegrationCredentials(data, type, credentials).catch(console.error)

    // Return the integration ID
    return NextResponse.json({ 
      id: data,
      message: 'Integration created successfully. Credentials are being verified.' 
    }, { status: 201 })

  } catch (error) {
    console.error('API Error:', error)
    if (error instanceof Error && error.message.includes('authorization')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// Helper function to verify integration credentials
async function verifyIntegrationCredentials(integrationId: string, type: string, credentials: string) {
  try {
    let isValid = false
    let errorMessage = null

    switch (type) {
      case 'openai':
        isValid = await verifyOpenAICredentials(credentials)
        break
      case 'google-cloud':
        isValid = await verifyGoogleCloudCredentials(credentials)
        break
      case 'aws':
        isValid = await verifyAWSCredentials(credentials)
        break
      case 'azure':
        isValid = await verifyAzureCredentials(credentials)
        break
      default:
        errorMessage = 'Unsupported integration type'
    }

    // Update integration status
    await supabase.rpc('update_integration_status', {
      p_integration_id: integrationId,
      p_status: isValid ? 'connected' : 'error',
      p_error_message: errorMessage
    })

  } catch (error) {
    console.error('Error verifying credentials:', error)
    
    await supabase.rpc('update_integration_status', {
      p_integration_id: integrationId,
      p_status: 'error',
      p_error_message: 'Failed to verify credentials: ' + (error as Error).message
    })
  }
}

// Credential verification functions
async function verifyOpenAICredentials(apiKey: string): Promise<boolean> {
  try {
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    })
    return response.ok
  } catch (error) {
    console.error('OpenAI verification error:', error)
    return false
  }
}

async function verifyGoogleCloudCredentials(serviceAccountJson: string): Promise<boolean> {
  try {
    const credentials = JSON.parse(serviceAccountJson)
    
    // Basic validation of service account structure
    const requiredFields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
    const hasAllFields = requiredFields.every(field => credentials[field])
    
    if (!hasAllFields || credentials.type !== 'service_account') {
      return false
    }

    // For a more complete verification, you could make an API call to Google Cloud
    // For now, we'll just validate the structure
    return true
  } catch (error) {
    console.error('Google Cloud verification error:', error)
    return false
  }
}

async function verifyAWSCredentials(credentials: string): Promise<boolean> {
  try {
    const awsCreds = JSON.parse(credentials)
    
    // Basic validation - should have access_key_id and secret_access_key
    return !!(awsCreds.access_key_id && awsCreds.secret_access_key)
  } catch (error) {
    console.error('AWS verification error:', error)
    return false
  }
}

async function verifyAzureCredentials(credentials: string): Promise<boolean> {
  try {
    const azureCreds = JSON.parse(credentials)
    
    // Basic validation for Azure credentials
    return !!(azureCreds.client_id && azureCreds.client_secret && azureCreds.tenant_id)
  } catch (error) {
    console.error('Azure verification error:', error)
    return false
  }
}
