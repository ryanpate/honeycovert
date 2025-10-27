# Quick Test Guide - Image Size Reduction Feature

## Testing Locally

### 1. Setup
```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the application
python app.py
```

### 2. Open in Browser
Navigate to: `http://localhost:5000`

### 3. Test the Feature

**What You Should See:**
- The familiar upload area at the top
- A new purple-bordered section labeled "Output Size:" between the file list and convert button
- A dropdown with 4 options:
  - Original (100%)
  - Large (75%) ← **Selected by default**
  - Medium (50%)
  - Small (25%)
- Helper text: "Reduce size to save space and speed up uploads"

**Test Scenarios:**

#### Test 1: Single File at Different Sizes
1. Upload one HEIC file
2. Select "Original (100%)" from dropdown
3. Click "Convert to PNG"
4. Note the file size of downloaded PNG
5. Upload the same HEIC file again
6. Select "Small (25%)" from dropdown
7. Convert and compare file sizes

**Expected Result:** The 25% version should be significantly smaller in both dimensions and file size

#### Test 2: Multiple Files
1. Upload 3-5 HEIC files
2. Select "Medium (50%)"
3. Convert to PNG
4. Extract the ZIP file
5. Check that all images are resized proportionally

**Expected Result:** All images should be 50% of their original dimensions

#### Test 3: Default Behavior
1. Upload files without changing the dropdown
2. Convert

**Expected Result:** Files should be converted at 75% (Large) by default

## Verification Checklist

- [ ] Dropdown appears and is styled correctly
- [ ] All 4 size options are present
- [ ] Default selection is "Large (75%)"
- [ ] Hover effects work on dropdown
- [ ] Size parameter is sent with form submission
- [ ] Images are resized correctly based on selection
- [ ] Original aspect ratio is maintained
- [ ] File sizes decrease proportionally
- [ ] Image quality remains good (using LANCZOS resampling)
- [ ] Works with single file download
- [ ] Works with multiple files (ZIP)

## Example Size Comparison

Original iPhone photo (4032 x 3024 pixels):

| Setting | Dimensions | Approx File Size | Use Case |
|---------|-----------|------------------|----------|
| Original (100%) | 4032 x 3024 | 5-8 MB | Printing, archival |
| Large (75%) | 3024 x 2268 | 3-5 MB | High-quality web, social media |
| Medium (50%) | 2016 x 1512 | 1-3 MB | Standard web use |
| Small (25%) | 1008 x 756 | 300-800 KB | Thumbnails, previews |

## Common Issues

**Issue:** Dropdown doesn't appear
- **Solution:** Clear browser cache and refresh

**Issue:** Images aren't resized
- **Solution:** Check browser console for errors, ensure form data includes 'size' parameter

**Issue:** Images look pixelated
- **Solution:** Verify LANCZOS resampling is being used (check app.py line 46)

## Browser Testing

Test in multiple browsers:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari

All should display the dropdown correctly and submit the size parameter.

## Deployment Testing

After deploying to Render/Railway:
1. Visit your deployed URL
2. Repeat all tests above
3. Verify size reduction works in production environment

## Success Criteria

✅ Feature is working when:
- Dropdown is visible and functional
- Images are resized according to selection
- File sizes are reduced appropriately
- Image quality remains acceptable
- No errors in console or server logs
- Works on both local and deployed versions

Happy testing! 🎉
