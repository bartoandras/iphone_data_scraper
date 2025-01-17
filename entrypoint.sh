#!/bin/bash
# Entrypoint script for iPhone Scraper container
# Manages cron service and logging

# Start cron service
service cron start

# Create log file if it doesn't exist
touch /var/log/cron/scraper.log

# Tail the log file to keep container running
tail -f /var/log/cron/scraper.log
