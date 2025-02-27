import cv2
import numpy as np
from typing import List
from skimage.metrics import structural_similarity as ssim


class SlideDetector:
    def __init__(self, similarity_threshold: float = 0.15):
        """
        Initialize the slide detector.
        
        Args:
            similarity_threshold: Threshold below which frames are considered different slides
                                  Higher values make detection more sensitive
        """
        self.similarity_threshold = similarity_threshold
    
    def is_new_slide(self, frame: np.ndarray, existing_slides: List[np.ndarray]) -> bool:
        """
        Determine if a frame contains a new slide compared to existing slides.
        
        Args:
            frame: The current frame to check
            existing_slides: List of previously detected slides
            
        Returns:
            True if this is a new slide, False otherwise
        """
        if not existing_slides:
            return True
            
        # Convert to grayscale for similarity comparison
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for existing_slide in existing_slides:
            # Convert existing slide to grayscale if needed
            if len(existing_slide.shape) == 3:
                existing_gray = cv2.cvtColor(existing_slide, cv2.COLOR_BGR2GRAY)
            else:
                existing_gray = existing_slide
                
            # Resize if dimensions don't match
            if existing_gray.shape != gray_frame.shape:
                existing_gray = cv2.resize(existing_gray, (gray_frame.shape[1], gray_frame.shape[0]))
                
            # Compare using structural similarity
            score = self._calculate_similarity(gray_frame, existing_gray)
            
            # If similarity is high, it's not a new slide
            if score > (1.0 - self.similarity_threshold):
                return False
                
        # If we get here, this frame is different from all existing slides
        return True
    
    def _calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate similarity score between two grayscale images.
        
        Args:
            img1: First image
            img2: Second image
            
        Returns:
            Similarity score (0-1) where 1 means identical
        """
        # Use SSIM for structural similarity
        score, _ = ssim(img1, img2, full=True)
        return score
    
    def detect_slide_region(self, frame: np.ndarray) -> np.ndarray:
        """
        Attempt to detect and extract just the slide region from a frame.
        
        Args:
            frame: Video frame
            
        Returns:
            Extracted slide region or original frame if detection fails
        """
        # This is a placeholder for more advanced slide region detection
        # In a real implementation, you might:
        # 1. Use edge detection to find rectangular regions
        # 2. Apply perspective correction
        # 3. Use ML-based approaches to identify the slide area
        
        # For now, we'll just return the original frame
        return frame
