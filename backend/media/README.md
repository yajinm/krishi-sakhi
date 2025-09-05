# Media Directory

This directory stores uploaded files and generated media.

## Subdirectories

- `tts/` - Text-to-speech generated audio files
- `uploads/` - User uploaded files
- `temp/` - Temporary files

## File Types

- Audio files: WAV, MP3, M4A
- Image files: JPG, JPEG, PNG
- Documents: PDF, DOC, DOCX

## Security

- Files are served through FastAPI static file serving
- Access is controlled through authentication
- File uploads are validated for type and size
