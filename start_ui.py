#!/usr/bin/env python3
"""
LinkedIn Post Automation - UI Launcher
Simple script to launch the Streamlit web interface.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit web UI."""
    print("🚀 Starting LinkedIn Post Automation Web UI...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('web_ui.py').exists():
        print("❌ Error: web_ui.py not found in current directory")
        print("Please run this script from the Linkedin_post_automation directory")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("Make sure to activate your virtual environment first:")
        print("source ../linkedinagent/bin/activate")
    
    # Check if required packages are installed
    try:
        import streamlit
        import plotly
        print("✅ Required packages found")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install required packages:")
        print("pip install streamlit plotly")
        sys.exit(1)
    
    # Launch Streamlit
    print("🌐 Launching web interface...")
    print("The UI will open in your default browser")
    print("If it doesn't open automatically, go to: http://localhost:8590")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run streamlit with specific configuration
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_ui.py",
            "--server.port", "8590",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped by user")
    except Exception as e:
        print(f"❌ Error starting web UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
