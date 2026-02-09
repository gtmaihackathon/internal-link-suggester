"""
Enhanced features module - Import URLs from CSV
Add this to your app for bulk URL management
"""

import pandas as pd
import streamlit as st
from io import StringIO

def show_csv_import():
    """Display CSV import interface in sidebar"""
    
    st.subheader("📥 Bulk Import URLs")
    
    st.markdown("""
    Upload a CSV file with the following columns:
    - `url` (required)
    - `title` (required)
    - `h1` (required)
    - `h2` (optional, separate multiple with semicolons)
    - `meta_description` (optional)
    """)
    
    # Download sample CSV template
    sample_csv = """url,title,h1,h2,meta_description
https://example.com/page1,Page Title 1,Main Heading 1,Subheading 1;Subheading 2,Meta description for page 1
https://example.com/page2,Page Title 2,Main Heading 2,Subheading A;Subheading B,Meta description for page 2"""
    
    st.download_button(
        "📄 Download CSV Template",
        sample_csv,
        file_name="url_template.csv",
        mime="text/csv",
        help="Download a sample CSV template"
    )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Upload your CSV file with URL data"
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_cols = ['url', 'title', 'h1']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                return
            
            # Preview
            st.write(f"**Preview** ({len(df)} URLs found)")
            st.dataframe(df.head())
            
            # Import button
            if st.button("📥 Import All URLs", use_container_width=True):
                imported = 0
                errors = []
                
                for idx, row in df.iterrows():
                    try:
                        url = str(row['url']).strip()
                        title = str(row['title']).strip()
                        h1 = str(row['h1']).strip()
                        
                        # Handle H2 (semicolon-separated)
                        h2_raw = str(row.get('h2', ''))
                        h2_list = [h.strip() for h in h2_raw.split(';') if h.strip()] if pd.notna(row.get('h2')) else []
                        
                        meta_desc = str(row.get('meta_description', '')).strip() if pd.notna(row.get('meta_description')) else ''
                        
                        # Validate
                        if not url or not title or not h1:
                            errors.append(f"Row {idx+2}: Missing required fields")
                            continue
                        
                        # Add to database
                        st.session_state.db.add_url(url, h1, h2_list, title, meta_desc)
                        imported += 1
                        
                    except Exception as e:
                        errors.append(f"Row {idx+2}: {str(e)}")
                
                # Show results
                if imported > 0:
                    st.success(f"✅ Successfully imported {imported} URLs!")
                
                if errors:
                    st.warning(f"⚠️ {len(errors)} errors occurred:")
                    for error in errors[:5]:  # Show first 5 errors
                        st.caption(error)
                
                if imported > 0:
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")


def export_urls_to_csv(url_database: dict):
    """Export URLs to CSV format"""
    
    if not url_database:
        return None
    
    # Prepare data
    data = []
    for url, info in url_database.items():
        data.append({
            'url': url,
            'title': info.get('title', ''),
            'h1': info.get('h1', ''),
            'h2': ';'.join(info.get('h2', [])),
            'meta_description': info.get('meta_description', '')
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Convert to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue()


def show_export_section():
    """Display export options"""
    
    st.subheader("📤 Export Database")
    
    urls = st.session_state.db.get_all_urls()
    
    if not urls:
        st.info("No URLs to export")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as CSV
        csv_data = export_urls_to_csv(urls)
        if csv_data:
            st.download_button(
                "📊 Export as CSV",
                csv_data,
                file_name="url_database.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        # Export as JSON
        import json
        json_data = json.dumps({"urls": urls}, indent=2)
        st.download_button(
            "📋 Export as JSON",
            json_data,
            file_name="url_database.json",
            mime="application/json",
            use_container_width=True
        )


# Add analytics tracking
def track_analytics():
    """Track basic usage analytics"""
    
    if 'analytics' not in st.session_state:
        st.session_state.analytics = {
            'total_analyses': 0,
            'total_suggestions': 0,
            'total_accepted': 0,
            'total_rejected': 0
        }
    
    return st.session_state.analytics


def show_analytics_dashboard():
    """Display analytics dashboard"""
    
    st.subheader("📈 Usage Analytics")
    
    analytics = track_analytics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Analyses Run", analytics['total_analyses'])
    
    with col2:
        st.metric("Suggestions Made", analytics['total_suggestions'])
    
    with col3:
        st.metric("Links Accepted", analytics['total_accepted'])
    
    with col4:
        acceptance_rate = 0
        if analytics['total_suggestions'] > 0:
            acceptance_rate = (analytics['total_accepted'] / analytics['total_suggestions']) * 100
        st.metric("Acceptance Rate", f"{acceptance_rate:.1f}%")


# To use these features, add to your main app.py:
"""
# In sidebar, add:
with st.expander("📥 Bulk Import/Export", expanded=False):
    show_csv_import()
    st.divider()
    show_export_section()

# In results tab, add:
show_analytics_dashboard()
"""
