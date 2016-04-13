#!/bin/bash

while true; do
    timeout 600 ./fetch.py >/dev/null 2>rss.new.log
    if ! diff -N rss.last.log rss.new.log &>/dev/null; then
        date >>rss.log
        cat rss.new.log >>rss.log
    fi
    mv rss.new.log rss.last.log
    sleep 1800
done
