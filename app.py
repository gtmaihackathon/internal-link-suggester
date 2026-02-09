import streamlit as st
import json
import os
from datetime import datetime
import re
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer, util
from collections import defaultdict

# Page config
st.set_page_config(
    page_title="Smart Internal Link Suggester",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
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
    .url-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
        margin-bottom: 0.5rem;
    }
    .suggestion-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .suggestion-card:hover {
        border-color: #2E86AB;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
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
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .accept-btn {
        background: #28a745 !important;
        color: white !important;
    }
    .reject-btn {
        background: #dc3545 !important;
        color: white !important;
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

# Database file path
DB_FILE = "url_database.json"
MODEL_NAME = 'all-MiniLM-L6-v2'

class URLDatabase:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.data = self.load()
    
    def load(self) -> Dict:
        """Load database from file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"urls": {}, "last_updated": None}
    
    def save(self):
        """Save database to file"""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_url(self, url: str, h1: str, h2: List[str], title: str, meta_desc: str):
        """Add or update a URL in the database"""
        self.data["urls"][url] = {
            "h1": h1,
            "h2": h2,
            "title": title,
            "meta_description": meta_desc,
            "added_date": datetime.now().isoformat()
        }
        self.save()
    
    def get_all_urls(self) -> Dict:
        """Get all URLs"""
        return self.data.get("urls", {})
    
    def delete_url(self, url: str):
        """Delete a URL from database"""
        if url in self.data["urls"]:
            del self.data["urls"][url]
            self.save()
    
    def clear_all(self):
        """Clear all URLs"""
        self.data = {"urls": {}, "last_updated": None}
        self.save()

class LinkSuggester:
    def __init__(self):
        self.model = self._load_model()
    
    @st.cache_resource
    def _load_model(_self):
        """Load sentence transformer model"""
        return SentenceTransformer(MODEL_NAME)
    
    def extract_text_chunks(self, content: str, chunk_size: int = 200) -> List[Dict]:
        """Extract meaningful text chunks from content"""
        # Split into sentences
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
    
    def calculate_relevance_score(self, content_embedding, url_embedding, 
                                   url_data: Dict, content: str) -> float:
        """Calculate comprehensive relevance score"""
        # Cosine similarity score (0-1)
        cosine_score = util.cos_sim(content_embedding, url_embedding).item()
        
        # Boost score based on keyword overlap
        content_lower = content.lower()
        url_text = f"{url_data.get('h1', '')} {url_data.get('title', '')} {' '.join(url_data.get('h2', []))}".lower()
        
        # Extract keywords (simple approach)
        content_words = set(re.findall(r'\b\w{4,}\b', content_lower))
        url_words = set(re.findall(r'\b\w{4,}\b', url_text))
        
        if content_words:
            keyword_overlap = len(content_words & url_words) / len(content_words)
        else:
            keyword_overlap = 0
        
        # Weighted final score
        final_score = (cosine_score * 0.7) + (keyword_overlap * 0.3)
        
        return final_score
    
    def suggest_anchor_text(self, chunk: str, url_data: Dict) -> str:
        """Suggest appropriate anchor text based on context"""
        chunk_lower = chunk.lower()
        
        # Check for exact or close matches with h1, title
        h1 = url_data.get('h1', '').lower()
        title = url_data.get('title', '').lower()
        
        # Look for natural phrase matches
        candidates = []
        
        # Try to find h1 or title in the chunk
        if h1 and h1 in chunk_lower:
            start = chunk_lower.index(h1)
            candidates.append(chunk[start:start+len(h1)])
        
        if title and title in chunk_lower:
            start = chunk_lower.index(title)
            candidates.append(chunk[start:start+len(title)])
        
        # Look for h2 matches
        for h2 in url_data.get('h2', []):
            h2_lower = h2.lower()
            if h2_lower in chunk_lower:
                start = chunk_lower.index(h2_lower)
                candidates.append(chunk[start:start+len(h2)])
        
        if candidates:
            # Return the longest match
            return max(candidates, key=len)
        
        # Fall back to h1 or title
        return url_data.get('h1', url_data.get('title', 'Learn more'))
    
    def generate_suggestions(self, content: str, url_database: Dict, 
                           max_suggestions: int = 15) -> List[Dict]:
        """Generate internal link suggestions using semantic analysis"""
        if not url_database:
            return []
        
        # Extract chunks from content
        chunks = self.extract_text_chunks(content)
        
        # Prepare URL data for embedding
        url_texts = {}
        for url, data in url_database.items():
            # Combine all text fields for better semantic understanding
            combined_text = f"{data.get('title', '')}. {data.get('h1', '')}. {data.get('meta_description', '')}. {' '.join(data.get('h2', []))}"
            url_texts[url] = combined_text
        
        # Generate embeddings
        chunk_embeddings = self.model.encode([chunk['text'] for chunk in chunks])
        url_embeddings = self.model.encode(list(url_texts.values()))
        
        # Find best matches for each chunk
        suggestions = []
        url_list = list(url_database.keys())
        
        for i, chunk in enumerate(chunks):
            chunk_embedding = chunk_embeddings[i]
            
            # Calculate scores for all URLs
            scores = []
            for j, url in enumerate(url_list):
                score = self.calculate_relevance_score(
                    chunk_embedding,
                    url_embeddings[j],
                    url_database[url],
                    chunk['text']
                )
                scores.append((url, score))
            
            # Get top matches for this chunk
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Add top 2-3 suggestions per chunk
            for url, score in scores[:2]:
                if score > 0.3:  # Minimum threshold
                    anchor = self.suggest_anchor_text(chunk['text'], url_database[url])
                    
                    suggestions.append({
                        'url': url,
                        'anchor_text': anchor,
                        'context': chunk['text'][:150] + "...",
                        'score': score,
                        'position': chunk['position'],
                        'target_h1': url_database[url].get('h1', ''),
                        'target_title': url_database[url].get('title', '')
                    })
        
        # Remove duplicates and sort by score
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
    st.markdown('<p class="sub-header">AI-powered semantic analysis for intelligent internal linking</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Database stats
        url_count = len(st.session_state.db.get_all_urls())
        st.markdown(f"""
        <div class="metric-card">
            <h3>{url_count}</h3>
            <p>URLs in Database</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # URL Management
        st.subheader("📚 Manage URLs")
        
        with st.expander("➕ Add New URL", expanded=False):
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
    
    # Main content area
    tab1, tab2 = st.tabs(["📝 Content Analysis", "📊 Results"])
    
    with tab1:
        st.subheader("Paste Your Content")
        
        content = st.text_area(
            "Content to analyze",
            height=300,
            placeholder="Paste your article or content here...\n\nThe tool will analyze your content and suggest relevant internal links based on semantic similarity with your URL database.",
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
                with st.spinner("🤖 Analyzing content with AI..."):
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
            
            # Summary metrics
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
                
                # Score badge
                score = suggestion['score']
                if score >= 0.7:
                    score_class = "score-high"
                    score_label = "High Relevance"
                elif score >= 0.5:
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
                
                # Create document with accepted links
                final_content = st.session_state.current_content
                
                # Sort by position (reverse to maintain correct indices)
                accepted_suggestions = [s for s in st.session_state.suggestions 
                                      if s['url'] in st.session_state.accepted_links]
                
                for suggestion in accepted_suggestions:
                    # Find the anchor text in content and replace with link
                    anchor = suggestion['anchor_text']
                    url = suggestion['url']
                    
                    # Create HTML link
                    link_html = f'<a href="{url}">{anchor}</a>'
                    
                    # Replace first occurrence near the position
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
