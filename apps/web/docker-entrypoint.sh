#!/bin/sh
set -eu
api_url="${FAIRFARM_API_URL:-http://localhost:8000/api/v1}"
printf 'window.__FAIRFARM_CONFIG__ = { API_URL: "%s" };' "$api_url" > /usr/share/nginx/html/config.js
