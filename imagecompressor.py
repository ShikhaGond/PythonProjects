#!/usr/bin/env python3
"""
Image Processor CLI Tool
A vibrant command-line tool for image compression, rotation, and resizing
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image, ImageEnhance
import colorama
from colorama import Fore, Back, Style
import inquirer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import time

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)
console = Console()

class ImageProcessor:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        self.unit_conversions = {
            'mm': 1,
            'cm': 10,
            'inch': 25.4,
            'inches': 25.4
        }
    
    def display_banner(self):
        """Display a vibrant welcome banner"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    🎨 IMAGE PROCESSOR CLI 🎨                             ║
║                                                          ║
║    ✨ Compress • Rotate • Resize • Transform ✨          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold magenta"))
    
    def show_menu(self):
        """Display interactive menu"""
        questions = [
            inquirer.List('action',
                         message="🚀 What would you like to do?",
                         choices=[
                             ('🗜️  Compress Image', 'compress'),
                             ('🔄 Rotate Image', 'rotate'),
                             ('📏 Resize Image', 'resize'),
                             ('🔍 Get Image Info', 'info'),
                             ('❌ Exit', 'exit')
                         ],
                         carousel=True)
        ]
        return inquirer.prompt(questions)['action']
    
    def get_image_path(self):
        """Get and validate image path"""
        while True:
            path = input(f"\n{Fore.CYAN}📁 Enter image path: {Style.RESET_ALL}")
            if not path:
                console.print("❌ Please enter a valid path!", style="red")
                continue
            
            img_path = Path(path)
            if not img_path.exists():
                console.print("❌ File not found!", style="red")
                continue
            
            if img_path.suffix.lower() not in self.supported_formats:
                console.print(f"❌ Unsupported format! Supported: {', '.join(self.supported_formats)}", style="red")
                continue
            
            return img_path
    
    def compress_image(self):
        """Compress image with quality selection"""
        console.print("\n🗜️ [bold green]IMAGE COMPRESSION[/bold green]")
        
        img_path = self.get_image_path()
        
        # Quality selection
        questions = [
            inquirer.List('quality',
                         message="Select compression quality:",
                         choices=[
                             ('🔥 High Quality (85%)', 85),
                             ('⭐ Good Quality (70%)', 70),
                             ('💾 Medium Quality (50%)', 50),
                             ('📱 Low Quality (30%)', 30),
                             ('🎯 Custom Quality', 'custom')
                         ])
        ]
        
        quality = inquirer.prompt(questions)['quality']
        
        if quality == 'custom':
            while True:
                try:
                    quality = int(input(f"{Fore.YELLOW}Enter quality (1-100): {Style.RESET_ALL}"))
                    if 1 <= quality <= 100:
                        break
                    else:
                        console.print("❌ Quality must be between 1-100", style="red")
                except ValueError:
                    console.print("❌ Please enter a valid number", style="red")
        
        output_path = self._get_output_path(img_path, f"_compressed_q{quality}")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("🗜️ Compressing image...", total=None)
            
            try:
                with Image.open(img_path) as img:
                    # Convert RGBA to RGB if saving as JPEG
                    if output_path.suffix.lower() in ['.jpg', '.jpeg'] and img.mode == 'RGBA':
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1] if len(img.split()) == 4 else None)
                        img = rgb_img
                    
                    img.save(output_path, optimize=True, quality=quality)
                
                original_size = img_path.stat().st_size
                compressed_size = output_path.stat().st_size
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                progress.update(task, completed=True)
            
            except Exception as e:
                console.print(f"❌ Error compressing image: {e}", style="red")
                return
        
        # Show results
        self._show_compression_results(img_path, output_path, original_size, compressed_size, reduction)
    
    def rotate_image(self):
        """Rotate image with angle selection"""
        console.print("\n🔄 [bold blue]IMAGE ROTATION[/bold blue]")
        
        img_path = self.get_image_path()
        
        questions = [
            inquirer.List('angle',
                         message="Select rotation angle:",
                         choices=[
                             ('↩️  90° Counter-clockwise', -90),
                             ('↪️  90° Clockwise', 90),
                             ('🔃 180°', 180),
                             ('↩️  270° Counter-clockwise', -270),
                             ('🎯 Custom Angle', 'custom')
                         ])
        ]
        
        angle = inquirer.prompt(questions)['angle']
        
        if angle == 'custom':
            while True:
                try:
                    angle = float(input(f"{Fore.YELLOW}Enter rotation angle (-360 to 360): {Style.RESET_ALL}"))
                    if -360 <= angle <= 360:
                        break
                    else:
                        console.print("❌ Angle must be between -360 and 360", style="red")
                except ValueError:
                    console.print("❌ Please enter a valid number", style="red")
        
        output_path = self._get_output_path(img_path, f"_rotated_{angle}deg")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("🔄 Rotating image...", total=None)
            
            try:
                with Image.open(img_path) as img:
                    rotated_img = img.rotate(-angle, expand=True, fillcolor='white')
                    rotated_img.save(output_path)
                
                progress.update(task, completed=True)
                
            except Exception as e:
                console.print(f"❌ Error rotating image: {e}", style="red")
                return
        
        console.print(f"✅ [green]Image rotated {angle}° and saved to:[/green] [cyan]{output_path}[/cyan]")
    
    def resize_image(self):
        """Resize image with unit support"""
        console.print("\n📏 [bold yellow]IMAGE RESIZING[/bold yellow]")
        
        img_path = self.get_image_path()
        
        with Image.open(img_path) as img:
            current_width, current_height = img.size
            dpi = img.info.get('dpi', (72, 72))[0]  # Default to 72 DPI
        
        # Show current dimensions
        table = Table(title="Current Image Dimensions")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Width (pixels)", str(current_width))
        table.add_row("Height (pixels)", str(current_height))
        table.add_row("Width (cm)", f"{(current_width / dpi) * 2.54:.2f}")
        table.add_row("Height (cm)", f"{(current_height / dpi) * 2.54:.2f}")
        table.add_row("DPI", str(dpi))
        
        console.print(table)
        
        # Resize method selection
        questions = [
            inquirer.List('method',
                         message="Choose resize method:",
                         choices=[
                             ('📐 By Dimensions (pixels)', 'pixels'),
                             ('📏 By Physical Size (cm/mm/inches)', 'physical'),
                             ('📊 By Percentage', 'percentage'),
                             ('🔒 Keep Aspect Ratio', 'aspect')
                         ])
        ]
        
        method = inquirer.prompt(questions)['method']
        
        if method == 'pixels':
            new_width, new_height = self._get_pixel_dimensions()
        elif method == 'physical':
            new_width, new_height = self._get_physical_dimensions(dpi)
        elif method == 'percentage':
            new_width, new_height = self._get_percentage_dimensions(current_width, current_height)
        else:  # aspect ratio
            new_width, new_height = self._get_aspect_ratio_dimensions(current_width, current_height)
        
        if not new_width or not new_height:
            return
        
        output_path = self._get_output_path(img_path, f"_resized_{new_width}x{new_height}")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("📏 Resizing image...", total=None)
            
            try:
                with Image.open(img_path) as img:
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_img.save(output_path)
                
                progress.update(task, completed=True)
                
            except Exception as e:
                console.print(f"❌ Error resizing image: {e}", style="red")
                return
        
        console.print(f"✅ [green]Image resized to {new_width}x{new_height} and saved to:[/green] [cyan]{output_path}[/cyan]")
    
    def get_image_info(self):
        """Display detailed image information"""
        console.print("\n🔍 [bold cyan]IMAGE INFORMATION[/bold cyan]")
        
        img_path = self.get_image_path()
        
        try:
            with Image.open(img_path) as img:
                file_size = img_path.stat().st_size
                dpi = img.info.get('dpi', (72, 72))
                
                table = Table(title=f"Image Info: {img_path.name}")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="magenta")
                
                table.add_row("File Path", str(img_path))
                table.add_row("Format", img.format)
                table.add_row("Mode", img.mode)
                table.add_row("Size (pixels)", f"{img.width} × {img.height}")
                table.add_row("File Size", self._format_file_size(file_size))
                table.add_row("DPI", f"{dpi[0]} × {dpi[1]}")
                
                # Physical dimensions
                if dpi[0] > 0:
                    width_cm = (img.width / dpi[0]) * 2.54
                    height_cm = (img.height / dpi[1]) * 2.54
                    table.add_row("Physical Size (cm)", f"{width_cm:.2f} × {height_cm:.2f}")
                    
                    width_inch = img.width / dpi[0]
                    height_inch = img.height / dpi[1]
                    table.add_row("Physical Size (inches)", f"{width_inch:.2f} × {height_inch:.2f}")
                
                console.print(table)
                
        except Exception as e:
            console.print(f"❌ Error reading image info: {e}", style="red")
    
    def _get_pixel_dimensions(self):
        """Get new dimensions in pixels"""
        try:
            width = int(input(f"{Fore.YELLOW}Enter new width (pixels): {Style.RESET_ALL}"))
            height = int(input(f"{Fore.YELLOW}Enter new height (pixels): {Style.RESET_ALL}"))
            return width, height
        except ValueError:
            console.print("❌ Please enter valid numbers", style="red")
            return None, None
    
    def _get_physical_dimensions(self, dpi):
        """Get new dimensions in physical units"""
        questions = [
            inquirer.List('unit',
                         message="Select unit:",
                         choices=[
                             ('📏 Centimeters (cm)', 'cm'),
                             ('📐 Millimeters (mm)', 'mm'),
                             ('📏 Inches', 'inches')
                         ])
        ]
        
        unit = inquirer.prompt(questions)['unit']
        
        try:
            width_physical = float(input(f"{Fore.YELLOW}Enter new width ({unit}): {Style.RESET_ALL}"))
            height_physical = float(input(f"{Fore.YELLOW}Enter new height ({unit}): {Style.RESET_ALL}"))
            
            # Convert to pixels
            if unit == 'cm':
                width_pixels = int((width_physical / 2.54) * dpi)
                height_pixels = int((height_physical / 2.54) * dpi)
            elif unit == 'mm':
                width_pixels = int((width_physical / 25.4) * dpi)
                height_pixels = int((height_physical / 25.4) * dpi)
            else:  # inches
                width_pixels = int(width_physical * dpi)
                height_pixels = int(height_physical * dpi)
            
            return width_pixels, height_pixels
        except ValueError:
            console.print("❌ Please enter valid numbers", style="red")
            return None, None
    
    def _get_percentage_dimensions(self, current_width, current_height):
        """Get new dimensions by percentage"""
        try:
            percentage = float(input(f"{Fore.YELLOW}Enter resize percentage (e.g., 50 for 50%): {Style.RESET_ALL}"))
            if percentage <= 0:
                console.print("❌ Percentage must be positive", style="red")
                return None, None
            
            scale = percentage / 100
            new_width = int(current_width * scale)
            new_height = int(current_height * scale)
            
            return new_width, new_height
        except ValueError:
            console.print("❌ Please enter a valid number", style="red")
            return None, None
    
    def _get_aspect_ratio_dimensions(self, current_width, current_height):
        """Get new dimensions while maintaining aspect ratio"""
        questions = [
            inquirer.List('dimension',
                         message="Which dimension to set?",
                         choices=[
                             ('📐 Set Width (auto height)', 'width'),
                             ('📏 Set Height (auto width)', 'height')
                         ])
        ]
        
        dimension = inquirer.prompt(questions)['dimension']
        
        try:
            if dimension == 'width':
                new_width = int(input(f"{Fore.YELLOW}Enter new width (pixels): {Style.RESET_ALL}"))
                aspect_ratio = current_height / current_width
                new_height = int(new_width * aspect_ratio)
            else:
                new_height = int(input(f"{Fore.YELLOW}Enter new height (pixels): {Style.RESET_ALL}"))
                aspect_ratio = current_width / current_height
                new_width = int(new_height * aspect_ratio)
            
            return new_width, new_height
        except ValueError:
            console.print("❌ Please enter a valid number", style="red")
            return None, None
    
    def _get_output_path(self, input_path, suffix):
        """Generate output path with suffix"""
        stem = input_path.stem
        extension = input_path.suffix
        output_dir = input_path.parent
        
        return output_dir / f"{stem}{suffix}{extension}"
    
    def _show_compression_results(self, original_path, compressed_path, original_size, compressed_size, reduction):
        """Display compression results"""
        table = Table(title="🗜️ Compression Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Original File", str(original_path.name))
        table.add_row("Compressed File", str(compressed_path.name))
        table.add_row("Original Size", self._format_file_size(original_size))
        table.add_row("Compressed Size", self._format_file_size(compressed_size))
        table.add_row("Size Reduction", f"{reduction:.1f}%")
        table.add_row("Space Saved", self._format_file_size(original_size - compressed_size))
        
        console.print(table)
        
        if reduction > 0:
            console.print(f"✅ [green]Great! You saved {reduction:.1f}% space![/green]")
        else:
            console.print("ℹ️ [yellow]The compressed file is larger (this can happen with high-quality settings)[/yellow]")
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def run(self):
        """Main application loop"""
        self.display_banner()
        
        while True:
            try:
                action = self.show_menu()
                
                if action == 'exit':
                    console.print("\n👋 [bold green]Thanks for using Image Processor CLI![/bold green]")
                    break
                elif action == 'compress':
                    self.compress_image()
                elif action == 'rotate':
                    self.rotate_image()
                elif action == 'resize':
                    self.resize_image()
                elif action == 'info':
                    self.get_image_info()
                
                # Ask if user wants to continue
                console.print("\n" + "="*60)
                continue_choice = input(f"\n{Fore.GREEN}Press Enter to continue or 'q' to quit: {Style.RESET_ALL}")
                if continue_choice.lower() == 'q':
                    console.print("\n👋 [bold green]Thanks for using Image Processor CLI![/bold green]")
                    break
                
            except KeyboardInterrupt:
                console.print("\n\n👋 [bold yellow]Goodbye![/bold yellow]")
                break
            except Exception as e:
                console.print(f"\n❌ [red]An error occurred: {e}[/red]")

def main():
    """Main entry point"""
    processor = ImageProcessor()
    processor.run()

if __name__ == "__main__":
    main()