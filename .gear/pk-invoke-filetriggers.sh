#/bin/sh -efu

/usr/lib/rpm/postupdate

if set /var/cache/apt/*.bin && [ -f "$1" ]; then
    rm -f "$@"
fi
