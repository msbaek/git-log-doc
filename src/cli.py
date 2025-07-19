import click
import sys
from pathlib import Path
from .utils.logger import setup_logger, get_logger
from .utils.errors import GitDocGenError, ConfigurationError
from .git_handler import GitHandler
from .commit_processor import CommitProcessor
from .diff_visualizer import DiffVisualizer
from .markdown_generator import MarkdownGenerator
from .progress_reporter import ProgressReporter


@click.command()
@click.option('--url', help='GitHub repository URL (e.g., https://github.com/user/repo/tree/branch)')
@click.option('--local', type=click.Path(exists=True), help='Local repository path')
@click.option('--branch', default='main', help='Branch name (default: main)')
@click.option('--commits', type=click.Path(exists=True), help='File containing commit hashes')
@click.option('--output', type=click.Path(), default='./output', help='Output directory (default: ./output)')
@click.option('--max-files', type=int, default=10, help='Maximum files per commit (default: 10)')
@click.option('--image-width', type=int, default=1200, help='Image width in pixels (default: 1200)')
@click.option('--exclude-patterns', help='Comma-separated patterns to exclude (e.g., *.lock,node_modules/*)')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def main(url, local, branch, commits, output, max_files, image_width, exclude_patterns, verbose):
    """Git Commit Documentation Generator
    
    Generate markdown documentation with visual diffs for git commits.
    """
    log_level = 'DEBUG' if verbose else 'INFO'
    logger = setup_logger('git-doc-gen', 'git-doc-gen.log', level=log_level)
    
    try:
        validate_inputs(url, local, commits)
        
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        images_path = output_path / 'images'
        images_path.mkdir(exist_ok=True)
        
        progress = ProgressReporter()
        
        progress.start_task("저장소 분석 중...")
        git_handler = GitHandler(url=url, local_path=local, branch=branch)
        repo_info = git_handler.get_repository_info()
        
        if commits:
            commit_list = read_commit_file(commits)
        else:
            commit_list = git_handler.get_commit_list()
        
        progress.update_task(f"총 {len(commit_list)}개의 커밋 발견")
        
        processor = CommitProcessor(
            git_handler=git_handler,
            max_files=max_files,
            exclude_patterns=exclude_patterns.split(',') if exclude_patterns else []
        )
        
        visualizer = DiffVisualizer(
            output_dir=images_path,
            image_width=image_width
        )
        
        generator = MarkdownGenerator(
            output_dir=output_path,
            repo_info=repo_info
        )
        
        processed_commits = []
        
        progress.start_progress("커밋 처리 중", total=len(commit_list))
        
        for idx, commit_hash in enumerate(commit_list):
            try:
                commit_info = processor.process_commit(commit_hash)
                
                image_filename = visualizer.generate_diff_image(
                    commit_info=commit_info,
                    index=idx + 1
                )
                
                commit_info['image_path'] = f"./images/{image_filename}"
                processed_commits.append(commit_info)
                
                progress.update_progress(idx + 1, f"커밋 {commit_hash[:8]} 처리 완료")
                
            except Exception as e:
                logger.error(f"커밋 {commit_hash} 처리 실패: {str(e)}")
                if verbose:
                    raise
                continue
        
        progress.complete_progress()
        
        progress.start_task("문서 작성 중...")
        markdown_file = generator.generate_document(processed_commits)
        progress.complete_task(f"✅ 완료! {markdown_file} 확인해주세요.")
        
    except ConfigurationError as e:
        logger.error(f"설정 오류: {str(e)}")
        click.echo(f"❌ 설정 오류: {str(e)}", err=True)
        sys.exit(1)
    except GitDocGenError as e:
        logger.error(f"실행 오류: {str(e)}")
        click.echo(f"❌ 실행 오류: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("예상치 못한 오류 발생")
        click.echo(f"❌ 예상치 못한 오류: {str(e)}", err=True)
        sys.exit(1)


def validate_inputs(url, local, commits):
    """Validate command line inputs"""
    if not any([url, local, commits]):
        raise ConfigurationError(
            "최소 하나의 입력 옵션이 필요합니다: --url, --local, 또는 --commits"
        )
    
    if sum(bool(x) for x in [url, local, commits]) > 1:
        raise ConfigurationError(
            "하나의 입력 옵션만 선택해주세요: --url, --local, 또는 --commits"
        )


def read_commit_file(filepath):
    """Read commit hashes from file"""
    commits = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                commits.append(line)
    return commits


if __name__ == '__main__':
    main()