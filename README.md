# Presentation Slide Extractor

A Python tool that extracts unique slides from presentation videos. This tool can process local video files or extract videos from webpages, then automatically extract and save distinct slides as separate image files.




## Features

- Extract slides from local video files
- Extract videos from any webpage that contains video content
- Automatically detect slide transitions
- Skip duplicate/similar frames
- Save extracted slides as images
- Customizable sensitivity settings
- Graphical user interface
- Available as standalone Windows executable (no Python installation required)

## Installation

### Option 1: Windows Standalone Executable

1. Download the latest release from the releases page
2. Extract the ZIP file
3. Run `SlideExtractor.exe`

No additional installation is required.

### Option 2: From Source

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd clipimgfromvideo
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode

To launch the graphical user interface:

```bash
python main.py
# or
python main.py --gui
# or
python run_gui.py
```

The GUI allows you to:
- Enter a URL or browse for a local video file
- Select an output directory
- Adjust threshold and frame skip settings
- Toggle debug mode
- View logs in real-time

### Command Line Mode

```bash
python main.py path/to/video.mp4
```

or for a video embedded in a webpage:

```bash
python main.py https://example.com/page-with-video
```

### Options

```
usage: main.py [-h] [-o OUTPUT] [-t THRESHOLD] [-s SKIP] [-d] [--gui] [input]

Extract slides from presentation videos

positional arguments:
  input                 Webpage URL or path to local video file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for extracted slides
  -t THRESHOLD, --threshold THRESHOLD
                        Similarity threshold for slide detection (0.0-1.0)
  -s SKIP, --skip SKIP  Number of frames to skip between checks
  -d, --debug           Enable debug mode
  --gui                 Launch the graphical user interface
```

## Building the Windows Executable

To build the standalone Windows executable:

1. Install the development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```bash
   python build_windows_app.py
   ```

3. The executable will be created in the `dist` folder.

## How It Works

1. The program loads the video from a file or extracts it from a webpage.
2. It processes the video frame by frame, skipping frames to improve performance.
3. For each processed frame, it checks if it's significantly different from previously detected slides.
4. If a new slide is detected, it saves it to the output directory.
5. The process continues until the end of the video.

## Supported Websites

The tool uses yt-dlp under the hood to extract videos, which supports thousands of websites including:
- YouTube, Vimeo, Dailymotion
- University and educational platforms (Coursera, edX, etc.)
- Conference websites
- And many more

## Parameters

- **threshold**: Controls sensitivity of slide detection. Lower values (0.1) will detect more subtle changes, while higher values (0.3) will only detect major changes.
- **skip**: Number of frames to skip between checks. Higher values improve performance but might miss quick slide transitions.

## License

MIT
