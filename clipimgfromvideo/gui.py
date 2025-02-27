import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from typing import Optional, Dict, Any, Callable

from .video_processor import VideoProcessor
from .utils import sniff_video_from_webpage, ensure_dir_exists


class StdoutRedirector:
    """Class to redirect stdout to a queue for GUI display"""
    
    def __init__(self, queue):
        self.queue = queue
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        
    def write(self, text):
        self.queue.put(text)
        self.stdout.write(text)
        
    def flush(self):
        self.stdout.flush()


class SlideCaptureGUI:
    """GUI application for extracting slides from videos"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Presentation Slide Extractor")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Fix for macOS: Add a try-except block for icon loading
        self.set_app_icon()
        
        # Configuration for macOS appearance
        if sys.platform == 'darwin':
            try:
                # Make app look more native on macOS
                from tkinter import _tkinter
                _tkinter.TkVersion  # This will raise an error if Tkinter isn't available
                self.root.tk.call('::tk::unsupported::MacWindowStyle', 'style', 
                                 self.root._w, 'document', 'closeBox')
            except Exception:
                pass
        
        # Configure the grid layout
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=7)
        self.root.rowconfigure(0, weight=1)
        
        # Create frames
        self.control_frame = ttk.LabelFrame(self.root, text="Controls")
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.log_frame = ttk.LabelFrame(self.root, text="Log")
        self.log_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure the control frame grid
        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=3)
        
        # Add form elements to control frame
        self.create_control_widgets()
        
        # Add log text area
        self.create_log_widgets()
        
        # Queue for redirecting stdout
        self.log_queue = queue.Queue()
        self.stdout_redirector = StdoutRedirector(self.log_queue)
        
        # Start the queue checking loop
        self.check_log_queue()
        
        # Flag for controlling the processing thread
        self.processing = False
        
        # Add special handling for macOS app activation
        if sys.platform == 'darwin':
            # Show a welcome message in the log
            self.update_log("Welcome to Presentation Slide Extractor!\n\n")
            self.update_log("To begin, enter a URL or select a video file, then click 'Extract Slides'.\n")
    
    def set_app_icon(self):
        """Set the application icon if available"""
        # Look for icon in different possible locations (for PyInstaller bundle support)
        possible_icon_paths = [
            os.path.join('icons', 'app_icon.png'),  # Development path
            os.path.join(os.path.dirname(sys.executable), 'icons', 'app_icon.png'),  # PyInstaller path
            os.path.join(getattr(sys, '_MEIPASS', ''), 'icons', 'app_icon.png')  # PyInstaller onefile path
        ]
        
        # For macOS bundle
        if sys.platform == 'darwin' and 'Contents/MacOS/' in getattr(sys, 'executable', ''):
            resources_path = os.path.abspath(os.path.join(
                os.path.dirname(sys.executable), 
                '../Resources/icons/app_icon.png'
            ))
            possible_icon_paths.append(resources_path)
        
        icon_path = None
        for path in possible_icon_paths:
            if os.path.exists(path):
                icon_path = path
                break
        
        if icon_path:
            try:
                # Use PhotoImage for cross-platform support
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
            except Exception as e:
                print(f"Could not set application icon: {str(e)}")
        
    def create_control_widgets(self):
        """Create form elements in the control frame"""
        row = 0
        
        # Input source
        ttk.Label(self.control_frame, text="Video Source:").grid(
            row=row, column=0, padx=5, pady=5, sticky="w")
        
        source_frame = ttk.Frame(self.control_frame)
        source_frame.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        source_frame.columnconfigure(0, weight=1)
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(source_frame, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=0, padx=2, sticky="ew")
        
        browse_btn = ttk.Button(source_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=1, padx=2)
        
        # Help text
        ttk.Label(
            self.control_frame, 
            text="Enter a URL or select a local video file",
            font=("", 8, "italic")
        ).grid(row=row+1, column=1, padx=5, sticky="w")
        
        row += 2
        
        # Output directory
        ttk.Label(self.control_frame, text="Output Directory:").grid(
            row=row, column=0, padx=5, pady=5, sticky="w")
        
        output_frame = ttk.Frame(self.control_frame)
        output_frame.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        output_frame.columnconfigure(0, weight=1)
        
        self.output_var = tk.StringVar(value="./extracted_slides")
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.grid(row=0, column=0, padx=2, sticky="ew")
        
        output_browse_btn = ttk.Button(output_frame, text="Browse", command=self.browse_dir)
        output_browse_btn.grid(row=0, column=1, padx=2)
        
        row += 1
        
        # Threshold
        ttk.Label(self.control_frame, text="Threshold:").grid(
            row=row, column=0, padx=5, pady=5, sticky="w")
        
        threshold_frame = ttk.Frame(self.control_frame)
        threshold_frame.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        
        self.threshold_var = tk.DoubleVar(value=0.15)
        self.threshold_scale = ttk.Scale(
            threshold_frame, 
            from_=0.01, 
            to=0.5, 
            orient="horizontal", 
            length=150, 
            variable=self.threshold_var,
            command=self.update_threshold_label
        )
        self.threshold_scale.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.threshold_label = ttk.Label(threshold_frame, text="0.15")
        self.threshold_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Help text for threshold
        ttk.Label(
            self.control_frame, 
            text="Lower values = more sensitive detection",
            font=("", 8, "italic")
        ).grid(row=row+1, column=1, padx=5, sticky="w")
        
        row += 2
        
        # Skip frames
        ttk.Label(self.control_frame, text="Skip Frames:").grid(
            row=row, column=0, padx=5, pady=5, sticky="w")
        
        self.skip_var = tk.IntVar(value=5)
        skip_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.skip_var,
            values=[1, 2, 3, 5, 10, 15, 30, 60],
            width=5
        )
        skip_combo.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        
        # Help text for skip frames
        ttk.Label(
            self.control_frame, 
            text="Higher values = faster but may miss slides",
            font=("", 8, "italic")
        ).grid(row=row+1, column=1, padx=5, sticky="w")
        
        row += 2
        
        # Debug mode
        self.debug_var = tk.BooleanVar(value=False)
        debug_check = ttk.Checkbutton(
            self.control_frame,
            text="Debug Mode",
            variable=self.debug_var
        )
        debug_check.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        row += 1
        
        # Go button
        self.go_button = ttk.Button(
            self.control_frame,
            text="Extract Slides",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.go_button.grid(row=row, column=0, columnspan=2, padx=5, pady=20, sticky="ew")
        
        # Create a themed button style
        style = ttk.Style()
        style.configure("Accent.TButton", font=("", 11, "bold"))
        
    def create_log_widgets(self):
        """Create the log text area"""
        self.log_frame.rowconfigure(0, weight=1)
        self.log_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            width=50,
            height=20
        )
        self.log_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)  # Make it read-only
        
        # Add clear log button
        clear_btn = ttk.Button(
            self.log_frame,
            text="Clear Log",
            command=self.clear_log
        )
        clear_btn.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    
    def update_threshold_label(self, value):
        """Update the threshold label when the slider changes"""
        value = round(float(value), 2)
        self.threshold_label.config(text=f"{value:.2f}")
    
    def browse_file(self):
        """Open file browser dialog"""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=(
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            )
        )
        if filename:
            self.input_var.set(filename)
    
    def browse_dir(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if directory:
            self.output_var.set(directory)
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def check_log_queue(self):
        """Check for new log messages in the queue"""
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.update_log(message)
        
        # Schedule the next queue check
        self.root.after(100, self.check_log_queue)
    
    def update_log(self, message):
        """Add a message to the log text area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)  # Scroll to the end
        self.log_text.config(state=tk.DISABLED)
    
    def start_processing(self):
        """Start processing the video in a separate thread"""
        if self.processing:
            return
        
        # Get input parameters
        input_path = self.input_var.get().strip()
        output_dir = self.output_var.get().strip()
        threshold = self.threshold_var.get()
        skip_frames = self.skip_var.get()
        debug_mode = self.debug_var.get()
        
        if not input_path:
            self.update_log("Error: Please enter a URL or select a video file.\n")
            return
        
        if not output_dir:
            output_dir = "./extracted_slides"
        
        # Clear log and show starting message
        self.clear_log()
        self.update_log(f"Starting slide extraction...\n")
        self.update_log(f"Input: {input_path}\n")
        self.update_log(f"Output directory: {output_dir}\n")
        self.update_log(f"Threshold: {threshold:.2f}\n")
        self.update_log(f"Skip frames: {skip_frames}\n")
        self.update_log(f"Debug mode: {'On' if debug_mode else 'Off'}\n\n")
        
        # Disable the Go button
        self.go_button.config(state=tk.DISABLED)
        self.processing = True
        
        # Start processing in a separate thread
        processing_thread = threading.Thread(
            target=self.process_video,
            args=(input_path, output_dir, threshold, skip_frames, debug_mode)
        )
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_video(self, input_path, output_dir, threshold, skip_frames, debug_mode):
        """Process the video and extract slides"""
        old_stdout = sys.stdout
        
        try:
            # Redirect stdout to our queue
            sys.stdout = self.stdout_redirector
            
            # Create output directory
            ensure_dir_exists(output_dir)
            
            # Process input (URL or file)
            if input_path.lower().startswith(('http://', 'https://', 'www.')):
                print(f"Extracting video from webpage: {input_path}...")
                video_path = sniff_video_from_webpage(input_path, output_dir=output_dir)
                if not video_path:
                    print("Failed to extract video from the webpage.")
                    return
            else:
                video_path = input_path
                if not os.path.exists(video_path):
                    print(f"Error: Video file '{video_path}' not found")
                    return
            
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
            
        except Exception as e:
            print(f"Error: {str(e)}")
            
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            
            # Re-enable the Go button
            self.root.after(0, lambda: self.go_button.config(state=tk.NORMAL))
            self.processing = False


def launch_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    app = SlideCaptureGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
