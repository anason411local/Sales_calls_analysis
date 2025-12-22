# 📄 DOCX Conversion Guide

## Overview

The Call Performance Analyzer now automatically generates reports in **two formats**:
1. **Markdown** (`.md`) - For viewing in text editors, GitHub, etc.
2. **DOCX** (`.docx`) - For Microsoft Word, professional presentations

---

## Automatic Conversion

### When You Run Analysis

```bash
cd d:\Sales_calls_analysis\ai_agents\call_performance_analyzer
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe main.py --run
```

**Output Files**:
- `D:\Sales_calls_analysis\reports\call_performance_analysis_report.md`
- `D:\Sales_calls_analysis\reports\call_performance_analysis_report.docx` ✨ (Automatically generated)

---

## Manual Conversion

### Convert Existing Markdown to DOCX

If you need to convert an existing Markdown report:

```bash
cd d:\Sales_calls_analysis\ai_agents\call_performance_analyzer
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe convert_to_docx.py
```

### Convert Custom File

```bash
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe convert_to_docx.py "path\to\your\report.md"
```

---

## DOCX Features

### Professional Styling

The DOCX converter includes:

✅ **Custom Styles**:
- Title: 24pt, Bold, Dark Blue, Centered
- Heading 1: 18pt, Bold, Dark Blue
- Heading 2: 14pt, Bold, Light Blue
- Body Text: 11pt, Calibri

✅ **Formatted Tables**:
- Professional grid styling
- Bold headers
- Proper spacing

✅ **Verbatim Quotes**:
- Courier New font
- Italic styling
- Indented for emphasis

✅ **Lists**:
- Bullet points
- Numbered lists
- Proper indentation

---

## File Locations

### Default Paths

| Format | Location |
|--------|----------|
| **Markdown** | `D:\Sales_calls_analysis\reports\call_performance_analysis_report.md` |
| **DOCX** | `D:\Sales_calls_analysis\reports\call_performance_analysis_report.docx` |
| **Logs** | `D:\Sales_calls_analysis\ai_agents\call_performance_analyzer\logs\` |

---

## Opening the DOCX Report

### In Microsoft Word

1. Navigate to: `D:\Sales_calls_analysis\reports\`
2. Double-click: `call_performance_analysis_report.docx`
3. Opens in Microsoft Word with full formatting

### Editing the Report

The DOCX file is fully editable:
- ✅ Add your own comments
- ✅ Highlight key sections
- ✅ Add company logo/branding
- ✅ Adjust formatting
- ✅ Export to PDF

---

## Technical Details

### Conversion Process

1. **Read Markdown**: Parse the `.md` file
2. **Convert Elements**:
   - Headings → Word Heading Styles
   - Tables → Word Tables with styling
   - Bold/Italic → Formatted text runs
   - Bullet points → Word Lists
   - Code blocks → Verbatim Quote style
3. **Apply Styling**: Professional formatting
4. **Save DOCX**: Microsoft Word format

### Dependencies

```
python-docx>=1.2.0  # Word document creation
lxml>=6.0.0         # XML processing
markdown>=3.10      # Markdown parsing (optional)
```

---

## Troubleshooting

### DOCX Not Generated

**Problem**: Analysis completes but no DOCX file

**Solution**:
1. Check logs for errors
2. Run manual conversion:
   ```bash
   python convert_to_docx.py
   ```
3. Verify `python-docx` is installed:
   ```bash
   pip list | findstr docx
   ```

### Formatting Issues

**Problem**: DOCX formatting looks incorrect

**Solution**:
1. Open in Microsoft Word (not Google Docs)
2. Enable "Compatibility Mode" if needed
3. Adjust styles in Word as needed

### File Not Found

**Problem**: "Markdown file not found" error

**Solution**:
1. Verify the Markdown report exists:
   ```
   D:\Sales_calls_analysis\reports\call_performance_analysis_report.md
   ```
2. Run analysis first if missing:
   ```bash
   python main.py --run
   ```

---

## Customization

### Modify Styling

Edit `utils/docx_converter.py` to customize:

```python
# Change title color
title_font.color.rgb = RGBColor(0, 51, 102)  # Dark blue

# Change font
title_font.name = 'Calibri'

# Change size
title_font.size = Pt(24)
```

### Add Company Branding

```python
# Add logo (in convert_markdown_to_docx method)
self.doc.add_picture('path/to/logo.png', width=Inches(2))
```

### Custom Header/Footer

```python
# Add header
section = self.doc.sections[0]
header = section.header
header_para = header.paragraphs[0]
header_para.text = "411 Locals - Confidential"
```

---

## Best Practices

### For CEO Presentations

1. ✅ **Use DOCX format** - Professional appearance
2. ✅ **Add cover page** - Company branding
3. ✅ **Highlight key findings** - Use Word's highlighting
4. ✅ **Add comments** - Executive notes
5. ✅ **Export to PDF** - For distribution

### For Training

1. ✅ **Print specific sections** - Agent playbooks
2. ✅ **Highlight verbatim examples** - For role-playing
3. ✅ **Create handouts** - From DOCX sections
4. ✅ **Annotate** - Add training notes

### For Archiving

1. ✅ **Keep both formats** - Markdown + DOCX
2. ✅ **Version control** - Date in filename
3. ✅ **Backup** - Cloud storage
4. ✅ **PDF export** - Long-term archival

---

## Examples

### Quick Conversion

```bash
# Navigate to analyzer directory
cd d:\Sales_calls_analysis\ai_agents\call_performance_analyzer

# Convert latest report
C:\Users\Rtx_5090\.conda\envs\sales_calls_ai_agent\python.exe convert_to_docx.py

# Output:
# [INFO] Converting: D:\Sales_calls_analysis\reports\call_performance_analysis_report.md
# [SUCCESS] DOCX report created!
# [INFO] Location: D:\Sales_calls_analysis\reports\call_performance_analysis_report.docx
```

### Batch Conversion

```bash
# Convert multiple reports
for file in reports/*.md; do
    python convert_to_docx.py "$file"
done
```

---

## Integration

### With Main Analysis

The DOCX conversion is **automatically integrated**:

```python
# In orchestrator/batch_orchestrator.py
markdown_path = self.data_handler.save_report(report)

# Automatic DOCX conversion
from utils.docx_converter import convert_report_to_docx
docx_path = convert_report_to_docx(markdown_path)
```

### Standalone Usage

```python
from utils.docx_converter import convert_report_to_docx

# Convert any Markdown file
docx_path = convert_report_to_docx(
    markdown_path="path/to/report.md",
    docx_path="path/to/output.docx"  # Optional
)
```

---

## FAQ

### Q: Can I convert other Markdown files?
**A**: Yes! Use the standalone script with any `.md` file.

### Q: Does it work with Google Docs?
**A**: Best viewed in Microsoft Word. Google Docs may have formatting differences.

### Q: Can I edit the DOCX?
**A**: Absolutely! The DOCX is fully editable in Word.

### Q: What if conversion fails?
**A**: The Markdown report is always available as a fallback.

### Q: Can I customize the styling?
**A**: Yes! Edit `utils/docx_converter.py` to modify styles.

---

## Summary

| Feature | Status |
|---------|--------|
| **Automatic Conversion** | ✅ Enabled |
| **Manual Conversion** | ✅ Available |
| **Professional Styling** | ✅ Included |
| **Tables** | ✅ Formatted |
| **Verbatim Quotes** | ✅ Styled |
| **Editable** | ✅ Yes |
| **Word Compatible** | ✅ Yes |

---

**The DOCX conversion feature makes your reports CEO-ready and presentation-perfect! 📊**

---

*For technical support, see the main README or contact the development team.*

