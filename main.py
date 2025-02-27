import argparse
import os
import sys
from pathlib import Path

from clipimgfromvideo.video_processor import VideoProcessor
from clipimgfromvideo.utils import sniff_video_from_webpage, ensure_dir_exists


def process_video(input_path, output_dir, threshold, skip_frames, debug_mode):
    """Process the video and extract slides"""
    # Create output directory
    ensure_dir_exists(output_dir)
    
    # Process input (URL or file)
    if input_path.lower().startswith(('http://', 'https://', 'www.')):
        print(f"Extracting video from webpage: {input_path}...")
        video_path = sniff_video_from_webpage(input_path, output_dir=output_dir)
        if not video_path:
            print("Failed to extract video from the webpage.")
            return False
    else:
        video_path = input_path
        if not os.path.exists(video_path):
            print(f"Error: Video file '{video_path}' not found")
            return False
    
    # Process the video
    processor = VideoProcessor(
        similarity_threshold=threshold,
        frame_skip=skip_frames,
        debug_mode=debug_mode
    )
    
    print(f"Processing video: {video_path}")
    slides = processor.extract_slides(video_path)
    
    # Save the extracted slides
    print(f"Saving {len(slides)} slides to {output_dir}")
    for i, slide in enumerate(slides):
        output_path = os.path.join(output_dir, f"slide_{i+1:03d}.jpg")
        processor.save_slide(slide, output_path)
    
    print("Processing complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description='Extract slides from presentation videos')
    parser.add_argument('input', nargs='?', help='Webpage URL or path to local video file')
    parser.add_argument('-o', '--output', help='Output directory for extracted slides',
                        default='./extracted_slides')
    parser.add_argument('-t', '--threshold', type=float, default=0.15,
                        help='Similarity threshold for slide detection (0.0-1.0)')
    parser.add_argument('-s', '--skip', type=int, default=5,
                        help='Number of frames to skip between checks')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--gui', action='store_true',
                        help='Launch the graphical user interface')
    
    args = parser.parse_args()
    
    # Check if GUI mode is requested
    if args.gui or args.input is None:
        try:
            from clipimgfromvideo.gui import launch_gui
            launch_gui()
            return
        except ImportError as e:
            print(f"Error importing GUI components: {str(e)}")
            print("Make sure tkinter is installed for your Python environment.")
            sys.exit(1)
    
    # Run in command-line mode
    process_video(
        input_path=args.input,
        output_dir=args.output,
        threshold=args.threshold,
        skip_frames=args.skip,
        debug_mode=args.debug
    )


if __name__ == "__main__":
    main()
