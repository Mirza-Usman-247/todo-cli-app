"""CLI interface for Todo application"""
import sys
from typing import Optional

from src.services.todo_service import TodoService


class TodoCLI:
    """Interactive CLI for managing todos"""

    def __init__(self, db_path: str = "db/todos.json"):
        """Initialize CLI with TodoService.

        Args:
            db_path: Path to JSON database file
        """
        self.service = TodoService(db_path)

    def run(self) -> None:
        """Run the main CLI loop"""
        while True:
            self.show_menu()
            choice = self.get_menu_choice()

            if choice == 1:
                self.add_todo()
            elif choice == 2:
                self.view_all_todos()
            elif choice == 3:
                self.toggle_status()
            elif choice == 4:
                self.update_todo()
            elif choice == 5:
                self.delete_todo()
            elif choice == 6:
                self.exit_app()
                break

    def show_menu(self) -> None:
        """Display the main menu"""
        print("\n=== Todo CLI ===")
        print("1. Add Todo")
        print("2. View All Todos")
        print("3. Toggle Status")
        print("4. Update Todo")
        print("5. Delete Todo")
        print("6. Exit")
        print()

    def get_menu_choice(self) -> int:
        """Get and validate menu choice from user.

        Returns:
            Valid menu option (1-6)
        """
        while True:
            try:
                choice_str = input("Choose option: ").strip()
                choice = int(choice_str)

                if 1 <= choice <= 6:
                    return choice
                else:
                    print("Error: Invalid option. Please choose 1-6.")
            except ValueError:
                print("Error: Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
            except EOFError:
                print("\nGoodbye!")
                sys.exit(0)

    def add_todo(self) -> None:
        """Handle Add Todo command (option 1)"""
        try:
            # Get title
            title = input("Enter title: ").strip()
            if not title:
                print("Error: Title cannot be empty")
                return

            # Get description (optional)
            description = input("Enter description (optional): ").strip()

            # Create todo
            todo = self.service.create_todo(title, description)

            # Confirmation
            print(f"✓ Todo #{todo.id} created: {todo.title}")

        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nCancelled")
        except EOFError:
            print("\nCancelled")

    def view_all_todos(self) -> None:
        """Handle View All Todos command (option 2)"""
        todos = self.service.get_all_todos()

        if not todos:
            print("No todos found. Create one with option 1!")
            return

        print("\n=== Your Todos ===\n")

        for todo in todos:
            # Status indicator
            status_symbol = "✓" if todo.completed else "✗"

            # Description display
            desc_display = todo.description if todo.description else "(no description)"

            # Format output
            print(f"[{todo.id}] {status_symbol} {todo.title}")
            print(f"    {desc_display}")
            print(f"    Created: {self.format_timestamp(todo.created_at)}")
            print()

    def toggle_status(self) -> None:
        """Handle Toggle Status command (option 3)"""
        try:
            # Get ID
            todo_id = self.get_todo_id()
            if todo_id is None:
                return

            # Toggle
            todo = self.service.toggle_todo(todo_id)

            # Confirmation with status
            if todo.completed:
                print(f"✓ Todo #{todo.id} marked as complete: {todo.title}")
            else:
                print(f"✗ Todo #{todo.id} marked as incomplete: {todo.title}")

        except KeyError:
            print(f"Error: Todo with ID {todo_id} not found")
        except KeyboardInterrupt:
            print("\nCancelled")
        except EOFError:
            print("\nCancelled")

    def update_todo(self) -> None:
        """Handle Update Todo command (option 4)"""
        try:
            # Get ID
            todo_id = self.get_todo_id()
            if todo_id is None:
                return

            # Get current todo
            try:
                current_todo = self.service.get_todo_by_id(todo_id)
            except KeyError:
                print(f"Error: Todo with ID {todo_id} not found")
                return

            # Display current values
            print(f"Current: [{current_todo.id}] {current_todo.title} - {current_todo.description or '(no description)'}")
            print()

            # Get new title (optional - press Enter to keep)
            new_title_input = input(f'Enter new title (or press Enter to keep "{current_todo.title}"): ').strip()
            new_title = new_title_input if new_title_input else None

            # Get new description (optional - press Enter to keep)
            new_desc_input = input("Enter new description (or press Enter to keep current): ").strip()
            new_description = new_desc_input if new_desc_input else None

            # Update
            updated_todo = self.service.update_todo(todo_id, new_title, new_description)

            # Confirmation
            print(f"✓ Todo #{updated_todo.id} updated: {updated_todo.title}")

        except ValueError as e:
            print(f"Error: {e}")
        except KeyError:
            print(f"Error: Todo with ID {todo_id} not found")
        except KeyboardInterrupt:
            print("\nCancelled")
        except EOFError:
            print("\nCancelled")

    def delete_todo(self) -> None:
        """Handle Delete Todo command (option 5)"""
        try:
            # Get ID
            todo_id = self.get_todo_id()
            if todo_id is None:
                return

            # Delete
            deleted_todo = self.service.delete_todo(todo_id)

            # Confirmation
            print(f"✓ Todo #{deleted_todo.id} deleted: {deleted_todo.title}")

        except KeyError:
            print(f"Error: Todo with ID {todo_id} not found")
        except KeyboardInterrupt:
            print("\nCancelled")
        except EOFError:
            print("\nCancelled")

    def exit_app(self) -> None:
        """Handle Exit command (option 6)"""
        print("Goodbye!")

    def get_todo_id(self) -> Optional[int]:
        """Get and validate todo ID from user.

        Returns:
            Valid todo ID, or None if cancelled/invalid
        """
        try:
            id_str = input("Enter todo ID: ").strip()
            todo_id = int(id_str)
            return todo_id
        except ValueError:
            print("Error: Please enter a valid number")
            return None

    def format_timestamp(self, timestamp: str) -> str:
        """Format ISO 8601 timestamp for display.

        Args:
            timestamp: ISO 8601 formatted timestamp

        Returns:
            Human-readable timestamp (YYYY-MM-DD HH:MM:SS)
        """
        # Simple formatting - just remove timezone and 'T'
        # Input: 2026-01-01T10:30:00+00:00
        # Output: 2026-01-01 10:30:00
        try:
            # Remove timezone info
            if '+' in timestamp:
                timestamp = timestamp.split('+')[0]
            elif timestamp.endswith('Z'):
                timestamp = timestamp[:-1]

            # Replace T with space
            timestamp = timestamp.replace('T', ' ')

            # Truncate microseconds if present
            if '.' in timestamp:
                timestamp = timestamp.split('.')[0]

            return timestamp
        except Exception:
            return timestamp


def main():
    """Entry point for CLI application"""
    cli = TodoCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
