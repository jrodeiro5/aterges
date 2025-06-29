# SUPABASE AUTH CONFIGURATION FIX
# How to disable email confirmation for development

## IMMEDIATE FIX COMPLETED ✅
# Used Supabase MCP to manually confirm existing users:
# - javirodeiro5@gmail.com ✅ 
# - kikirikuiri@gmail.com ✅
# Both users can now login!

## PERMANENT FIX: Configure Supabase Auth Settings

### Step 1: Go to Supabase Dashboard
1. Visit: https://app.supabase.com/project/zsmnqwjeeknohsumhmlx
2. Navigate to: Authentication → Settings → Auth
3. Find: "Enable email confirmations"
4. Set to: DISABLED (for development)

### Step 2: Alternative - Auto-confirm via SQL Trigger
-- This SQL trigger auto-confirms new users upon signup
CREATE OR REPLACE FUNCTION auto_confirm_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Auto-confirm email for development
  NEW.email_confirmed_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_confirm_user_trigger
  BEFORE INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION auto_confirm_user();

### Step 3: Verify Configuration
# Test signup → login flow:
# 1. Sign up new user
# 2. Login immediately (no email confirmation needed)
# 3. Should work without 401 error

## WHY THIS HAPPENED
- Supabase default: Require email confirmation before login
- Signup: Creates user with email_confirmed_at = null  
- Login: Fails if email_confirmed_at is null
- Solution: Either disable confirmation or auto-confirm

## PRODUCTION NOTES  
- For production: Re-enable email confirmation
- Set up proper email templates and SMTP
- Handle confirmation flow in frontend
