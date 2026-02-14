# Supabase Setup Guide

This guide will help you set up Supabase for the Joyan event management system.

## Prerequisites
- A Supabase account (sign up at https://supabase.com)
- A Vercel account (if deploying via Vercel)

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in your project details:
   - Name: `Joyan` (or your preferred name)
   - Database Password: Create a strong password
   - Region: Choose closest to your users
4. Click "Create new project"

## Step 2: Create the Events Table

1. In your Supabase project dashboard, go to **SQL Editor**
2. Run the following SQL to create the `events` table:

```sql
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  city TEXT NOT NULL,
  brand TEXT NOT NULL,
  theme TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow public read access
CREATE POLICY "Enable read access for all users" ON events
  FOR SELECT USING (true);

-- Create a policy to allow public insert (you may want to restrict this in production)
CREATE POLICY "Enable insert access for all users" ON events
  FOR INSERT WITH CHECK (true);
```

## Step 3: Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** > **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://xxxxxxxxxxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

## Step 4: Configure Your Application

### Option A: Direct Configuration (Quick Start)

Open `index.html` and replace the placeholder values around line 334:

```javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';
```

With your actual credentials:

```javascript
const SUPABASE_URL = 'https://xxxxxxxxxxxxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
```

### Option B: Environment Variables (Recommended for Vercel)

If deploying to Vercel:

1. Go to your Vercel project settings
2. Navigate to **Environment Variables**
3. Add the following variables:
   - `VITE_SUPABASE_URL`: Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key

Then update `index.html` to use environment variables (requires a build step).

## Step 5: Test the Integration

1. Open your application in a browser
2. Click the "+ A New Event" button
3. Fill in the form with test data
4. Click "Save Event"
5. Check your Supabase dashboard to verify the data was saved

## Security Considerations

⚠️ **Important for Production:**

1. **Row Level Security**: The example policies allow public read/write access. In production, you should:
   - Implement authentication
   - Restrict write access to authenticated users only
   - Add validation rules

2. **API Keys**: Never commit your Supabase credentials to version control:
   - Add `index.html` to `.gitignore` if it contains credentials
   - Use environment variables for production deployments

3. **Update RLS Policies** for production:

```sql
-- Remove public insert policy
DROP POLICY "Enable insert access for all users" ON events;

-- Add authenticated user policy
CREATE POLICY "Enable insert for authenticated users only" ON events
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

## Troubleshooting

### Error: "Supabase is not configured"
- Make sure you've replaced the placeholder credentials in `index.html`
- Check that the Supabase URL starts with `https://`

### Error: "Failed to save event: permission denied"
- Check your Row Level Security policies
- Ensure the anon key has the correct permissions

### Events not appearing in database
- Open browser DevTools Console to check for errors
- Verify the table name is exactly `events` (case-sensitive)
- Check that all required fields are filled in the form

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
