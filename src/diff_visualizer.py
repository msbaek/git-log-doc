import os
import platform
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams, font_manager
from PIL import Image, ImageDraw, ImageFont
from .utils.logger import get_logger
from .utils.errors import DiffVisualizationError


class DiffVisualizer:
    """Generate visual diff images from commit information"""
    
    def __init__(self, output_dir, image_width=1200):
        self.logger = get_logger('git-doc-gen')
        self.output_dir = Path(output_dir)
        self.image_width = image_width
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure matplotlib for better text rendering with Korean font support
        self._setup_korean_font()
        rcParams['font.size'] = 10
        rcParams['axes.unicode_minus'] = False  # Fix minus sign display
    
    def _setup_korean_font(self):
        """Setup Korean font for matplotlib"""
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            # Use AppleGothic which is available on all macOS systems
            rcParams['font.family'] = 'AppleGothic'
        elif system == 'Windows':
            rcParams['font.family'] = 'Malgun Gothic'
        else:  # Linux
            rcParams['font.family'] = 'DejaVu Sans'
        
        self.logger.info(f"Font set to: {rcParams['font.family']}")
        
    def generate_diff_image(self, commit_info, index):
        """Generate a diff image for a commit"""
        filename = f"{index:03d}-{commit_info['hash']}.png"
        output_path = self.output_dir / filename
        
        try:
            if not commit_info['files']:
                self._create_empty_diff_image(output_path, commit_info)
            else:
                self._create_diff_image(output_path, commit_info)
            
            self.logger.debug(f"이미지 생성 완료: {output_path}")
            return filename
            
        except Exception as e:
            raise DiffVisualizationError(f"이미지 생성 실패: {str(e)}")
    
    def _create_diff_image(self, output_path, commit_info):
        """Create a diff image with matplotlib"""
        # Calculate image dimensions
        total_lines = sum(len(f['diff_content']) for f in commit_info['files'])
        header_lines = 4 + len(commit_info['files']) * 3
        # Increase height per line from 20 to 30 pixels for better spacing
        total_height = max(600, (total_lines + header_lines) * 30)
        
        fig_height = total_height / 100
        fig, ax = plt.subplots(figsize=(self.image_width/100, fig_height))
        
        # Remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Create header
        y_position = 0.98
        # Increase line height for better readability
        line_height = 0.025
        
        # Commit information
        ax.text(0.02, y_position, f"Commit: {commit_info['full_hash']}", 
                fontsize=12, weight='bold')
        y_position -= line_height * 1.5
        
        ax.text(0.02, y_position, f"Author: {commit_info['author']} <{commit_info['email']}>", 
                fontsize=10)
        y_position -= line_height
        
        ax.text(0.02, y_position, f"Date: {commit_info['date']}", 
                fontsize=10)
        y_position -= line_height * 1.5
        
        ax.text(0.02, y_position, commit_info['message'], 
                fontsize=10, wrap=True)
        y_position -= line_height * 2
        
        # Stats
        stats = commit_info['stats']
        ax.text(0.02, y_position, 
                f"Files changed: {stats['files_changed']} | +{stats['insertions']} -{stats['deletions']}", 
                fontsize=10, color='gray')
        y_position -= line_height * 2
        
        # File diffs
        for file_info in commit_info['files']:
            # File header
            file_color = self._get_file_color(file_info['change_type'])
            ax.text(0.02, y_position, f"{file_info['change_type'].upper()}: {file_info['path']}", 
                    fontsize=10, weight='bold', color=file_color)
            y_position -= line_height * 1.5
            
            # Diff lines
            for line_info in file_info['diff_content'][:50]:  # Limit lines per file
                if line_info['type'] == 'add':
                    ax.text(0.02, y_position, f"+ {line_info['content'][:100]}", 
                            fontsize=9, color='green')
                elif line_info['type'] == 'delete':
                    ax.text(0.02, y_position, f"- {line_info['content'][:100]}", 
                            fontsize=9, color='red')
                elif line_info['type'] == 'hunk':
                    ax.text(0.02, y_position, line_info['content'], 
                            fontsize=9, color='blue')
                elif line_info['type'] == 'truncated':
                    ax.text(0.02, y_position, line_info['content'], 
                            fontsize=9, color='gray', style='italic')
                
                y_position -= line_height
                
                if y_position < 0.02:
                    break
            
            y_position -= line_height
            
            if y_position < 0.02:
                break
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _create_empty_diff_image(self, output_path, commit_info):
        """Create an image for commits with no file changes"""
        fig, ax = plt.subplots(figsize=(self.image_width/100, 4))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Commit information
        y_position = 0.8
        ax.text(0.5, y_position, f"Commit: {commit_info['full_hash']}", 
                fontsize=12, weight='bold', ha='center')
        
        ax.text(0.5, 0.5, commit_info['message'], 
                fontsize=10, ha='center', wrap=True)
        
        ax.text(0.5, 0.2, "No file changes in this commit", 
                fontsize=10, ha='center', color='gray')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _get_file_color(self, change_type):
        """Get color for file change type"""
        colors = {
            'added': 'green',
            'deleted': 'red',
            'modified': 'blue',
            'renamed': 'purple'
        }
        return colors.get(change_type, 'black')