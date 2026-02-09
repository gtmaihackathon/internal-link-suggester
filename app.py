import streamlit as st
import json
import os
from datetime import datetime
import re
from typing import List, Dict
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Page config
st.set_page_config(
    page_title="Smart Internal Link Suggester",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #2E86AB 0%, #A23B72 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .suggestion-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .score-high {
        background: #d4edda;
        color: #155724;
    }
    .score-medium {
        background: #fff3cd;
        color: #856404;
    }
    .score-low {
        background: #f8d7da;
        color: #721c24;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "url_database.json"
UPLOADED_FILE_PATH = "uploaded_urls_file"  # Stores the uploaded file

class URLDatabase:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.data = self.load()
    
    def load(self) -> Dict:
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"urls": {}, "last_updated": None}
    
    def save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_url(self, url: str, h1: str, h2: List[str], title: str, meta_desc: str):
        self.data["urls"][url] = {
            "h1": h1,
            "h2": h2,
            "title": title,
            "meta_description": meta_desc,
            "added_date": datetime.now().isoformat()
        }
        self.save()
    
    def get_all_urls(self) -> Dict:
        return self.data.get("urls", {})
    
    def delete_url(self, url: str):
        if url in self.data["urls"]:
            del self.data["urls"][url]
            self.save()
    
    def clear_all(self):
        self.data = {"urls": {}, "last_updated": None}
        self.save()

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to disk and return the path"""
    # Determine file extension
    file_extension = os.path.splitext(uploaded_file.name)[1]
    file_path = f"{UPLOADED_FILE_PATH}{file_extension}"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def get_uploaded_file_info() -> Dict:
    """Get info about the currently uploaded file"""
    # Check for common file extensions
    for ext in ['.xlsx', '.xls', '.csv']:
        file_path = f"{UPLOADED_FILE_PATH}{ext}"
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': file_size,
                'modified': modified_time,
                'exists': True
            }
    return {'exists': False}

def delete_uploaded_file():
    """Delete the uploaded file"""
    for ext in ['.xlsx', '.xls', '.csv']:
        file_path = f"{UPLOADED_FILE_PATH}{ext}"
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    return False

def parse_uploaded_file(file_path: str) -> pd.DataFrame:
    """Parse Excel or CSV file and return DataFrame"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:  # .xlsx or .xls
            df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def import_urls_from_file(file_path: str, db: URLDatabase) -> tuple:
    """Import URLs from uploaded file into database"""
    df = parse_uploaded_file(file_path)
    
    if df is None:
        return 0, []
    
    # Expected columns (case-insensitive)
    required_cols = ['url', 'title', 'h1']
    optional_cols = ['meta_description', 'h2']
    
    # Normalize column names to lowercase
    df.columns = df.columns.str.lower().str.strip()
    
    # Check for required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return 0, [f"Missing required columns: {', '.join(missing_cols)}"]
    
    # Add optional columns if missing
    for col in optional_cols:
        if col not in df.columns:
            df[col] = ''
    
    imported = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            url = str(row['url']).strip()
            title = str(row['title']).strip()
            h1 = str(row['h1']).strip()
            
            # Validate required fields
            if not url or url == 'nan' or not title or title == 'nan' or not h1 or h1 == 'nan':
                errors.append(f"Row {idx + 2}: Missing required field (URL, Title, or H1)")
                continue
            
            # Parse H2 (can be semicolon or comma separated)
            h2_raw = str(row.get('h2', ''))
            if h2_raw and h2_raw != 'nan':
                # Try semicolon first, then comma
                if ';' in h2_raw:
                    h2_list = [h.strip() for h in h2_raw.split(';') if h.strip()]
                else:
                    h2_list = [h.strip() for h in h2_raw.split(',') if h.strip()]
            else:
                h2_list = []
            
            # Get meta description
            meta_desc = str(row.get('meta_description', '')).strip()
            if meta_desc == 'nan':
                meta_desc = ''
            
            # Add to database
            db.add_url(url, h1, h2_list, title, meta_desc)
            imported += 1
            
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
    
    return imported, errors

class LinkSuggester:
    """Lightweight version using TF-IDF instead of sentence transformers"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english'
        )
    
    def extract_text_chunks(self, content: str, chunk_size: int = 200) -> List[Dict]:
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = ""
        start_pos = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "position": start_pos
                    })
                current_chunk = sentence + ". "
                start_pos = content.find(sentence, start_pos)
        
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "position": start_pos
            })
        
        return chunks
    
    def calculate_relevance_score(self, content_text: str, url_text: str, 
                                   url_data: Dict, content: str) -> float:
        # Combine texts for TF-IDF
        texts = [content_text, url_text]
        
        try:
            # Calculate TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Keyword overlap boost
            content_lower = content.lower()
            url_text_lower = url_text.lower()
            
            content_words = set(re.findall(r'\b\w{4,}\b', content_lower))
            url_words = set(re.findall(r'\b\w{4,}\b', url_text_lower))
            
            if content_words:
                keyword_overlap = len(content_words & url_words) / len(content_words)
            else:
                keyword_overlap = 0
            
            # Weighted score
            final_score = (similarity * 0.7) + (keyword_overlap * 0.3)
            
            return final_score
        except:
            return 0.0
    
    def suggest_anchor_text(self, chunk: str, url_data: Dict) -> str:
        chunk_lower = chunk.lower()
        
        h1 = url_data.get('h1', '').lower()
        title = url_data.get('title', '').lower()
        
        candidates = []
        
        if h1 and h1 in chunk_lower:
            start = chunk_lower.index(h1)
            candidates.append(chunk[start:start+len(h1)])
        
        if title and title in chunk_lower:
            start = chunk_lower.index(title)
            candidates.append(chunk[start:start+len(title)])
        
        for h2 in url_data.get('h2', []):
            h2_lower = h2.lower()
            if h2_lower in chunk_lower:
                start = chunk_lower.index(h2_lower)
                candidates.append(chunk[start:start+len(h2)])
        
        if candidates:
            return max(candidates, key=len)
        
        return url_data.get('h1', url_data.get('title', 'Learn more'))
    
    def generate_suggestions(self, content: str, url_database: Dict, 
                           max_suggestions: int = 15) -> List[Dict]:
        if not url_database:
            return []
        
        chunks = self.extract_text_chunks(content)
        
        # Prepare URL texts
        url_texts = {}
        for url, data in url_database.items():
            combined_text = f"{data.get('title', '')}. {data.get('h1', '')}. {data.get('meta_description', '')}. {' '.join(data.get('h2', []))}"
            url_texts[url] = combined_text
        
        suggestions = []
        url_list = list(url_database.keys())
        
        for chunk in chunks:
            chunk_text = chunk['text']
            
            # Calculate scores for all URLs
            scores = []
            for url in url_list:
                score = self.calculate_relevance_score(
                    chunk_text,
                    url_texts[url],
                    url_database[url],
                    chunk_text
                )
                scores.append((url, score))
            
            # Get top matches
            scores.sort(key=lambda x: x[1], reverse=True)
            
            for url, score in scores[:2]:
                if score > 0.25:  # Lower threshold for TF-IDF
                    anchor = self.suggest_anchor_text(chunk_text, url_database[url])
                    
                    suggestions.append({
                        'url': url,
                        'anchor_text': anchor,
                        'context': chunk_text[:150] + "...",
                        'score': score,
                        'position': chunk['position'],
                        'target_h1': url_database[url].get('h1', ''),
                        'target_title': url_database[url].get('title', '')
                    })
        
        # Remove duplicates and sort
        seen_urls = set()
        unique_suggestions = []
        for sugg in sorted(suggestions, key=lambda x: x['score'], reverse=True):
            if sugg['url'] not in seen_urls:
                seen_urls.add(sugg['url'])
                unique_suggestions.append(sugg)
            
            if len(unique_suggestions) >= max_suggestions:
                break
        
        return unique_suggestions

def main():
    # Initialize session state
    if 'db' not in st.session_state:
        st.session_state.db = URLDatabase(DB_FILE)
    
    if 'suggester' not in st.session_state:
        st.session_state.suggester = LinkSuggester()
    
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []
    
    if 'accepted_links' not in st.session_state:
        st.session_state.accepted_links = []
    
    if 'rejected_links' not in st.session_state:
        st.session_state.rejected_links = []
    
    # Header
    st.markdown('<h1 class="main-header">🔗 Smart Internal Link Suggester</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload Excel/CSV or add URLs manually • AI-powered link suggestions</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        url_count = len(st.session_state.db.get_all_urls())
        st.markdown(f"""
        <div class="metric-card">
            <h3>{url_count}</h3>
            <p>URLs in Database</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("📚 Manage URLs")
        
        # File Upload Section
        with st.expander("📤 Upload Excel/CSV File", expanded=False):
            st.markdown("""
            **Upload a file with your URLs and metadata**
            
            Required columns:
            - `url` - Full URL
            - `title` - Page title (meta title)
            - `h1` - Main H1 heading
            
            Optional columns:
            - `meta_description` - Meta description
            - `h2` - H2 headings (separate with ; or ,)
            """)
            
            # Show current file info
            file_info = get_uploaded_file_info()
            if file_info['exists']:
                st.info(f"""
                📁 **Current file:** {file_info['name']}  
                📊 **Size:** {file_info['size'] / 1024:.1f} KB  
                🕒 **Uploaded:** {file_info['modified'].strftime('%Y-%m-%d %H:%M')}
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reload from File", use_container_width=True):
                        with st.spinner("Loading URLs from file..."):
                            imported, errors = import_urls_from_file(file_info['path'], st.session_state.db)
                        
                        if imported > 0:
                            st.success(f"✅ Loaded {imported} URLs from file!")
                        
                        if errors:
                            with st.expander("⚠️ View Errors"):
                                for error in errors[:10]:  # Show first 10 errors
                                    st.caption(error)
                        
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Remove File", use_container_width=True):
                        if delete_uploaded_file():
                            st.success("✅ File removed!")
                            st.rerun()
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose Excel or CSV file",
                type=['xlsx', 'xls', 'csv'],
                help="Upload your file with URL data",
                key="url_file_uploader"
            )
            
            if uploaded_file is not None:
                # Show preview
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    # Normalize columns
                    df.columns = df.columns.str.lower().str.strip()
                    
                    st.write(f"**Preview** ({len(df)} rows)")
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # Import button
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if st.button("📥 Import URLs from File", use_container_width=True, type="primary"):
                            # Save file
                            with st.spinner("Saving file..."):
                                file_path = save_uploaded_file(uploaded_file)
                            
                            # Import URLs
                            with st.spinner("Importing URLs..."):
                                imported, errors = import_urls_from_file(file_path, st.session_state.db)
                            
                            if imported > 0:
                                st.success(f"✅ Successfully imported {imported} URLs!")
                            
                            if errors:
                                st.warning(f"⚠️ {len(errors)} errors occurred")
                                with st.expander("View Errors"):
                                    for error in errors[:10]:
                                        st.caption(error)
                            
                            st.rerun()
                    
                    with col2:
                        # Download template
                        template_data = {
                            'url': ['https://example.com/page1', 'https://example.com/page2'],
                            'title': ['Page 1 Title', 'Page 2 Title'],
                            'h1': ['Main Heading 1', 'Main Heading 2'],
                            'meta_description': ['Description 1', 'Description 2'],
                            'h2': ['H2-1; H2-2', 'H2-A; H2-B']
                        }
                        template_df = pd.DataFrame(template_data)
                        
                        # Convert to Excel bytes
                        from io import BytesIO
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            template_df.to_excel(writer, index=False, sheet_name='URLs')
                        excel_data = output.getvalue()
                        
                        st.download_button(
                            "📄 Template",
                            excel_data,
                            file_name="url_template.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        with st.expander("➕ Add Single URL", expanded=False):
            with st.form("add_url_form"):
                url = st.text_input("URL*", placeholder="https://example.com/page")
                title = st.text_input("Page Title*", placeholder="Complete Guide to...")
                h1 = st.text_input("H1 Heading*", placeholder="Main heading")
                h2_input = st.text_area("H2 Headings (one per line)", placeholder="Subheading 1\nSubheading 2")
                meta_desc = st.text_area("Meta Description", placeholder="Brief description...")
                
                submit = st.form_submit_button("💾 Add URL", use_container_width=True)
                
                if submit:
                    if url and title and h1:
                        h2_list = [h.strip() for h in h2_input.split('\n') if h.strip()]
                        st.session_state.db.add_url(url, h1, h2_list, title, meta_desc)
                        st.success("✅ URL added successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ Please fill in all required fields")
        
        with st.expander("📋 View All URLs", expanded=False):
            urls = st.session_state.db.get_all_urls()
            if urls:
                for url, data in urls.items():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{data.get('title', 'No title')}**")
                        st.caption(url)
                    with col2:
                        if st.button("🗑️", key=f"del_{url}"):
                            st.session_state.db.delete_url(url)
                            st.rerun()
            else:
                st.info("No URLs added yet")
        
        if url_count > 0:
            if st.button("🗑️ Clear All URLs", use_container_width=True):
                st.session_state.db.clear_all()
                st.rerun()
    
    # Main content
    tab1, tab2 = st.tabs(["📝 Content Analysis", "📊 Results"])
    
    with tab1:
        st.subheader("Paste Your Content")
        
        content = st.text_area(
            "Content to analyze",
            height=300,
            placeholder="Paste your article or content here...",
            help="Paste the content you want to add internal links to"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            max_suggestions = st.slider("Max suggestions", 5, 20, 15)
        
        if st.button("🔍 Analyze & Generate Suggestions", type="primary", use_container_width=True):
            if not content:
                st.error("⚠️ Please paste some content first")
            elif url_count == 0:
                st.error("⚠️ Please add URLs to the database first")
            else:
                with st.spinner("🔍 Analyzing content..."):
                    urls = st.session_state.db.get_all_urls()
                    suggestions = st.session_state.suggester.generate_suggestions(
                        content, urls, max_suggestions
                    )
                    st.session_state.suggestions = suggestions
                    st.session_state.accepted_links = []
                    st.session_state.rejected_links = []
                    st.session_state.current_content = content
                
                st.success(f"✅ Found {len(suggestions)} relevant link opportunities!")
                st.info("👉 Switch to the 'Results' tab to review suggestions")
    
    with tab2:
        if st.session_state.suggestions:
            st.subheader(f"📊 Link Suggestions ({len(st.session_state.suggestions)} found)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Suggestions", len(st.session_state.suggestions))
            with col2:
                st.metric("Accepted", len(st.session_state.accepted_links))
            with col3:
                st.metric("Rejected", len(st.session_state.rejected_links))
            
            st.divider()
            
            # Display suggestions
            for idx, suggestion in enumerate(st.session_state.suggestions):
                if suggestion['url'] in st.session_state.rejected_links:
                    continue
                
                if suggestion['url'] in st.session_state.accepted_links:
                    st.success(f"✅ Accepted: {suggestion['anchor_text']} → {suggestion['url']}")
                    continue
                
                score = suggestion['score']
                if score >= 0.6:
                    score_class = "score-high"
                    score_label = "High Relevance"
                elif score >= 0.4:
                    score_class = "score-medium"
                    score_label = "Medium Relevance"
                else:
                    score_class = "score-low"
                    score_label = "Low Relevance"
                
                st.markdown(f"""
                <div class="suggestion-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0;">Suggestion #{idx + 1}</h3>
                        <span class="score-badge {score_class}">{score_label} ({score:.2%})</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Anchor Text:** `{suggestion['anchor_text']}`")
                    st.markdown(f"**Target URL:** {suggestion['url']}")
                    st.markdown(f"**Target Page:** {suggestion['target_title']}")
                    
                    with st.expander("📄 Context Preview"):
                        st.write(suggestion['context'])
                
                with col2:
                    st.write("")
                    st.write("")
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("✅ Accept", key=f"accept_{idx}", use_container_width=True):
                            st.session_state.accepted_links.append(suggestion['url'])
                            st.rerun()
                    
                    with col_b:
                        if st.button("❌ Reject", key=f"reject_{idx}", use_container_width=True):
                            st.session_state.rejected_links.append(suggestion['url'])
                            st.rerun()
                
                st.divider()
            
            # Generate final document
            if st.session_state.accepted_links:
                st.subheader("📄 Final Document")
                
                final_content = st.session_state.current_content
                
                accepted_suggestions = [s for s in st.session_state.suggestions 
                                      if s['url'] in st.session_state.accepted_links]
                
                for suggestion in accepted_suggestions:
                    anchor = suggestion['anchor_text']
                    url = suggestion['url']
                    link_html = f'<a href="{url}">{anchor}</a>'
                    final_content = final_content.replace(anchor, link_html, 1)
                
                st.code(final_content, language="html")
                
                st.download_button(
                    "💾 Download HTML Document",
                    final_content,
                    file_name="document_with_links.html",
                    mime="text/html",
                    use_container_width=True
                )
        else:
            st.info("👈 Analyze your content first to see suggestions here")

if __name__ == "__main__":
    main()
