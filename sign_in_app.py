import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import pandas as pd
import os

class StudentSignInApp:
    def __init__(self, master):
        # Set up main window
        self.master = master
        master.title("AI and Robotics Club Sign-In")
        master.geometry("1920x1080")  # Full-screen resolution

        # Path to the background image
        self.bg_image_path = "MDC Roboticts sign page.png"

        # Create and configure directory for daily logs
        self.directory = "daily_logs"
        os.makedirs(self.directory, exist_ok=True)

        # Load valid users from CSV
        self.valid_users = self.load_valid_users_from_csv(
            "Robotics Club Member Roster CSV.csv"
        )

        # Load and set background image
        self.load_background()

        # Create GUI elements
        self.create_widgets()

    def load_valid_users_from_csv(self, file_path):
        """Load valid user IDs from the specified CSV file"""
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()  # Clean column names
            if 'Student ID' not in df.columns:
                raise KeyError(
                    f"'Student ID' column not found in {file_path}. Available columns: {df.columns.tolist()}"
                )
            return set(df['Student ID'].astype(str))  # Convert IDs to strings for consistency
        except FileNotFoundError:
            messagebox.showerror("Error", f"{file_path} file not found!")
            return set()
        except KeyError as e:
            messagebox.showerror("Error", str(e))
            return set()

    def load_background(self):
        """Load the background image"""
        try:
            # Open and resize the image to fit the window size
            bg_image = Image.open(self.bg_image_path)
            bg_image = bg_image.resize((1920, 1080), Image.LANCZOS)

            # Convert to PhotoImage for Tkinter
            self.bg_image = ImageTk.PhotoImage(bg_image)

            # Create a label to display the background image
            self.bg_label = tk.Label(self.master, image=self.bg_image)
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background image: {e}")

    def daily_log_generation(self):
        """Generate or load daily log DataFrame"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.directory, f"{current_date}.csv")

        # If the file doesn't exist, create a new DataFrame and write it to CSV
        if not os.path.exists(file_path):
            df = pd.DataFrame(columns=["Student ID", "Status", "Date", "Time"])
            df.to_csv(file_path, index=False)

        # Load the DataFrame from the CSV file
        return pd.read_csv(file_path)

    def student_already_signed_in(self, df, student_id):
        """Check if student has already signed in today"""
        # Check if student is already signed in
        signed_in = df[(df['Student ID'] == student_id) & (df['Status'] == "Signed In")]
        return not signed_in.empty

    def log_student_sign_in(self, df, file_path, student_id, status="Signed In"):
        """Log student sign-in or sign-out to CSV file"""
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Add a new row for the sign-in or sign-out event
        new_row = pd.DataFrame({
            "Student ID": [student_id],
            "Status": [status],
            "Date": [current_date],
            "Time": [current_time]
        })

        # Append the new row to the DataFrame
        df = pd.concat([df, new_row], ignore_index=True)

        # Save the updated DataFrame back to the CSV file
        df.to_csv(file_path, index=False)

    def create_widgets(self):
        """Create GUI widgets"""
        # Title Label
        self.title_label = tk.Label(
            self.master,
            text="AI and Robotics Club Sign-In",
            font=("Helvetica", 24, "bold"),
            fg="black",  # Text color
            bg="white",  # Background color (box)
            borderwidth=2,
            relief="solid"
        )
        self.title_label.pack(pady=(20, 10))

        # Student ID Entry Label
        self.id_label = tk.Label(
            self.master,
            text="Enter Student ID:",
            fg="black",  # Text color
            bg="white",  # Background color (box)
            font=("Helvetica", 16),
            borderwidth=2,
            relief="solid"
        )
        self.id_label.pack()

        self.id_entry = tk.Entry(
            self.master,
            font=("Helvetica", 14),
            fg="black",  # Text color
            bg="white",  # Input background color
            justify='center',
            borderwidth=2,
            relief="solid"
        )
        self.id_entry.pack(pady=(5, 10), padx=50)
        self.id_entry.bind('<Return>', self.sign_in)  # Allow Enter key submission

        # Sign In Button
        self.signin_button = tk.Button(
            self.master,
            text="Sign In / Sign Out",
            command=self.sign_in,
            bg="black",  # Button background color
            fg="white",  # Button text color
            font=("Helvetica", 12, "bold"),
            activebackground="white",  # Hover background color
            activeforeground="black"   # Hover text color
        )
        self.signin_button.pack(pady=10)

        # Status Label
        self.status_label = tk.Label(
            self.master,
            text="",
            font=("Helvetica", 14),
            fg="black",  # Text color
            bg="white",  # Background color (box)
            borderwidth=2,
            relief="solid"
        )
        self.status_label.pack(pady=10)

    def sign_in(self, event=None):
        """Handle sign-in/sign-out process"""
        # Get student ID
        login = self.id_entry.get().strip()

        # Validate student ID
        if not login:
            self.status_label.config(text="Please enter a Student ID", fg='red')
            return

        if login not in self.valid_users:
            self.status_label.config(text="Please enter a valid STUDENT ID", fg='red')
            self.id_entry.delete(0, tk.END)
            return

        # Generate or load the daily log DataFrame
        daily_log_df = self.daily_log_generation()
        daily_log_file = os.path.join(self.directory, f"{datetime.now().strftime('%Y-%m-%d')}.csv")

        # Check if student has already signed in
        if self.student_already_signed_in(daily_log_df, login):
            # If already signed in, log out
            self.log_student_sign_in(daily_log_df, daily_log_file, login, "Signed Out")
            self.status_label.config(text="Thank you. You have been successfully logged out.", fg='green')
        else:
            # Log student sign-in
            self.log_student_sign_in(daily_log_df, daily_log_file, login, "Signed In")
            self.status_label.config(text="Thank you. You have been signed in.", fg='green')

        # Clear the input field and focus it again
        self.id_entry.delete(0, tk.END)
        self.id_entry.focus_set()

def main():
    root = tk.Tk()
    app = StudentSignInApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
