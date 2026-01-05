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
├── templates/             # HTML templates (14 pages)
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

# TODO: Critical Items for SEO & AdSense Approval

## HIGH PRIORITY - Google Search Console
- [x] GSC verification complete (site already verified, removed placeholder meta tags 2026-01-05)
- [x] Submit sitemap to Google Search Console (completed 2026-01-05)
- [ ] Request indexing for all 14 pages via URL Inspection Tool

## HIGH PRIORITY - Static Assets
- [x] Add actual favicon.png (32x32 or 64x64 PNG) - completed 2026-01-05
- [x] Add apple-touch-icon.png (180x180 PNG) - completed 2026-01-05
- [x] Add og-image.png (1200x630 PNG) - completed 2026-01-05

## MEDIUM PRIORITY - Content & Engagement
- [x] Add testimonials/social proof to homepage (completed 2026-01-05)
- [x] Create more internal links within content (completed 2026-01-05)
- [ ] Add author/team information to About page for E-E-A-T signals
- [ ] Consider adding a blog section for fresh content

## MEDIUM PRIORITY - Link Building
- [ ] Submit to Product Hunt
- [ ] List on AlternativeTo.net as HEIC converter alternative
- [ ] Create Twitter/X account for brand presence
- [ ] Create LinkedIn company page
- [ ] Submit to free web directories

## LOW PRIORITY - Future Enhancements
- [ ] Add image editing features (crop, rotate)
- [ ] Implement URL-based conversion
- [ ] Create browser extension
- [ ] Build mobile app versions
- [ ] Add API access for developers

---

## Development Commands
```bash
# Local development
python app.py

# Production (Railway uses gunicorn)
gunicorn app:app
```

## Recent Changes
- 2026-01-05: Added testimonials section to homepage (3 user reviews with star ratings)
- 2026-01-05: Removed GSC verification placeholder meta tags (site already verified)
- 2026-01-05: Added contextual internal links to all 9 SEO content pages
- 2026-01-05: Added site-wide navigation, standardized footer, updated sitemap dates
- 2026-01-05: Created static assets (favicon.png, apple-touch-icon.png, og-image.png)
- 2025-12-20: Added 4 new SEO content pages
- 2025-12-20: Added HEIC Not Opening on Windows troubleshooting page
- 2025-12-20: Added Google Analytics 4 tracking
