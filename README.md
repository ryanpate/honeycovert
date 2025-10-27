# HEIC to PNG Converter

A user-friendly Flask web application that converts iPhone HEIC images to PNG format.

## Features

- 🖼️ Convert multiple HEIC/HEIF files at once
- 📁 Drag & drop or click to upload files
- 📏 **Choose output size: Original, Large (75%), Medium (50%), or Small (25%)**
- 💾 Maintains original filenames (just changes extension)
- 📦 Single file downloads directly, multiple files in a ZIP
- 🎨 Beautiful, responsive UI
- ⚡ Fast and efficient conversion

## Installation

### For Local Development

1. Install Python 3.8 or higher

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

**Note for macOS users:** You may need to install `libheif` first:
```bash
brew install libheif
```

**Note for Linux users:** Install required system libraries:
```bash
# Ubuntu/Debian
sudo apt-get install libheif-dev

# Fedora
sudo dnf install libheif-devel
```

### For Deployment

**⚠️ Important:** Netlify does NOT support Flask applications. See **[DEPLOYMENT.md](DEPLOYMENT.md)** for proper deployment options.

**Recommended:** Use Render.com (free tier available) - see detailed instructions in DEPLOYMENT.md

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - Click the upload area or drag & drop your HEIC files
   - Review the selected files
   - Click "Convert to PNG" to start the conversion
   - Your converted PNG files will download automatically

## How It Works

1. **Upload**: Select one or more HEIC/HEIF files from your iPhone
2. **Choose Size**: Select the output size (Original, Large, Medium, or Small) to reduce file size if needed
3. **Convert**: The server converts each file to PNG format, maintaining the original filename
4. **Download**: 
   - Single file: Downloads immediately as PNG
   - Multiple files: Downloads as a ZIP archive containing all converted PNGs

## Technical Details

- **Backend**: Flask (Python web framework)
- **Image Processing**: Pillow + pillow-heif
- **File Handling**: Secure filename handling with Werkzeug
- **Max File Size**: 100MB per upload
- **Supported Formats**: .heic, .heif

## File Structure

```
heic-to-png-converter/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
└── temp_uploads/         # Temporary storage (created automatically)
```

## Troubleshooting

**"No module named 'pillow_heif'"**
- Make sure you've installed all requirements: `pip install -r requirements.txt`

**"Error converting file"**
- Ensure the file is a valid HEIC/HEIF image
- Check that you have the system libraries installed (libheif)

**"413 Request Entity Too Large"**
- Individual files must be under 100MB
- The limit can be adjusted in `app.py` by modifying `MAX_CONTENT_LENGTH`

## Security Notes

- Files are temporarily stored during conversion and deleted immediately after
- Filenames are sanitized to prevent directory traversal attacks
- Maximum file size limits prevent abuse

## License

This project is free to use and modify for personal and commercial purposes.

## Support

For issues or questions, please check:
1. That all dependencies are installed correctly
2. That your HEIC files are valid and not corrupted
3. That you have sufficient disk space for temporary file storage
