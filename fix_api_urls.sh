#!/bin/bash

# Fix all API URLs to include /api/v1 prefix
cd /Users/rohindaswani/Projects/immigration_app/frontend/src/api

# List of files to update
files=("history.ts" "profile.ts" "documents.ts" "timeline.ts")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "Updating $file..."
        # Replace API endpoints to include /api/v1 prefix
        sed -i '' 's|apiClient\.\(get\\|post\\|put\\|patch\\|delete\)('\''\/\([^'\'']*\)|apiClient.\1('\''/api/v1/\2|g' "$file"
        sed -i '' 's|apiClient\.\(get\\|post\\|put\\|patch\\|delete\)(`\/\([^`]*\)|apiClient.\1(`/api/v1/\2|g' "$file"
    fi
done

echo "API URLs updated!"