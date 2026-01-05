# HoneyConvert - Project Context

## Overview
HoneyConvert is a free online HEIC to PNG/JPEG/WebP converter built with Flask and Python. The site converts iPhone photos (HEIC/HEIF format) to universally compatible image formats.

## Tech Stack
- **Backend**: Flask (Python)
- **Image Processing**: Pillow + pillow-heif
- **Deployment**: Railway
- **Analytics**: Google Analytics 4 (G-ZCREHPYLHH)
- **Monetization**: Google AdSense (ca-pub-5523870768931777)

## Project Structure
```
/honeyconvert
├── app.py                 # Main Flask application
├── templates/             # HTML templates (15 pages)
│   ├── index.html         # Homepage with converter tool
│   ├── about.html         # About page
│   ├── contact.html       # Contact page
│   ├── privacy.html       # Privacy policy
│   ├── terms.html         # Terms of service
│   └── [9 SEO content pages]
├── static/                # Static assets (favicon, images)
├── requirements.txt       # Python dependencies
└── CLAUDE.md              # This file
```

## Key URLs
- Production: https://honeyconvert.com
- Routes defined in app.py (lines 103-157)
- Sitemap: /sitemap.xml (dynamic, lines 175-266)
- Robots: /robots.txt (dynamic, lines 159-173)

## SEO Content Pages
1. /what-is-heic - Educational content about HEIC format
2. /heic-vs-png - Format comparison
3. /why-iphone-uses-heic - Apple's reasoning
4. /how-to-convert-heic-to-png - Step-by-step guide
5. /heic-not-opening-windows - Troubleshooting
6. /heic-to-jpeg-vs-png - Output format comparison
7. /batch-convert-heic - Batch conversion guide
8. /heic-converter-mac - Mac-specific guide
9. /convert-heic-without-losing-quality - Quality preservation

## Important Notes
- All templates include Google AdSense and GA4 tracking
- Schema markup implemented (WebApplication, FAQPage, HowTo, Article, BreadcrumbList)
- Security headers configured in app.py after_request handler
- Gzip compression enabled via Flask-Compress

---

# Google AdSense Status

**Status:** Submitted for approval (2026-01-05)
- [x] ads.txt file added at /ads.txt
- [x] AdSense code installed on all pages (ca-pub-5523870768931777)
- [x] Privacy Policy includes ad disclosure
- [x] Terms of Service published

## AdSense Approval Checklist

The site meets Google AdSense requirements:

### Content Quality
- [x] **Original, valuable content** - 15 unique pages with educational HEIC/image conversion content
- [x] **Functional tool** - Working HEIC converter with real utility for users
- [x] **Sufficient content depth** - Each SEO page has 500+ words of original content
- [x] **Clear navigation** - Site header and footer on all pages

### Technical Requirements
- [x] **ads.txt** - Properly configured at /ads.txt
- [x] **Privacy Policy** - Comprehensive policy at /privacy mentioning ad personalization
- [x] **Terms of Service** - Published at /terms
- [x] **Contact page** - Available at /contact with support email
- [x] **About page** - Team info with E-E-A-T signals at /about
- [x] **HTTPS** - Site served over SSL
- [x] **Mobile responsive** - All pages work on mobile devices
- [x] **Fast loading** - Gzip compression enabled, optimized assets

### Policy Compliance
- [x] **No prohibited content** - Site contains only image conversion tools and educational content
- [x] **No excessive ads** - AdSense code present but not cluttering content
- [x] **User-first design** - Tool is prominently featured, ads are secondary

---

# Open TODO Items

## Google Search Console (Manual Tasks)
- [ ] Request indexing for all 15 pages via URL Inspection Tool

## Link Building & Marketing
- [ ] Submit to Product Hunt
- [ ] List on AlternativeTo.net as HEIC converter alternative
- [ ] Create Twitter/X account for brand presence
- [ ] Create LinkedIn company page
- [ ] Submit to free web directories

## Future Enhancements
- [ ] Create browser extension
- [ ] Build mobile app versions

---

## Development Commands
```bash
# Local development
python app.py

# Production (Railway uses gunicorn)
gunicorn app:app
```

## Recent Changes
- 2026-01-05: Added ads.txt for Google AdSense verification, submitted site for approval
- 2026-01-05: Added public API with /api/convert endpoint and documentation page at /api
- 2026-01-05: Added URL-based conversion (convert HEIC from direct URL with /convert-url endpoint)
- 2026-01-05: Added image editing features (rotate: 0°/90°/180°/270°, crop: 1:1, 4:3, 16:9, etc.)
- 2026-01-05: Added author/team section to About page with Person schema for E-E-A-T
- 2026-01-05: Added testimonials section to homepage (3 user reviews with star ratings)
- 2026-01-05: Removed GSC verification placeholder meta tags (site already verified)
- 2026-01-05: Added contextual internal links to all 9 SEO content pages
- 2026-01-05: Added site-wide navigation, standardized footer, updated sitemap dates
- 2026-01-05: Created static assets (favicon.png, apple-touch-icon.png, og-image.png)
- 2025-12-20: Added 4 new SEO content pages
- 2025-12-20: Added HEIC Not Opening on Windows troubleshooting page
- 2025-12-20: Added Google Analytics 4 tracking
