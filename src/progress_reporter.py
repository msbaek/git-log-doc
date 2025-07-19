from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import print as rprint


class ProgressReporter:
    """Report progress using rich library"""
    
    def __init__(self):
        self.console = Console()
        self.progress = None
        self.current_task = None
    
    def start_task(self, description):
        """Start a simple task with spinner"""
        self.console.print(f"📁 {description}")
    
    def update_task(self, message):
        """Update current task message"""
        self.console.print(f"   ↳ {message}")
    
    def complete_task(self, message=None):
        """Complete current task"""
        if message:
            self.console.print(f"   {message}")
    
    def start_progress(self, description, total):
        """Start a progress bar"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
        self.progress.start()
        self.current_task = self.progress.add_task(description, total=total)
    
    def update_progress(self, completed, description=None):
        """Update progress bar"""
        if self.progress and self.current_task is not None:
            if description:
                self.progress.update(self.current_task, completed=completed, description=description)
            else:
                self.progress.update(self.current_task, completed=completed)
    
    def complete_progress(self):
        """Complete and close progress bar"""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.current_task = None
    
    def show_summary(self, stats):
        """Show summary table"""
        table = Table(title="실행 요약")
        
        table.add_column("항목", style="cyan", no_wrap=True)
        table.add_column("값", style="magenta")
        
        for key, value in stats.items():
            table.add_row(key, str(value))
        
        self.console.print(table)
    
    def error(self, message):
        """Show error message"""
        self.console.print(f"[red]❌ {message}[/red]")
    
    def warning(self, message):
        """Show warning message"""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")
    
    def success(self, message):
        """Show success message"""
        self.console.print(f"[green]✅ {message}[/green]")