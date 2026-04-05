#!/bin/bash 
set -euo pipefail 
 
FILE="${1:-}" 
DEST="gdrive1:CCTV_Motion_Clips" 
LOG="/var/log/motion/rclone_motion.log" 
 
[ -n "$FILE" ] || exit 0 
[ -f "$FILE" ] || exit 0 
 
prev_size=0 
for i in {1..10}; do 
 size=$(stat -c%s "$FILE" 2>/dev/null || echo 0) 
 if [ "$size" -gt 0 ] && [ "$size" -eq "$prev_size" ]; then 
   break 
 fi 
 prev_size="$size" 
 sleep 0.3 
done 
 
/usr/bin/rclone copy "$FILE" "$DEST" \ 
 --log-file="$LOG" \ 
 --log-level INFO 
 
rm -f "$FILE"