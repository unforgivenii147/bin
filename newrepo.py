#!/usr/bin/env python3
"""
GitHub Repository Manager
Equivalent of the bash version with the same workflow.
"""

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


class GitHubRepoManager:

    def __init__(self):
        """Initialize the GitHub Repository Manager."""
        self.repo_dir = Path.cwd()
        self.repo_name = self.repo_dir.name
        self.home_dir = Path.home()

    def _run_command(self, command: list) -> Tuple[int, str, str]:
        """Execute shell command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
            )
            stdout = result.stdout.strip() if result.stdout else ''
            stderr = result.stderr.strip() if result.stderr else ''
            return result.returncode, stdout, stderr
        except Exception as e:
            print(f'Error executing command: {" ".join(command)}')
            print(f'Exception: {e}')
            return 1, '', str(e)

    def _repo_exists_locally(self) -> bool:
        """Check if . git directory exists."""
        return (self.repo_dir / '.git').exists()

    def _repo_exists_on_github(self) -> bool:
        """Check if repository exists on GitHub."""
        returncode, _, _ = self._run_command(
            ['gh', 'repo', 'view', self.repo_name])
        return returncode == 0

    def _init_git_repo(self):
        """Initialize git repository if needed."""
        if not self._repo_exists_locally():
            print('📦 Initializing git repository...')
            returncode, _, stderr = self._run_command(['git', 'init'])
            if returncode != 0:
                print(f'Error:  {stderr}')
                sys.exit(1)
            print('✓ Git repository initialized')

    def _ensure_main_branch(self):
        """Ensure branch is 'main'."""
        print("\n🔄 Ensuring 'main' branch...")

        # Get current branch
        returncode, current_branch, _ = self._run_command(
            ['git', 'symbolic-ref', '--short', 'HEAD'])

        if returncode != 0:
            # No branch exists, create main
            print("Creating 'main' branch...")
            returncode, _, stderr = self._run_command(
                ['git', 'checkout', '-b', 'main'])
            if returncode != 0:
                print(f'Error:  {stderr}')
                sys.exit(1)
        elif current_branch != 'main':
            # Rename current branch to main
            print(f"Renaming '{current_branch}' to 'main'...")
            returncode, _, stderr = self._run_command(
                ['git', 'branch', '-M', 'main'])
            if returncode != 0:
                print(f'Error: {stderr}')
                sys.exit(1)

        print("✓ Using 'main' branch")

    def _copy_gitignore(self):
        """Copy .gitignore from home directory if it exists."""
        print('\n📄 Checking for .gitignore...')
        home_gitignore = self.home_dir / '.gitignore'
        local_gitignore = self.repo_dir / '.gitignore'

        if home_gitignore.exists():
            shutil.copy2(home_gitignore, local_gitignore)
            print(f'✓ .gitignore copied from {home_gitignore}')
        else:
            print(f'⚠️  Warning: {home_gitignore} not found')

    def _create_github_repo(self):
        """Create GitHub repository if it doesn't exist."""
        print(f"\n🌐 Creating GitHub repository '{self.repo_name}'...")

        if self._repo_exists_on_github():
            print(f"✓ Repository '{self.repo_name}' already exists on GitHub")
            return

        returncode, stdout, stderr = self._run_command([
            'gh',
            'repo',
            'create',
            self.repo_name,
            '--source=.',
            '--remote=origin',
            '--public',
            '--push=false',
        ])

        if returncode != 0:
            print(f'Error creating repository: {stderr}')
            sys.exit(1)

        print(f"✓ Repository '{self.repo_name}' created on GitHub")

    def _stage_changes(self):
        """Stage all changes."""
        print('\n📝 Staging all changes...')
        returncode, _, stderr = self._run_command(['git', 'add', '-A'])
        if returncode != 0:
            print(f'Error:  {stderr}')
            sys.exit(1)
        print('✓ Changes staged')

    def _commit_changes(self):
        """Commit changes with current date and time."""
        print('\n💾 Checking for changes to commit...')

        # Check if there are changes
        returncode, _, _ = self._run_command(
            ['git', 'diff', '--cached', '--quiet'])

        if returncode == 0:
            # No changes to commit
            print('⚠️  Nothing to commit')
            return False

        # Create commit message with current date and time
        commit_msg = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Committing with message: '{commit_msg}'")

        returncode, _, stderr = self._run_command(
            ['git', 'commit', '-m', commit_msg])
        if returncode != 0:
            print(f'Error: {stderr}')
            sys.exit(1)

        print('✓ Changes committed')
        return True

    def _push_to_github(self):
        """Push to GitHub."""
        print('\n🚀 Pushing to GitHub...')
        returncode, stdout, stderr = self._run_command(
            ['git', 'push', '-u', 'origin', 'main'])

        if returncode != 0:
            print(f'Error:  {stderr}')
            sys.exit(1)

        print('✓ Pushed to GitHub')

    def run(self):
        """Main execution method."""
        print('=' * 60)
        print('GitHub Repository Manager')
        print('=' * 60)
        print(f'Repository name: {self.repo_name}')
        print(f'Directory: {self.repo_dir}')
        print('=' * 60)

        # Execute workflow
        self._init_git_repo()
        self._ensure_main_branch()
        self._copy_gitignore()
        self._create_github_repo()
        self._stage_changes()
        self._commit_changes()
        self._push_to_github()

        print('\n' + '=' * 60)
        print('✅ Done.  Repository pushed to GitHub.')
        print(f'📍 https://github.com/uno2os3es/{self.repo_name}')
        print('=' * 60)


def main():
    """Main entry point."""
    try:
        manager = GitHubRepoManager()
        manager.run()
    except KeyboardInterrupt:
        print('\n\nExiting...')
        sys.exit(0)
    except Exception as e:
        print(f'\n❌ Unexpected error: {e}')
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
