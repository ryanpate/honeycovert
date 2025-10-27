from flask import Flask, render_template, request, send_file, jsonify
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

def convert_heic_to_png(heic_path, output_path):
    """Convert HEIC file to PNG"""
    try:
        # Open the HEIC image
        image = Image.open(heic_path)
        
        # Convert to RGB if necessary (HEIC can be in different color modes)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as PNG
        image.save(output_path, 'PNG')
        return True
    except Exception as e:
        print(f"Error converting {heic_path}: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
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
            
            # Convert to PNG
            if convert_heic_to_png(heic_path, png_path):
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
    app.run(debug=True, host='0.0.0.0', port=5000)
