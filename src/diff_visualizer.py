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
        self.line_height = 0.020  # Initialize line height
        
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
        """Create a side-by-side diff image with matplotlib"""
        # Calculate image dimensions
        total_diff_lines = 0
        for file_info in commit_info['files']:
            left_lines, right_lines = self._prepare_side_by_side_diff(file_info['diff_content'])
            total_diff_lines += max(len(left_lines), len(right_lines))
        
        header_lines = 6 + len(commit_info['files']) * 3
        total_height = max(800, (total_diff_lines + header_lines) * 25)
        
        fig_height = total_height / 100
        fig, ax = plt.subplots(figsize=(self.image_width/100, fig_height))
        
        # Setup axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Header section
        y_position = 0.98
        line_height = 0.020
        
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
                    fontsize=11, weight='bold', color=file_color)
            y_position -= line_height * 1.5
            
            # Draw column headers for side-by-side view
            ax.text(0.02, y_position, "Original", fontsize=9, weight='bold', color='darkred')
            ax.text(0.52, y_position, "Modified", fontsize=9, weight='bold', color='darkgreen')
            y_position -= line_height
            
            # Draw separator line
            ax.plot([0.02, 0.48], [y_position + line_height/2, y_position + line_height/2], 
                   color='lightgray', linewidth=0.5)
            ax.plot([0.52, 0.98], [y_position + line_height/2, y_position + line_height/2], 
                   color='lightgray', linewidth=0.5)
            
            # Prepare side-by-side diff
            left_lines, right_lines = self._prepare_side_by_side_diff(file_info['diff_content'])
            
            # Draw side-by-side diff
            max_lines = min(50, max(len(left_lines), len(right_lines)))
            for i in range(max_lines):
                # Left side (original/deleted)
                if i < len(left_lines):
                    self._draw_diff_line(ax, left_lines[i], 0.02, y_position, 0.46, 'left')
                
                # Center divider
                ax.plot([0.5, 0.5], [y_position + line_height/2, y_position - line_height/2], 
                       color='lightgray', linewidth=0.5)
                
                # Right side (new/added)
                if i < len(right_lines):
                    self._draw_diff_line(ax, right_lines[i], 0.52, y_position, 0.46, 'right')
                
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
    
    def _prepare_side_by_side_diff(self, diff_content):
        """Prepare diff content for side-by-side display"""
        left_lines = []  # Original (deleted) content
        right_lines = [] # New (added) content
        
        i = 0
        while i < len(diff_content):
            line = diff_content[i]
            
            if line['type'] == 'hunk':
                # Add hunk header to both sides
                left_lines.append(line)
                right_lines.append(line)
            elif line['type'] == 'delete':
                # Collect consecutive delete lines
                delete_block = []
                while i < len(diff_content) and diff_content[i]['type'] == 'delete':
                    delete_block.append(diff_content[i])
                    i += 1
                
                # Check if followed by add lines
                add_block = []
                while i < len(diff_content) and diff_content[i]['type'] == 'add':
                    add_block.append(diff_content[i])
                    i += 1
                
                # Pair them up
                max_len = max(len(delete_block), len(add_block))
                for j in range(max_len):
                    if j < len(delete_block):
                        left_lines.append(delete_block[j])
                    else:
                        left_lines.append({'type': 'empty', 'content': ''})
                    
                    if j < len(add_block):
                        right_lines.append(add_block[j])
                    else:
                        right_lines.append({'type': 'empty', 'content': ''})
                
                i -= 1  # Adjust because we've already processed adds
            elif line['type'] == 'add':
                # Standalone add (no preceding delete)
                left_lines.append({'type': 'empty', 'content': ''})
                right_lines.append(line)
            else:
                # Context lines appear on both sides
                left_lines.append({'type': 'context', 'content': line.get('content', '')})
                right_lines.append({'type': 'context', 'content': line.get('content', '')})
            
            i += 1
        
        return left_lines, right_lines
    
    def _draw_diff_line(self, ax, line_info, x_pos, y_pos, width, side):
        """Draw a single line of diff content"""
        if line_info['type'] == 'empty':
            return
        
        # Set colors based on type and side
        if line_info['type'] == 'delete':
            bg_color = '#ffdddd'
            text_color = 'darkred'
        elif line_info['type'] == 'add':
            bg_color = '#ddffdd'
            text_color = 'darkgreen'
        elif line_info['type'] == 'hunk':
            bg_color = '#f0f0f0'
            text_color = 'blue'
        else:  # context
            bg_color = None
            text_color = 'black'
        
        # Draw background
        if bg_color:
            rect = plt.Rectangle((x_pos, y_pos - self.line_height/2), width, self.line_height,
                               facecolor=bg_color, edgecolor='none', alpha=0.5)
            ax.add_patch(rect)
        
        # Draw text
        content = line_info['content']
        if len(content) > 80:
            content = content[:77] + '...'
        
        ax.text(x_pos + 0.01, y_pos, content, fontsize=8, color=text_color, 
                verticalalignment='center')
    
    def _get_file_color(self, change_type):
        """Get color for file change type"""
        colors = {
            'added': 'green',
            'deleted': 'red',
            'modified': 'blue',
            'renamed': 'purple'
        }
        return colors.get(change_type, 'black')