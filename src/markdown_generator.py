from pathlib import Path
from datetime import datetime
from .utils.logger import get_logger
from .utils.errors import FileSystemError


class MarkdownGenerator:
    """Generate markdown documentation from processed commits"""
    
    def __init__(self, output_dir, repo_info):
        self.logger = get_logger('git-doc-gen')
        self.output_dir = Path(output_dir)
        self.repo_info = repo_info
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_document(self, commits):
        """Generate the main markdown document"""
        output_file = self.output_dir / 'commit-history.md'
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write header
                f.write(self._generate_header())
                
                # Write table of contents
                if len(commits) > 10:
                    f.write(self._generate_toc(commits))
                
                # Write commit sections
                for commit in commits:
                    f.write(self._generate_commit_section(commit))
                
                # Write footer
                f.write(self._generate_footer())
            
            self.logger.info(f"마크다운 문서 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            raise FileSystemError(f"마크다운 문서 생성 실패: {str(e)}")
    
    def _generate_header(self):
        """Generate document header"""
        header = f"# Git Commit History - {self.repo_info.get('name', 'Repository')}\n\n"
        
        if 'branch' in self.repo_info:
            header += f"**Branch:** `{self.repo_info['branch']}`\n\n"
        
        if 'url' in self.repo_info:
            header += f"**Repository:** [{self.repo_info['url']}]({self.repo_info['url']})\n\n"
        
        header += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        header += "---\n\n"
        
        return header
    
    def _generate_toc(self, commits):
        """Generate table of contents"""
        toc = "## Table of Contents\n\n"
        
        for i, commit in enumerate(commits[:20]):  # Limit TOC to first 20 commits
            message = commit['message'].split('\n')[0][:60]
            if len(commit['message'].split('\n')[0]) > 60:
                message += "..."
            
            toc += f"{i+1}. [{commit['hash']} - {message}](#{commit['hash']})\n"
        
        if len(commits) > 20:
            toc += f"\n*... and {len(commits) - 20} more commits*\n"
        
        toc += "\n---\n\n"
        return toc
    
    def _generate_commit_section(self, commit):
        """Generate markdown section for a single commit"""
        section = f"## <a id=\"{commit['hash']}\"></a>{commit['hash']} - {commit['message'].split(chr(10))[0]}\n\n"
        
        # Commit metadata
        section += f"**Author:** {commit['author']} <{commit['email']}>  \n"
        section += f"**Date:** {commit['date']}  \n"
        
        # Stats
        stats = commit['stats']
        section += f"**Changes:** {stats['files_changed']} files | "
        section += f"+{stats['insertions']} insertions | -{stats['deletions']} deletions\n\n"
        
        # Full commit message if multi-line
        if '\n' in commit['message']:
            section += "### Commit Message\n\n"
            section += "```\n"
            section += commit['message']
            section += "\n```\n\n"
        
        # Diff image
        if 'image_path' in commit:
            section += f"### Visual Diff\n\n"
            section += f"![diff]({commit['image_path']})\n\n"
        
        # Changed files summary
        if commit['files']:
            section += "### Changed Files\n\n"
            
            for file in commit['files']:
                icon = self._get_change_icon(file['change_type'])
                section += f"- {icon} `{file['path']}` "
                section += f"(+{file['insertions']} -{file['deletions']})\n"
            
            section += "\n"
        
        # Main changes summary
        section += self._generate_changes_summary(commit)
        
        section += "---\n\n"
        return section
    
    def _generate_changes_summary(self, commit):
        """Generate a summary of main changes"""
        if not commit['files']:
            return ""
        
        summary = "### Summary of Changes\n\n"
        
        # Group files by extension
        extensions = {}
        for file in commit['files']:
            ext = Path(file['path']).suffix or 'no-extension'
            if ext not in extensions:
                extensions[ext] = []
            extensions[ext].append(file)
        
        # Generate summary by file type
        for ext, files in extensions.items():
            total_insertions = sum(f['insertions'] for f in files)
            total_deletions = sum(f['deletions'] for f in files)
            
            if ext == 'no-extension':
                summary += f"- Configuration files: "
            else:
                summary += f"- {ext} files: "
            
            summary += f"{len(files)} file(s) modified "
            summary += f"(+{total_insertions} -{total_deletions})\n"
        
        summary += "\n"
        return summary
    
    def _get_change_icon(self, change_type):
        """Get icon for change type"""
        icons = {
            'added': '🟢',
            'deleted': '🔴',
            'modified': '🔵',
            'renamed': '🟣'
        }
        return icons.get(change_type, '⚪')
    
    def _generate_footer(self):
        """Generate document footer"""
        footer = "\n---\n\n"
        footer += f"*Generated by [git-doc-gen](https://github.com/yourusername/git-doc-gen) "
        footer += f"on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        return footer