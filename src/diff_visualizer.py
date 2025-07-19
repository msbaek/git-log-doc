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
        self.line_height = 0.025  # Initialize line height (increased for larger font)
        
        # Configure matplotlib for better text rendering with Korean font support
        self._setup_korean_font()
        rcParams['font.size'] = 14  # Increased default font size
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
        """Create a GitHub-style side-by-side diff image"""
        # Calculate total lines needed
        total_diff_lines = 0
        for file_info in commit_info['files']:
            left_lines, right_lines = self._prepare_side_by_side_diff(file_info['diff_content'])
            total_diff_lines += max(len(left_lines), len(right_lines))
        
        # Calculate dimensions
        header_height = 200  # pixels for commit header
        file_header_height = 80  # pixels per file header
        line_height_px = 35  # pixels per line (increased from 20)
        total_height = header_height + len(commit_info['files']) * file_header_height + total_diff_lines * line_height_px + 150
        
        fig_height = max(10, total_height / 100)
        fig = plt.figure(figsize=(self.image_width/100, fig_height), facecolor='white')
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Variables for layout
        y_position = 0.98
        line_height = 0.025  # Increased from 0.015
        
        # Commit information
        ax.text(0.02, y_position, f"Commit: {commit_info['full_hash']}", 
                fontsize=16, weight='bold')  # Increased from 12
        y_position -= line_height * 1.5
        
        ax.text(0.02, y_position, f"Author: {commit_info['author']} <{commit_info['email']}>", 
                fontsize=14)  # Increased from 10
        y_position -= line_height
        
        ax.text(0.02, y_position, f"Date: {commit_info['date']}", 
                fontsize=14)  # Increased from 10
        y_position -= line_height * 1.5
        
        ax.text(0.02, y_position, commit_info['message'], 
                fontsize=14, wrap=True)  # Increased from 10
        y_position -= line_height * 2
        
        # Stats
        stats = commit_info['stats']
        ax.text(0.02, y_position, 
                f"Files changed: {stats['files_changed']} | +{stats['insertions']} -{stats['deletions']}", 
                fontsize=14, color='gray')  # Increased from 10
        y_position -= line_height * 2
        
        # File diffs
        for file_idx, file_info in enumerate(commit_info['files']):
            if y_position < 0.1:
                break
                
            # File header with GitHub style
            file_bg_color = '#f6f8fa'
            file_rect = plt.Rectangle((0.01, y_position - line_height*1.5), 0.98, line_height*1.5,
                                    facecolor=file_bg_color, edgecolor='#e1e4e8', linewidth=1)
            ax.add_patch(file_rect)
            
            file_path = file_info['path']
            ax.text(0.02, y_position - line_height*0.7, file_path, 
                    fontsize=14, weight='bold', color='#24292e')  # Increased from 10
            y_position -= line_height * 2
            
            # Prepare side-by-side diff
            left_lines, right_lines = self._prepare_side_by_side_diff(file_info['diff_content'])
            
            # Track line numbers (parse from hunk headers if available)
            left_line_num = 1
            right_line_num = 1
            
            # Find first hunk to get starting line numbers
            for line in left_lines:
                if line['type'] == 'hunk':
                    import re
                    hunk_match = re.match(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line['content'])
                    if hunk_match:
                        left_line_num = int(hunk_match.group(1))
                        right_line_num = int(hunk_match.group(2))
                    break
            
            # Draw GitHub-style diff
            max_lines = min(50, max(len(left_lines), len(right_lines)))
            for i in range(max_lines):
                if y_position < 0.02:
                    break
                
                left_line = left_lines[i] if i < len(left_lines) else {'type': 'empty', 'content': ''}
                right_line = right_lines[i] if i < len(right_lines) else {'type': 'empty', 'content': ''}
                
                # Draw the diff line with line numbers
                self._draw_github_diff_line(ax, left_line, right_line, 
                                          left_line_num, right_line_num, 
                                          y_position)
                
                # Update line numbers
                if left_line['type'] != 'empty' and left_line['type'] != 'add':
                    left_line_num += 1
                if right_line['type'] != 'empty' and right_line['type'] != 'delete':
                    right_line_num += 1
                
                y_position -= line_height
            
            y_position -= line_height
        
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
    
    def _draw_github_diff_line(self, ax, left_line, right_line, left_num, right_num, y_pos):
        """Draw a GitHub-style diff line with line numbers"""
        # GitHub color scheme
        colors = {
            'delete_bg': '#ffeef0',
            'delete_text': '#cb2431',
            'add_bg': '#e6ffed',
            'add_text': '#22863a',
            'hunk_bg': '#f1f8ff',
            'hunk_text': '#005cc5',
            'line_num_bg': '#f6f8fa',
            'line_num_text': '#959da5',
            'border': '#e1e4e8'
        }
        
        # Line number width
        num_width = 0.06
        code_start = num_width * 2 + 0.01
        
        # Determine background colors
        if left_line['type'] == 'delete' or right_line['type'] == 'add':
            if left_line['type'] == 'delete':
                left_bg = colors['delete_bg']
            else:
                left_bg = 'white'
            
            if right_line['type'] == 'add':
                right_bg = colors['add_bg']
            else:
                right_bg = 'white'
        elif left_line['type'] == 'hunk' or right_line['type'] == 'hunk':
            left_bg = right_bg = colors['hunk_bg']
        else:
            left_bg = right_bg = 'white'
        
        # Draw backgrounds
        # Left side background
        left_rect = plt.Rectangle((0.01, y_pos - self.line_height/2), 0.48, self.line_height,
                                facecolor=left_bg, edgecolor='none')
        ax.add_patch(left_rect)
        
        # Right side background
        right_rect = plt.Rectangle((0.51, y_pos - self.line_height/2), 0.48, self.line_height,
                                 facecolor=right_bg, edgecolor='none')
        ax.add_patch(right_rect)
        
        # Draw line numbers
        # Left line numbers
        if left_line['type'] != 'empty':
            if left_line['type'] == 'hunk':
                left_num_text = '...'
            else:
                left_num_text = str(left_num)
            ax.text(0.03, y_pos, left_num_text, fontsize=12, 
                   color=colors['line_num_text'], ha='right', va='center')  # Increased from 8
        
        # Right line numbers  
        if right_line['type'] != 'empty':
            if right_line['type'] == 'hunk':
                right_num_text = '...'
            else:
                right_num_text = str(right_num)
            ax.text(0.53, y_pos, right_num_text, fontsize=12,
                   color=colors['line_num_text'], ha='right', va='center')  # Increased from 8
        
        # Draw code content
        # Left side code
        if left_line['type'] != 'empty':
            content = left_line['content']
            if len(content) > 60:
                content = content[:57] + '...'
            
            if left_line['type'] == 'delete':
                text_color = colors['delete_text']
                ax.text(code_start - 0.005, y_pos, '-', fontsize=12, color=text_color, va='center')  # Increased from 8
            elif left_line['type'] == 'hunk':
                text_color = colors['hunk_text']
            else:
                text_color = '#24292e'
            
            ax.text(code_start + 0.01, y_pos, content, fontsize=12, 
                   color=text_color, va='center')  # Increased from 8
        
        # Right side code
        if right_line['type'] != 'empty':
            content = right_line['content']
            if len(content) > 60:
                content = content[:57] + '...'
            
            if right_line['type'] == 'add':
                text_color = colors['add_text']
                ax.text(0.51 + code_start - 0.005, y_pos, '+', fontsize=12, color=text_color, va='center')  # Increased from 8
            elif right_line['type'] == 'hunk':
                text_color = colors['hunk_text']
            else:
                text_color = '#24292e'
            
            ax.text(0.51 + code_start + 0.01, y_pos, content, fontsize=12,
                   color=text_color, va='center')  # Increased from 8
        
        # Draw vertical separator
        ax.plot([0.5, 0.5], [y_pos + self.line_height/2, y_pos - self.line_height/2],
               color=colors['border'], linewidth=0.5)
        
        # Draw horizontal lines
        ax.plot([0.01, 0.99], [y_pos - self.line_height/2, y_pos - self.line_height/2],
               color=colors['border'], linewidth=0.5)
    
    def _get_file_color(self, change_type):
        """Get color for file change type"""
        colors = {
            'added': 'green',
            'deleted': 'red',
            'modified': 'blue',
            'renamed': 'purple'
        }
        return colors.get(change_type, 'black')