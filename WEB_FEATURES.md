# Web Application Features Documentation

## Overview
This document describes the new web-based features that replicate functionality from the Tkinter desktop application.

## New Features

### 1. Reference Image Management (`/references`)

The reference image management page allows users to upload, view, and manage reference images for parking space setup.

#### Features:
- **Upload Reference Images**: Support for JPG, JPEG, PNG, and BMP formats
- **Auto-dimension Detection**: Automatically detects image width and height
- **Video Association**: Link reference images to video sources
- **Image Preview**: Real-time preview during upload
- **Grid View**: Displays all saved references in a responsive grid
- **Delete Functionality**: Remove reference images with automatic file cleanup

#### API Endpoints:
- `GET /references` - View reference management page
- `POST /api/references/add` - Upload a new reference image
  - Parameters: `name`, `width`, `height`, `video_source`, `image` (file)
- `DELETE /api/references/<id>/delete` - Delete a reference image
- `GET /media/references/<filename>` - Serve reference image files

#### Usage:
```bash
# Upload a reference image
curl -X POST http://localhost:5000/api/references/add \
  -F "name=Main Parking Lot" \
  -F "width=1280" \
  -F "height=720" \
  -F "video_source=media/carPark.mp4" \
  -F "image=@/path/to/image.jpg"

# Delete a reference image
curl -X DELETE http://localhost:5000/api/references/1/delete
```

### 2. Parking Space Setup (`/setup`)

The setup page provides an interactive canvas for drawing parking spaces and managing groups.

#### Features:
- **Interactive Canvas**: Draw parking spaces with mouse
- **Drawing Mode**: Click and drag to create parking spaces
- **Select Mode**: Multi-select parking spaces for grouping
- **Group Management**: Create groups for larger vehicles (trucks, buses)
- **Bulk Operations**: Delete multiple selected spaces at once
- **Save/Load Layouts**: Persist parking configurations
- **Real-time Statistics**: Display total spaces, selected spaces, and groups

#### API Endpoints:
- `GET /setup` - View parking space setup page
- `POST /api/groups/create` - Create a parking space group
  - Parameters: `name`, `member_spaces` (JSON array)
- `POST /api/setup/save` - Save parking space layout
  - Parameters: `spaces` (JSON array), `reference_id`
- `GET /api/setup/load` - Load saved parking space layout

#### Usage:
```bash
# Create a parking space group
curl -X POST http://localhost:5000/api/groups/create \
  -d "name=Large Vehicle Zone" \
  -d 'member_spaces=["S1","S2","S3"]'

# Save parking layout
curl -X POST http://localhost:5000/api/setup/save \
  -d 'spaces=[{"x":10,"y":10,"width":100,"height":50,"id":"S1"}]' \
  -d "reference_id=1"

# Load saved layout
curl -X GET http://localhost:5000/api/setup/load
```

## Database Models

### ReferenceImage
Stores metadata for reference images used in parking space setup.

**Fields:**
- `id` (Integer): Primary key
- `name` (String): Unique reference name
- `filename` (String): Stored filename
- `width` (Integer): Image width in pixels
- `height` (Integer): Image height in pixels
- `video_source` (String): Associated video file path (optional)
- `created_at` (DateTime): Creation timestamp

### ParkingSpaceGroup
Stores parking space groups for managing larger vehicle areas.

**Fields:**
- `id` (Integer): Primary key
- `group_id` (String): Unique group identifier (e.g., GROUP_001)
- `name` (String): Human-readable group name
- `member_spaces` (Text): JSON array of space IDs in the group
- `section` (String): Section/zone designation
- `is_occupied` (Boolean): Current occupancy status
- `created_at` (DateTime): Creation timestamp

## File Structure

```
Smart_Parking_System/
├── models/
│   ├── database.py           # SQLAlchemy models
│   └── parking_manager.py    # Existing parking logic
├── templates/
│   ├── index.html            # Main dashboard
│   ├── references.html       # Reference management page
│   └── setup.html           # Parking space setup page
├── media/
│   └── references/          # Uploaded reference images
├── config/
│   ├── parking.db          # SQLite database
│   └── parking_layout.json # Saved parking layouts
└── web_app.py              # Flask application with new routes
```

## Security Features

1. **File Validation**: 
   - Extension checking (jpg, jpeg, png, bmp only)
   - Image verification using PIL to prevent malicious uploads
   - Automatic cleanup on validation failure

2. **Database Security**:
   - SQLAlchemy ORM to prevent SQL injection
   - Transaction rollback on errors
   - Unique constraints on names

3. **File Serving**:
   - Secure filename handling with `secure_filename()`
   - Timestamped filenames to prevent collisions
   - Restricted media directory access

## Configuration

### Media Files
Reference images are stored in `media/references/` and excluded from git via `.gitignore`.

### Database
SQLite database is stored at `config/parking.db` and automatically created on first run.

### Environment Variables
No environment variables required for basic functionality. All settings use sensible defaults.

## Browser Compatibility

The web interface uses:
- Bootstrap 5.3.0 for responsive design
- jQuery 3.6.0 for AJAX operations
- HTML5 Canvas for parking space drawing
- Modern JavaScript (ES6+)

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Reference images not displaying
- Check that `media/references/` directory exists and has write permissions
- Verify image files are not corrupted
- Check browser console for 404 errors

### Database errors
- Ensure SQLite is installed
- Check `config/` directory permissions
- Delete `config/parking.db` to reset database

### Canvas not working
- Enable JavaScript in browser
- Check browser console for errors
- Ensure reference image is loaded before drawing

## Migration from Tkinter

The web application replicates these Tkinter features:

| Tkinter Feature | Web Feature | Status |
|----------------|-------------|---------|
| Reference image upload | `/references` page | ✅ Complete |
| Reference image preview | Image preview in form | ✅ Complete |
| Reference TreeView | Grid view of references | ✅ Complete |
| Parking space drawing | Canvas drawing in `/setup` | ✅ Complete |
| Multi-select mode | Select mode toggle | ✅ Complete |
| Group creation | Group management buttons | ✅ Complete |
| Layout persistence | Save/load API | ✅ Complete |

## Next Steps

Future enhancements could include:
1. Drag-and-drop file upload
2. Image cropping/editing tools
3. Batch reference image import
4. Advanced grouping with sub-groups
5. Export/import parking layouts
6. Real-time collaboration features
