# Offline Mode Configuration

## Overview

The AI Camera v2.0 system has been configured to work completely offline by downloading and storing all external CSS and JavaScript libraries locally. This ensures the application functions properly even without internet connectivity.

## Libraries Included

### Bootstrap 5.1.3
- **CSS**: `libs/bootstrap/bootstrap.min.css`
- **JavaScript**: `libs/bootstrap/bootstrap.bundle.min.js`
- **Purpose**: UI framework for responsive design and components

### Font Awesome 6.0.0
- **CSS**: `libs/font-awesome/all.min.css`
- **Fonts**: `libs/font-awesome/webfonts/`
  - `fa-solid-900.woff2` (Solid icons)
  - `fa-regular-400.woff2` (Regular icons)
  - `fa-brands-400.woff2` (Brand icons)
- **Purpose**: Icon library for UI elements

### Google Fonts
- **CSS**: `libs/google-fonts/fonts-local.css`
- **Fonts**: `libs/google-fonts/fonts/`
  - **Inter**: 300, 400, 500, 600, 700, 800 weights
  - **Montserrat**: 300, 400, 500, 600, 700, 800 weights
  - **JetBrains Mono**: 300, 400, 500, 600, 700 weights
- **Purpose**: Typography for modern, professional appearance

### Socket.IO 4.0.1
- **JavaScript**: `libs/socket.io/socket.io.js`
- **Purpose**: Real-time communication between client and server

### Chart.js
- **JavaScript**: `libs/chart.js/chart.min.js`
- **Purpose**: Data visualization and charts for analytics

## Directory Structure

```
edge/src/web/static/
├── libs/
│   ├── bootstrap/
│   │   ├── bootstrap.min.css
│   │   └── bootstrap.bundle.min.js
│   ├── font-awesome/
│   │   ├── all.min.css
│   │   └── webfonts/
│   │       ├── fa-solid-900.woff2
│   │       ├── fa-regular-400.woff2
│   │       └── fa-brands-400.woff2
│   ├── google-fonts/
│   │   ├── fonts-local.css
│   │   └── fonts/
│   │       ├── Inter-*.ttf
│   │       ├── Montserrat-*.ttf
│   │       └── JetBrainsMono-*.ttf
│   ├── socket.io/
│   │   └── socket.io.js
│   └── chart.js/
│       └── chart.min.js
└── setup-offline-mode.sh
```

## Setup Script

The `setup-offline-mode.sh` script automates the entire process of downloading and configuring offline libraries:

### Usage

```bash
cd edge/src/web/static
./setup-offline-mode.sh
```

### What the script does:

1. **Creates directory structure** for all libraries
2. **Downloads all external resources** from CDN sources
3. **Updates font paths** in CSS files to reference local files
4. **Creates local font CSS** with proper @font-face declarations
5. **Sets proper permissions** for all files
6. **Provides status updates** throughout the process

### Re-running the script

The script can be run multiple times to update libraries to newer versions. It will overwrite existing files with the latest versions from CDN sources.

## Template Updates

All HTML templates have been updated to use local resources instead of CDN links:

### Before (CDN)
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
```

### After (Local)
```html
<link href="{{ url_for('static', filename='libs/bootstrap/bootstrap.min.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='libs/font-awesome/all.min.css') }}" rel="stylesheet">
<script src="{{ url_for('static', filename='libs/socket.io/socket.io.js') }}"></script>
```

## Benefits

### Offline Functionality
- Application works without internet connectivity
- No dependency on external CDN services
- Consistent performance regardless of network conditions

### Performance
- Faster loading times (no external requests)
- Reduced bandwidth usage
- Predictable resource availability

### Reliability
- No CDN outages affecting the application
- Consistent version control of libraries
- Reduced external dependencies

### Security
- No external JavaScript execution from CDNs
- Complete control over library versions
- Reduced attack surface

## Maintenance

### Updating Libraries
To update libraries to newer versions:

1. Run the setup script again:
   ```bash
   ./setup-offline-mode.sh
   ```

2. Test the application thoroughly after updates

3. Update this documentation if library versions change

### Version Control
- All library files are included in version control
- Changes to library versions should be committed with clear messages
- Consider the impact of library updates on application functionality

## Troubleshooting

### Font Loading Issues
If fonts don't load properly:

1. Check file permissions: `ls -la libs/google-fonts/fonts/`
2. Verify font files exist: `ls libs/google-fonts/fonts/*.ttf`
3. Check browser console for 404 errors
4. Ensure `fonts-local.css` is being loaded correctly

### Icon Display Issues
If Font Awesome icons don't display:

1. Check font file permissions: `ls -la libs/font-awesome/webfonts/`
2. Verify CSS paths are correct in `all.min.css`
3. Check browser console for font loading errors

### Bootstrap Issues
If Bootstrap components don't work:

1. Verify both CSS and JS files are loaded
2. Check browser console for JavaScript errors
3. Ensure file paths in templates are correct

## File Sizes

Approximate file sizes for offline libraries:

- **Bootstrap CSS**: ~160KB
- **Bootstrap JS**: ~76KB
- **Font Awesome CSS**: ~87KB
- **Font Awesome Fonts**: ~250KB total
- **Google Fonts**: ~2MB total
- **Socket.IO**: ~180KB
- **Chart.js**: ~203KB

**Total**: ~3MB for complete offline functionality

## Conclusion

The offline mode configuration ensures the AI Camera system operates reliably in any network environment while maintaining the modern, professional appearance and functionality expected from the application.
