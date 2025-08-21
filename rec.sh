#!/bin/bash

find . -type f -name "*.txt" | while read -r file; do 
  txt_file="${file%.txt}.py"
  mv "$file" "$txt_file"

  echo "converted: $file -> $txt_file"

done


# find . -type d -name "__pycache__" | while read -r dir; do 
#   rm -rf "$dir"
#   echo "removed $dir"
#
# done
