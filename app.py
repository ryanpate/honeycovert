from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, make_response
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

# Create temp folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'heic', 'heif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_heic_to_png(heic_path, output_path, size_percent=100):
    """Convert HEIC file to PNG with optional resizing
    
    Args:
        heic_path: Path to input HEIC file
        output_path: Path to output PNG file
        size_percent: Percentage to resize (100 = original, 75 = 75%, etc.)
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
        
        # Save as PNG
        image.save(output_path, 'PNG')
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
    <lastmod>2024-10-27</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/about</loc>
    <lastmod>2024-10-27</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/privacy</loc>
    <lastmod>2024-10-27</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/terms</loc>
    <lastmod>2024-10-27</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://honeyconvert.com/contact</loc>
    <lastmod>2024-10-27</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
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
            
            # Create PNG filename (replace .heic/.heif with .png)
            png_filename = os.path.splitext(filename)[0] + '.png'
            png_path = os.path.join(batch_folder, png_filename)
            
            # Convert to PNG with size parameter
            if convert_heic_to_png(heic_path, png_path, size_percent):
                converted_files.append({
                    'original': filename,
                    'converted': png_filename,
                    'path': png_path
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
        png_path = converted_files[0]['path']
        png_filename = converted_files[0]['converted']
        
        return send_file(
            png_path,
            as_attachment=True,
            download_name=png_filename,
            mimetype='image/png'
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
