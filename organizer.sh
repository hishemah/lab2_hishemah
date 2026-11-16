#!/bin/bash

source_file="grades.csv"
archive_dir="archive"
log_file="organizer.log"

if [ ! -f "$source_file" ]; then
    echo "Error: $source_file was not found in $(pwd)." >&2
    exit 1
fi

if [ ! -s "$source_file" ]; then
    echo "Warning: $source_file is empty, it will be archived anyway."
fi

if [ -e "$archive_dir" ] && [ ! -d "$archive_dir" ]; then
    echo "Error: '$archive_dir' exists but is not a directory." >&2
    exit 1
fi

if [ ! -d "$archive_dir" ]; then
    mkdir "$archive_dir" || exit 1
    echo "Created the '$archive_dir' directory."
fi

timestamp=$(date +%Y%m%d-%H%M%S)
archived_file="$archive_dir/grades_$timestamp.csv"

while [ -e "$archived_file" ]; do
    sleep 1
    timestamp=$(date +%Y%m%d-%H%M%S)
    archived_file="$archive_dir/grades_$timestamp.csv"
done

mv "$source_file" "$archived_file" || exit 1
touch "$source_file" || exit 1

echo "$timestamp | original: $source_file | archived: $archived_file" >> "$log_file"

echo "Archived $source_file as $archived_file"
echo "Created a new empty $source_file"
echo "Logged the operation in $log_file"
