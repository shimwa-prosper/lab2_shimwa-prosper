#!/bin/bash
# organizer.sh - Archives grades.csv with a timestamp, resets the workspace,
# and logs the operation to organizer.log.

SOURCE_FILE="grades.csv"
ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

# 1. Make sure the file to archive exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: '$SOURCE_FILE' not found in $(pwd). Nothing to archive." >&2
    exit 1
fi

# 2. Create the archive directory if it does not exist
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir "$ARCHIVE_DIR" || { echo "Error: could not create '$ARCHIVE_DIR'." >&2; exit 1; }
    echo "Created directory: $ARCHIVE_DIR"
fi

# 3. Build the timestamped name, e.g. grades_20251105-170000.csv
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"

# 4. Move (rename) the file into the archive
if ! mv "$SOURCE_FILE" "$ARCHIVE_DIR/$ARCHIVED_NAME"; then
    echo "Error: failed to archive '$SOURCE_FILE'." >&2
    exit 1
fi

# 5. Workspace reset: fresh empty grades.csv
touch "$SOURCE_FILE"

# 6. Append to the log (never overwrite)
echo "[$TIMESTAMP] Original: $SOURCE_FILE | Archived as: $ARCHIVE_DIR/$ARCHIVED_NAME" >> "$LOG_FILE"

echo "Archived $SOURCE_FILE -> $ARCHIVE_DIR/$ARCHIVED_NAME"
echo "New empty $SOURCE_FILE created. Logged to $LOG_FILE."
