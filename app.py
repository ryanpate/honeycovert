from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, make_response
from flask_compress import Compress
import os
from PIL import Image
from pillow_heif import register_heif_opener
import io
import zipfile
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
    """Add security and cache headers to all responses"""
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

    # Cache headers based on content type
    if request.path.startswith('/static/'):
        # Static assets: cache for 1 year
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    elif request.path in ['/', '/about', '/privacy', '/terms', '/contact',
                          '/what-is-heic', '/heic-vs-png', '/why-iphone-uses-heic',
                          '/how-to-convert-heic-to-png', '/heic-not-opening-windows',
                          '/heic-to-jpeg-vs-png', '/batch-convert-heic',
                          '/heic-converter-mac', '/convert-heic-without-losing-quality']:
        # HTML pages: cache for 1 hour, revalidate
        response.headers['Cache-Control'] = 'public, max-age=3600, must-revalidate'
    elif request.path in ['/robots.txt', '/sitemap.xml']:
        # SEO files: cache for 1 day
        response.headers['Cache-Control'] = 'public, max-age=86400'

    return response

ALLOWED_EXTENSIONS = {'heic', 'heif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_heic_to_image(heic_path, output_path, output_format='png', size_percent=100, quality=90):
    """Convert HEIC file to specified format with optional resizing

    Args:
        heic_path: Path to input HEIC file
        output_path: Path to output file
        output_format: Output format ('png', 'jpeg', 'webp')
        size_percent: Percentage to resize (100 = original, 75 = 75%, etc.)
        quality: Quality for JPEG/WebP (1-100, ignored for PNG)
    """
    try:
        # Open the HEIC image
        image = Image.open(heic_path)

        # Convert to RGB if necessary (HEIC can be in different color modes)
        if image.mode != 'RGB':
            image = image.convert('RGB')

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
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://honeyconvert.com/</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/about</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/what-is-heic</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-vs-png</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/why-iphone-uses-heic</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/how-to-convert-heic-to-png</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.95</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-not-opening-windows</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/privacy</loc>
    <lastmod>2025-11-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/terms</loc>
    <lastmod>2025-11-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/contact</loc>
    <lastmod>2025-11-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-to-jpeg-vs-png</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/batch-convert-heic</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/heic-converter-mac</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/convert-heic-without-losing-quality</loc>
    <lastmod>2025-12-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
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

            # Convert to requested format
            if convert_heic_to_image(heic_path, output_path, output_format, size_percent, quality):
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
