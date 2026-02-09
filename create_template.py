#!/usr/bin/env python3
"""
Generate Sample Excel Template for URL Import
Run this to create a template file you can use
"""

import pandas as pd
from datetime import datetime

def create_template():
    """Create Excel template with sample data"""
    
    # Sample data
    data = {
        'url': [
            'https://example.com/seo-guide',
            'https://example.com/keyword-research',
            'https://example.com/content-marketing',
            'https://example.com/link-building',
            'https://example.com/local-seo'
        ],
        'title': [
            'Complete SEO Guide 2024 - Boost Your Rankings',
            'Keyword Research Tutorial - Find the Right Keywords',
            'Content Marketing Strategy - Drive Traffic',
            'Link Building Guide - Build Quality Backlinks',
            'Local SEO Guide - Rank in Local Search'
        ],
        'h1': [
            'The Ultimate SEO Guide for 2024',
            'Keyword Research: Complete Tutorial',
            'Content Marketing Strategy Guide',
            'Link Building Strategies That Work',
            'Local SEO: Complete Guide'
        ],
        'meta_description': [
            'Learn everything about SEO in 2024. Complete guide covering on-page, technical SEO, link building, and content optimization.',
            'Discover how to find profitable keywords. Complete tutorial on keyword research tools, long-tail keywords, and competitive analysis.',
            'Master content marketing with our comprehensive guide. Learn to create engaging content, distribute effectively, and measure ROI.',
            'Build high-quality backlinks with proven link building strategies. Learn guest posting, broken link building, and relationship building.',
            'Dominate local search with our local SEO guide. Optimize Google My Business, build citations, manage reviews, and create local content.'
        ],
        'h2': [
            'What is SEO?; On-Page SEO Techniques; Technical SEO Checklist; Link Building Strategies; Content Optimization',
            'Why Keywords Matter; Keyword Research Tools; Long-tail Keywords; Competitor Analysis; Search Intent',
            'Understanding Content Marketing; Creating Engaging Content; Distribution Channels; Measuring Performance; ROI Tracking',
            'White Hat Link Building; Guest Posting Tips; Broken Link Building; Building Relationships; Outreach Strategy',
            'Google My Business; Local Citations; Reviews Management; Local Content Strategy; Local Schema Markup'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to Excel
    filename = 'url_import_template.xlsx'
    df.to_excel(filename, index=False, sheet_name='URLs')
    
    print(f"✅ Template created: {filename}")
    print(f"📊 {len(df)} sample URLs included")
    print(f"\nColumns:")
    for col in df.columns:
        print(f"  - {col}")
    print(f"\nYou can now:")
    print(f"1. Open {filename} in Excel or Google Sheets")
    print(f"2. Modify the sample data or add your own")
    print(f"3. Upload to the app")
    
    return filename

def create_empty_template():
    """Create empty template for users to fill"""
    
    data = {
        'url': ['https://example.com/page1', 'https://example.com/page2'],
        'title': ['Page Title 1', 'Page Title 2'],
        'h1': ['Main Heading 1', 'Main Heading 2'],
        'meta_description': ['Meta description for page 1', 'Meta description for page 2'],
        'h2': ['H2-1; H2-2; H2-3', 'H2-A; H2-B; H2-C']
    }
    
    df = pd.DataFrame(data)
    
    filename = 'url_template_empty.xlsx'
    df.to_excel(filename, index=False, sheet_name='URLs')
    
    print(f"\n✅ Empty template created: {filename}")
    print(f"📝 2 example rows included - replace with your data")
    
    return filename

if __name__ == "__main__":
    print("📤 URL Import Template Generator")
    print("=" * 50)
    print()
    
    # Create templates
    template_file = create_template()
    empty_file = create_empty_template()
    
    print("\n" + "=" * 50)
    print("🎉 Templates ready!")
    print(f"\n📁 Files created:")
    print(f"  1. {template_file} - With 5 sample URLs")
    print(f"  2. {empty_file} - Empty template to fill")
    print("\n💡 Tip: Open in Excel or Google Sheets to edit")
