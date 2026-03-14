#!/bin/bash

SOURCE_DIR="/run/media/nanta/Nanta/Skyrim/skyrimse"
DEST_DIR="/mnt/data/Mods"
FOLDERS_FILE="/home/nanta/Project/GateToSovngarde/GTSv101.txt"

mkdir -p "$DEST_DIR"

while IFS= read -r folder_name; do
    find "$SOURCE_DIR" -type f \( -iname "*.zip" -o -iname "*.7z" -o -iname "*.rar" \) -iname "*${folder_name}*" -exec cp -v {} "$DEST_DIR" \;
done < "$FOLDERS_FILE"

echo "Done! Files copied to $DEST_DIR"
