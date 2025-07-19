class GitDocGenError(Exception):
    """Base exception for git-doc-gen"""
    pass


class GitRepositoryError(GitDocGenError):
    """Raised when there's an issue with Git repository operations"""
    pass


class GitHubAPIError(GitDocGenError):
    """Raised when GitHub API requests fail"""
    pass


class FileSystemError(GitDocGenError):
    """Raised when file system operations fail"""
    pass


class DiffVisualizationError(GitDocGenError):
    """Raised when diff image generation fails"""
    pass


class ConfigurationError(GitDocGenError):
    """Raised when configuration is invalid"""
    pass