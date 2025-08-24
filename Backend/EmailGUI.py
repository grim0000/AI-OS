import tkinter as tk
from tkinter import ttk, messagebox
import threading

class EmailSendDialog:
    def __init__(self, to_email="", subject="", body="", cc_email="", bcc_email=""):
        self.root = tk.Tk()
        self.root.title("Send Email")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"600x600+{x}+{y}")
        
        # Set minimum size
        self.root.minsize(500, 500)
        
        # Make window stay on top and ensure it's visible
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.root.grab_set()  # Make window modal
        
        # Add a border to make it more visible
        self.root.configure(bg='#f0f0f0')
        
        # Ensure window is on screen
        self.root.update_idletasks()
        if self.root.winfo_x() < 0 or self.root.winfo_y() < 0:
            self.root.geometry(f"600x600+100+100")
        
        # Variables
        self.to_email = tk.StringVar(value=to_email)
        self.subject = tk.StringVar(value=subject)
        self.cc_email = tk.StringVar(value=cc_email)
        self.bcc_email = tk.StringVar(value=bcc_email)
        self.body = body
        
        self.result = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Configure grid weights for the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for main frame
        main_frame.grid_rowconfigure(5, weight=1)  # Make body text area expandable
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Send Email", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # To Email
        ttk.Label(main_frame, text="To:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        to_entry = ttk.Entry(main_frame, textvariable=self.to_email, width=60)
        to_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Subject
        ttk.Label(main_frame, text="Subject:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        subject_entry = ttk.Entry(main_frame, textvariable=self.subject, width=60)
        subject_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # CC Email
        ttk.Label(main_frame, text="CC:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        cc_entry = ttk.Entry(main_frame, textvariable=self.cc_email, width=60)
        cc_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # BCC Email
        ttk.Label(main_frame, text="BCC:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        bcc_entry = ttk.Entry(main_frame, textvariable=self.bcc_email, width=60)
        bcc_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Body
        ttk.Label(main_frame, text="Message:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=(tk.NW), pady=5)
        
        # Create a frame for the text area with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        # Text area with scrollbar
        self.body_text = tk.Text(text_frame, height=15, width=60, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.body_text.yview)
        self.body_text.configure(yscrollcommand=scrollbar.set)
        
        self.body_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.body_text.insert(tk.END, self.body)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to send email")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Send button
        self.send_button = ttk.Button(button_frame, text="Send Email", command=self.send_email, style="Accent.TButton")
        self.send_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side=tk.LEFT)
        
        # Focus on first entry
        to_entry.focus()
        
        # Bind Enter key to send
        self.root.bind('<Return>', lambda e: self.send_email())
        self.root.bind('<Escape>', lambda e: self.cancel())
        
    def send_email(self):
        """Send the email"""
        # Get values
        to_email = self.to_email.get().strip()
        subject = self.subject.get().strip()
        cc_email = self.cc_email.get().strip()
        bcc_email = self.bcc_email.get().strip()
        body = self.body_text.get("1.0", tk.END).strip()
        
        # Validate
        if not to_email:
            messagebox.showerror("Error", "Please enter a recipient email address.")
            return
        
        if not subject:
            messagebox.showerror("Error", "Please enter a subject.")
            return
        
        if not body:
            messagebox.showerror("Error", "Please enter a message.")
            return
        
        # Disable send button and update status
        self.send_button.config(state='disabled')
        self.status_var.set("Authenticating with Gmail...")
        self.root.update()
        
        # Send email in a separate thread
        def send_thread():
            try:
                # Import here to avoid circular import
                from .GmailIntegration import gmail_integration
                
                # Update status
                self.root.after(0, lambda: self.status_var.set("Authenticating with Gmail..."))
                
                # First authenticate
                auth_result = gmail_integration.authenticate()
                if "successful" not in auth_result:
                    self.root.after(0, lambda: self.show_result(f"❌ Authentication failed: {auth_result}"))
                    return
                
                # Update status
                self.root.after(0, lambda: self.status_var.set("Sending email..."))
                
                # Send the email
                result = gmail_integration.send_email(to_email, subject, body, cc_email, bcc_email)
                
                # Show result in main thread
                self.root.after(0, lambda: self.show_result(result))
                
            except Exception as e:
                error_msg = f"Error sending email: {str(e)}"
                self.root.after(0, lambda: self.show_result(error_msg))
        
        threading.Thread(target=send_thread, daemon=True).start()
    
    def show_result(self, result):
        """Show the result of sending the email"""
        if "successfully" in result.lower():
            self.status_var.set("Email sent successfully!")
            messagebox.showinfo("Success", result)
            self.result = "success"
            self.root.destroy()
        else:
            self.status_var.set("Failed to send email")
            messagebox.showerror("Error", result)
            # Re-enable send button
            self.send_button.config(state='normal')
    
    def cancel(self):
        """Cancel sending email"""
        self.result = "cancelled"
        self.root.destroy()
    
    def run(self):
        """Run the dialog and return the result"""
        self.root.mainloop()
        return self.result

def open_email_gui(to_email="", subject="", body="", cc_email="", bcc_email=""):
    """Open the email GUI dialog"""
    dialog = EmailSendDialog(to_email, subject, body, cc_email, bcc_email)
    return dialog.run()
