#!/bin/bash

# Update Font Awesome CSS to use local font paths
sed -i 's|url(../webfonts/|url(webfonts/|g' all.min.css

echo "Font Awesome paths updated to use local webfonts directory"
