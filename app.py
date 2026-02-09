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
    
    def add_url(self, url: str, h1: str, h2: List[str], title: str, meta_desc: str, page_type: str = "Other"):
        self.data["urls"][url] = {
            "h1": h1,
            "h2": h2,
            "title": title,
            "meta_description": meta_desc,
            "page_type": page_type,
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
    optional_cols = ['meta_description', 'h2', 'page_type', 'type', 'category']
    
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
            
            # Get or detect page type
            page_type = str(row.get('page_type', row.get('type', row.get('category', '')))).strip()
            if page_type == 'nan' or not page_type:
                # Auto-detect from URL and title
                page_type = detect_page_type(url, title, h1)
            
            # Add to database
            db.add_url(url, h1, h2_list, title, meta_desc, page_type)
            imported += 1
            
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")
    
    return imported, errors

def detect_page_type(url: str, title: str, h1: str) -> str:
    """Auto-detect page type from URL, title, and H1"""
    url_lower = url.lower()
    title_lower = title.lower()
    h1_lower = h1.lower()
    
    combined = f"{url_lower} {title_lower} {h1_lower}"
    
    # Check for product pages
    if any(word in combined for word in ['product', '/product/', '/shop/', 'buy', 'price', '/item/']):
        return "Product"
    
    # Check for glossary/definition pages
    if any(word in combined for word in ['glossary', 'definition', 'what is', 'meaning of', '/glossary/', '/define/']):
        return "Glossary"
    
    # Check for guide pages
    if any(word in combined for word in ['guide', 'tutorial', 'how to', 'step by step', 'complete guide', 'ultimate guide']):
        return "Guide"
    
    # Check for blog pages
    if any(word in combined for word in ['/blog/', 'article', '/post/', '/news/', 'tips']):
        return "Blog"
    
    # Check for category pages
    if any(word in combined for word in ['category', 'categories', '/cat/', 'collection']):
        return "Category"
    
    # Check for landing pages
    if any(word in combined for word in ['landing', 'services', 'solutions']):
        return "Landing Page"
    
    return "Other"

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
        
        # Prepare URL texts and organize by page type
        url_texts = {}
        url_by_type = {}
        
        for url, data in url_database.items():
            combined_text = f"{data.get('title', '')}. {data.get('h1', '')}. {data.get('meta_description', '')}. {' '.join(data.get('h2', []))}"
            url_texts[url] = combined_text
            
            page_type = data.get('page_type', 'Other')
            if page_type not in url_by_type:
                url_by_type[page_type] = []
            url_by_type[page_type].append(url)
        
        all_suggestions = []
        url_list = list(url_database.keys())
        
        # Process each chunk
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
                
                # Boost score based on page type diversity
                page_type = url_database[url].get('page_type', 'Other')
                
                # Slight boost for non-blog pages to ensure diversity
                if page_type in ['Product', 'Glossary', 'Guide']:
                    score *= 1.1
                elif page_type == 'Landing Page':
                    score *= 1.05
                
                scores.append((url, score))
            
            # Get top matches for this chunk
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Add top 3 suggestions per chunk
            for url, score in scores[:3]:
                if score > 0.20:  # Lower threshold for more suggestions
                    anchor = self.suggest_anchor_text(chunk_text, url_database[url])
                    
                    all_suggestions.append({
                        'url': url,
                        'anchor_text': anchor,
                        'context': chunk_text[:150] + "...",
                        'score': score,
                        'position': chunk['position'],
                        'target_h1': url_database[url].get('h1', ''),
                        'target_title': url_database[url].get('title', ''),
                        'page_type': url_database[url].get('page_type', 'Other')
                    })
        
        # Deduplicate and ensure diversity
        seen_urls = set()
        diverse_suggestions = []
        page_type_counts = {}
        
        # Sort by score
        all_suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        # First pass: Add high-scoring suggestions (>0.5) ensuring diversity
        for sugg in all_suggestions:
            if sugg['url'] in seen_urls:
                continue
            
            page_type = sugg['page_type']
            
            # Limit suggestions per page type to ensure diversity
            type_count = page_type_counts.get(page_type, 0)
            
            # Allow more for diverse types, limit blog to 40% of total
            if page_type == 'Blog' and type_count >= max_suggestions * 0.4:
                continue
            elif type_count >= max_suggestions * 0.5:
                continue
            
            if sugg['score'] > 0.35:  # Higher threshold for first pass
                seen_urls.add(sugg['url'])
                diverse_suggestions.append(sugg)
                page_type_counts[page_type] = type_count + 1
                
                if len(diverse_suggestions) >= max_suggestions:
                    break
        
        # Second pass: Fill remaining slots with any good matches
        if len(diverse_suggestions) < max_suggestions:
            for sugg in all_suggestions:
                if sugg['url'] in seen_urls:
                    continue
                
                if sugg['score'] > 0.25:  # Lower threshold
                    seen_urls.add(sugg['url'])
                    diverse_suggestions.append(sugg)
                    
                    if len(diverse_suggestions) >= max_suggestions:
                        break
        
        # Sort final results by score
        diverse_suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        return diverse_suggestions[:max_suggestions]

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
        
        # Status indicator
        if url_count > 0:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                <h3>{url_count}</h3>
                <p>URLs Ready ✅</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check if file exists
            file_info = get_uploaded_file_info()
            if file_info['exists']:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);">
                    <h3>⚠️</h3>
                    <p>File Uploaded<br>Need to Import!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
                    <h3>0</h3>
                    <p>No URLs Yet</p>
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
                st.success(f"""
                ✅ **File uploaded:** {file_info['name']}  
                📊 **Size:** {file_info['size'] / 1024:.1f} KB  
                🕒 **Uploaded:** {file_info['modified'].strftime('%Y-%m-%d %H:%M')}
                """)
                
                # Check if database is empty
                current_url_count = len(st.session_state.db.get_all_urls())
                
                if current_url_count == 0:
                    st.warning("⚠️ **File uploaded but URLs not imported yet!**")
                    st.info("👇 Click the button below to load URLs from your file:")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 LOAD URLs FROM FILE", 
                               use_container_width=True,
                               type="primary",
                               key="reload_from_file"):
                        with st.spinner("📥 Loading URLs from file..."):
                            imported, errors = import_urls_from_file(file_info['path'], st.session_state.db)
                        
                        if imported > 0:
                            st.success(f"✅ Loaded {imported} URLs into database!")
                            st.balloons()
                        else:
                            st.error("❌ No URLs were loaded")
                        
                        if errors:
                            with st.expander("⚠️ View Errors"):
                                for error in errors[:10]:
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
                    
                    st.write(f"**📊 Preview** ({len(df)} rows found)")
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # Check for required columns
                    required_cols = ['url', 'title', 'h1']
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                        st.info("Required: url, title, h1")
                    else:
                        st.success(f"✅ All required columns found!")
                        
                        # Import button
                        st.markdown("---")
                        st.markdown("**⚠️ IMPORTANT:** Click the button below to import URLs into database")
                        
                        if st.button("📥 IMPORT URLs INTO DATABASE", 
                                   use_container_width=True, 
                                   type="primary",
                                   key="import_urls_button"):
                            # Save file
                            with st.spinner("💾 Saving file..."):
                                file_path = save_uploaded_file(uploaded_file)
                            
                            # Import URLs
                            with st.spinner("📥 Importing URLs into database..."):
                                imported, errors = import_urls_from_file(file_path, st.session_state.db)
                            
                            if imported > 0:
                                st.success(f"✅ Successfully imported {imported} URLs into database!")
                                st.balloons()
                            else:
                                st.error("❌ No URLs were imported")
                            
                            if errors:
                                st.warning(f"⚠️ {len(errors)} errors occurred")
                                with st.expander("View Errors"):
                                    for error in errors[:10]:
                                        st.caption(error)
                            
                            st.info("👉 Now you can analyze your content!")
                            st.rerun()
                    
                    # Download template button
                    st.markdown("---")
                    st.markdown("**Need a template?**")
                    
                    template_data = {
                        'url': ['https://example.com/seo-guide', 'https://example.com/keyword-tool'],
                        'title': ['SEO Guide 2024', 'Keyword Research Tool'],
                        'h1': ['Complete SEO Guide', 'Find Keywords Fast'],
                        'meta_description': ['Learn SEO basics and advanced techniques', 'Discover profitable keywords for your content'],
                        'h2': ['Basics; Advanced; Tools', 'Features; Pricing'],
                        'page_type': ['Guide', 'Product']
                    }
                    template_df = pd.DataFrame(template_data)
                    
                    # Convert to Excel bytes
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        template_df.to_excel(writer, index=False, sheet_name='URLs')
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        "📄 Download Template",
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
                
                page_type = st.selectbox(
                    "Page Type*",
                    options=["Blog", "Product", "Glossary", "Guide", "Category", "Landing Page", "Other"],
                    help="Select the type of page"
                )
                
                submit = st.form_submit_button("💾 Add URL", use_container_width=True)
                
                if submit:
                    if url and title and h1:
                        h2_list = [h.strip() for h in h2_input.split('\n') if h.strip()]
                        st.session_state.db.add_url(url, h1, h2_list, title, meta_desc, page_type)
                        st.success("✅ URL added successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ Please fill in all required fields")
        
        with st.expander("📋 View All URLs", expanded=False):
            urls = st.session_state.db.get_all_urls()
            if urls:
                # Group by page type
                urls_by_type = {}
                for url, data in urls.items():
                    page_type = data.get('page_type', 'Other')
                    if page_type not in urls_by_type:
                        urls_by_type[page_type] = []
                    urls_by_type[page_type].append((url, data))
                
                # Show counts by type
                st.markdown("**📊 By Type:**")
                type_counts = {pt: len(urls) for pt, urls in urls_by_type.items()}
                cols = st.columns(len(type_counts))
                for idx, (page_type, count) in enumerate(type_counts.items()):
                    with cols[idx]:
                        st.metric(page_type, count)
                
                st.markdown("---")
                
                # Show URLs grouped by type
                for page_type, url_list in sorted(urls_by_type.items()):
                    st.markdown(f"**{page_type} ({len(url_list)})**")
                    for url, data in url_list:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"📄 **{data.get('title', 'No title')}**")
                            st.caption(url)
                        with col2:
                            if st.button("🗑️", key=f"del_{url}"):
                                st.session_state.db.delete_url(url)
                                st.rerun()
                    st.markdown("---")
            else:
                st.info("No URLs added yet")
        
        if url_count > 0:
            if st.button("🗑️ Clear All URLs", use_container_width=True):
                st.session_state.db.clear_all()
                st.rerun()
    
    # Main content area - SPLIT VIEW
    st.subheader("📝 Content Analysis & Link Suggestions")
    
    # Two column layout
    col_editor, col_suggestions = st.columns([1.2, 1], gap="large")
    
    with col_editor:
        st.markdown("### 📄 Your Content")
        
        content = st.text_area(
            "Paste your content here",
            height=500,
            placeholder="Paste your article or content here...\n\nThe tool will analyze and suggest relevant internal links from all your page types (blog, products, glossary, guides, etc.)",
            help="Paste the content you want to add internal links to",
            key="content_editor"
        )
        
        col1, col2 = st.columns([1, 2])
        with col1:
            max_suggestions = st.slider("Max suggestions", 5, 25, 15)
        
        with col2:
            if st.button("🔍 Analyze & Generate Suggestions", type="primary", use_container_width=True):
                if not content:
                    st.error("⚠️ Please paste some content first")
                elif url_count == 0:
                    # Check if there's an uploaded file
                    file_info = get_uploaded_file_info()
                    if file_info['exists']:
                        st.error("⚠️ File uploaded but URLs not loaded into database!")
                        st.info("👉 Go to sidebar → 'Upload Excel/CSV File' → Click '📥 LOAD URLs FROM FILE'")
                    else:
                        st.error("⚠️ Please add URLs to the database first")
                        st.info("👉 Upload a file or add URLs manually in the sidebar")
                else:
                    with st.spinner("🤖 Analyzing content..."):
                        urls = st.session_state.db.get_all_urls()
                        suggestions = st.session_state.suggester.generate_suggestions(
                            content, urls, max_suggestions
                        )
                        st.session_state.suggestions = suggestions
                        st.session_state.accepted_links = []
                        st.session_state.rejected_links = []
                        st.session_state.current_content = content
                    
                    st.success(f"✅ Found {len(suggestions)} relevant link opportunities!")
        
        # Show current content with accepted links highlighted
        if st.session_state.accepted_links and hasattr(st.session_state, 'current_content'):
            st.markdown("---")
            st.markdown("### ✅ Content with Accepted Links")
            
            # Create preview with accepted links
            final_content = st.session_state.current_content
            accepted_suggestions = [s for s in st.session_state.suggestions 
                                  if s['url'] in st.session_state.accepted_links]
            
            for suggestion in accepted_suggestions:
                anchor = suggestion['anchor_text']
                url = suggestion['url']
                link_html = f'<a href="{url}" style="color: #2E86AB; font-weight: bold;">{anchor}</a>'
                final_content = final_content.replace(anchor, link_html, 1)
            
            st.markdown(final_content, unsafe_allow_html=True)
            
            st.download_button(
                "💾 Download HTML Document",
                final_content,
                file_name="document_with_links.html",
                mime="text/html",
                use_container_width=True
            )
    
    with col_suggestions:
        st.markdown("### 🔗 Link Suggestions")
        
        if st.session_state.suggestions:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(st.session_state.suggestions))
            with col2:
                st.metric("✅", len(st.session_state.accepted_links))
            with col3:
                st.metric("❌", len(st.session_state.rejected_links))
            
            st.markdown("---")
            
            # Scrollable suggestions area
            suggestions_container = st.container()
            
            with suggestions_container:
                for idx, suggestion in enumerate(st.session_state.suggestions):
                    if suggestion['url'] in st.session_state.rejected_links:
                        continue
                    
                    if suggestion['url'] in st.session_state.accepted_links:
                        st.success(f"✅ **{suggestion['anchor_text']}**")
                        st.caption(f"→ {suggestion['url']}")
                        st.markdown("---")
                        continue
                    
                    # Score badge
                    score = suggestion['score']
                    if score >= 0.6:
                        score_class = "score-high"
                        score_label = "High"
                        score_emoji = "🟢"
                    elif score >= 0.4:
                        score_class = "score-medium"
                        score_label = "Medium"
                        score_emoji = "🟡"
                    else:
                        score_class = "score-low"
                        score_label = "Low"
                        score_emoji = "🟠"
                    
                    # Compact suggestion card
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #2E86AB; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong>#{idx + 1}</strong>
                            <span class="score-badge {score_class}">{score_emoji} {score_label} {score:.0%}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Anchor:** `{suggestion['anchor_text']}`")
                    st.caption(f"**Page:** {suggestion['target_title']}")
                    st.caption(f"**URL:** {suggestion['url']}")
                    
                    # Page type indicator if available
                    page_type = suggestion.get('page_type', 'Unknown')
                    if page_type != 'Unknown':
                        st.caption(f"📑 **Type:** {page_type}")
                    
                    with st.expander("👁️ Context"):
                        st.write(suggestion['context'])
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅", key=f"accept_{idx}", use_container_width=True):
                            st.session_state.accepted_links.append(suggestion['url'])
                            st.rerun()
                    
                    with col_b:
                        if st.button("❌", key=f"reject_{idx}", use_container_width=True):
                            st.session_state.rejected_links.append(suggestion['url'])
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("👈 Paste content and click 'Analyze' to see suggestions here")
            
            # Show example of what suggestions will look like
            st.markdown("### Example Suggestion")
            st.markdown("""
            <div style="background: #f8f9fa; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #2E86AB;">
                <strong>#1</strong> <span style="background: #d4edda; color: #155724; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.85rem;">🟢 High 85%</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**Anchor:** `keyword research`")
            st.caption("**Page:** Keyword Research Guide")
            st.caption("**Type:** Guide")
            st.caption("**Context:** Finding the right keywords...")


if __name__ == "__main__":
    main()
