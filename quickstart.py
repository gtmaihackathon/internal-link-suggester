#!/usr/bin/env python3
"""
Quick Start Script - Loads sample data automatically
Run this to quickly test the app with pre-loaded URLs
"""

import json
import os

def create_sample_database():
    """Create a sample URL database for testing"""
    
    sample_data = {
        "urls": {
            "https://example.com/seo-guide": {
                "h1": "The Ultimate SEO Guide for 2024",
                "h2": [
                    "What is SEO?",
                    "On-Page SEO Techniques",
                    "Technical SEO Checklist",
                    "Link Building Strategies",
                    "Content Optimization Tips"
                ],
                "title": "Complete SEO Guide 2024 - Boost Your Rankings",
                "meta_description": "Learn everything about SEO in 2024. Complete guide covering on-page, technical SEO, link building, and content optimization strategies.",
                "added_date": "2024-01-01T00:00:00"
            },
            "https://example.com/content-marketing": {
                "h1": "Content Marketing Strategy Guide",
                "h2": [
                    "Understanding Content Marketing",
                    "Creating Engaging Content",
                    "Content Distribution Channels",
                    "Measuring Content Performance"
                ],
                "title": "Content Marketing Strategy - Drive Traffic & Engagement",
                "meta_description": "Master content marketing with our comprehensive guide. Learn to create engaging content, distribute effectively, and measure ROI.",
                "added_date": "2024-01-01T00:00:00"
            },
            "https://example.com/keyword-research": {
                "h1": "Keyword Research: Complete Tutorial",
                "h2": [
                    "Why Keyword Research Matters",
                    "Tools for Keyword Research",
                    "Long-tail Keywords",
                    "Competitor Analysis"
                ],
                "title": "Keyword Research Tutorial - Find the Right Keywords",
                "meta_description": "Discover how to find profitable keywords. Complete tutorial on keyword research tools, long-tail keywords, and competitive analysis.",
                "added_date": "2024-01-01T00:00:00"
            },
            "https://example.com/link-building": {
                "h1": "Link Building Strategies That Work",
                "h2": [
                    "White Hat Link Building",
                    "Guest Posting Tips",
                    "Broken Link Building",
                    "Building Relationships"
                ],
                "title": "Link Building Guide - Build Quality Backlinks",
                "meta_description": "Build high-quality backlinks with proven link building strategies. Learn guest posting, broken link building, and relationship building.",
                "added_date": "2024-01-01T00:00:00"
            },
            "https://example.com/local-seo": {
                "h1": "Local SEO: Complete Guide",
                "h2": [
                    "Google My Business Optimization",
                    "Local Citations",
                    "Reviews Management",
                    "Local Content Strategy"
                ],
                "title": "Local SEO Guide - Rank in Local Search Results",
                "meta_description": "Dominate local search with our local SEO guide. Optimize Google My Business, build citations, manage reviews, and create local content.",
                "added_date": "2024-01-01T00:00:00"
            },
            "https://example.com/technical-seo": {
                "h1": "Technical SEO Essentials",
                "h2": [
                    "Site Speed Optimization",
                    "Mobile-First Indexing",
                    "Schema Markup",
                    "XML Sitemaps"
                ],
                "title": "Technical SEO Guide - Optimize Your Website",
                "meta_description": "Master technical SEO with our comprehensive guide. Learn about site speed, mobile optimization, schema markup, and more.",
                "added_date": "2024-01-01T00:00:00"
            }
        },
        "last_updated": "2024-01-01T00:00:00"
    }
    
    # Save to file
    db_file = "url_database.json"
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Sample database created successfully!")
    print(f"📁 File: {os.path.abspath(db_file)}")
    print(f"📊 URLs loaded: {len(sample_data['urls'])}")
    print("\n🚀 Now run: streamlit run app.py")
    print("\nSample URLs loaded:")
    for url in sample_data['urls'].keys():
        print(f"  • {url}")

if __name__ == "__main__":
    print("🔗 Smart Internal Link Suggester - Quick Start\n")
    
    # Check if database already exists
    if os.path.exists("url_database.json"):
        response = input("⚠️  Database file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled. Existing database preserved.")
            exit(0)
    
    create_sample_database()
