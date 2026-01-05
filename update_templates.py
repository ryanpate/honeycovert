#!/usr/bin/env python3
"""Update all templates with navigation header and footer"""

import os
import re

# Header HTML to insert
HEADER_HTML = '''    <header class="site-header">
        <div class="header-content">
            <a href="/" class="logo">HoneyConvert</a>
            <button class="nav-toggle" onclick="document.getElementById('navLinks').classList.toggle('active')">☰</button>
            <nav class="nav-links" id="navLinks">
                <a href="/">Home</a>
                <a href="/how-to-convert-heic-to-png">Guides</a>
                <a href="/what-is-heic">What is HEIC?</a>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </nav>
        </div>
    </header>
    <main class="main-content">'''

# Footer HTML
FOOTER_HTML = '''    </main>
    <footer class="site-footer">
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">HoneyConvert</span>
                <p class="footer-tagline">Free HEIC to PNG, JPEG, WebP Converter</p>
            </div>
            <div class="footer-links">
                <div class="footer-column">
                    <h4>Convert</h4>
                    <a href="/">HEIC Converter</a>
                    <a href="/batch-convert-heic">Batch Convert</a>
                </div>
                <div class="footer-column">
                    <h4>Learn</h4>
                    <a href="/what-is-heic">What is HEIC?</a>
                    <a href="/heic-vs-png">HEIC vs PNG</a>
                </div>
                <div class="footer-column">
                    <h4>Company</h4>
                    <a href="/about">About Us</a>
                    <a href="/contact">Contact</a>
                    <a href="/privacy">Privacy Policy</a>
                    <a href="/terms">Terms of Service</a>
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 HoneyConvert.com - All rights reserved.</p>
        </div>
    </footer>'''

# Header CSS to add
HEADER_CSS = '''        /* Site Header & Footer */
        .site-header { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 15px 20px; position: sticky; top: 0; z-index: 1000; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { color: white; font-size: 24px; font-weight: 700; text-decoration: none; }
        .nav-links { display: flex; gap: 25px; }
        .nav-links a { color: white; text-decoration: none; font-size: 15px; opacity: 0.9; }
        .nav-links a:hover { opacity: 1; }
        .nav-toggle { display: none; background: none; border: none; color: white; font-size: 24px; cursor: pointer; }
        @media (max-width: 768px) { .nav-links { display: none; position: absolute; top: 100%; left: 0; right: 0; background: rgba(102,126,234,0.98); flex-direction: column; padding: 20px; gap: 15px; } .nav-links.active { display: flex; } .nav-toggle { display: block; } }
        .main-content { padding: 30px 20px; }
        .site-footer { background: rgba(0,0,0,0.2); padding: 40px 20px 20px; margin-top: 40px; }
        .footer-content { max-width: 1200px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 40px; justify-content: space-between; }
        .footer-brand { flex: 1; min-width: 200px; }
        .footer-logo { color: white; font-size: 24px; font-weight: 700; }
        .footer-tagline { color: rgba(255,255,255,0.7); font-size: 14px; margin-top: 8px; }
        .footer-links { display: flex; flex-wrap: wrap; gap: 40px; }
        .footer-column { min-width: 140px; }
        .footer-column h4 { color: white; font-size: 14px; font-weight: 600; margin-bottom: 15px; text-transform: uppercase; }
        .footer-column a { display: block; color: rgba(255,255,255,0.8); text-decoration: none; font-size: 14px; margin-bottom: 10px; }
        .footer-column a:hover { color: white; }
        .footer-bottom { max-width: 1200px; margin: 30px auto 0; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2); text-align: center; }
        .footer-bottom p { color: rgba(255,255,255,0.6); font-size: 13px; }
        @media (max-width: 768px) { .footer-content, .footer-links { flex-direction: column; gap: 25px; } .footer-brand, .footer-column { text-align: center; } }

'''

# SEO content pages to update
SEO_PAGES = [
    'what-is-heic.html',
    'why-iphone-uses-heic.html',
    'heic-vs-png.html',
    'how-to-convert-heic-to-png.html',
    'heic-not-opening-windows.html',
    'heic-to-jpeg-vs-png.html',
    'batch-convert-heic.html',
    'heic-converter-mac.html',
    'convert-heic-without-losing-quality.html',
]

def update_template(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Skip if already updated
    if 'site-header' in content:
        print(f"  Already updated: {filepath}")
        return

    # Add CSS after body styles (before first rule if present)
    # Find the body style and add header/footer CSS after it
    body_style_match = re.search(r'(body\s*\{[^}]+\})', content)
    if body_style_match:
        insert_pos = body_style_match.end()
        # Also fix body padding if present
        content = re.sub(r'(body\s*\{[^}]*)(padding:\s*20px;)', r'\1', content)
        content = re.sub(r'(body\s*\{[^}]*min-height:\s*100vh;)', r'\1', content)

    # Add header/footer CSS after body style
    style_end = content.find('</style>')
    if style_end > 0:
        # Find a good place to insert CSS - after body definition
        insert_match = re.search(r'(body\s*\{[^}]+\}\s*\n)', content)
        if insert_match:
            insert_pos = insert_match.end()
            content = content[:insert_pos] + HEADER_CSS + content[insert_pos:]

    # Replace body opening with header
    content = re.sub(
        r'<body>\s*\n\s*<div class="container">',
        '<body>\n' + HEADER_HTML + '\n        <div class="container">',
        content
    )

    # Replace footer pattern - several variations
    # Pattern 1: footer inside container at end
    content = re.sub(
        r'<footer>\s*<div>\s*<a href="/">Home</a>.*?</footer>\s*</div>\s*</body>',
        '</div>\n' + FOOTER_HTML + '\n</body>',
        content,
        flags=re.DOTALL
    )

    # Pattern 2: another common footer pattern
    content = re.sub(
        r'<footer>\s*<a href="/">Home</a>.*?</footer>\s*</div>\s*</body>',
        '</div>\n' + FOOTER_HTML + '\n</body>',
        content,
        flags=re.DOTALL
    )

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"  Updated: {filepath}")

if __name__ == '__main__':
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

    for page in SEO_PAGES:
        filepath = os.path.join(templates_dir, page)
        if os.path.exists(filepath):
            update_template(filepath)
        else:
            print(f"  Not found: {page}")

    print("\nDone!")
