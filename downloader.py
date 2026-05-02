#!/usr/bin/env python3
"""
🎬 Video/Audio Downloader
Enter any video link, choose format, and download to your device
Fixed version - compatible with all yt-dlp versions
"""

import os
import sys
import subprocess
import platform
import time
import shutil
from pathlib import Path

# ANSI color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class VideoDownloader:
    def __init__(self):
        self.download_folder = self.get_download_folder()
        self.download_count = 0
        self.check_dependencies()
        self.check_ffmpeg()
    
    def get_download_folder(self):
        """Get the user's Downloads folder path"""
        if platform.system() == "Windows":
            return os.path.join(os.environ['USERPROFILE'], 'Downloads')
        else:  # macOS and Linux
            return os.path.join(os.path.expanduser('~'), 'Downloads')
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}🎬 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    
    def print_success(self, message):
        """Print success message in green"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def print_error(self, message):
        """Print error message in red"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def print_info(self, message):
        """Print info message in blue"""
        print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")
    
    def print_warning(self, message):
        """Print warning message in yellow"""
        print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")
    
    def print_prompt(self, message):
        """Print prompt in purple"""
        print(f"{Colors.PURPLE}{message}{Colors.END}", end="")
    
    def check_dependencies(self):
        """Check if yt-dlp is installed, install if not"""
        try:
            # Get yt-dlp version
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.yt_dlp_version = result.stdout.strip()
            self.print_success(f"yt-dlp version {self.yt_dlp_version} found!")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_info("Installing yt-dlp...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], 
                             check=True)
                self.print_success("yt-dlp installed successfully!")
                # Get version after install
                result = subprocess.run(['yt-dlp', '--version'], 
                                      capture_output=True, text=True, check=True)
                self.yt_dlp_version = result.stdout.strip()
            except subprocess.CalledProcessError:
                self.print_error("Failed to install yt-dlp")
                sys.exit(1)
    
    def check_ffmpeg(self):
        """Check if ffmpeg is installed"""
        self.ffmpeg_installed = shutil.which('ffmpeg') is not None
        if not self.ffmpeg_installed:
            self.print_warning("FFmpeg not found! Audio conversion to MP3 will not work.")
            self.print_info("WebM audio will work fine without ffmpeg.")
    
    def get_video_info(self, url):
        """Get video information without downloading"""
        try:
            cmd = [
                'yt-dlp',
                '--no-download',
                '--print', '%(title)s',
                '--print', '%(uploader)s',
                '--print', '%(duration)s',
                '--no-warnings',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            if len(lines) >= 3:
                # Clean the title (remove emojis and special chars)
                title = lines[0].encode('ascii', 'ignore').decode('ascii')
                
                info = {
                    'title': title,
                    'uploader': lines[1],
                    'duration': self.format_duration(int(lines[2])) if lines[2].isdigit() else "Unknown",
                }
                return info
            return None
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to get video info: {e}")
            return None
    
    def format_duration(self, seconds):
        """Format duration in seconds to MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def clean_filename(self, title):
        """Clean filename of invalid characters"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        # Remove extra spaces
        title = ' '.join(title.split())
        # Limit length
        return title[:50]
    
    def download_video(self, url, quality='best'):
        """Download video only - single MP4 file"""
        self.print_info("Downloading video (MP4 format)...")
        
        # Get video info for filename
        info = self.get_video_info(url)
        if info:
            clean_title = self.clean_filename(info['title'])
            filename = os.path.join(self.download_folder, f"{clean_title}.mp4")
        else:
            # Fallback to default naming
            filename = os.path.join(self.download_folder, "%(title)s.mp4")
        
        # Basic command without problematic options
        cmd = [
            'yt-dlp',
            '-f', f'{quality}[ext=mp4]/best[ext=mp4]/best',
            '-o', filename,
            '--no-playlist',
            '--no-warnings',
            '--progress',
            '--newline',
            url
        ]
        
        try:
            subprocess.run(cmd, check=True)
            self.download_count += 1
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Download failed: {e}")
            return False
    
    def download_audio_webm(self, url):
        """Download audio as WebM (no conversion, always works)"""
        self.print_info("Downloading audio (WebM format)...")
        
        # Get video info for filename
        info = self.get_video_info(url)
        if info:
            clean_title = self.clean_filename(info['title'])
            filename = os.path.join(self.download_folder, f"{clean_title}.webm")
        else:
            # Fallback to default naming
            filename = os.path.join(self.download_folder, "%(title)s.webm")
        
        # Basic command without problematic options
        cmd = [
            'yt-dlp',
            '-f', 'bestaudio/best',
            '-o', filename,
            '--no-playlist',
            '--no-warnings',
            '--progress',
            '--newline',
            url
        ]
        
        try:
            subprocess.run(cmd, check=True)
            self.download_count += 1
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Download failed: {e}")
            return False
    
    def download_audio_mp3(self, url, quality='320'):
        """Download audio as MP3 (requires ffmpeg)"""
        if not self.ffmpeg_installed:
            self.print_error("FFmpeg not installed! Cannot convert to MP3.")
            return False
        
        self.print_info("Downloading and converting to MP3...")
        
        # Get video info for filename
        info = self.get_video_info(url)
        if info:
            clean_title = self.clean_filename(info['title'])
            filename = os.path.join(self.download_folder, f"{clean_title}.mp3")
        else:
            # Fallback to default naming
            filename = os.path.join(self.download_folder, "%(title)s.mp3")
        
        # Basic command for MP3 conversion
        cmd = [
            'yt-dlp',
            '-f', 'bestaudio/best',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', quality,
            '-o', filename,
            '--no-playlist',
            '--no-warnings',
            '--progress',
            '--newline',
            url
        ]
        
        try:
            subprocess.run(cmd, check=True)
            self.download_count += 1
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Download failed: {e}")
            return False
    
    def show_download_location(self):
        """Show where files are downloaded"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}📁 Files will be saved to:{Colors.END}")
        print(f"{Colors.GREEN}{self.download_folder}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    def open_download_folder(self):
        """Open the download folder in file explorer"""
        try:
            if platform.system() == "Windows":
                os.startfile(self.download_folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', self.download_folder])
            else:  # Linux
                subprocess.run(['xdg-open', self.download_folder])
        except:
            self.print_warning("Could not open folder automatically")
    
    def process_single_video(self):
        """Process one video download"""
        self.clear_screen()
        self.print_header("VIDEO/AUDIO DOWNLOADER")
        
        # Show download count if any
        if self.download_count > 0:
            print(f"{Colors.GREEN}📥 Downloaded so far: {self.download_count} file(s){Colors.END}\n")
        
        print(f"{Colors.BOLD}📋 Enter a video link to download:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print("Supported sites: YouTube, Vimeo, Facebook, TikTok, Twitter, Instagram")
        print(f"{Colors.YELLOW}(Type 'menu' to go back or 'quit' to exit){Colors.END}")
        
        # Get URL from user
        self.print_prompt("🔗 Link: ")
        url = input().strip()
        
        if url.lower() == 'quit' or url.lower() == 'exit':
            return 'quit'
        elif url.lower() == 'menu' or url.lower() == 'back':
            return 'menu'
        
        if not url:
            self.print_error("Please enter a valid URL!")
            time.sleep(2)
            return 'retry'
        
        # Get video info
        self.clear_screen()
        self.print_header("FETCHING VIDEO INFO")
        print(f"\n{Colors.YELLOW}Please wait... Getting video information{Colors.END}")
        
        info = self.get_video_info(url)
        
        if not info:
            self.print_error("Could not fetch video information. The link might be invalid.")
            time.sleep(2)
            return 'retry'
        
        # Show video info
        self.clear_screen()
        self.print_header("VIDEO INFORMATION")
        
        print(f"\n{Colors.BOLD}📌 Title:{Colors.END} {info['title']}")
        print(f"{Colors.BOLD}👤 Uploader:{Colors.END} {info['uploader']}")
        print(f"{Colors.BOLD}⏱️ Duration:{Colors.END} {info['duration']}")
        
        # Ask what to download
        print(f"\n{Colors.BOLD}🎯 What would you like to download?{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print("1. 🎬 Video (MP4 format) - Single file")
        print("2. 🎵 Audio (WebM format) - Single file, works on all players")
        if self.ffmpeg_installed:
            print("3. 🎵 Audio (MP3 format) - Requires conversion")
        print("4. ❌ Cancel this video")
        
        if self.ffmpeg_installed:
            choice = input(f"\n{Colors.PURPLE}Choose (1-4): {Colors.END}").strip()
        else:
            choice = input(f"\n{Colors.PURPLE}Choose (1, 2, or 4): {Colors.END}").strip()
        
        if choice == "4" or (choice == "3" and not self.ffmpeg_installed):
            self.print_info("Download cancelled")
            time.sleep(1)
            return 'continue'
        
        # Quality selection for video
        if choice == "1":
            self.clear_screen()
            self.print_header("VIDEO QUALITY")
            
            print(f"\n{Colors.BOLD}📊 Select video quality:{Colors.END}")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
            print("1. 🔥 Best quality")
            print("2. 📱 1080p (Full HD)")
            print("3. 📱 720p (HD)")
            print("4. 📱 480p (SD)")
            print("5. 💾 Lowest quality")
            
            quality_choice = input(f"\n{Colors.PURPLE}Choose (1-5): {Colors.END}").strip()
            
            quality_map = {
                '1': 'best',
                '2': 'best[height<=1080]',
                '3': 'best[height<=720]',
                '4': 'best[height<=480]',
                '5': 'worst'
            }
            
            quality = quality_map.get(quality_choice, 'best')
            
            # Show download location
            self.show_download_location()
            
            confirm = input(f"\n{Colors.PURPLE}Start download? (yes/no): {Colors.END}").lower()
            if confirm in ['yes', 'y']:
                success = self.download_video(url, quality)
                
                if success:
                    self.print_success("Video downloaded successfully!")
                    self.print_info(f"File saved to: {self.download_folder}")
                else:
                    self.print_error("Download failed!")
        
        # Audio as WebM (no conversion)
        elif choice == "2":
            self.show_download_location()
            confirm = input(f"\n{Colors.PURPLE}Start download? (yes/no): {Colors.END}").lower()
            if confirm in ['yes', 'y']:
                success = self.download_audio_webm(url)
                
                if success:
                    self.print_success("Audio downloaded successfully (WebM format)!")
                    self.print_info(f"File saved to: {self.download_folder}")
                    self.print_info("WebM files play in VLC, Chrome, Firefox, and most media players")
                else:
                    self.print_error("Download failed!")
        
        # Audio as MP3 (requires ffmpeg)
        elif choice == "3" and self.ffmpeg_installed:
            self.clear_screen()
            self.print_header("AUDIO QUALITY")
            
            print(f"\n{Colors.BOLD}🎵 Select audio quality:{Colors.END}")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
            print("1. 🎧 320 kbps (Best quality)")
            print("2. 🎧 256 kbps (High quality)")
            print("3. 🎧 192 kbps (Good quality)")
            print("4. 🎧 128 kbps (Standard quality)")
            
            quality_choice = input(f"\n{Colors.PURPLE}Choose (1-4): {Colors.END}").strip()
            
            quality_map = {
                '1': '320',
                '2': '256',
                '3': '192',
                '4': '128'
            }
            
            quality = quality_map.get(quality_choice, '192')
            
            # Show download location
            self.show_download_location()
            
            confirm = input(f"\n{Colors.PURPLE}Start download? (yes/no): {Colors.END}").lower()
            if confirm in ['yes', 'y']:
                success = self.download_audio_mp3(url, quality)
                
                if success:
                    self.print_success("Audio downloaded successfully (MP3 format)!")
                    self.print_info(f"File saved to: {self.download_folder}")
                else:
                    self.print_error("Download failed!")
        
        return 'continue'
    
    def run(self):
        """Main program loop"""
        while True:
            self.clear_screen()
            self.print_header("VIDEO/AUDIO DOWNLOADER")
            
            print(f"\n{Colors.BOLD}🌟 WELCOME TO VIDEO DOWNLOADER{Colors.END}")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
            print("1. 🎬 Download videos/audio")
            print("2. 📂 Open download folder")
            print("3. 🚪 Exit")
            
            if not self.ffmpeg_installed:
                print(f"\n{Colors.YELLOW}Note: WebM audio works without ffmpeg{Colors.END}")
                print(f"{Colors.YELLOW}Install ffmpeg for MP3 conversion{Colors.END}")
            
            main_choice = input(f"\n{Colors.PURPLE}Choose (1-3): {Colors.END}").strip()
            
            if main_choice == "1":
                # Download loop
                while True:
                    result = self.process_single_video()
                    
                    if result == 'quit':
                        self.print_success("Thanks for using Video Downloader!")
                        return
                    elif result == 'menu':
                        break
                    
                    # Ask if user wants to download another
                    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
                    another = input(f"{Colors.PURPLE}📥 Download another video? (yes/no/menu): {Colors.END}").lower()
                    
                    if another == 'menu' or another == 'm':
                        break
                    elif another not in ['yes', 'y']:
                        self.print_success(f"Downloaded {self.download_count} file(s). Thanks for using Video Downloader!")
                        return
                    
            elif main_choice == "2":
                self.open_download_folder()
                input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
                
            elif main_choice == "3":
                self.print_success(f"Downloaded {self.download_count} file(s). Goodbye!")
                break

def main():
    """Main entry point"""
    try:
        downloader = VideoDownloader()
        downloader.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Download cancelled. Goodbye!{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()