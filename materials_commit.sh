#!/bin/bash

# Target directory relative to root
TARGET_DIR="materials"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' not found from this root path."
    exit 1
fi

echo "Scanning for academic records and promotional documents inside $TARGET_DIR from root workspace..."

# Force git to list individual documents down the untracked folder path tree
git status --porcelain -uall "$TARGET_DIR" | grep -E '^(\?\?| M|M ) ' | sed 's/^...//' | while read -r FILE; do
    
    # Strip wrapping quotes if git outputs them for paths containing spaces/special chars
    FILE=$(echo "$FILE" | sed -e 's/^"//' -e 's/"$//')

    # Guard against directories or temp locks
    if [ -d "$FILE" ]; then
        continue
    fi

    # Extract base filename for granular identification
    FILENAME=$(basename "$FILE")

    # Dynamically structure granular, descriptive commit messages based on tracking indices
    if [[ "$FILE" == "$TARGET_DIR/certificates_directory/NOC"* ]] || [[ "$FILE" == "$TARGET_DIR/certificates_directory/NPTEL"* ]]; then
        MSG="Academic Records: Archiving official National Programme on Technology Enhanced Learning (NPTEL) course completion certificate ($FILENAME) tracking metrics"
    elif [[ "$FILE" == "$TARGET_DIR/certificates_directory/24F"* ]] || [[ "$FILE" == "$TARGET_DIR/certificates_directory/Certificate_"* ]]; then
        MSG="Academic Records: Indexing verified institutional program credentials, skills certification documents, and baseline program records ($FILENAME)"
    elif [[ "$FILE" == "$TARGET_DIR/certificates_directory/"* ]]; then
        MSG="Academic Records: Staging cryptographic document verification hashes and verified registration records for asset validation ($FILENAME)"
    elif [[ "$FILE" == "$TARGET_DIR/promotional_materials/"* ]]; then
        MSG="Institutional Reference: Cataloging official academic brochures, curriculum syllabi schemas, and program structural criteria booklets ($FILENAME)"
    else
        MSG="Maintenance Update: Staging routine structural workspace synchronization protocols and tracking configurations for portfolio asset $FILENAME"
    fi

    echo "Staging document file: $FILE"
    git add "$FILE"

    echo "Committing with detailed message: '$MSG'"
    git commit -m "$MSG"
    
    echo "----------------------------------------------------------------------"
done

# Push the final chain of individual commits to the repository remote
echo "Pushing all individual academic credential commits sequentially to the remote repository branch..."
git push
