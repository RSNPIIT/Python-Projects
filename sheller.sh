git ls-files --others --exclude-standard | while read -r file; do
    if [ "$file" != "sheller.sh" ]; then
        git add "$file"
        git commit -m "Add $file"
        git push origin main
    fi
done

