# Flask Authentication Portal

A secure local authentication portal built using Python and Flask.

## Features
- User registration with input validation
- Email verification workflow using timed secure tokens (`itsdangerous`)
- Password hashing with PBKDF2/SHA256 (`werkzeug.security`)
- Session management for authenticated users
- Clean logout functionality

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt