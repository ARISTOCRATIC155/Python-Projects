import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ My Todo List ✨")
        self.root.geometry("550x600")
        self.root.configure(bg='#f0f8ff')
        
        # Color scheme
        self.colors = {
            'bg': '#f0f8ff',
            'header_bg': '#1e88e5',
            'header_fg': 'white',
            'completed': '#4caf50',
            'awaiting': '#ffc107',
            'overdue': '#f44336',
            'text_dark': '#333333',
            'text_light': '#666666',
            'white': '#ffffff',
            'border': '#bbdefb'
        }
        
        # Start with empty tasks
        self.tasks = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['header_bg'], height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        
        title_label = tk.Label(
            header_frame, 
            text="📋 MY TASKS 📋", 
            font=('Helvetica', 24, 'bold'),
            bg=self.colors['header_bg'],
            fg=self.colors['header_fg']
        )
        title_label.pack(pady=20)
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg=self.colors['bg'])
        input_frame.pack(fill='x', padx=20, pady=20)
        
        # Task Entry
        self.task_entry = tk.Entry(
            input_frame,
            font=('Helvetica', 14),
            bg=self.colors['white'],
            fg=self.colors['text_dark'],
            insertbackground=self.colors['header_bg'],
            relief='solid',
            bd=1
        )
        self.task_entry.pack(side='left', fill='x', expand=True, ipady=8)
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        # Add Button
        add_btn = tk.Button(
            input_frame,
            text="➕ ADD TASK",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['header_bg'],
            fg='white',
            relief='flat',
            padx=20,
            cursor='hand2',
            command=self.add_task
        )
        add_btn.pack(side='right', padx=(10, 0))
        
        # Due Date Frame
        date_frame = tk.Frame(self.root, bg=self.colors['bg'])
        date_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(
            date_frame,
            text="Due Date:",
            font=('Helvetica', 11),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(side='left', padx=(0, 10))
        
        self.due_date_entry = tk.Entry(
            date_frame,
            font=('Helvetica', 11),
            bg=self.colors['white'],
            fg=self.colors['text_light'],
            relief='solid',
            bd=1,
            width=15
        )
        self.due_date_entry.pack(side='left')
        self.due_date_entry.insert(0, "YYYY-MM-DD")
        self.due_date_entry.bind('<FocusIn>', self.clear_date_placeholder)
        self.due_date_entry.bind('<FocusOut>', self.restore_date_placeholder)
        
        tk.Label(
            date_frame,
            text="(optional)",
            font=('Helvetica', 9, 'italic'),
            bg=self.colors['bg'],
            fg=self.colors['text_light']
        ).pack(side='left', padx=(5, 0))
        
        # Filter Frame
        filter_frame = tk.Frame(self.root, bg=self.colors['bg'])
        filter_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(
            filter_frame,
            text="Show:",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(side='left')
        
        self.filter_var = tk.StringVar(value="all")
        filters = [
            ("All", "all"),
            ("Awaiting", "awaiting"),
            ("Completed", "completed"),
            ("Overdue", "overdue")
        ]
        
        for text, value in filters:
            rb = tk.Radiobutton(
                filter_frame,
                text=text,
                value=value,
                variable=self.filter_var,
                command=self.display_tasks,
                bg=self.colors['bg'],
                fg=self.colors['text_dark'],
                selectcolor=self.colors['white'],
                activebackground=self.colors['bg'],
                font=('Helvetica', 10)
            )
            rb.pack(side='left', padx=(15, 0))
        
        # Tasks Frame (Scrollable)
        self.canvas = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")
        
        # Footer
        footer_frame = tk.Frame(self.root, bg=self.colors['bg'])
        footer_frame.pack(fill='x', padx=20, pady=20)
        
        self.stats_label = tk.Label(
            footer_frame,
            text="",
            font=('Helvetica', 11, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        )
        self.stats_label.pack(side='left')
        
        clear_btn = tk.Button(
            footer_frame,
            text="🗑️ Clear Completed",
            font=('Helvetica', 11),
            bg=self.colors['white'],
            fg=self.colors['text_dark'],
            relief='solid',
            bd=1,
            cursor='hand2',
            command=self.clear_completed
        )
        clear_btn.pack(side='right')
        
        # Initial display
        self.display_tasks()
        
    def clear_date_placeholder(self, event):
        if self.due_date_entry.get() == "YYYY-MM-DD":
            self.due_date_entry.delete(0, tk.END)
            self.due_date_entry.config(fg=self.colors['text_dark'])
    
    def restore_date_placeholder(self, event):
        if not self.due_date_entry.get():
            self.due_date_entry.insert(0, "YYYY-MM-DD")
            self.due_date_entry.config(fg=self.colors['text_light'])
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        due_date = self.due_date_entry.get().strip()
        
        if task_text:
            if due_date == "YYYY-MM-DD" or not due_date:
                due_date = None
            
            task = {
                'text': task_text,
                'completed': False,
                'due_date': due_date,
                'created': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            self.tasks.append(task)
            self.task_entry.delete(0, tk.END)
            self.due_date_entry.delete(0, tk.END)
            self.due_date_entry.insert(0, "YYYY-MM-DD")
            self.due_date_entry.config(fg=self.colors['text_light'])
            self.display_tasks()
            self.save_tasks()
        else:
            messagebox.showwarning("⚠️ Warning", "Please enter a task!")
    
    def get_task_status(self, task):
        # SAFE access using .get() method
        if task.get('completed', False):
            return 'completed'
        
        due_date = task.get('due_date')
        if due_date:
            try:
                due = datetime.strptime(due_date, "%Y-%m-%d")
                today = datetime.now()
                if due.date() < today.date():
                    return 'overdue'
            except (ValueError, TypeError):
                pass
        
        return 'awaiting'
    
    def get_status_color(self, status):
        return {
            'completed': self.colors['completed'],
            'awaiting': self.colors['awaiting'],
            'overdue': self.colors['overdue']
        }.get(status, self.colors['white'])
    
    def toggle_task(self, index):
        self.tasks[index]['completed'] = not self.tasks[index]['completed']
        self.display_tasks()
        self.save_tasks()
    
    def delete_task(self, index):
        if messagebox.askyesno("🗑️ Confirm Delete", "Delete this task?"):
            del self.tasks[index]
            self.display_tasks()
            self.save_tasks()
    
    def clear_completed(self):
        self.tasks = [task for task in self.tasks if not task.get('completed', False)]
        self.display_tasks()
        self.save_tasks()
    
    def display_tasks(self):
        # Clear current tasks
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Filter tasks
        filter_by = self.filter_var.get()
        filtered_tasks = []
        
        for i, task in enumerate(self.tasks):
            status = self.get_task_status(task)
            
            if filter_by == "all":
                filtered_tasks.append((i, task, status))
            elif filter_by == "completed" and status == 'completed':
                filtered_tasks.append((i, task, status))
            elif filter_by == "awaiting" and status == 'awaiting':
                filtered_tasks.append((i, task, status))
            elif filter_by == "overdue" and status == 'overdue':
                filtered_tasks.append((i, task, status))
        
        # Display tasks
        for idx, (original_idx, task, status) in enumerate(filtered_tasks):
            status_color = self.get_status_color(status)
            
            # Task card frame
            task_frame = tk.Frame(
                self.scrollable_frame,
                bg=self.colors['white'],
                relief='solid',
                bd=1,
                highlightbackground=self.colors['border'],
                highlightcolor=self.colors['border'],
                highlightthickness=1
            )
            task_frame.pack(fill='x', pady=5, ipady=8)
            
            # Status indicator (colored stripe)
            status_stripe = tk.Frame(
                task_frame,
                bg=status_color,
                width=5
            )
            status_stripe.pack(side='left', fill='y')
            
            # Content frame
            content_frame = tk.Frame(task_frame, bg=self.colors['white'])
            content_frame.pack(side='left', fill='both', expand=True, padx=(10, 5))
            
            # Top row: Checkbox and task text
            top_row = tk.Frame(content_frame, bg=self.colors['white'])
            top_row.pack(fill='x', pady=(0, 2))
            
            # Checkbox
            checkbox_text = "✅" if task.get('completed', False) else "⬜"
            checkbox = tk.Label(
                top_row,
                text=checkbox_text,
                font=('Helvetica', 14),
                bg=self.colors['white'],
                fg='black',
                cursor='hand2'
            )
            checkbox.pack(side='left', padx=(0, 8))
            checkbox.bind('<Button-1>', lambda e, idx=original_idx: self.toggle_task(idx))
            
            # Task text
            task_text = task.get('text', 'Unnamed task')
            if len(task_text) > 50:
                task_text = task_text[:47] + "..."
            
            text_color = self.colors['text_light'] if task.get('completed', False) else self.colors['text_dark']
            text_widget = tk.Label(
                top_row,
                text=task_text,
                font=('Helvetica', 12, 'overstrike' if task.get('completed', False) else 'normal'),
                bg=self.colors['white'],
                fg=text_color,
                wraplength=300,
                justify='left'
            )
            text_widget.pack(side='left', fill='x', expand=True)
            
            # Bottom row: Date info
            bottom_row = tk.Frame(content_frame, bg=self.colors['white'])
            bottom_row.pack(fill='x')
            
            # Status text
            status_text = f"Status: {status.capitalize()}"
            status_label = tk.Label(
                bottom_row,
                text=status_text,
                font=('Helvetica', 9, 'bold'),
                bg=self.colors['white'],
                fg=status_color
            )
            status_label.pack(side='left')
            
            # Due date
            due_date = task.get('due_date')
            if due_date:
                due_text = f"  |  Due: {due_date}"
                due_label = tk.Label(
                    bottom_row,
                    text=due_text,
                    font=('Helvetica', 9),
                    bg=self.colors['white'],
                    fg=self.colors['text_light']
                )
                due_label.pack(side='left')
            
            # Delete button
            delete_btn = tk.Label(
                task_frame,
                text="🗑️",
                font=('Helvetica', 14),
                bg=self.colors['white'],
                fg='#ff4444',
                cursor='hand2'
            )
            delete_btn.pack(side='right', padx=(5, 15))
            delete_btn.bind('<Button-1>', lambda e, idx=original_idx: self.delete_task(idx))
        
        # Update stats
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.get('completed', False))
        
        awaiting = 0
        overdue = 0
        
        for task in self.tasks:
            if not task.get('completed', False):
                due_date = task.get('due_date')
                if due_date:
                    try:
                        due = datetime.strptime(due_date, "%Y-%m-%d")
                        if due.date() < datetime.now().date():
                            overdue += 1
                        else:
                            awaiting += 1
                    except (ValueError, TypeError):
                        awaiting += 1
                else:
                    awaiting += 1
        
        stats_text = f"📊 Total: {total}  |  ✅ Completed: {completed}  |  ⏳ Awaiting: {awaiting}  |  ⚠️ Overdue: {overdue}"
        self.stats_label.config(text=stats_text)
        
        # Show empty message if no tasks
        if not filtered_tasks:
            empty_label = tk.Label(
                self.scrollable_frame,
                text="✨ No tasks to show. Add one above! ✨",
                font=('Helvetica', 14, 'italic'),
                bg=self.colors['bg'],
                fg=self.colors['text_light']
            )
            empty_label.pack(pady=50)
    
    def save_tasks(self):
        with open('my_tasks.json', 'w') as f:  # Different filename
            json.dump(self.tasks, f)
    
    # Removed load_tasks completely - starting fresh!

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()