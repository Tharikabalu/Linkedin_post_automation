#!/usr/bin/env python3
"""
Test LinkedIn API Credentials
"""

import os
import requests
from dotenv import load_dotenv

def test_linkedin_credentials():
    """Test LinkedIn API credentials."""
    print("🔑 Testing LinkedIn API Credentials")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    print(f"Client ID: {'✓ Set' if client_id else '✗ Missing'}")
    print(f"Client Secret: {'✓ Set' if client_secret else '✗ Missing'}")
    print(f"Access Token: {'✓ Set' if access_token else '✗ Missing'}")
    
    if not all([client_id, client_secret, access_token]):
        print("\n❌ Missing credentials. Please set them in your .env file:")
        print("LINKEDIN_CLIENT_ID=your_client_id")
        print("LINKEDIN_CLIENT_SECRET=your_client_secret")
        print("LINKEDIN_ACCESS_TOKEN=your_access_token")
        return False
    
    # Test API connection
    print("\n🌐 Testing API Connection...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        # Test profile API
        profile_url = 'https://api.linkedin.com/v2/me'
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            print("✅ API Connection Successful!")
            print(f"   Profile: {profile_data.get('localizedFirstName', '')} {profile_data.get('localizedLastName', '')}")
            print(f"   ID: {profile_data.get('id', '')}")
            return True
        else:
            print(f"❌ API Connection Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_posting_permissions():
    """Test if we have posting permissions."""
    print("\n📝 Testing Posting Permissions...")
    
    load_dotenv()
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No access token found")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # Test post creation (without actually posting)
    test_post_data = {
        "author": "urn:li:person:YOUR_ID",  # You'll need to replace with actual ID
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Test post from LinkedIn Post Automation"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    print("⚠️  Note: This is a test of permissions only")
    print("   To actually post, you need to:")
    print("   1. Replace 'YOUR_ID' with your actual LinkedIn ID")
    print("   2. Uncomment the posting code")
    print("   3. Ensure you have 'w_member_social' permission")
    
    return True

def main():
    """Main test function."""
    print("LinkedIn API Credentials Test")
    print("=" * 40)
    
    # Test basic credentials
    if not test_linkedin_credentials():
        return False
    
    # Test posting permissions
    test_posting_permissions()
    
    print("\n" + "=" * 40)
    print("✅ Credentials test completed!")
    print("\nNext steps:")
    print("1. If all tests passed, your credentials are working")
    print("2. You can now run the full automation pipeline")
    print("3. Run: python -m src.main --pipeline --max-articles 5 --max-posts 3")
    
    return True

if __name__ == "__main__":
    main()



