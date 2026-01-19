from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, make_response
from flask_compress import Compress
import os
from PIL import Image
from pillow_heif import register_heif_opener
import io
import zipfile
import requests
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

# Register HEIF opener with Pillow
register_heif_opener()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Enable gzip compression
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'text/javascript',
    'application/json', 'application/javascript', 'application/xml'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
Compress(app)

# Create temp folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.after_request
def add_security_headers(response):
    """Add security, cache, and canonical headers to all responses"""
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

    # Canonical URL mapping for SEO (prevents keyword cannibalization)
    canonical_urls = {
        '/': 'https://honeyconvert.com/',
        '/about': 'https://honeyconvert.com/about',
        '/privacy': 'https://honeyconvert.com/privacy',
        '/terms': 'https://honeyconvert.com/terms',
        '/contact': 'https://honeyconvert.com/contact',
        '/api': 'https://honeyconvert.com/api',
        '/what-is-heic': 'https://honeyconvert.com/what-is-heic',
        '/heic-vs-png': 'https://honeyconvert.com/heic-vs-png',
        '/heic-vs-jpeg': 'https://honeyconvert.com/heic-vs-jpeg',
        '/is-heic-lossless': 'https://honeyconvert.com/is-heic-lossless',
        '/why-iphone-uses-heic': 'https://honeyconvert.com/why-iphone-uses-heic',
        '/how-to-convert-heic-to-png': 'https://honeyconvert.com/how-to-convert-heic-to-png',
        '/heic-not-opening-windows': 'https://honeyconvert.com/heic-not-opening-windows',
        '/heic-to-jpeg-vs-png': 'https://honeyconvert.com/heic-to-jpeg-vs-png',
        '/batch-convert-heic': 'https://honeyconvert.com/batch-convert-heic',
        '/heic-converter-mac': 'https://honeyconvert.com/heic-converter-mac',
        '/convert-heic-without-losing-quality': 'https://honeyconvert.com/convert-heic-without-losing-quality',
        '/heic-to-png-converter': 'https://honeyconvert.com/heic-to-png-converter',
        '/heic-to-jpg-converter': 'https://honeyconvert.com/heic-to-jpg-converter',
        '/heic-to-webp-converter': 'https://honeyconvert.com/heic-to-webp-converter',
        '/open-heic-file': 'https://honeyconvert.com/open-heic-file',
    }

    # Add canonical Link header for HTML pages
    if request.path in canonical_urls:
        response.headers['Link'] = f'<{canonical_urls[request.path]}>; rel="canonical"'

    # Cache headers based on content type
    if request.path.startswith('/static/'):
        # Static assets: cache for 1 year
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    elif request.path in canonical_urls:
        # HTML pages: cache for 1 hour, revalidate
        response.headers['Cache-Control'] = 'public, max-age=3600, must-revalidate'
    elif request.path in ['/robots.txt', '/sitemap.xml']:
        # SEO files: cache for 1 day
        response.headers['Cache-Control'] = 'public, max-age=86400'

    return response

ALLOWED_EXTENSIONS = {'heic', 'heif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_heic_to_image(heic_path, output_path, output_format='png', size_percent=100, quality=90, rotate=0, crop_ratio=None):
    """Convert HEIC file to specified format with optional resizing, rotation, and cropping

    Args:
        heic_path: Path to input HEIC file
        output_path: Path to output file
        output_format: Output format ('png', 'jpeg', 'webp')
        size_percent: Percentage to resize (100 = original, 75 = 75%, etc.)
        quality: Quality for JPEG/WebP (1-100, ignored for PNG)
        rotate: Rotation angle (0, 90, 180, 270)
        crop_ratio: Crop aspect ratio ('1:1', '4:3', '16:9', '3:2', None for no crop)
    """
    try:
        # Open the HEIC image
        image = Image.open(heic_path)

        # Convert to RGB if necessary (HEIC can be in different color modes)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Apply rotation if requested
        if rotate in [90, 180, 270]:
            image = image.rotate(-rotate, expand=True)  # Negative for clockwise rotation

        # Apply crop if requested
        if crop_ratio and crop_ratio != 'none':
            width, height = image.size

            # Parse aspect ratio
            ratio_map = {
                '1:1': (1, 1),
                '4:3': (4, 3),
                '3:4': (3, 4),
                '16:9': (16, 9),
                '9:16': (9, 16),
                '3:2': (3, 2),
                '2:3': (2, 3)
            }

            if crop_ratio in ratio_map:
                target_w, target_h = ratio_map[crop_ratio]
                target_aspect = target_w / target_h
                current_aspect = width / height

                if current_aspect > target_aspect:
                    # Image is wider than target, crop width
                    new_width = int(height * target_aspect)
                    left = (width - new_width) // 2
                    image = image.crop((left, 0, left + new_width, height))
                else:
                    # Image is taller than target, crop height
                    new_height = int(width / target_aspect)
                    top = (height - new_height) // 2
                    image = image.crop((0, top, width, top + new_height))

        # Resize if requested
        if size_percent != 100:
            width, height = image.size
            new_width = int(width * (size_percent / 100))
            new_height = int(height * (size_percent / 100))
            # Use LANCZOS for high-quality downsampling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save in requested format
        if output_format == 'png':
            image.save(output_path, 'PNG', optimize=True)
        elif output_format == 'jpeg':
            image.save(output_path, 'JPEG', quality=quality, optimize=True)
        elif output_format == 'webp':
            image.save(output_path, 'WEBP', quality=quality, optimize=True)
        else:
            image.save(output_path, 'PNG', optimize=True)

        return True
    except Exception as e:
        print(f"Error converting {heic_path}: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/what-is-heic')
def what_is_heic():
    return render_template('what-is-heic.html')

@app.route('/heic-vs-png')
def heic_vs_png():
    return render_template('heic-vs-png.html')

@app.route('/heic-vs-jpeg')
def heic_vs_jpeg():
    return render_template('heic-vs-jpeg.html')

@app.route('/is-heic-lossless')
def is_heic_lossless():
    return render_template('is-heic-lossless.html')

@app.route('/open-heic-file')
def open_heic_file():
    return render_template('open-heic-file.html')

@app.route('/why-iphone-uses-heic')
def why_iphone_uses_heic():
    return render_template('why-iphone-uses-heic.html')

@app.route('/how-to-convert-heic-to-png')
def how_to_convert_heic_to_png():
    return render_template('how-to-convert-heic-to-png.html')

@app.route('/heic-not-opening-windows')
def heic_not_opening_windows():
    return render_template('heic-not-opening-windows.html')

@app.route('/heic-to-jpeg-vs-png')
def heic_to_jpeg_vs_png():
    return render_template('heic-to-jpeg-vs-png.html')

@app.route('/batch-convert-heic')
def batch_convert_heic():
    return render_template('batch-convert-heic.html')

@app.route('/heic-converter-mac')
def heic_converter_mac():
    return render_template('heic-converter-mac.html')

@app.route('/convert-heic-without-losing-quality')
def convert_heic_without_losing_quality():
    return render_template('convert-heic-without-losing-quality.html')

@app.route('/heic-to-png-converter')
def heic_to_png_converter():
    return render_template('heic-to-png-converter.html')

@app.route('/heic-to-jpg-converter')
def heic_to_jpg_converter():
    return render_template('heic-to-jpg-converter.html')

@app.route('/heic-to-webp-converter')
def heic_to_webp_converter():
    return render_template('heic-to-webp-converter.html')

@app.route('/ads.txt')
def ads_txt():
    content = "google.com, pub-5523870768931777, DIRECT, f08c47fec0942fa0\n"
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/BingSiteAuth.xml')
def bing_site_auth():
    content = """<?xml version="1.0"?>
<users>
	<user>29ACAC7E27CA9CB577CE5708757F488A</user>
</users>"""
    response = make_response(content)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/sw.js')
def service_worker():
    """Serve service worker from root for proper scope"""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')


@app.route('/manifest.json')
def manifest():
    """Serve manifest from root"""
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')


@app.route('/robots.txt')
def robots():
    content = """User-agent: *
Allow: /
Sitemap: https://honeyconvert.com/sitemap.xml

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /
"""
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/sitemap.xml')
def sitemap():
    # Priority hierarchy:
    # 1.0  - Homepage (main converter tool)
    # 0.9  - Dedicated converter landing pages (high commercial intent)
    # 0.8  - High-value how-to/troubleshooting guides (problem-solving)
    # 0.7  - Educational SEO content (informational)
    # 0.6  - API documentation (developer resource)
    # 0.4  - Support pages (about, contact)
    # 0.3  - Legal pages (privacy, terms)
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://honeyconvert.com/</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-to-png-converter</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-to-jpg-converter</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/batch-convert-heic</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-to-webp-converter</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/how-to-convert-heic-to-png</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-not-opening-windows</loc>
    <lastmod>2026-01-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-converter-mac</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/convert-heic-without-losing-quality</loc>
    <lastmod>2026-01-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/what-is-heic</loc>
    <lastmod>2026-01-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-vs-png</loc>
    <lastmod>2026-01-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-vs-jpeg</loc>
    <lastmod>2026-01-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/is-heic-lossless</loc>
    <lastmod>2026-01-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/open-heic-file</loc>
    <lastmod>2026-01-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/why-iphone-uses-heic</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-to-jpeg-vs-png</loc>
    <lastmod>2026-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/api</loc>
    <lastmod>2026-01-05</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/about</loc>
    <lastmod>2026-01-05</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.4</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/contact</loc>
    <lastmod>2025-11-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.4</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/privacy</loc>
    <lastmod>2025-11-18</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/terms</loc>
    <lastmod>2025-11-18</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>"""
    response = make_response(content)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/convert', methods=['POST'])
def convert():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files[]')

    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400

    # Get size parameter from form data (default to 100 = original size)
    size_percent = int(request.form.get('size', 100))

    # Validate size parameter
    if size_percent not in [100, 75, 50, 25]:
        size_percent = 100

    # Get output format (default to png)
    output_format = request.form.get('format', 'png').lower()
    if output_format not in ['png', 'jpeg', 'webp']:
        output_format = 'png'

    # Get quality parameter for JPEG/WebP (default 90)
    quality = int(request.form.get('quality', 90))
    if quality < 1 or quality > 100:
        quality = 90

    # Get rotation parameter (default 0)
    rotate = int(request.form.get('rotate', 0))
    if rotate not in [0, 90, 180, 270]:
        rotate = 0

    # Get crop ratio parameter (default none)
    crop_ratio = request.form.get('crop', 'none')
    valid_crops = ['none', '1:1', '4:3', '3:4', '16:9', '9:16', '3:2', '2:3']
    if crop_ratio not in valid_crops:
        crop_ratio = 'none'

    # Format-specific settings
    format_extensions = {'png': '.png', 'jpeg': '.jpg', 'webp': '.webp'}
    format_mimetypes = {'png': 'image/png', 'jpeg': 'image/jpeg', 'webp': 'image/webp'}

    converted_files = []
    failed_files = []

    # Create a temporary directory for this conversion batch
    batch_id = os.urandom(16).hex()
    batch_folder = os.path.join(app.config['UPLOAD_FOLDER'], batch_id)
    os.makedirs(batch_folder, exist_ok=True)

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Save uploaded HEIC file
            heic_path = os.path.join(batch_folder, filename)
            file.save(heic_path)

            # Create output filename with correct extension
            output_filename = os.path.splitext(filename)[0] + format_extensions[output_format]
            output_path = os.path.join(batch_folder, output_filename)

            # Convert to requested format with editing options
            if convert_heic_to_image(heic_path, output_path, output_format, size_percent, quality, rotate, crop_ratio):
                converted_files.append({
                    'original': filename,
                    'converted': output_filename,
                    'path': output_path
                })
                # Remove the original HEIC file to save space
                os.remove(heic_path)
            else:
                failed_files.append(filename)
                if os.path.exists(heic_path):
                    os.remove(heic_path)
        else:
            failed_files.append(file.filename)

    if not converted_files:
        return jsonify({'error': 'No files were successfully converted'}), 400

    # If only one file, return it directly
    if len(converted_files) == 1:
        output_path = converted_files[0]['path']
        output_filename = converted_files[0]['converted']

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype=format_mimetypes[output_format]
        )

    # If multiple files, create a ZIP archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_info in converted_files:
            zip_file.write(file_info['path'], file_info['converted'])

    zip_buffer.seek(0)

    # Clean up temporary files
    for file_info in converted_files:
        if os.path.exists(file_info['path']):
            os.remove(file_info['path'])

    if os.path.exists(batch_folder):
        os.rmdir(batch_folder)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='converted_images.zip',
        mimetype='application/zip'
    )

@app.route('/convert-url', methods=['POST'])
def convert_url():
    """Convert HEIC image from URL"""
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data.get('url', '').strip()

    # Validate URL
    if not url:
        return jsonify({'error': 'Empty URL'}), 400

    try:
        parsed = urlparse(url)
        if not parsed.scheme in ['http', 'https']:
            return jsonify({'error': 'Invalid URL scheme. Use http or https.'}), 400
    except Exception:
        return jsonify({'error': 'Invalid URL format'}), 400

    # Check file extension
    url_path = parsed.path.lower()
    if not (url_path.endswith('.heic') or url_path.endswith('.heif')):
        return jsonify({'error': 'URL must point to a .heic or .heif file'}), 400

    # Get conversion options
    output_format = data.get('format', 'png').lower()
    if output_format not in ['png', 'jpeg', 'webp']:
        output_format = 'png'

    size_percent = int(data.get('size', 100))
    if size_percent not in [100, 75, 50, 25]:
        size_percent = 100

    quality = int(data.get('quality', 90))
    if quality < 1 or quality > 100:
        quality = 90

    rotate = int(data.get('rotate', 0))
    if rotate not in [0, 90, 180, 270]:
        rotate = 0

    crop_ratio = data.get('crop', 'none')
    valid_crops = ['none', '1:1', '4:3', '3:4', '16:9', '9:16', '3:2', '2:3']
    if crop_ratio not in valid_crops:
        crop_ratio = 'none'

    # Format settings
    format_extensions = {'png': '.png', 'jpeg': '.jpg', 'webp': '.webp'}
    format_mimetypes = {'png': 'image/png', 'jpeg': 'image/jpeg', 'webp': 'image/webp'}

    # Create temporary directory
    batch_id = os.urandom(16).hex()
    batch_folder = os.path.join(app.config['UPLOAD_FOLDER'], batch_id)
    os.makedirs(batch_folder, exist_ok=True)

    try:
        # Download the file with timeout and size limit
        headers = {'User-Agent': 'HoneyConvert/1.0'}
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        # Check content length (limit to 50MB)
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 50 * 1024 * 1024:
            return jsonify({'error': 'File too large (max 50MB)'}), 400

        # Extract filename from URL
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = 'image.heic'
        filename = secure_filename(filename)

        # Save downloaded file
        heic_path = os.path.join(batch_folder, filename)
        with open(heic_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Create output filename
        output_filename = os.path.splitext(filename)[0] + format_extensions[output_format]
        output_path = os.path.join(batch_folder, output_filename)

        # Convert the image
        if convert_heic_to_image(heic_path, output_path, output_format, size_percent, quality, rotate, crop_ratio):
            # Remove original file
            os.remove(heic_path)

            # Send the converted file
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype=format_mimetypes[output_format]
            )
        else:
            return jsonify({'error': 'Conversion failed'}), 500

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. The URL took too long to respond.'}), 408
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download file: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Conversion error: {str(e)}'}), 500
    finally:
        # Cleanup
        try:
            for f in os.listdir(batch_folder):
                os.remove(os.path.join(batch_folder, f))
            os.rmdir(batch_folder)
        except:
            pass


@app.route('/api/convert', methods=['POST', 'OPTIONS'])
def api_convert():
    """
    Public API endpoint for HEIC conversion.

    Accepts multipart/form-data with:
    - file: HEIC/HEIF file (required)
    - format: Output format - png, jpeg, webp (default: png)
    - size: Size percentage - 100, 75, 50, 25 (default: 100)
    - quality: JPEG/WebP quality 1-100 (default: 90)
    - rotate: Rotation degrees - 0, 90, 180, 270 (default: 0)
    - crop: Aspect ratio - none, 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3 (default: none)

    Returns: Converted image file or JSON error
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response

    # Check for file
    if 'file' not in request.files:
        response = jsonify({
            'success': False,
            'error': 'No file provided',
            'code': 'MISSING_FILE',
            'documentation': 'https://honeyconvert.com/api'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400

    file = request.files['file']

    if file.filename == '':
        response = jsonify({
            'success': False,
            'error': 'No file selected',
            'code': 'EMPTY_FILE',
            'documentation': 'https://honeyconvert.com/api'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400

    if not allowed_file(file.filename):
        response = jsonify({
            'success': False,
            'error': 'Invalid file type. Only .heic and .heif files are supported.',
            'code': 'INVALID_FILE_TYPE',
            'documentation': 'https://honeyconvert.com/api'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400

    # Get conversion options
    output_format = request.form.get('format', 'png').lower()
    if output_format not in ['png', 'jpeg', 'webp']:
        output_format = 'png'

    size_percent = int(request.form.get('size', 100))
    if size_percent not in [100, 75, 50, 25]:
        size_percent = 100

    quality = int(request.form.get('quality', 90))
    if quality < 1 or quality > 100:
        quality = 90

    rotate = int(request.form.get('rotate', 0))
    if rotate not in [0, 90, 180, 270]:
        rotate = 0

    crop_ratio = request.form.get('crop', 'none')
    valid_crops = ['none', '1:1', '4:3', '3:4', '16:9', '9:16', '3:2', '2:3']
    if crop_ratio not in valid_crops:
        crop_ratio = 'none'

    # Format settings
    format_extensions = {'png': '.png', 'jpeg': '.jpg', 'webp': '.webp'}
    format_mimetypes = {'png': 'image/png', 'jpeg': 'image/jpeg', 'webp': 'image/webp'}

    # Create temporary directory
    batch_id = os.urandom(16).hex()
    batch_folder = os.path.join(app.config['UPLOAD_FOLDER'], batch_id)
    os.makedirs(batch_folder, exist_ok=True)

    try:
        filename = secure_filename(file.filename)
        heic_path = os.path.join(batch_folder, filename)
        file.save(heic_path)

        # Create output filename
        output_filename = os.path.splitext(filename)[0] + format_extensions[output_format]
        output_path = os.path.join(batch_folder, output_filename)

        # Convert the image
        if convert_heic_to_image(heic_path, output_path, output_format, size_percent, quality, rotate, crop_ratio):
            os.remove(heic_path)

            response = send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype=format_mimetypes[output_format]
            )
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['X-HoneyConvert-Format'] = output_format
            response.headers['X-HoneyConvert-Size'] = str(size_percent)
            return response
        else:
            response = jsonify({
                'success': False,
                'error': 'Conversion failed. The file may be corrupted or not a valid HEIC/HEIF image.',
                'code': 'CONVERSION_FAILED',
                'documentation': 'https://honeyconvert.com/api'
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500

    except Exception as e:
        response = jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'code': 'SERVER_ERROR',
            'documentation': 'https://honeyconvert.com/api'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500
    finally:
        # Cleanup
        try:
            for f in os.listdir(batch_folder):
                os.remove(os.path.join(batch_folder, f))
            os.rmdir(batch_folder)
        except:
            pass


@app.route('/api')
def api_docs():
    """API documentation page"""
    return render_template('api.html')


@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files"""
    try:
        # This can be called to clean up old temporary files
        for folder in os.listdir(app.config['UPLOAD_FOLDER']):
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    os.remove(os.path.join(folder_path, file))
                os.rmdir(folder_path)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # For local development only
    # In production, gunicorn will run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
