#!/usr/bin/env bash
set -e

git init
git branch -M main
git remote add origin https://github.com/claaudiacaarbo/Proyecto.git 2>/dev/null || true
git add .
git commit -m "Subida final del proyecto" || true
git push -u origin main
