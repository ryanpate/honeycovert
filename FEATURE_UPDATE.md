# New Feature: Image Size Reduction

## What's New?

Your HEIC to PNG converter now includes an **Output Size selector** that allows users to reduce the image dimensions during conversion!

## Changes Made

### 1. Backend Updates (`app.py`)
- Modified `convert_heic_to_png()` function to accept a `size_percent` parameter
- Added high-quality image resizing using PIL's LANCZOS resampling algorithm
- Updated `/convert` route to accept and validate size parameter from form data
- Supports 4 size options: 100% (Original), 75% (Large), 50% (Medium), 25% (Small)

### 2. Frontend Updates (`templates/index.html`)
- Added a styled dropdown selector for choosing output size
- Default selection is "Large (75%)" for a good balance between quality and file size
- Updated JavaScript to send the size parameter with form submission
- Added helpful hint text: "Reduce size to save space and speed up uploads"

### 3. User Interface
The new size selector appears between the file list and the convert button, featuring:
- Clean, modern styling that matches the existing design
- Purple gradient theme consistency (#667eea to #764ba2)
- Smooth hover effects
- Clear labels and descriptions

## Benefits

- **Smaller File Sizes**: Reduce PNG file sizes by up to 75% (at 25% setting)
- **Faster Uploads**: Smaller files mean faster upload speeds for sharing
- **Web Optimization**: Create web-friendly image sizes without additional tools
- **Flexible Options**: Users can choose based on their needs (quality vs size)

## Size Comparison Examples

Original iPhone HEIC (12MP, ~4000x3000 pixels):
- **Original (100%)**: ~4000x3000px PNG (~5-8 MB)
- **Large (75%)**: ~3000x2250px PNG (~3-5 MB) ⭐ **Recommended**
- **Medium (50%)**: ~2000x1500px PNG (~1-3 MB)
- **Small (25%)**: ~1000x750px PNG (~300-800 KB)

## Technical Details

- **Algorithm**: Lanczos resampling (high-quality downsampling)
- **Validation**: Backend validates size values (100, 75, 50, 25 only)
- **Default**: 75% for optimal balance
- **Image Quality**: No quality loss from conversion, only from intentional resizing

## Usage

1. Upload your HEIC files
2. Select your preferred output size from the dropdown
3. Click "Convert to PNG"
4. Download your resized PNG images

## Deployment

All deployment configurations remain the same. Simply push the updated code to your hosting platform (Render, Railway, etc.) and the new feature will be available immediately.

No additional dependencies required - uses existing Pillow library functionality!
