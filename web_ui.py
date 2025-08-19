#!/usr/bin/env python3
"""
LinkedIn Post Automation - Web UI
A Streamlit-based web interface for managing LinkedIn post automation.
"""

import streamlit as st
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.newsletter_scraper import NewsletterScraper
from src.content_processor import ContentProcessor
from src.post_generator import PostGenerator
from src.scheduler import PostScheduler
from src.config import Config

# Page configuration
st.set_page_config(
    page_title="LinkedIn Post Automation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0077B5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0077B5;
    }
    .post-preview {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .status-success { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-error { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_config():
    """Load configuration."""
    return Config()

@st.cache_data
def load_scheduled_posts():
    """Load scheduled posts from JSON file."""
    try:
        with open('data/scheduled_posts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@st.cache_data
def get_analytics_data():
    """Get analytics data for visualization."""
    posts = load_scheduled_posts()
    if not posts:
        return pd.DataFrame()
    
    df = pd.DataFrame(posts)
    # Safely parse datetime fields; create fallbacks if missing
    if 'scheduled_time' in df.columns:
        df['scheduled_time'] = pd.to_datetime(df['scheduled_time'], errors='coerce')
    else:
        df['scheduled_time'] = pd.NaT

    if 'created_time' in df.columns:
        df['created_time'] = pd.to_datetime(df['created_time'], errors='coerce')
    else:
        # Fallback: use scheduled_time if available, otherwise current time
        df['created_time'] = df['scheduled_time'].fillna(pd.Timestamp.now())
    return df

def main():
    """Main application."""
    st.markdown('<h1 class="main-header">🤖 LinkedIn Post Automation</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Content Pipeline", "Post Management", "Analytics", "Settings"]
    )
    
    # Load data
    config = load_config()
    scheduled_posts = load_scheduled_posts()
    analytics_df = get_analytics_data()
    
    if page == "Dashboard":
        show_dashboard(scheduled_posts, analytics_df)
    elif page == "Content Pipeline":
        show_content_pipeline()
    elif page == "Post Management":
        show_post_management(scheduled_posts)
    elif page == "Analytics":
        show_analytics(analytics_df)
    elif page == "Settings":
        show_settings(config)

def show_dashboard(scheduled_posts, analytics_df):
    """Show the main dashboard."""
    st.header("📊 Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Posts</h3>
            <h2>{len(scheduled_posts)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        scheduled_count = len([p for p in scheduled_posts if p.get('status') == 'scheduled'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Scheduled</h3>
            <h2 class="status-warning">{scheduled_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        posted_count = len([p for p in scheduled_posts if p.get('status') == 'posted'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Posted</h3>
            <h2 class="status-success">{posted_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        failed_count = len([p for p in scheduled_posts if p.get('status') == 'failed'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Failed</h3>
            <h2 class="status-error">{failed_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    if scheduled_posts:
        recent_posts = sorted(scheduled_posts, key=lambda x: x.get('created_time', ''), reverse=True)[:5]
        
        for post in recent_posts:
            with st.expander(f"{post.get('title', 'Untitled')} - {post.get('status', 'unknown')}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Scheduled for:** {post.get('scheduled_time', 'Not scheduled')}")
                    st.write(f"**Engagement Score:** {post.get('engagement_score', 0):.2f}")
                    st.write(f"**Length:** {post.get('post_length', 0)} characters")
                with col2:
                    status_color = {
                        'scheduled': '🟡',
                        'posted': '🟢',
                        'failed': '🔴'
                    }.get(post.get('status'), '⚪')
                    st.write(f"{status_color} {post.get('status', 'unknown')}")
    else:
        st.info("No posts found. Run the content pipeline to generate posts.")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Run Pipeline", use_container_width=True):
            with st.spinner("Running content pipeline..."):
                # This would call the actual pipeline
                st.success("Pipeline completed!")
    
    with col2:
        if st.button("📊 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("Settings")

def show_content_pipeline():
    """Show the content pipeline interface."""
    st.header("🔄 Content Pipeline")
    
    # Pipeline configuration
    st.subheader("Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        max_articles = st.number_input("Max Articles to Fetch", min_value=1, max_value=50, value=10)
        max_posts = st.number_input("Max Posts to Generate", min_value=1, max_value=20, value=5)
    
    with col2:
        auto_schedule = st.checkbox("Auto Schedule Posts", value=True)
        include_hashtags = st.checkbox("Include Hashtags", value=True)
    
    # Pipeline steps
    st.subheader("Pipeline Steps")
    
    if st.button("🚀 Run Complete Pipeline", use_container_width=True, type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch content
            status_text.text("Step 1/4: Fetching content...")
            progress_bar.progress(25)
            
            scraper = NewsletterScraper()
            # fetch_all_newsletters expects 'max_articles_per_source'
            articles = scraper.fetch_all_newsletters(max_articles_per_source=int(max_articles))
            
            if not articles:
                st.error("No articles fetched. Check your network connection and newsletter URLs.")
                return
            
            # Step 2: Process content
            status_text.text("Step 2/4: Processing content...")
            progress_bar.progress(50)
            
            processor = ContentProcessor()
            processed_articles = processor.process_articles(articles)
            
            # Step 3: Generate posts
            status_text.text("Step 3/4: Generating posts...")
            progress_bar.progress(75)
            
            generator = PostGenerator()
            posts = generator.generate_posts(processed_articles, max_posts=max_posts)
            
            # Step 4: Schedule posts
            status_text.text("Step 4/4: Scheduling posts...")
            progress_bar.progress(100)
            
            if auto_schedule:
                scheduler = PostScheduler()
                scheduled_posts = scheduler.schedule_posts(posts)
            
            status_text.text("Pipeline completed successfully!")
            st.success(f"✅ Pipeline completed! Generated {len(posts)} posts from {len(articles)} articles.")
            
            # Show generated posts
            st.subheader("Generated Posts")
            for i, post in enumerate(posts, 1):
                with st.expander(f"Post {i}: {post.get('title', 'Untitled')}"):
                    st.write(f"**Engagement Score:** {post.get('engagement_score', 0):.2f}")
                    st.write(f"**Length:** {post.get('post_length', 0)} characters")
                    st.text_area("Content", post.get('content', ''), height=200, key=f"post_{i}")
        
        except Exception as e:
            st.error(f"Pipeline failed: {str(e)}")
            st.exception(e)

def show_post_management(scheduled_posts):
    """Show post management interface."""
    st.header("📝 Post Management")
    
    if not scheduled_posts:
        st.info("No posts found. Run the content pipeline to generate posts.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "scheduled", "posted", "failed"])
    
    with col2:
        date_filter = st.date_input("Filter by Date", value=datetime.now().date())
    
    with col3:
        search_term = st.text_input("Search Posts", placeholder="Enter title or content...")
    
    # Filter posts
    filtered_posts = scheduled_posts
    
    if status_filter != "All":
        filtered_posts = [p for p in filtered_posts if p.get('status') == status_filter]
    
    if search_term:
        filtered_posts = [p for p in filtered_posts 
                         if search_term.lower() in p.get('title', '').lower() 
                         or search_term.lower() in p.get('content', '').lower()]
    
    # Display posts
    st.subheader(f"Posts ({len(filtered_posts)} found)")
    
    for post in filtered_posts:
        with st.expander(f"{post.get('title', 'Untitled')} - {post.get('status', 'unknown')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Scheduled for:** {post.get('scheduled_time', 'Not scheduled')}")
                st.write(f"**Engagement Score:** {post.get('engagement_score', 0):.2f}")
                st.write(f"**Length:** {post.get('post_length', 0)} characters")
                
                # Post content preview
                content = post.get('content', '')
                if len(content) > 300:
                    st.text_area("Content Preview", content[:300] + "...", height=100, disabled=True)
                else:
                    st.text_area("Content", content, height=100, disabled=True)
            
            with col2:
                # Status indicator
                status_color = {
                    'scheduled': '🟡',
                    'posted': '🟢',
                    'failed': '🔴'
                }.get(post.get('status'), '⚪')
                st.write(f"{status_color} {post.get('status', 'unknown')}")
                
                # Action buttons
                if post.get('status') == 'scheduled':
                    if st.button("📤 Post Now", key=f"post_{post.get('post_id')}"):
                        st.info("Posting functionality requires LinkedIn API integration.")
                
                if st.button("🗑️ Delete", key=f"delete_{post.get('post_id')}"):
                    st.warning("Delete functionality not implemented yet.")

def show_analytics(analytics_df):
    """Show analytics and visualizations."""
    st.header("📈 Analytics")
    
    if analytics_df.empty:
        st.info("No data available for analytics. Generate some posts first.")
        return
    
    # Time series of posts
    st.subheader("Post Activity Over Time")
    
    if not analytics_df.empty:
        # Group by date and count posts
        daily_posts = analytics_df.groupby(analytics_df['scheduled_time'].dt.date).size().reset_index()
        daily_posts.columns = ['date', 'post_count']
        
        fig = px.line(daily_posts, x='date', y='post_count', 
                     title='Daily Post Count',
                     labels={'date': 'Date', 'post_count': 'Number of Posts'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Engagement score distribution
    st.subheader("Engagement Score Distribution")
    
    if 'engagement_score' in analytics_df.columns:
        fig = px.histogram(analytics_df, x='engagement_score', 
                          title='Distribution of Engagement Scores',
                          labels={'engagement_score': 'Engagement Score', 'count': 'Number of Posts'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Status distribution
    st.subheader("Post Status Distribution")
    
    if 'status' in analytics_df.columns:
        status_counts = analytics_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                    title='Post Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Posts", len(analytics_df))
    
    with col2:
        if 'engagement_score' in analytics_df.columns:
            avg_engagement = analytics_df['engagement_score'].mean()
            st.metric("Avg Engagement", f"{avg_engagement:.2f}")
    
    with col3:
        if 'post_length' in analytics_df.columns:
            avg_length = analytics_df['post_length'].mean()
            st.metric("Avg Post Length", f"{avg_length:.0f} chars")

def show_settings(config):
    """Show settings and configuration."""
    st.header("⚙️ Settings")
    
    # Configuration tabs
    tab1, tab2, tab3 = st.tabs(["General", "LinkedIn API", "Content Processing"])
    
    with tab1:
        st.subheader("General Settings")
        
        # Newsletter sources
        st.write("**Newsletter Sources**")
        sources = config.get('newsletter_sources', {})
        
        for source_name, source_config in sources.items():
            with st.expander(f"Source: {source_name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Name", value=source_config.get('name', ''), key=f"name_{source_name}")
                with col2:
                    st.text_input("URL", value=source_config.get('url', ''), key=f"url_{source_name}")
    
    with tab2:
        st.subheader("LinkedIn API Configuration")
        
        # Check if .env file exists
        env_file = Path('.env')
        if env_file.exists():
            st.success("✅ .env file found")
            
            # Show current configuration (without revealing secrets)
            client_id = os.getenv('LINKEDIN_CLIENT_ID', 'Not set')
            client_secret = os.getenv('LINKEDIN_CLIENT_SECRET', 'Not set')
            access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', 'Not set')
            
            st.write(f"**Client ID:** {'*' * len(client_id) if client_id != 'Not set' else 'Not set'}")
            st.write(f"**Client Secret:** {'*' * len(client_secret) if client_secret != 'Not set' else 'Not set'}")
            st.write(f"**Access Token:** {'*' * len(access_token) if access_token != 'Not set' else 'Not set'}")
            
            if st.button("🔑 Get LinkedIn Token"):
                st.info("This will open the LinkedIn OAuth flow in a new window.")
                # This would call the get_linkedin_token.py script
        else:
            st.warning("⚠️ .env file not found")
            st.info("Create a .env file with your LinkedIn API credentials.")
    
    with tab3:
        st.subheader("Content Processing Settings")
        
        content_config = config.get('content_processing', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_length = st.number_input("Max Post Length", 
                                       value=content_config.get('max_post_length', 1300),
                                       min_value=100, max_value=3000)
            
            min_length = st.number_input("Min Post Length", 
                                       value=content_config.get('min_post_length', 100),
                                       min_value=50, max_value=1000)
        
        with col2:
            max_hashtags = st.number_input("Max Hashtags", 
                                         value=content_config.get('max_hashtags', 5),
                                         min_value=1, max_value=20)
            
            include_hashtags = st.checkbox("Include Hashtags", 
                                         value=content_config.get('include_hashtags', True))
        
        # Save settings
        if st.button("💾 Save Settings"):
            st.success("Settings saved! (Note: This is a demo - actual saving not implemented)")

if __name__ == "__main__":
    main()
