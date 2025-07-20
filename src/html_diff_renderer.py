from pathlib import Path
from .utils.logger import get_logger
from .utils.errors import DiffVisualizationError
import html


class HTMLDiffRenderer:
    """Generate HTML-formatted diffs with GitHub-style formatting"""
    
    def __init__(self):
        self.logger = get_logger('git-doc-gen')
    
    def render_diff(self, commit_info):
        """Render commit diff as HTML"""
        try:
            if not commit_info['files']:
                return self._render_empty_diff(commit_info)
            
            html_parts = []
            
            # Add CSS styles once at the beginning
            html_parts.append(self._get_css_styles())
            
            # Render each file diff
            for file_info in commit_info['files']:
                html_parts.append(self._render_file_diff(file_info))
            
            return '\n'.join(html_parts)
            
        except Exception as e:
            raise DiffVisualizationError(f"HTML diff 렌더링 실패: {str(e)}")
    
    def _get_css_styles(self):
        """Get CSS styles for diff rendering"""
        return """<style>
.diff-container {
    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    font-size: 12px;
    line-height: 20px;
    color: #24292e;
    background-color: #fff;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    margin: 16px 0;
    overflow: auto;
}

.diff-file-header {
    background-color: #f6f8fa;
    border-bottom: 1px solid #e1e4e8;
    padding: 10px 16px;
    font-weight: 600;
}

.diff-table {
    width: 100%;
    border-collapse: collapse;
}

.diff-table td {
    padding: 0 10px;
    vertical-align: top;
    white-space: pre;
    font-size: 12px;
    line-height: 20px;
}

.line-num {
    width: 1%;
    min-width: 50px;
    text-align: right;
    color: #959da5;
    background-color: #f6f8fa;
    border-right: 1px solid #e1e4e8;
    user-select: none;
}

.line-code {
    position: relative;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.line-deleted {
    background-color: #ffeef0;
}

.line-deleted .line-code {
    background-color: #ffeef0;
}

.line-added {
    background-color: #e6ffed;
}

.line-added .line-code {
    background-color: #e6ffed;
}

.line-context {
    color: #24292e;
}

.diff-hunk {
    background-color: #f1f8ff;
    color: #005cc5;
    font-weight: normal;
}

.diff-hunk td {
    padding: 4px 10px;
    border-top: 1px solid #e1e4e8;
    border-bottom: 1px solid #e1e4e8;
}

.line-marker {
    user-select: none;
    width: 20px;
    display: inline-block;
    text-align: center;
}

.deletion-marker {
    color: #cb2431;
}

.addition-marker {
    color: #22863a;
}

/* Responsive design */
@media (max-width: 768px) {
    .diff-container {
        font-size: 11px;
    }
    
    .diff-table td {
        padding: 0 5px;
    }
}
</style>"""
    
    def _render_file_diff(self, file_info):
        """Render a single file diff"""
        html_parts = []
        
        # File header
        html_parts.append(f'<div class="diff-container">')
        html_parts.append(f'  <div class="diff-file-header">{html.escape(file_info["path"])}</div>')
        html_parts.append('  <table class="diff-table">')
        
        # Process diff content
        left_lines, right_lines = self._prepare_side_by_side_diff(file_info['diff_content'])
        
        # Track line numbers
        left_line_num = 1
        right_line_num = 1
        
        # Find starting line numbers from first hunk
        for line in file_info['diff_content']:
            if line['type'] == 'hunk':
                import re
                hunk_match = re.match(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line['content'])
                if hunk_match:
                    left_line_num = int(hunk_match.group(1))
                    right_line_num = int(hunk_match.group(2))
                break
        
        # Render diff lines
        for i in range(len(left_lines)):
            left_line = left_lines[i] if i < len(left_lines) else {'type': 'empty', 'content': ''}
            right_line = right_lines[i] if i < len(right_lines) else {'type': 'empty', 'content': ''}
            
            if left_line['type'] == 'hunk' or right_line['type'] == 'hunk':
                # Render hunk header
                hunk_content = left_line['content'] if left_line['type'] == 'hunk' else right_line['content']
                html_parts.append(f'    <tr class="diff-hunk">')
                html_parts.append(f'      <td class="line-num">...</td>')
                html_parts.append(f'      <td class="line-code" colspan="3">{html.escape(hunk_content)}</td>')
                html_parts.append(f'    </tr>')
            else:
                html_parts.append('    <tr>')
                
                # Left side (deletions)
                if left_line['type'] != 'empty':
                    line_class = 'line-deleted' if left_line['type'] == 'delete' else 'line-context'
                    marker = '<span class="line-marker deletion-marker">-</span>' if left_line['type'] == 'delete' else '<span class="line-marker"> </span>'
                    html_parts.append(f'      <td class="line-num {line_class}">{left_line_num}</td>')
                    html_parts.append(f'      <td class="line-code {line_class}">{marker}{html.escape(left_line["content"])}</td>')
                    left_line_num += 1
                else:
                    html_parts.append('      <td class="line-num"></td>')
                    html_parts.append('      <td class="line-code"></td>')
                
                # Right side (additions)
                if right_line['type'] != 'empty':
                    line_class = 'line-added' if right_line['type'] == 'add' else 'line-context'
                    marker = '<span class="line-marker addition-marker">+</span>' if right_line['type'] == 'add' else '<span class="line-marker"> </span>'
                    html_parts.append(f'      <td class="line-num {line_class}">{right_line_num}</td>')
                    html_parts.append(f'      <td class="line-code {line_class}">{marker}{html.escape(right_line["content"])}</td>')
                    right_line_num += 1
                else:
                    html_parts.append('      <td class="line-num"></td>')
                    html_parts.append('      <td class="line-code"></td>')
                
                html_parts.append('    </tr>')
        
        html_parts.append('  </table>')
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _render_empty_diff(self, commit_info):
        """Render message for commits with no file changes"""
        return f"""<div class="diff-container">
  <div style="text-align: center; padding: 40px; color: #6a737d;">
    <p><strong>Commit:</strong> {html.escape(commit_info['full_hash'])}</p>
    <p>{html.escape(commit_info['message'])}</p>
    <p style="margin-top: 20px; font-style: italic;">No file changes in this commit</p>
  </div>
</div>"""
    
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
            elif line['type'] == 'truncated':
                # Handle truncated marker
                left_lines.append(line)
                right_lines.append(line)
            else:
                # Context lines appear on both sides
                left_lines.append({'type': 'context', 'content': line.get('content', '')})
                right_lines.append({'type': 'context', 'content': line.get('content', '')})
            
            i += 1
        
        return left_lines, right_lines