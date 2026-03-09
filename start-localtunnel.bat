@echo off
echo Starting localtunnel for port 8080...
echo Make sure you have npx and localtunnel installed
echo.
echo Install with: npm install -g localtunnel
echo.
npx localtunnel --port 8080 --subdomain yomu-japanese
pause
