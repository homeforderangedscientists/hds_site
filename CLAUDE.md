# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple static website for HDS (Hiker Data Services). The site uses plain HTML and images with no build system or JavaScript framework.

## Development

No build step required. Open HTML files directly in a browser or use a simple local server:

```bash
python3 -m http.server 8000
```

Then visit http://localhost:8000

## Structure

- HTML files in the root directory
- Images in an `images/` or `assets/` folder
- CSS in a `css/` or `styles/` folder (if separated from HTML)

## Deployment

Static files can be deployed to any web host, CDN, or static hosting service (GitHub Pages, Netlify, Vercel, etc.).
