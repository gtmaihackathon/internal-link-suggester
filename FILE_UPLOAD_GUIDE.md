# 📤 File Upload Guide - Bulk Import URLs

## Overview

The app now supports **bulk import** of URLs via Excel or CSV files. Upload your file once, and all URLs will be saved permanently until you remove or replace the file.

---

## 📁 Supported File Formats

- ✅ **Excel** (.xlsx, .xls)
- ✅ **CSV** (.csv)
- ✅ **Google Sheets** (export as .xlsx or .csv)

---

## 📊 Required File Structure

Your file must have these **required columns** (case-insensitive):

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **url** | ✅ Yes | Full URL of the page | https://example.com/seo-guide |
| **title** | ✅ Yes | Page title (meta title) | Complete SEO Guide 2024 |
| **h1** | ✅ Yes | Main H1 heading | The Ultimate SEO Guide |
| **meta_description** | ⚪ Optional | Meta description | Learn everything about SEO... |
| **h2** | ⚪ Optional | H2 headings (separated by ; or ,) | On-Page SEO; Link Building |

---

## 📝 Example File Structure

### Excel/CSV Format

```
url                              | title                    | h1                      | meta_description                | h2
https://example.com/seo-guide    | Complete SEO Guide 2024  | The Ultimate SEO Guide  | Learn everything about SEO...   | On-Page SEO; Technical SEO; Link Building
https://example.com/keywords     | Keyword Research Guide   | Keyword Research 101    | Find profitable keywords...     | Tools; Long-tail; Analysis
https://example.com/content      | Content Marketing Guide  | Content Strategy Guide  | Create engaging content...      | Planning; Creation; Distribution
```

### Multiple H2 Tags

You can separate H2 headings using:
- **Semicolon** (recommended): `H2-1; H2-2; H2-3`
- **Comma**: `H2-1, H2-2, H2-3`

**Example:**
```
h2: On-Page SEO; Technical SEO; Link Building; Content Optimization
```

---

## 🚀 How to Upload Your File

### Step 1: Prepare Your File

**Option A: Use the Template**
1. Click "📄 Template" button in the upload section
2. Download `url_template.xlsx`
3. Open in Excel or Google Sheets
4. Fill in your URLs and metadata
5. Save the file

**Option B: Create Your Own**
1. Create new Excel or Google Sheets file
2. Add required column headers: `url`, `title`, `h1`
3. Add optional headers: `meta_description`, `h2`
4. Fill in your data
5. Save as .xlsx or export as .csv

### Step 2: Upload to App

1. Go to sidebar → **📚 Manage URLs**
2. Expand **📤 Upload Excel/CSV File**
3. Click **"Choose Excel or CSV file"**
4. Select your file
5. Preview will show (first 3 rows)
6. Click **📥 Import URLs from File**
7. Wait for confirmation

### Step 3: Verify Import

- Check success message: "✅ Successfully imported X URLs!"
- View any errors in the expandable section
- URLs are now in your database
- File is saved and will persist

---

## 💾 File Persistence

### How It Works

- **Uploaded file is saved** to disk as `uploaded_urls_file.xlsx` (or .csv)
- **Persists across sessions** - survives app restarts
- **Remains until removed** - won't disappear when you refresh
- **Can be reloaded** - use "🔄 Reload from File" button

### File Info Display

When a file is uploaded, you'll see:
```
📁 Current file: uploaded_urls_file.xlsx
📊 Size: 12.3 KB
🕒 Uploaded: 2024-02-09 14:30
```

---

## 🔄 Managing Your Uploaded File

### Reload from File

If you edit your Excel file externally:
1. Save changes to the file
2. Upload it again OR
3. Click **🔄 Reload from File**
4. URLs will be re-imported

### Replace File

To upload a different file:
1. Click **🗑️ Remove File**
2. Upload new file
3. New URLs will be imported

### Remove File

To delete the uploaded file:
1. Click **🗑️ Remove File**
2. File is deleted from disk
3. URLs in database remain (unless you clear them)

---

## 📋 Complete Workflow Example

### Scenario: Import 50 URLs from Google Sheets

**1. Prepare in Google Sheets**
```
A: url
B: title
C: h1
D: meta_description
E: h2

[Fill in 50 rows of data]
```

**2. Export**
- File → Download → Microsoft Excel (.xlsx)
- Or: File → Download → CSV

**3. Upload to App**
- Sidebar → Upload Excel/CSV File
- Choose downloaded file
- Preview shows correctly
- Click Import

**4. Confirmation**
```
✅ Successfully imported 50 URLs!
```

**5. Use the App**
- Paste your content
- Analyze & get suggestions
- URLs from your file are used for matching

**6. File Persists**
- Close browser
- Reopen app later
- File and URLs still there!

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Missing required columns"

**Problem:** File doesn't have `url`, `title`, or `h1` columns

**Solution:**
- Check column names (case doesn't matter)
- Make sure headers are in first row
- No spaces in column names (use underscores)

✅ Correct: `url`, `title`, `h1`  
❌ Wrong: `URL `, `Page Title`, `H 1`

### Issue 2: "Row X: Missing required field"

**Problem:** Some rows have empty cells in required columns

**Solution:**
- Fill in all required fields: url, title, h1
- Remove empty rows
- Check for cells with just spaces

### Issue 3: "Error reading file"

**Problem:** File format issue or corrupt file

**Solution:**
- Save as .xlsx (not .xlsm or other formats)
- For CSV: Use UTF-8 encoding
- Remove special formatting (keep it simple)
- Try re-exporting from Google Sheets

### Issue 4: H2 tags not parsing

**Problem:** H2 headings appear as one long string

**Solution:**
- Use semicolon `;` to separate (recommended)
- Or use comma `,`
- Example: `SEO Tips; Link Building; Content Strategy`

### Issue 5: Special characters in URLs

**Problem:** URLs with spaces or special chars fail

**Solution:**
- Use properly encoded URLs
- No spaces in URLs
- Example: `https://example.com/seo-guide` not `example.com/seo guide`

---

## 📈 Best Practices

### File Organization

**✅ DO:**
- Use clear, descriptive column headers
- Keep one URL per row
- Fill required fields first
- Use consistent formatting
- Test with small file first (5-10 rows)

**❌ DON'T:**
- Leave required fields empty
- Merge cells
- Use formulas in data cells
- Include duplicate URLs
- Mix languages without proper encoding

### Data Quality

**High Quality Example:**
```csv
url,title,h1,meta_description,h2
https://example.com/guide,Complete SEO Guide,SEO Guide 2024,Learn SEO from scratch,Basics; Advanced; Tools
```

**Low Quality Example:**
```csv
url,title,h1,meta_description,h2
example.com/guide,,SEO,,
```

### Performance Tips

- **Small files** (<100 URLs): Import instantly
- **Medium files** (100-500 URLs): ~5-10 seconds
- **Large files** (500+ URLs): May take 30-60 seconds
- **Huge files** (1000+ URLs): Consider splitting into multiple files

---

## 🔍 Verification Checklist

After uploading, verify:

- [ ] Success message shows correct count
- [ ] No critical errors displayed
- [ ] URLs appear in "View All URLs" section
- [ ] File info shows in upload section
- [ ] Can reload from file successfully
- [ ] Suggestions work with new URLs

---

## 📊 Template Download

The app provides a ready-to-use template:

**What's included:**
- All required columns
- Example data (2 rows)
- Proper formatting
- Ready to fill and upload

**How to use:**
1. Click "📄 Template" button
2. Download `url_template.xlsx`
3. Open in Excel/Google Sheets
4. Replace example data with yours
5. Add more rows as needed
6. Save and upload

---

## 🎯 Advanced Usage

### Google Sheets Integration

**Workflow:**
1. Maintain master list in Google Sheets
2. Share with team for collaborative editing
3. When updated: File → Download → Excel
4. Upload to app
5. Or schedule automatic exports

### Version Control

Keep track of changes:
```
urls_v1.xlsx - Initial import (50 URLs)
urls_v2.xlsx - Added products (75 URLs)
urls_v3.xlsx - Updated titles (75 URLs)
```

### Multiple Categories

Organize by category in different sheets:
```
Blog_URLs.xlsx
Product_URLs.xlsx
Service_URLs.xlsx
```

Import each separately or combine into one master file.

---

## 🆘 Troubleshooting

### Import Fails Completely

1. Check file format (must be .xlsx, .xls, or .csv)
2. Open file in Excel - does it open correctly?
3. Try exporting from Google Sheets again
4. Remove any complex formatting
5. Start with template and add data

### Partial Import

Some rows import, others fail:

1. Check error messages (expand "View Errors")
2. Fix problematic rows
3. Re-upload file
4. Existing URLs will be updated

### File Won't Upload

1. Check file size (keep under 10MB)
2. Close file in Excel before uploading
3. Try different browser
4. Clear browser cache
5. Try CSV format instead

---

## 📞 Support

**Need help?**

1. Check error messages in app
2. Review this guide
3. Try the template file
4. Start with small test file (3-5 URLs)
5. Check example data format above

---

## ✅ Quick Reference

**File Format:**
```
url | title | h1 | meta_description | h2
```

**Upload Steps:**
1. Prepare file with required columns
2. Upload via sidebar
3. Preview and verify
4. Click Import
5. File persists automatically

**File Persists:**
- ✅ Saved to disk
- ✅ Survives app restarts
- ✅ Can reload anytime
- ✅ Until removed or replaced

---

**Happy bulk importing! 📤✨**
