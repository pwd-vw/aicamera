#!/bin/bash

# AI Camera v2.0 - Offline CSS Setup Script
# This script downloads and configures all external CSS/JS libraries for offline mode

set -e

echo "=== AI Camera v2.0 - Offline CSS Setup ==="
echo "Setting up local copies of external libraries for offline mode..."

# Create directory structure
mkdir -p libs/{bootstrap,font-awesome,google-fonts,socket.io,chart.js}
mkdir -p libs/font-awesome/webfonts
mkdir -p libs/google-fonts/fonts

echo "✓ Directory structure created"

# Download Bootstrap
echo "Downloading Bootstrap..."
wget -q -O libs/bootstrap/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css
wget -q -O libs/bootstrap/bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js
echo "✓ Bootstrap downloaded"

# Download Font Awesome
echo "Downloading Font Awesome..."
wget -q -O libs/font-awesome/all.min.css https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css
wget -q -O libs/font-awesome/webfonts/fa-solid-900.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2
wget -q -O libs/font-awesome/webfonts/fa-regular-400.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2
wget -q -O libs/font-awesome/webfonts/fa-brands-400.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.woff2
echo "✓ Font Awesome downloaded"

# Update Font Awesome paths
sed -i 's|url(../webfonts/|url(webfonts/|g' libs/font-awesome/all.min.css
echo "✓ Font Awesome paths updated"

# Download Socket.IO
echo "Downloading Socket.IO..."
wget -q -O libs/socket.io/socket.io.js https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.4/socket.io.js
echo "✓ Socket.IO downloaded"

# Download Chart.js
echo "Downloading Chart.js..."
wget -q -O libs/chart.js/chart.min.js https://cdn.jsdelivr.net/npm/chart.js
echo "✓ Chart.js downloaded"

# Download Google Fonts
echo "Downloading Google Fonts..."
wget -q -O libs/google-fonts/fonts.css "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap"

# Download individual font files
echo "Downloading font files..."
wget -q -O libs/google-fonts/fonts/Inter-300.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuOKfMZg.ttf"
wget -q -O libs/google-fonts/fonts/Inter-400.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZg.ttf"
wget -q -O libs/google-fonts/fonts/Inter-500.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuI6fMZg.ttf"
wget -q -O libs/google-fonts/fonts/Inter-600.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf"
wget -q -O libs/google-fonts/fonts/Inter-700.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuFuYMZg.ttf"
wget -q -O libs/google-fonts/fonts/Inter-800.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuDyYMZg.ttf"

wget -q -O libs/google-fonts/fonts/JetBrainsMono-300.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8lqxjPQ.ttf"
wget -q -O libs/google-fonts/fonts/JetBrainsMono-400.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjPQ.ttf"
wget -q -O libs/google-fonts/fonts/JetBrainsMono-500.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8-qxjPQ.ttf"
wget -q -O libs/google-fonts/fonts/JetBrainsMono-600.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8FqtjPQ.ttf"
wget -q -O libs/google-fonts/fonts/JetBrainsMono-700.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8L6tjPQ.ttf"

wget -q -O libs/google-fonts/fonts/Montserrat-300.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCs16Ew-.ttf"
wget -q -O libs/google-fonts/fonts/Montserrat-400.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCtr6Ew-.ttf"
wget -q -O libs/google-fonts/fonts/Montserrat-500.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCtZ6Ew-.ttf"
wget -q -O libs/google-fonts/fonts/Montserrat-600.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCu170w-.ttf"
wget -q -O libs/google-fonts/fonts/Montserrat-700.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCuM70w-.ttf"
wget -q -O libs/google-fonts/fonts/Montserrat-800.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCvr70w-.ttf"
echo "✓ Google Fonts downloaded"

# Create local fonts CSS
cat > libs/google-fonts/fonts-local.css << 'EOF'
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url(../google-fonts/fonts/Inter-300.ttf) format('truetype');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url(../google-fonts/fonts/Inter-400.ttf) format('truetype');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url(../google-fonts/fonts/Inter-500.ttf) format('truetype');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url(../google-fonts/fonts/Inter-600.ttf) format('truetype');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url(../google-fonts/fonts/Inter-700.ttf) format('truetype');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 800;
  font-display: swap;
  src: url(../google-fonts/fonts/Inter-800.ttf) format('truetype');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url(../google-fonts/fonts/JetBrainsMono-300.ttf) format('truetype');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url(../google-fonts/fonts/JetBrainsMono-400.ttf) format('truetype');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url(../google-fonts/fonts/JetBrainsMono-500.ttf) format('truetype');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url(../google-fonts/fonts/JetBrainsMono-600.ttf) format('truetype');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url(../google-fonts/fonts/JetBrainsMono-700.ttf) format('truetype');
}
@font-face {
  font-family: 'Montserrat';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url(../google-fonts/fonts/Montserrat-300.ttf) format('truetype');
}
@font-face {
  font-family: 'Montserrat';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url(../google-fonts/fonts/Montserrat-400.ttf) format('truetype');
}
@font-face {
  font-family: 'Montserrat';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url(../google-fonts/fonts/Montserrat-500.ttf) format('truetype');
}
@font-face {
  font-family: 'Montserrat';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url(../google-fonts/fonts/Montserrat-600.ttf) format('truetype');
}
@font-face {
  font-family: 'Montserrat';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url(../google-fonts/fonts/Montserrat-700.ttf) format('truetype');
}
@font-face {
  font-family: 'Montserrat';
  font-style: normal;
  font-weight: 800;
  font-display: swap;
  src: url(../google-fonts/fonts/Montserrat-800.ttf) format('truetype');
}
EOF

echo "✓ Local fonts CSS created"

# Set proper permissions
chmod -R 644 libs/
chmod 755 libs/ libs/*/ libs/*/*/

echo ""
echo "=== Offline Mode Setup Complete ==="
echo "All external libraries have been downloaded and configured for offline use."
echo ""
echo "Libraries included:"
echo "  ✓ Bootstrap 5.1.3 (CSS + JS)"
echo "  ✓ Font Awesome 6.0.0 (CSS + Fonts)"
echo "  ✓ Socket.IO 4.0.1"
echo "  ✓ Chart.js"
echo "  ✓ Google Fonts (Montserrat, Inter, JetBrains Mono)"
echo ""
echo "The application will now work completely offline!"
echo ""
echo "To update libraries in the future, run this script again."
