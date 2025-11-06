# Ultrasound Image Capture System

A desktop application for capturing images from a USB webcam to simulate a live ultrasound feed, with automatic PDF report generation.

## Features

- Live webcam feed display
- Patient information entry (name, ID, exam title)
- Snapshot capture with timestamp
- Organized file storage structure
- Automatic PDF report generation with:
  - Patient information header
  - All captured images
  - Blank area for clinical notes
  - Signature section
- Fully offline operation
- Cross-platform support (Windows, macOS, Linux)

## Requirements

- Python 3.8 or higher
- USB webcam or built-in camera
- Operating System: Windows, macOS, or Linux

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python app.py
```

2. Enter patient information:
   - Patient Name (required)
   - Patient ID (required)
   - Exam Title (optional)

3. Click "Start Session" to begin:
   - The webcam will activate
   - Live feed will display on the left panel

4. Capture images:
   - Click "Capture Snapshot" to take pictures
   - Each snapshot is saved automatically
   - Captured images list appears on the right panel

5. Finish the session:
   - Click "Finish Session" to complete
   - PDF report is generated automatically
   - All files are saved in: `/reports/PatientName_ID_Timestamp/`

## Output Structure

```
reports/
└── PatientName_ID_20250106_143022/
    ├── snapshot_1_20250106_143045_123.jpg
    ├── snapshot_2_20250106_143102_456.jpg
    └── report.pdf
```

## PDF Report Contents

1. Header with title "ULTRASOUND EXAMINATION REPORT"
2. Patient information table
3. All captured images (one per page)
4. Clinical notes section with blank lines
5. Physician signature and date fields

## Troubleshooting

### Camera not detected
- Ensure your webcam is properly connected
- Check if other applications are using the camera
- Try restarting the application

### Permission errors
- On macOS/Linux: Ensure the application has camera permissions
- On Windows: Check privacy settings for camera access

### PDF generation fails
- Ensure the reports folder has write permissions
- Check that all image files exist before finishing the session

## Technical Details

- **GUI Framework**: Tkinter (built-in with Python)
- **Camera Handling**: OpenCV (cv2)
- **Image Processing**: Pillow (PIL)
- **PDF Generation**: ReportLab
- **No Database**: All data stored as files locally

## License

This application is provided as-is for medical imaging simulation purposes.
