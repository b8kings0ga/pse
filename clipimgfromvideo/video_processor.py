import cv2
import numpy as np
from typing import List, Tuple, Optional
import time

from .slide_detector import SlideDetector


class VideoProcessor:
    def __init__(
        self,
        similarity_threshold: float = 0.15,
        frame_skip: int = 5,
        debug_mode: bool = False
    ):
        """
        Initialize the video processor.
        
        Args:
            similarity_threshold: Threshold for determining if frames are different slides
            frame_skip: Number of frames to skip between comparisons
            debug_mode: Whether to print debug info
        """
        self.similarity_threshold = similarity_threshold
        self.frame_skip = frame_skip
        self.debug_mode = debug_mode
        self.slide_detector = SlideDetector(similarity_threshold)
        
    def extract_slides(self, video_path: str) -> List[np.ndarray]:
        """
        Process a video file and extract unique slides.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of unique slide images as numpy arrays
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        if self.debug_mode:
            print(f"Video info: {total_frames} frames, {fps:.2f} fps, {duration:.2f} seconds")
        
        # Process video frames to detect slides
        unique_slides = []
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            
                
            # Process every nth frame
            if frame_count % self.frame_skip == 0:
                # Update progress in debug mode
                if self.debug_mode and frame_count % (self.frame_skip * 20) == 0:
                    progress = frame_count / total_frames * 100 if total_frames > 0 else 0
                    elapsed = time.time() - start_time
                    print(f"Progress: {progress:.1f}% (Frame {frame_count}/{total_frames}), "
                          f"Time: {elapsed:.1f}s")
                
                # Check if this frame contains a new slide
                processed_frame = self._preprocess_frame(frame)
                if self.slide_detector.is_new_slide(processed_frame, unique_slides):
                    unique_slides.append(processed_frame)
                    if self.debug_mode:
                        print(f"Found new slide #{len(unique_slides)} at frame {frame_count}")
            
            frame_count += 1
            
        cap.release()
        
        if self.debug_mode:
            print(f"Processed {frame_count} frames, found {len(unique_slides)} unique slides")
            print(f"Total processing time: {time.time() - start_time:.2f} seconds")
            
        return unique_slides
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess a frame for slide detection.
        
        Args:
            frame: Original video frame
            
        Returns:
            Preprocessed frame
        """
        # Resize for faster processing if needed
        height, width = frame.shape[:2]
        max_dimension = 1024
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
            
        # Additional preprocessing can be added here if needed
        return frame
    
    def save_slide(self, slide: np.ndarray, output_path: str) -> None:
        """
        Save a slide image to disk.
        
        Args:
            slide: The slide image as a numpy array
            output_path: Path where the slide should be saved
        """
        cv2.imwrite(output_path, slide)
