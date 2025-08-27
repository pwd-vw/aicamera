#!/bin/bash

# Download Google Fonts for offline use
# This script downloads all the font files referenced in fonts.css

mkdir -p fonts

# Download Inter fonts
wget -O fonts/Inter-300.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuOKfMZg.ttf"
wget -O fonts/Inter-400.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZg.ttf"
wget -O fonts/Inter-500.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuI6fMZg.ttf"
wget -O fonts/Inter-600.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf"
wget -O fonts/Inter-700.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuFuYMZg.ttf"
wget -O fonts/Inter-800.ttf "https://fonts.gstatic.com/s/inter/v19/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuDyYMZg.ttf"

# Download JetBrains Mono fonts
wget -O fonts/JetBrainsMono-300.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8lqxjPQ.ttf"
wget -O fonts/JetBrainsMono-400.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjPQ.ttf"
wget -O fonts/JetBrainsMono-500.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8-qxjPQ.ttf"
wget -O fonts/JetBrainsMono-600.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8FqtjPQ.ttf"
wget -O fonts/JetBrainsMono-700.ttf "https://fonts.gstatic.com/s/jetbrainsmono/v23/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8L6tjPQ.ttf"

# Download Montserrat fonts
wget -O fonts/Montserrat-300.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCs16Ew-.ttf"
wget -O fonts/Montserrat-400.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCtr6Ew-.ttf"
wget -O fonts/Montserrat-500.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCtZ6Ew-.ttf"
wget -O fonts/Montserrat-600.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCu170w-.ttf"
wget -O fonts/Montserrat-700.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCuM70w-.ttf"
wget -O fonts/Montserrat-800.ttf "https://fonts.gstatic.com/s/montserrat/v30/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCvr70w-.ttf"

echo "All fonts downloaded successfully!"
