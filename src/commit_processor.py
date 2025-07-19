import fnmatch
from datetime import datetime
from .utils.logger import get_logger
from .utils.errors import GitRepositoryError


class CommitProcessor:
    """Process git commits and extract relevant information"""
    
    TEXT_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
        '.md', '.txt', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',
        '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.sql', '.graphql', '.proto', '.dockerfile', '.makefile'
    }
    
    def __init__(self, git_handler, max_files=10, exclude_patterns=None):
        self.logger = get_logger('git-doc-gen')
        self.git_handler = git_handler
        self.max_files = max_files
        self.exclude_patterns = exclude_patterns or []
        
        self.exclude_patterns.extend([
            '*.lock', 'package-lock.json', 'yarn.lock', 'Gemfile.lock',
            'node_modules/*', '__pycache__/*', '*.pyc', '.git/*',
            '.DS_Store', 'Thumbs.db', '*.min.js', '*.min.css'
        ])
    
    def process_commit(self, commit_hash):
        """Process a single commit and extract information"""
        self.logger.debug(f"커밋 처리 중: {commit_hash}")
        
        try:
            commit = self.git_handler.get_commit(commit_hash)
            diffs = self.git_handler.get_commit_diff(commit)
            
            commit_info = {
                'hash': commit.hexsha[:8],
                'full_hash': commit.hexsha,
                'message': commit.message.strip(),
                'author': commit.author.name,
                'email': commit.author.email,
                'date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                'files': [],
                'stats': {
                    'files_changed': 0,
                    'insertions': 0,
                    'deletions': 0
                }
            }
            
            processed_files = 0
            
            for diff in diffs:
                if processed_files >= self.max_files:
                    break
                
                file_path = diff.b_path or diff.a_path
                
                if self._should_skip_file(file_path):
                    continue
                
                if not self._is_text_file(file_path):
                    continue
                
                file_info = self._process_diff(diff)
                if file_info:
                    commit_info['files'].append(file_info)
                    processed_files += 1
                    
                    commit_info['stats']['insertions'] += file_info['insertions']
                    commit_info['stats']['deletions'] += file_info['deletions']
            
            commit_info['stats']['files_changed'] = len(commit_info['files'])
            
            return commit_info
            
        except Exception as e:
            raise GitRepositoryError(f"커밋 {commit_hash} 처리 실패: {str(e)}")
    
    def _should_skip_file(self, file_path):
        """Check if file should be skipped based on exclude patterns"""
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                self.logger.debug(f"파일 건너뛰기 (패턴 매칭): {file_path}")
                return True
        return False
    
    def _is_text_file(self, file_path):
        """Check if file is a text file based on extension"""
        if not file_path:
            return False
        
        file_ext = '.' + file_path.split('.')[-1].lower() if '.' in file_path else ''
        
        if file_path.lower() in ['makefile', 'dockerfile', 'jenkinsfile', 'rakefile']:
            return True
        
        return file_ext in self.TEXT_EXTENSIONS
    
    def _process_diff(self, diff):
        """Process a single file diff"""
        try:
            file_path = diff.b_path or diff.a_path
            
            file_info = {
                'path': file_path,
                'change_type': self._get_change_type(diff),
                'insertions': 0,
                'deletions': 0,
                'diff_content': []
            }
            
            if diff.diff:
                diff_lines = diff.diff.decode('utf-8', errors='ignore').split('\n')
                
                line_changes = []
                for line in diff_lines:
                    if line.startswith('+') and not line.startswith('+++'):
                        file_info['insertions'] += 1
                        line_changes.append({'type': 'add', 'content': line[1:]})
                    elif line.startswith('-') and not line.startswith('---'):
                        file_info['deletions'] += 1
                        line_changes.append({'type': 'delete', 'content': line[1:]})
                    elif line.startswith('@@'):
                        line_changes.append({'type': 'hunk', 'content': line})
                
                if len(line_changes) > 100:
                    file_info['diff_content'] = line_changes[:50] + \
                        [{'type': 'truncated', 'content': f'... {len(line_changes) - 100} lines truncated ...'}] + \
                        line_changes[-50:]
                else:
                    file_info['diff_content'] = line_changes
            
            return file_info
            
        except Exception as e:
            self.logger.error(f"Diff 처리 실패: {str(e)}")
            return None
    
    def _get_change_type(self, diff):
        """Get the type of change for a file"""
        if diff.new_file:
            return 'added'
        elif diff.deleted_file:
            return 'deleted'
        elif diff.renamed_file:
            return 'renamed'
        else:
            return 'modified'