#!/usr/bin/env python3
"""
YouTube Video Downloader - Properly Fixed
Careful bug fixes and proper error handling
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import subprocess
import sys
from pathlib import Path
import re
import time
import glob

class FixedYouTubeDownloader:
    def __init__(self):
        self.root = None
        self.download_path = str(Path.home() / "Videos")
        self.is_downloading = False
        self.process = None
        self.download_thread = None
        
        # Initialize GUI with proper error handling
        self.init_gui()
    
    def init_gui(self):
        """Initialize GUI with maximum error handling"""
        try:
            print("Starting GUI initialization...")
            
            # Create root window
            self.root = tk.Tk()
            self.root.title("YouTube Video Downloader - Fixed Version")
            self.root.geometry("800x600")
            self.root.minsize(700, 500)
            
            print("Root window created successfully")
            
            # Variables
            self.url_var = tk.StringVar()
            self.status_var = tk.StringVar(value="Ready to download")
            self.progress_var = tk.DoubleVar()
            self.force_download_var = tk.BooleanVar()
            self.selected_format = tk.StringVar(value="best[height<=720]")
            self.available_formats = []
            
            print("Variables created successfully")
            
            # Create main interface
            self.create_interface()
            print("Interface created successfully")
            
            # Handle window closing
            self.root.protocol("WM_DELETE_WINDOW", self.safe_close)
            print("Window protocol set successfully")
            
            # Check dependencies (but don't let it crash the app)
            try:
                self.check_yt_dlp()
                print("yt-dlp check completed")
            except Exception as e:
                print(f"yt-dlp check failed: {e}")
                # Don't crash, just log the error
                self.log(f"Warning: Could not check yt-dlp: {e}")
            
            print("GUI initialization completed successfully")
            
        except Exception as e:
            print(f"GUI initialization error: {e}")
            import traceback
            traceback.print_exc()
            # Try to show error if possible
            try:
                if self.root:
                    messagebox.showerror("Initialization Error", f"Failed to initialize GUI: {e}")
                else:
                    print("Cannot show error dialog - root window not created")
            except Exception as e2:
                print(f"Error showing error dialog: {e2}")
    
    def create_interface(self):
        """Create the user interface"""
        try:
            # Main frame
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title = ttk.Label(main_frame, text="YouTube Video Downloader", 
                             font=("Arial", 16, "bold"))
            title.pack(pady=(0, 20))
            
            # URL input
            url_frame = ttk.Frame(main_frame)
            url_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(url_frame, text="YouTube URL:").pack(anchor=tk.W)
            self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=80)
            self.url_entry.pack(fill=tk.X, pady=5)
            
            # Filename input
            filename_frame = ttk.Frame(main_frame)
            filename_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(filename_frame, text="Custom Filename (optional):").pack(anchor=tk.W)
            self.filename_var = tk.StringVar()
            self.filename_entry = ttk.Entry(filename_frame, textvariable=self.filename_var, width=80)
            self.filename_entry.pack(fill=tk.X, pady=5)
            ttk.Label(filename_frame, text="Leave empty to use video title", font=("Arial", 8)).pack(anchor=tk.W)
            
            # Format selection
            format_frame = ttk.LabelFrame(main_frame, text="Format Selection", padding="5")
            format_frame.pack(fill=tk.X, pady=10)
            
            # Format buttons
            format_buttons_frame = ttk.Frame(format_frame)
            format_buttons_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(format_buttons_frame, text="Get Formats", 
                      command=self.get_formats_sync).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Button(format_buttons_frame, text="Clear URL", 
                      command=self.clear_url).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Button(format_buttons_frame, text="Clear Filename", 
                      command=self.clear_filename).pack(side=tk.LEFT)
            
            # Format listbox
            self.format_listbox = tk.Listbox(format_frame, height=4)
            self.format_listbox.pack(fill=tk.X, pady=5)
            
            # Selected format display
            format_info_frame = ttk.Frame(format_frame)
            format_info_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(format_info_frame, text="Selected:").pack(side=tk.LEFT)
            self.selected_format_label = ttk.Label(format_info_frame, text="best[height<=720] (default)", 
                                                 font=("Arial", 9, "bold"))
            self.selected_format_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Audio quality selection
            audio_frame = ttk.LabelFrame(main_frame, text="Audio Quality (for high-res videos)", padding="5")
            audio_frame.pack(fill=tk.X, pady=5)
            
            self.audio_quality_var = tk.StringVar(value="bestaudio")
            audio_quality_frame = ttk.Frame(audio_frame)
            audio_quality_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(audio_quality_frame, text="Audio Quality:").pack(side=tk.LEFT)
            
            audio_options = [
                ("Best Audio", "bestaudio"),
                ("High Quality (192kbps)", "bestaudio[abr<=192]"),
                ("Medium Quality (128kbps)", "bestaudio[abr<=128]"),
                ("Low Quality (64kbps)", "bestaudio[abr<=64]")
            ]
            
            for text, value in audio_options:
                ttk.Radiobutton(audio_quality_frame, text=text, variable=self.audio_quality_var, 
                               value=value).pack(side=tk.LEFT, padx=(10, 0))
            
            # Download path
            path_frame = ttk.Frame(main_frame)
            path_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(path_frame, text="Download to:").pack(anchor=tk.W)
            path_input_frame = ttk.Frame(path_frame)
            path_input_frame.pack(fill=tk.X, pady=5)
            
            self.path_var = tk.StringVar(value=self.download_path)
            self.path_entry = ttk.Entry(path_input_frame, textvariable=self.path_var)
            self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            ttk.Button(path_input_frame, text="Browse", 
                      command=self.browse_folder).pack(side=tk.RIGHT)
            
            # Options
            options_frame = ttk.Frame(main_frame)
            options_frame.pack(fill=tk.X, pady=5)
            
            self.force_checkbox = ttk.Checkbutton(options_frame, text="Force download (overwrite existing files)", 
                                                variable=self.force_download_var)
            self.force_checkbox.pack(anchor=tk.W)
            
            self.speed_boost_var = tk.BooleanVar(value=True)
            self.speed_checkbox = ttk.Checkbutton(options_frame, text="Speed boost (8x concurrent downloads)", 
                                                variable=self.speed_boost_var)
            self.speed_checkbox.pack(anchor=tk.W)
            
            self.fast_download_var = tk.BooleanVar(value=False)
            self.fast_checkbox = ttk.Checkbutton(options_frame, text="Fast download (lower quality for speed)", 
                                                variable=self.fast_download_var)
            self.fast_checkbox.pack(anchor=tk.W)
            
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=20)
            
            self.download_btn = ttk.Button(button_frame, text="Download", 
                                          command=self.start_download)
            self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            self.retry_btn = ttk.Button(button_frame, text="Retry Download", 
                                       command=self.retry_download, state="disabled")
            self.retry_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            self.cancel_btn = ttk.Button(button_frame, text="Cancel", 
                                        command=self.cancel_download, state="disabled")
            self.cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            self.open_folder_btn = ttk.Button(button_frame, text="Open Videos", 
                                            command=self.open_videos_folder)
            self.open_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Progress
            self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                              maximum=100)
            self.progress_bar.pack(fill=tk.X, pady=10)
            
            # Status
            self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
            self.status_label.pack(pady=5)
            
            # Log area
            log_frame = ttk.LabelFrame(main_frame, text="Download Log", padding="5")
            log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(log_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            self.log_text = tk.Text(text_frame, height=12, wrap=tk.WORD, font=("Consolas", 9))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
            self.log_text.configure(yscrollcommand=scrollbar.set)
            
            self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Clear log button
            ttk.Button(log_frame, text="Clear Log", command=self.clear_log).pack(pady=5)
            
            # Bind format selection
            self.format_listbox.bind('<<ListboxSelect>>', self.on_format_select)
            
            # Initial log message
            self.log("Application started successfully")
            self.log("Note: For 1080p, 1440p, and 4K videos, audio will be downloaded separately and merged automatically")
            self.log("Speed boost is enabled by default - 8x concurrent downloads with ZERO sleep timers")
            self.log("Audio quality can be selected for high-resolution videos")
            self.log("Tip: Enable 'Fast download' for lower quality but much faster downloads")
            self.log("Network resilience: 10 retries, 120s timeout, ZERO sleep delays")
            
        except Exception as e:
            print(f"Interface creation error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def log(self, message):
        """Add message to log safely"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        except Exception as e:
            print(f"Log error: {e}")
    
    def clear_log(self):
        """Clear log safely"""
        try:
            self.log_text.delete(1.0, tk.END)
        except Exception as e:
            print(f"Clear log error: {e}")
    
    def show_error(self, message):
        """Show error message safely"""
        try:
            self.log(f"Error: {message}")
            messagebox.showerror("Error", message)
        except Exception as e:
            print(f"Error showing message: {e}")
            print(f"Original error: {message}")
    
    def browse_folder(self):
        """Browse for download folder"""
        try:
            folder = filedialog.askdirectory(initialdir=self.download_path)
            if folder:
                self.download_path = folder
                self.path_var.set(folder)
                self.log(f"Download folder changed to: {folder}")
        except Exception as e:
            self.show_error(f"Error browsing folder: {e}")
    
    def check_yt_dlp(self):
        """Check if yt-dlp is available"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log(f"yt-dlp version: {result.stdout.strip()}")
                # Check for ffmpeg
                self.check_ffmpeg()
            else:
                self.log("yt-dlp not found - please install it")
                self.show_install_help()
        except Exception as e:
            self.log(f"Error checking yt-dlp: {e}")
            self.show_install_help()
    
    def check_ffmpeg(self):
        """Check if ffmpeg is available for merging"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log("ffmpeg found - audio merging will work properly")
            else:
                self.log("WARNING: ffmpeg not found - audio merging may not work")
                self.show_ffmpeg_help()
        except Exception as e:
            self.log("WARNING: ffmpeg not found - audio merging may not work")
            self.show_ffmpeg_help()
    
    def show_install_help(self):
        """Show installation help"""
        help_text = """yt-dlp not found. To install:

1. Open Command Prompt
2. Run: pip install yt-dlp
3. Restart this application"""
        
        try:
            messagebox.showinfo("Install yt-dlp", help_text)
        except Exception as e:
            print(f"Error showing help: {e}")
    
    def show_ffmpeg_help(self):
        """Show ffmpeg installation help"""
        help_text = """ffmpeg not found. To install for audio merging:

1. Download ffmpeg from: https://ffmpeg.org/download.html
2. Extract to a folder (e.g., C:\\ffmpeg)
3. Add to PATH environment variable
4. Restart this application

OR use chocolatey:
1. Open Command Prompt as Administrator
2. Run: choco install ffmpeg
3. Restart this application"""
        
        try:
            messagebox.showwarning("Install ffmpeg", help_text)
        except Exception as e:
            print(f"Error showing ffmpeg help: {e}")
    
    def validate_url(self, url):
        """Simple URL validation"""
        if not url or not url.strip():
            return False, "URL cannot be empty"
        
        url = url.strip()
        
        # Check for YouTube URLs
        if any(pattern in url for pattern in ['youtube.com', 'youtu.be']):
            return True, "Valid YouTube URL"
        
        return False, "Not a YouTube URL"
    
    def get_formats_sync(self):
        """Get available formats synchronously"""
        url = self.url_var.get().strip()
        if not url:
            self.show_error("Please enter a YouTube URL first!")
            return
        
        # Validate URL
        is_valid, error_msg = self.validate_url(url)
        if not is_valid:
            self.show_error(f"Invalid URL: {error_msg}")
            return
        
        self.log("Getting available formats...")
        self.status_var.set("Getting available formats...")
        self.root.update()
        
        try:
            cmd = ['yt-dlp', '--list-formats', '--no-playlist', url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                formats = self.parse_formats(result.stdout)
                self.update_format_list(formats)
                self.log(f"Found {len(formats)} available formats")
                self.status_var.set(f"Found {len(formats)} formats - Select one to download")
            else:
                error_msg = result.stderr or "Unknown error"
                self.log(f"Error getting formats: {error_msg}")
                self.status_var.set("Error getting formats")
                
        except subprocess.TimeoutExpired:
            self.log("Timeout getting formats")
            self.status_var.set("Timeout getting formats")
        except Exception as e:
            self.log(f"Error fetching formats: {e}")
            self.status_var.set("Error getting formats")
    
    def parse_formats(self, output):
        """Parse format output from yt-dlp"""
        formats = []
        lines = output.split('\n')
        
        for line in lines:
            if 'ID' in line and 'EXT' in line and 'RESOLUTION' in line:
                continue  # Skip header
            
            parts = line.split()
            if len(parts) >= 4:
                format_id = parts[0]
                ext = parts[1]
                resolution = parts[2] if parts[2] != 'audio' else 'audio'
                size = parts[3] if len(parts) > 3 else 'unknown'
                
                if format_id and ext:
                    format_info = {
                        'id': format_id,
                        'ext': ext,
                        'resolution': resolution,
                        'size': size,
                        'display': f"{format_id} - {ext} - {resolution} - {size}"
                    }
                    formats.append(format_info)
        
        return formats
    
    def update_format_list(self, formats):
        """Update the format listbox"""
        try:
            self.available_formats = formats
            self.format_listbox.delete(0, tk.END)
            
            for format_info in formats:
                self.format_listbox.insert(tk.END, format_info['display'])
            
        except Exception as e:
            print(f"Error updating format list: {e}")
    
    def on_format_select(self, event):
        """Handle format selection"""
        try:
            selection = self.format_listbox.curselection()
            if selection:
                index = selection[0]
                if index < len(self.available_formats):
                    selected_format = self.available_formats[index]
                    self.selected_format.set(selected_format['id'])
                    self.selected_format_label.config(text=selected_format['display'])
                    self.log(f"Selected format: {selected_format['display']}")
        except Exception as e:
            print(f"Error selecting format: {e}")
    
    def clear_url(self):
        """Clear the URL field for a new download"""
        try:
            self.url_var.set("")
            self.filename_var.set("")
            self.format_listbox.delete(0, tk.END)
            self.selected_format_label.config(text="best[height<=720] (default)")
            self.selected_format.set("best[height<=720]")
            self.available_formats = []
            self.status_var.set("Ready to download")
            self.log("URL and filename fields cleared - ready for new download")
        except Exception as e:
            print(f"Error clearing URL: {e}")
    
    def clear_filename(self):
        """Clear the filename field"""
        try:
            self.filename_var.set("")
            self.log("Filename field cleared - will use video title")
        except Exception as e:
            print(f"Clear filename error: {e}")
    
    def start_download(self):
        """Start download process"""
        if self.is_downloading:
            self.show_error("Download already in progress!")
            return
        
        url = self.url_var.get().strip()
        if not url:
            self.show_error("Please enter a YouTube URL!")
            return
        
        # Validate URL
        is_valid, error_msg = self.validate_url(url)
        if not is_valid:
            self.show_error(f"Invalid URL: {error_msg}")
            return
        
        # Get download path
        download_path = self.path_var.get().strip() or self.download_path
        if not os.path.exists(download_path):
            self.show_error("Download path does not exist!")
            return
        
        # Start download in thread
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_var.set(0)
        self.status_var.set("Starting download...")
        
        # Start download thread
        try:
            self.download_thread = threading.Thread(target=self.download_video, args=(url, download_path))
            self.download_thread.daemon = True
            self.download_thread.start()
        except Exception as e:
            self.show_error(f"Failed to start download: {e}")
            self.reset_buttons()
    
    def cancel_download(self):
        """Cancel download"""
        if self.is_downloading:
            self.is_downloading = False
            self.status_var.set("Cancelling...")
            self.log("Download cancelled by user")
            
            # Terminate process if running
            if self.process and self.process.poll() is None:
                try:
                    self.process.terminate()
                except Exception as e:
                    print(f"Error terminating process: {e}")
    
    def retry_download(self):
        """Retry the last download"""
        if hasattr(self, 'last_url') and self.last_url:
            self.log("Retrying download with network recovery...")
            self.url_var.set(self.last_url)
            self.start_download()
        else:
            self.log("No previous download to retry")
    
    def reset_buttons(self):
        """Reset button states"""
        self.is_downloading = False
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.retry_btn.config(state="disabled")
        self.progress_var.set(0)
    
    def download_video(self, url, download_path):
        """Download video in separate thread with audio merging for high-res formats"""
        try:
            # Store the URL for retry functionality
            self.last_url = url
            self.log(f"Starting download: {url}")
            self.log(f"Download path: {download_path}")
            self.log(f"Selected format: {self.selected_format.get()}")
            
            # Check if we need to merge audio (for high-res formats)
            selected_format = self.selected_format.get()
            optimized_format = self.get_optimized_format(selected_format)
            needs_audio_merge = self.needs_audio_merge(optimized_format)
            
            if needs_audio_merge:
                self.log("High-resolution format detected - will download video and audio separately, then merge")
                self.download_with_audio_merge(url, download_path, optimized_format)
            else:
                self.log("Standard format - downloading directly")
                self.download_standard(url, download_path, optimized_format)
                
        except Exception as e:
            self.log(f"Download error: {e}")
            self.status_var.set("Download failed!")
            try:
                messagebox.showerror("Error", f"Download failed: {e}")
            except Exception as e2:
                print(f"Error showing error message: {e2}")
        
        finally:
            # Cleanup
            if self.process and self.process.poll() is None:
                try:
                    self.process.terminate()
                except Exception as e:
                    print(f"Error terminating process: {e}")
            
            self.reset_buttons()
    
    def needs_audio_merge(self, format_id):
        """Check if format needs audio merging (high-res formats)"""
        # High-resolution formats that typically need audio merging
        high_res_formats = ['137', '299', '298', '136', '135', '134', '133', '160', '248', '271', '272', '313', '315', '308']
        
        # Check if format ID is in high-res list
        if format_id in high_res_formats:
            return True
        
        # Check if any available format contains high-res info
        for format_info in self.available_formats:
            if format_info['id'] == format_id:
                resolution = format_info.get('resolution', '').lower()
                if any(res in resolution for res in ['1080', '1440', '2160', '4k']):
                    return True
                break
        
        return False
    
    def get_optimized_format(self, format_id):
        """Get optimized format for faster downloads if enabled"""
        if self.fast_download_var.get():
            # For fast downloads, prefer smaller formats
            if format_id in ['271', '272', '313', '315', '308']:  # 1440p, 4K formats
                # Try to find 1080p alternative
                for format_info in self.available_formats:
                    if format_info['id'] == '248' and '1080' in format_info.get('resolution', ''):
                        self.log(f"Fast download: Using 1080p instead of {format_id} for speed")
                        return '248'
            elif format_id in ['137', '299', '298']:  # 1080p formats
                # Try to find 720p alternative
                for format_info in self.available_formats:
                    if format_info['id'] in ['136', '135'] and '720' in format_info.get('resolution', ''):
                        self.log(f"Fast download: Using 720p instead of {format_id} for speed")
                        return format_info['id']
        
        return format_id
    
    def download_with_audio_merge(self, url, download_path, video_format):
        """Download video and audio separately, then merge them"""
        try:
            # Use custom filename if provided, otherwise use video title
            custom_filename = self.filename_var.get().strip()
            if custom_filename:
                # Clean filename and add extension
                import re
                clean_filename = re.sub(r'[<>:"/\\|?*]', '_', custom_filename)
                output_template = os.path.join(download_path, f'{clean_filename}.%(ext)s')
                self.log(f"Using custom filename: {clean_filename}")
            else:
                output_template = os.path.join(download_path, '%(title)s.%(ext)s')
                self.log("Using video title as filename")
            
            # Step 1: Download video and audio separately with speed optimizations
            audio_quality = self.audio_quality_var.get()
            self.log(f"Step 1: Downloading video and audio separately with speed optimizations...")
            self.log(f"Video format: {video_format}, Audio quality: {audio_quality}")
            
            cmd = [
                'yt-dlp',
                '-o', output_template,
                '--progress',
                '--newline',
                '--no-playlist',
                '--format', f'{video_format}+{audio_quality}/best',
                '--merge-output-format', 'mp4',
                '--embed-metadata',
                url
            ]
            
            # Add speed optimizations if enabled
            if self.speed_boost_var.get():
                cmd.extend([
                    '--concurrent-fragments', '8',
                    '--fragment-retries', '10',
                    '--retries', '10',
                    '--socket-timeout', '120',
                    '--buffer-size', '16K',
                    '--http-chunk-size', '10M',
                    '--sleep-requests', '0',
                    '--sleep-interval', '0',
                    '--max-sleep-interval', '0'
                ])
                self.log("Speed boost enabled - using 8 concurrent downloads with ZERO sleep timers")
            
            # Add force overwrite if checkbox is checked
            if self.force_download_var.get():
                cmd.insert(-1, '--force-overwrites')
                self.log("Force download enabled - will overwrite existing files")
            
            self.log(f"Command: {' '.join(cmd)}")
            
            # Execute download
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          universal_newlines=True, bufsize=1)
            
            for line in self.process.stdout:
                if not self.is_downloading:
                    break
                
                line = line.strip()
                if line:
                    self.log(line)
                    
                    # Parse progress
                    if '[download]' in line and '%' in line:
                        try:
                            percent_str = line.split('%')[0].split()[-1]
                            percent = float(percent_str)
                            self.progress_var.set(percent)
                            self.status_var.set(f"Downloading & merging... {percent:.1f}%")
                        except (ValueError, IndexError):
                            pass
            
            if self.is_downloading:
                self.process.wait()
                
                if self.process.returncode == 0:
                    self.status_var.set("Download completed!")
                    self.log("Download and merge completed successfully!")
                    
                    # Find the downloaded file
                    downloaded_file = self.find_downloaded_file(download_path)
                    if downloaded_file:
                        file_size = os.path.getsize(downloaded_file)
                        self.log(f"File saved to: {downloaded_file}")
                        self.log(f"File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                        
                        if file_size > 0:
                            self.log("High-quality video with audio successfully downloaded and merged!")
                            try:
                                messagebox.showinfo("Success", f"Download completed!\n\nFile saved to:\n{downloaded_file}\n\nFile size: {file_size/1024/1024:.2f} MB\n\nVideo and audio have been merged successfully!")
                            except Exception as e:
                                print(f"Error showing success message: {e}")
                        else:
                            self.log("WARNING: Downloaded file is empty (0 bytes)")
                            try:
                                messagebox.showwarning("Warning", "Download completed but file is empty.\nThis might indicate a download issue.\nCheck the log for details.")
                            except Exception as e:
                                print(f"Error showing warning message: {e}")
                    else:
                        self.log("Download completed but file location not found")
                        self.log("This might indicate a download issue.")
                        try:
                            messagebox.showwarning("Warning", "Download completed but file not found.\nThis might indicate a download issue.\nCheck the log for details.")
                        except Exception as e:
                            print(f"Error showing warning message: {e}")
                else:
                    self.status_var.set("Download failed!")
                    self.log("Download failed!")
                    try:
                        messagebox.showerror("Error", "Download failed! Check log for details.")
                    except Exception as e:
                        print(f"Error showing error message: {e}")
            else:
                self.status_var.set("Download cancelled!")
                self.log("Download cancelled by user")
                
        except Exception as e:
            self.log(f"Download with merge error: {e}")
            self.status_var.set("Download failed!")
            try:
                messagebox.showerror("Error", f"Download failed: {e}")
            except Exception as e2:
                print(f"Error showing error message: {e2}")
    
    def download_standard(self, url, download_path, format_id):
        """Download standard format (no audio merging needed)"""
        try:
            # Use custom filename if provided, otherwise use video title
            custom_filename = self.filename_var.get().strip()
            if custom_filename:
                # Clean filename and add extension
                import re
                clean_filename = re.sub(r'[<>:"/\\|?*]', '_', custom_filename)
                output_template = os.path.join(download_path, f'{clean_filename}.%(ext)s')
                self.log(f"Using custom filename: {clean_filename}")
            else:
                output_template = os.path.join(download_path, '%(title)s.%(ext)s')
                self.log("Using video title as filename")
            cmd = [
                'yt-dlp',
                '-o', output_template,
                '--progress',
                '--newline',
                '--no-playlist',
                '--format', format_id,
                url
            ]
            
            # Add speed optimizations if enabled
            if self.speed_boost_var.get():
                cmd.extend([
                    '--concurrent-fragments', '8',
                    '--fragment-retries', '10',
                    '--retries', '10',
                    '--socket-timeout', '120',
                    '--buffer-size', '16K',
                    '--http-chunk-size', '10M',
                    '--sleep-requests', '0',
                    '--sleep-interval', '0',
                    '--max-sleep-interval', '0'
                ])
                self.log("Speed boost enabled - using 8 concurrent downloads with ZERO sleep timers")
            
            # Add force overwrite if checkbox is checked
            if self.force_download_var.get():
                cmd.insert(-1, '--force-overwrites')
                self.log("Force download enabled - will overwrite existing files")
            
            self.log(f"Command: {' '.join(cmd)}")
            
            # Execute download
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                          universal_newlines=True, bufsize=1)
            
            for line in self.process.stdout:
                if not self.is_downloading:
                    break
                
                line = line.strip()
                if line:
                    self.log(line)
                    
                    # Parse progress
                    if '[download]' in line and '%' in line:
                        try:
                            percent_str = line.split('%')[0].split()[-1]
                            percent = float(percent_str)
                            self.progress_var.set(percent)
                            self.status_var.set(f"Downloading... {percent:.1f}%")
                        except (ValueError, IndexError):
                            pass
            
            if self.is_downloading:
                self.process.wait()
                
                if self.process.returncode == 0:
                    self.status_var.set("Download completed!")
                    self.log("Download completed successfully!")
                    
                    # Find the downloaded file
                    downloaded_file = self.find_downloaded_file(download_path)
                    if downloaded_file:
                        file_size = os.path.getsize(downloaded_file)
                        self.log(f"File saved to: {downloaded_file}")
                        self.log(f"File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                        
                        if file_size > 0:
                            self.log("You can now download another video or close the application.")
                            try:
                                messagebox.showinfo("Success", f"Download completed!\n\nFile saved to:\n{downloaded_file}\n\nFile size: {file_size/1024/1024:.2f} MB\n\nApplication will remain open for more downloads.")
                            except Exception as e:
                                print(f"Error showing success message: {e}")
                        else:
                            self.log("WARNING: Downloaded file is empty (0 bytes)")
                            try:
                                messagebox.showwarning("Warning", "Download completed but file is empty.\nThis might indicate a download issue.\nCheck the log for details.")
                            except Exception as e:
                                print(f"Error showing warning message: {e}")
                    else:
                        self.log("Download completed but file location not found")
                        self.log("This might indicate a download issue.")
                        try:
                            messagebox.showwarning("Warning", "Download completed but file not found.\nThis might indicate a download issue.\nCheck the log for details.")
                        except Exception as e:
                            print(f"Error showing warning message: {e}")
                else:
                    self.status_var.set("Download failed!")
                    self.log("Download failed!")
                    try:
                        messagebox.showerror("Error", "Download failed! Check log for details.")
                    except Exception as e:
                        print(f"Error showing error message: {e}")
            else:
                self.status_var.set("Download cancelled!")
                self.log("Download cancelled by user")
                
        except Exception as e:
            self.log(f"Standard download error: {e}")
            self.status_var.set("Download failed!")
            try:
                messagebox.showerror("Error", f"Download failed: {e}")
            except Exception as e2:
                print(f"Error showing error message: {e2}")
    
    def find_downloaded_file(self, download_path):
        """Find the most recently downloaded file"""
        try:
            # Look for common video/audio files
            patterns = ['*.mp4', '*.webm', '*.mkv', '*.avi', '*.mp3', '*.wav']
            files = []
            
            for pattern in patterns:
                files.extend(glob.glob(os.path.join(download_path, pattern)))
            
            if not files:
                return None
            
            # Get the most recently modified file
            latest_file = max(files, key=os.path.getmtime)
            
            # Check if it was modified in the last 5 minutes (likely our download)
            current_time = time.time()
            file_time = os.path.getmtime(latest_file)
            
            if current_time - file_time < 300:  # 5 minutes
                return latest_file
            
            return None
            
        except Exception as e:
            print(f"Error finding downloaded file: {e}")
            return None
    
    def open_videos_folder(self):
        """Open the videos folder in file explorer"""
        try:
            download_path = self.path_var.get().strip() or self.download_path
            
            if sys.platform == "win32":
                os.startfile(download_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(['open', download_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', download_path], check=True)
                
            self.log(f"Opened videos folder: {download_path}")
            
        except Exception as e:
            self.show_error(f"Error opening videos folder: {e}")
    
    def safe_close(self):
        """Safely close the application"""
        try:
            if self.is_downloading:
                if messagebox.askokcancel("Quit", "Download in progress. Quit anyway?"):
                    self.is_downloading = False
                    if self.process and self.process.poll() is None:
                        try:
                            self.process.terminate()
                        except Exception as e:
                            print(f"Error terminating process: {e}")
                    self.root.destroy()
            else:
                self.root.destroy()
        except Exception as e:
            print(f"Error closing application: {e}")
            try:
                self.root.destroy()
            except Exception as e2:
                print(f"Error destroying root: {e2}")
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application interrupted by user")
        except Exception as e:
            print(f"Application error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function with maximum error handling"""
    try:
        print("Starting YouTube Downloader...")
        app = FixedYouTubeDownloader()
        print("App created successfully, starting mainloop...")
        app.run()
        print("Application finished")
    except KeyboardInterrupt:
        print("Application interrupted")
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Startup Error", f"Failed to start: {e}")
        except Exception as e2:
            print(f"Error showing startup error: {e2}")
        sys.exit(1)

if __name__ == "__main__":
    main()
