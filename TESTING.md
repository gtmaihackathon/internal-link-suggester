# 🧪 Testing Guide

Complete testing checklist to ensure your Internal Link Suggester works perfectly.

## Quick Test (5 minutes)

### Step 1: Setup Test Data

Run the quick start script:
```bash
python quickstart.py
```

This loads 6 sample URLs into your database.

### Step 2: Launch App

```bash
streamlit run app.py
```

### Step 3: Basic Test

1. **Verify Database**
   - Check sidebar shows "6 URLs in Database"
   - Click "📋 View All URLs"
   - Verify all 6 URLs are listed

2. **Test Analysis**
   - Go to "📝 Content Analysis" tab
   - Paste this sample text:
   ```
   SEO is crucial for online success. Keyword research helps you find the right terms. 
   Content marketing drives engagement. Link building improves authority. 
   For local businesses, local SEO is essential.
   ```
   - Set "Max suggestions" to 10
   - Click "🔍 Analyze & Generate Suggestions"
   - Should see 5-8 suggestions

3. **Review Suggestions**
   - Switch to "📊 Results" tab
   - Verify suggestions appear with:
     - ✅ Relevance scores
     - ✅ Anchor text
     - ✅ Target URLs
     - ✅ Context preview
   - All high-relevance suggestions should be >70%

4. **Accept/Reject Flow**
   - Click "✅ Accept" on 2-3 suggestions
   - Click "❌ Reject" on 1-2 suggestions
   - Verify counters update correctly

5. **Export Document**
   - Scroll to "📄 Final Document"
   - Verify HTML contains accepted links
   - Download and check file opens

### Expected Result
✅ All features working  
✅ Suggestions are relevant  
✅ Accept/reject works  
✅ Export successful

---

## Comprehensive Test (15 minutes)

### Test 1: URL Management

**Add URL:**
```
URL: https://example.com/test-page
Title: Test Page Title
H1: Test Main Heading
H2: 
Test Subheading 1
Test Subheading 2
Meta: This is a test page
```

**Verify:**
- ✅ URL added successfully
- ✅ Counter increases to 7
- ✅ URL appears in list

**Delete URL:**
- Click 🗑️ next to test URL
- Verify it's removed
- Counter back to 6

**Clear All:**
- Click "🗑️ Clear All URLs"
- Confirm action
- Verify all URLs removed
- Reload sample data with `python quickstart.py`

### Test 2: Content Analysis Variations

**Short Content (100 words):**
```
SEO optimization is important. Keyword research finds opportunities.
Technical SEO improves performance. Content marketing engages users.
Link building creates authority.
```
- Should get 3-5 suggestions
- Relevance scores: 50-80%

**Medium Content (300 words):**
```
Search engine optimization requires comprehensive strategy. Start with keyword research
to identify target terms. Use tools to analyze competition and search volume.

Technical SEO ensures your site is crawlable. Improve site speed, fix broken links,
and implement schema markup. Mobile optimization is crucial for rankings.

Content marketing drives organic traffic. Create valuable content that answers
user questions. Optimize for search intent and readability.

Link building remains important. Focus on quality over quantity. Guest posting
and relationship building generate natural backlinks.

For local businesses, optimize Google My Business. Build citations and encourage
reviews. Create location-specific content.
```
- Should get 8-12 suggestions
- Mix of high/medium relevance
- Different anchor text options

**Long Content (500+ words):**
- Use content from SAMPLE_DATA.md
- Should get 12-15 suggestions
- All major topics covered

### Test 3: Embedding Quality

**Test semantic similarity:**

Content about "keyword research":
```
Finding the right keywords is essential for SEO success. Use keyword research tools
to discover opportunities. Focus on long-tail keywords with lower competition.
Analyze competitor keywords to find gaps.
```

**Expected:**
- "Keyword Research Tutorial" should be top suggestion
- Score >75%
- Anchor text: "keyword research" or "keyword research tools"

**Test irrelevant content:**
```
The weather is nice today. I like pizza and coffee. 
My favorite color is blue. Dogs are great pets.
```

**Expected:**
- Few or no suggestions
- Low relevance scores (<40%)
- Shows system correctly filters irrelevant matches

### Test 4: Edge Cases

**Very short content:**
```
SEO is important.
```
- Should handle gracefully
- May show 0-1 suggestions

**Empty content:**
- Click analyze with empty text area
- Should show error message
- No crash

**Special characters:**
```
SEO & keyword research! Technical optimization? Link building (2024).
```
- Should handle special chars
- Normal suggestions

**Multiple languages:**
```
SEO optimization. Optimización de motores de búsqueda. 搜索引擎优化
```
- English content gets suggestions
- Other languages may have lower scores

### Test 5: UI/UX Testing

**Responsiveness:**
- Resize browser window
- Check mobile view (DevTools)
- Sidebar should collapse on mobile
- All buttons visible

**Loading States:**
- First analysis should show spinner
- "Analyzing content with AI..."
- Progress indication

**Error Handling:**
- Try with 0 URLs in database
- Try with corrupted database file
- App should handle gracefully

**Performance:**
- 10 URLs: <3 seconds analysis
- 50 URLs: <10 seconds analysis
- 100 URLs: <30 seconds analysis

### Test 6: Data Persistence

**Test session persistence:**
1. Add 3 URLs
2. Run analysis
3. Accept 2 suggestions
4. Refresh page (F5)
5. Verify:
   - ✅ URLs still in database
   - ❌ Suggestions cleared (expected)
   - ❌ Accepted links cleared (expected)

**Test database file:**
1. Add URLs
2. Close app
3. Check `url_database.json` exists
4. Restart app
5. URLs should persist

---

## Load Testing

### Test with Many URLs

**Create 100 test URLs:**
```python
# Run this script
import json
from datetime import datetime

data = {"urls": {}, "last_updated": datetime.now().isoformat()}

for i in range(100):
    url = f"https://example.com/page-{i}"
    data["urls"][url] = {
        "title": f"Page {i} Title - SEO Guide",
        "h1": f"Main Heading for Page {i}",
        "h2": [f"Subheading {i}-1", f"Subheading {i}-2"],
        "meta_description": f"Meta description for page {i} about SEO and optimization",
        "added_date": datetime.now().isoformat()
    }

with open("url_database.json", "w") as f:
    json.dump(data, f, indent=2)

print("Created 100 test URLs")
```

**Test performance:**
- Run analysis
- Should complete in <30 seconds
- All suggestions should be relevant
- No memory errors

### Stress Test

**Large content (2000+ words):**
- Paste very long article
- Should handle without crash
- May take 10-15 seconds
- Consider pagination for very long content

---

## Automated Testing

### Unit Tests

Create `test_app.py`:
```python
import unittest
from app import URLDatabase, LinkSuggester

class TestURLDatabase(unittest.TestCase):
    def setUp(self):
        self.db = URLDatabase("test_db.json")
    
    def test_add_url(self):
        self.db.add_url(
            "https://test.com",
            "Test H1",
            ["H2-1"],
            "Test Title",
            "Test meta"
        )
        urls = self.db.get_all_urls()
        self.assertIn("https://test.com", urls)
    
    def test_delete_url(self):
        self.db.add_url("https://test.com", "H1", [], "Title", "Meta")
        self.db.delete_url("https://test.com")
        urls = self.db.get_all_urls()
        self.assertNotIn("https://test.com", urls)

class TestLinkSuggester(unittest.TestCase):
    def setUp(self):
        self.suggester = LinkSuggester()
    
    def test_extract_chunks(self):
        text = "This is a test. " * 50
        chunks = self.suggester.extract_text_chunks(text)
        self.assertGreater(len(chunks), 0)
    
    def test_suggest_anchor_text(self):
        chunk = "This is about SEO optimization and keyword research"
        url_data = {"h1": "SEO Guide", "title": "SEO", "h2": []}
        anchor = self.suggester.suggest_anchor_text(chunk, url_data)
        self.assertTrue(len(anchor) > 0)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python test_app.py
```

---

## Browser Compatibility

Test in multiple browsers:
- ✅ Chrome (Latest)
- ✅ Firefox (Latest)
- ✅ Safari (Latest)
- ✅ Edge (Latest)
- ✅ Mobile Safari (iOS)
- ✅ Chrome Mobile (Android)

---

## Deployment Testing

### Pre-Deployment Checklist

- [ ] All local tests pass
- [ ] Database persists correctly
- [ ] UI looks good on mobile
- [ ] No console errors
- [ ] Requirements.txt updated
- [ ] README is clear
- [ ] Sample data works

### Post-Deployment Testing

After deploying to Streamlit Cloud:

1. **Verify app loads**
   - No errors on startup
   - Model downloads successfully
   - UI renders correctly

2. **Test core features**
   - Add URL
   - Analyze content
   - Accept/reject suggestions
   - Download document

3. **Check performance**
   - Initial load: <10 seconds
   - Analysis: <5 seconds
   - No timeouts

4. **Monitor logs**
   - Check for warnings
   - Verify no errors
   - Monitor resource usage

---

## Bug Report Template

If you find a bug:

```markdown
**Bug Description:**
[What went wrong?]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**
[What should happen?]

**Actual Behavior:**
[What actually happened?]

**Screenshots:**
[If applicable]

**Environment:**
- OS: [Windows/Mac/Linux]
- Browser: [Chrome/Firefox/Safari]
- App Version: [Local/Cloud]

**Additional Context:**
[Any other info]
```

---

## Performance Benchmarks

### Target Metrics

| Operation | Time Limit | Actual |
|-----------|-----------|--------|
| App startup | <10s | ✓ |
| Model load | <5s | ✓ |
| Add URL | <1s | ✓ |
| Analyze (10 URLs) | <3s | ✓ |
| Analyze (50 URLs) | <10s | ✓ |
| Analyze (100 URLs) | <30s | ✓ |
| Generate suggestions | <2s | ✓ |

### Resource Usage

| Resource | Limit | Expected |
|----------|-------|----------|
| RAM | <1GB | 400-600MB |
| CPU | <80% | 20-50% |
| Storage | <500MB | 100-200MB |

---

## Success Criteria

Your app passes all tests if:

- ✅ All basic features work
- ✅ Suggestions are relevant (>60% accuracy)
- ✅ No crashes or errors
- ✅ Performance within targets
- ✅ Data persists correctly
- ✅ UI is responsive
- ✅ Export works correctly

---

## Continuous Testing

**After each update:**
1. Run quick test (5 min)
2. Check specific feature changed
3. Verify no regressions
4. Update tests if needed

**Weekly:**
- Full comprehensive test
- Check for edge cases
- Review user feedback
- Update documentation

---

**Happy Testing! 🧪**

Report issues on GitHub if you find any problems.
