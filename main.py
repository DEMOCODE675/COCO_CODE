#!/usr/bin/env python3
"""
COCO_CODE CLI - Main Entry Point
===========================================

A powerful Python CLI tool that generates complete web projects dynamically.

Usage:
    python main.py
    
Features:
    - Dynamic framework selection (React, Vue, Next.js, Express, etc.)
    - Automatic package installation via npm
    - Smart config generation (tsconfig, tailwind, vite, etc.)
    - Full project folder structure creation
    - Extensible configuration via config.json
    - TypeScript support
    - Error handling and recovery
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()

