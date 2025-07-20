import os
import re
import tempfile
from urllib.parse import urlparse
from pathlib import Path
from git import Repo
import requests
from .utils.errors import GitRepositoryError, GitHubAPIError
from .utils.logger import get_logger


class GitHandler:
    """Handle Git repository operations for both local and remote repositories"""
    
    def __init__(self, url=None, local_path=None, branch='main', all_commits=False):
        self.logger = get_logger('git-doc-gen')
        self.branch = branch
        self.all_commits = all_commits
        self.repo = None
        self.repo_info = {}
        
        if url:
            self._setup_github_repo(url)
        elif local_path:
            self._setup_local_repo(local_path)
        else:
            raise GitRepositoryError("URL 또는 로컬 경로가 필요합니다")
    
    def _setup_github_repo(self, url):
        """Setup repository from GitHub URL"""
        self.logger.info(f"GitHub 저장소 설정: {url}")
        
        match = re.match(r'https://github\.com/([^/]+)/([^/]+)(?:/tree/(.+))?', url)
        if not match:
            raise GitRepositoryError(f"잘못된 GitHub URL 형식: {url}")
        
        owner, repo_name, branch = match.groups()
        self.repo_info = {
            'owner': owner,
            'name': repo_name,
            'branch': branch or self.branch,
            'url': f'https://github.com/{owner}/{repo_name}'
        }
        
        clone_url = f'https://github.com/{owner}/{repo_name}.git'
        
        self.temp_dir = tempfile.mkdtemp(prefix='git-doc-gen-')
        self.logger.info(f"임시 디렉토리에 클론 중: {self.temp_dir}")
        
        try:
            self.repo = Repo.clone_from(clone_url, self.temp_dir)
            self.repo.git.checkout(self.repo_info['branch'])
        except Exception as e:
            raise GitRepositoryError(f"저장소 클론 실패: {str(e)}")
    
    def _setup_local_repo(self, local_path):
        """Setup repository from local path"""
        self.logger.info(f"로컬 저장소 설정: {local_path}")
        
        try:
            self.repo = Repo(local_path)
            if self.repo.bare:
                raise GitRepositoryError("Bare 저장소는 지원되지 않습니다")
            
            self.repo_info = {
                'name': Path(local_path).name,
                'branch': self.branch,
                'path': local_path
            }
            
            self.repo.git.checkout(self.branch)
            
        except Exception as e:
            raise GitRepositoryError(f"로컬 저장소 열기 실패: {str(e)}")
    
    def get_repository_info(self):
        """Get repository information"""
        return self.repo_info
    
    def get_commit_list(self):
        """Get list of commit hashes from current branch"""
        self.logger.info(f"브랜치 {self.repo_info['branch']}의 커밋 목록 가져오기")
        
        try:
            current_branch = self.repo_info['branch']
            
            # Find the common ancestor with main/master branch
            main_branch = None
            for branch_name in ['main', 'master']:
                try:
                    self.repo.commit(branch_name)
                    main_branch = branch_name
                    break
                except:
                    continue
            
            if self.all_commits or not main_branch or current_branch == main_branch:
                # Get all commits in the branch
                commits = list(self.repo.iter_commits(current_branch))
                self.logger.info(f"Getting all commits from {current_branch}")
            else:
                # Get commits that are only in the current branch
                # Using git log syntax: branch1..branch2 shows commits in branch2 but not in branch1
                commit_range = f"{main_branch}..{current_branch}"
                commits = list(self.repo.iter_commits(commit_range))
                self.logger.info(f"Getting commits unique to {current_branch} (excluding {main_branch})")
                
                # 브랜치가 완전히 병합된 경우 감지
                if not commits:
                    try:
                        # 브랜치의 최신 커밋이 main에 포함되어 있는지 확인
                        branch_head = self.repo.commit(current_branch)
                        main_commits = set(c.hexsha for c in self.repo.iter_commits(main_branch))
                        
                        if branch_head.hexsha in main_commits:
                            self.logger.info(f"브랜치 '{current_branch}'가 '{main_branch}'에 완전히 병합되어 있습니다.")
                        else:
                            self.logger.info(f"브랜치 '{current_branch}'에 고유한 커밋이 없습니다.")
                    except Exception as e:
                        self.logger.debug(f"브랜치 병합 상태 확인 중 오류: {str(e)}")
            
            # Reverse to get chronological order (oldest first)
            commits.reverse()
            commit_hashes = [commit.hexsha for commit in commits]
            self.logger.info(f"총 {len(commit_hashes)}개의 커밋 발견")
            return commit_hashes
            
        except Exception as e:
            raise GitRepositoryError(f"커밋 목록 가져오기 실패: {str(e)}")
    
    def get_commit(self, commit_hash):
        """Get a specific commit object"""
        try:
            return self.repo.commit(commit_hash)
        except Exception as e:
            raise GitRepositoryError(f"커밋 {commit_hash} 가져오기 실패: {str(e)}")
    
    def get_commit_diff(self, commit):
        """Get diff information for a commit"""
        try:
            if commit.parents:
                parent = commit.parents[0]
                diffs = parent.diff(commit, create_patch=True)
            else:
                diffs = commit.diff(None, create_patch=True)
            
            return diffs
            
        except Exception as e:
            raise GitRepositoryError(f"커밋 diff 가져오기 실패: {str(e)}")
    
    def cleanup(self):
        """Clean up temporary resources"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            self.logger.info(f"임시 디렉토리 삭제: {self.temp_dir}")
            shutil.rmtree(self.temp_dir)
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()