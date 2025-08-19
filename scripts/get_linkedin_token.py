#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 Token Generator
"""

import os
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
from dotenv import load_dotenv

def get_linkedin_token():
    """Get LinkedIn access token through OAuth 2.0 flow."""
    print("🔑 LinkedIn OAuth 2.0 Token Generator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    if not client_id:
        print("❌ LINKEDIN_CLIENT_ID not found in .env file")
        print("Please set your LinkedIn Client ID first")
        return None
    
    if not client_secret:
        print("❌ LINKEDIN_CLIENT_SECRET not found in .env file")
        print("Please set your LinkedIn Client Secret first")
        return None
    
    # OAuth 2.0 parameters
    redirect_uri = "http://localhost:8000/callback"
    scope = "r_liteprofile w_member_social"
    
    # Step 1: Get authorization URL
    auth_url = "https://www.linkedin.com/oauth/v2/authorization"
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': 'random_state_string'
    }
    
    auth_url_with_params = f"{auth_url}?{urlencode(auth_params)}"
    
    print("Step 1: Authorization")
    print(f"Opening browser to: {auth_url_with_params}")
    print("\nIf browser doesn't open automatically, copy and paste the URL above")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url_with_params)
    except:
        print("Could not open browser automatically")
    
    print("\nAfter authorization, you'll be redirected to a URL like:")
    print("http://localhost:8000/callback?code=AUTHORIZATION_CODE&state=random_state_string")
    
    # Step 2: Get authorization code from user
    print("\n" + "=" * 50)
    print("Step 2: Enter Authorization Code")
    print("Copy the 'code' parameter from the redirect URL above")
    
    auth_code = input("Enter authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return None
    
    # Step 3: Exchange authorization code for access token
    print("\n" + "=" * 50)
    print("Step 3: Exchanging Code for Access Token")
    
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            expires_in = token_info.get('expires_in')
            
            print("✅ Access token obtained successfully!")
            print(f"Token expires in: {expires_in} seconds")
            
            # Save to .env file
            save_token_to_env(access_token)
            
            return access_token
        else:
            print(f"❌ Failed to get access token: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error exchanging code for token: {e}")
        return None

def save_token_to_env(access_token):
    """Save access token to .env file."""
    env_file = ".env"
    
    # Read existing .env file
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add LINKEDIN_ACCESS_TOKEN
    token_line = f"LINKEDIN_ACCESS_TOKEN={access_token}\n"
    token_updated = False
    
    for i, line in enumerate(env_lines):
        if line.startswith('LINKEDIN_ACCESS_TOKEN='):
            env_lines[i] = token_line
            token_updated = True
            break
    
    if not token_updated:
        env_lines.append(token_line)
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Access token saved to {env_file}")

def main():
    """Main function."""
    print("LinkedIn OAuth 2.0 Token Generator")
    print("This script will help you get a LinkedIn access token")
    print("\nPrerequisites:")
    print("1. LinkedIn Developer Account")
    print("2. LinkedIn App with Client ID and Client Secret")
    print("3. .env file with LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET")
    
    print("\n" + "=" * 50)
    
    # Check if credentials are already set
    load_dotenv()
    existing_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    if existing_token:
        print("⚠️  Access token already exists in .env file")
        replace = input("Do you want to replace it? (y/N): ").strip().lower()
        if replace != 'y':
            print("Keeping existing token")
            return
    
    # Get new token
    access_token = get_linkedin_token()
    
    if access_token:
        print("\n" + "=" * 50)
        print("🎉 Success! Your LinkedIn access token is ready")
        print("\nNext steps:")
        print("1. Test your credentials: python test_linkedin_api.py")
        print("2. Run the automation: python -m src.main --pipeline")
    else:
        print("\n❌ Failed to get access token")
        print("Please check your credentials and try again")

if __name__ == "__main__":
    main()



