#!/bin/bash

SERVER="lprserver.tail605477.ts.net"
USER="aicamera"
REMOTE_DIR="/home/devuser/aicamera/server/storage"
LOCAL_FILE="$1"

if [ -z "$LOCAL_FILE" ]; then
    echo "Usage: $0 <local-file-path>"
    exit 1
fi

echo "Uploading $LOCAL_FILE to $SERVER..."
sftp $USER@$SERVER << EOF
cd $REMOTE_DIR
put "$LOCAL_FILE"
exit
EOF

if [ $? -eq 0 ]; then
    echo "✅ Upload successful!"
else
    echo "❌ Upload failed!"
    exit 1
fi