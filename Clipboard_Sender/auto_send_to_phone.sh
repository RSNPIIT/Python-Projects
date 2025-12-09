#!/bin/bash

LAST=""

while true; do
    CURRENT=$(xclip -o -selection clipboard 2>/dev/null)

    if [ "$CURRENT" != "$LAST" ]; then
        echo "$CURRENT" > ~/latest_clip.txt
        LAST="$CURRENT"
        echo "[AUTO] Updated laptop clipboard for phone"
    fi

    sleep 0.2
done
