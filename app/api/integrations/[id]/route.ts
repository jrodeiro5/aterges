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

// GET /api/integrations/[id] - Get specific integration details
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getUserFromAuth(request)

    const { data: integration, error } = await supabase
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
      .eq('id', params.id)
      .eq('user_id', user.id)
      .single()

    if (error || !integration) {
      return NextResponse.json({ error: 'Integration not found' }, { status: 404 })
    }

    return NextResponse.json({ integration })
  } catch (error) {
    console.error('API Error:', error)
    if (error instanceof Error && error.message.includes('authorization')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// PUT /api/integrations/[id] - Update integration
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getUserFromAuth(request)
    const body = await request.json()
    const { name, credentials, config, is_active } = body

    // If credentials are being updated, use the secure vault function
    if (credentials) {
      const { error } = await supabase.rpc('update_integration_credentials', {
        p_integration_id: params.id,
        p_credentials: credentials
      })

      if (error) {
        console.error('Error updating credentials:', error)
        return NextResponse.json({ 
          error: 'Failed to update credentials: ' + error.message 
        }, { status: 500 })
      }
    }

    // Update other fields if provided
    const updateData: any = { updated_at: new Date().toISOString() }
    if (name !== undefined) updateData.name = name
    if (config !== undefined) updateData.config = config
    if (is_active !== undefined) updateData.is_active = is_active

    if (Object.keys(updateData).length > 1) { // More than just updated_at
      const { error } = await supabase
        .from('integrations')
        .update(updateData)
        .eq('id', params.id)
        .eq('user_id', user.id)

      if (error) {
        console.error('Error updating integration:', error)
        return NextResponse.json({ 
          error: 'Failed to update integration' 
        }, { status: 500 })
      }
    }

    return NextResponse.json({ message: 'Integration updated successfully' })
  } catch (error) {
    console.error('API Error:', error)
    if (error instanceof Error && error.message.includes('authorization')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

// DELETE /api/integrations/[id] - Delete integration and its vault secrets
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await getUserFromAuth(request)

    // Delete integration and associated vault secrets
    const { data, error } = await supabase.rpc('delete_integration_with_vault', {
      p_integration_id: params.id
    })

    if (error) {
      console.error('Error deleting integration:', error)
      return NextResponse.json({ 
        error: 'Failed to delete integration: ' + error.message 
      }, { status: 500 })
    }

    return NextResponse.json({ message: 'Integration deleted successfully' })
  } catch (error) {
    console.error('API Error:', error)
    if (error instanceof Error && error.message.includes('authorization')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
