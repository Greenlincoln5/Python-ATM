import tkinter as tk
from tkinter import messagebox
import csv
import datetime

# Load account data from CSV
def load_accounts(file_path='/Users/lincolngreen/PycharmProjects/MIS303-9/webscraper/.venv/lib/sample_accounts_v2.csv'):
    accounts = {}
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                accounts[row["Routing Number"]] = {
                    "pin": row["PIN"],
                    "balance": float(row["Balance"])
                }
    except FileNotFoundError:
        print(f"Account file '{file_path}' not found. Please check the file path.")
        return None
    return accounts

# Save account data back to CSV
def save_accounts(accounts, file_path='/Users/lincolngreen/PycharmProjects/MIS303-9/webscraper/.venv/lib/sample_accounts_v2.csv'):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Routing Number", "PIN", "Balance"])  # Header
        for routing_number, data in accounts.items():
            writer.writerow([routing_number, data["pin"], f"{data['balance']:.2f}"])

# Log transaction to CSV file
def log_transaction(routing_number, action, amount, balance, file='transaction_log.csv'):
    with open(file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([routing_number, action, f"${amount:.2f}", f"${balance:.2f}", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

# GUI class for ATM
class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Machine")
        self.root.geometry("400x400")
        self.accounts = load_accounts()
        if not self.accounts:
            messagebox.showerror("Error", "Unable to load accounts. Please check the CSV file.")
            self.root.destroy()
            return
        self.current_user = None

        # Create login screen
        self.create_login_screen()

    def create_login_screen(self):
        self.clear_window()

        tk.Label(self.root, text="ATM Login", font=('Helvetica', 16)).pack(pady=20)

        tk.Label(self.root, text="Routing Number:").pack()
        self.routing_entry = tk.Entry(self.root)
        self.routing_entry.pack(pady=5)

        tk.Label(self.root, text="PIN:").pack()
        self.pin_entry = tk.Entry(self.root, show="*")
        self.pin_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.authenticate_user).pack(pady=20)

    def create_main_menu(self):
        self.clear_window()
        tk.Label(self.root, text="ATM Menu", font=('Helvetica', 16)).pack(pady=20)

        tk.Button(self.root, text="Check Balance", command=self.show_balance).pack(pady=10)
        tk.Button(self.root, text="Deposit", command=self.deposit_money).pack(pady=10)
        tk.Button(self.root, text="Withdraw", command=self.withdraw_money).pack(pady=10)
        tk.Button(self.root, text="Transfer", command=self.transfer_money).pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.logout_user).pack(pady=20)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def authenticate_user(self):
        routing_number = self.routing_entry.get()
        pin = self.pin_entry.get()

        if routing_number in self.accounts and self.accounts[routing_number]['pin'] == pin:
            self.current_user = routing_number
            messagebox.showinfo("Login Success", "Login Successful!")
            log_transaction(self.current_user, "Login", 0, self.accounts[self.current_user]["balance"])
            self.create_main_menu()
        else:
            messagebox.showerror("Error", "Invalid routing number or PIN. Please try again.")

    def show_balance(self):
        balance = self.accounts[self.current_user]['balance']
        messagebox.showinfo("Balance", f"Your balance is: ${balance:.2f}")
        log_transaction(self.current_user, "Check Balance", 0, balance)

    def deposit_money(self):
        def perform_deposit():
            try:
                amount = float(deposit_entry.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Enter a positive amount.")
                else:
                    self.accounts[self.current_user]['balance'] += amount
                    save_accounts(self.accounts)
                    messagebox.showinfo("Success", f"${amount:.2f} deposited successfully!")
                    log_transaction(self.current_user, "Deposit", amount, self.accounts[self.current_user]['balance'])
                    deposit_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.")

        deposit_window = tk.Toplevel(self.root)
        deposit_window.title("Deposit Money")
        deposit_window.geometry("300x200")

        tk.Label(deposit_window, text="Enter amount to deposit:").pack(pady=20)
        deposit_entry = tk.Entry(deposit_window)
        deposit_entry.pack(pady=10)

        tk.Button(deposit_window, text="Deposit", command=perform_deposit).pack(pady=20)

    def withdraw_money(self):
        def perform_withdrawal():
            try:
                amount = float(withdraw_entry.get())
                balance = self.accounts[self.current_user]['balance']

                if amount > balance:
                    messagebox.showerror("Error", "Insufficient funds.")
                elif amount <= 0:
                    messagebox.showerror("Error", "Enter a positive amount.")
                else:
                    self.accounts[self.current_user]['balance'] -= amount
                    save_accounts(self.accounts)
                    messagebox.showinfo("Success", f"${amount:.2f} withdrawn successfully!")
                    log_transaction(self.current_user, "Withdraw", amount, self.accounts[self.current_user]['balance'])
                    withdraw_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.")

        withdraw_window = tk.Toplevel(self.root)
        withdraw_window.title("Withdraw Money")
        withdraw_window.geometry("300x200")

        tk.Label(withdraw_window, text="Enter amount to withdraw:").pack(pady=20)
        withdraw_entry = tk.Entry(withdraw_window)
        withdraw_entry.pack(pady=10)

        tk.Button(withdraw_window, text="Withdraw", command=perform_withdrawal).pack(pady=20)

    def transfer_money(self):
        def perform_transfer():
            recipient_routing = recipient_entry.get()
            try:
                amount = float(transfer_entry.get())
                sender_balance = self.accounts[self.current_user]['balance']

                if recipient_routing not in self.accounts:
                    messagebox.showerror("Error", "Recipient routing number not found.")
                elif amount > sender_balance:
                    messagebox.showerror("Error", "Insufficient funds for the transfer.")
                elif amount <= 0:
                    messagebox.showerror("Error", "Enter a positive amount.")
                else:
                    self.accounts[self.current_user]['balance'] -= amount
                    self.accounts[recipient_routing]['balance'] += amount
                    save_accounts(self.accounts)
                    messagebox.showinfo("Success", f"${amount:.2f} transferred successfully!")
                    log_transaction(self.current_user, f"Transfer to {recipient_routing}", amount, self.accounts[self.current_user]['balance'])
                    transfer_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.")

        transfer_window = tk.Toplevel(self.root)
        transfer_window.title("Transfer Money")
        transfer_window.geometry("300x250")

        tk.Label(transfer_window, text="Recipient's Routing Number:").pack(pady=10)
        recipient_entry = tk.Entry(transfer_window)
        recipient_entry.pack(pady=5)

        tk.Label(transfer_window, text="Amount to Transfer:").pack(pady=10)
        transfer_entry = tk.Entry(transfer_window)
        transfer_entry.pack(pady=5)

        tk.Button(transfer_window, text="Transfer", command=perform_transfer).pack(pady=20)

    def logout_user(self):
        messagebox.showinfo("Logout", "You have been logged out.")
        log_transaction(self.current_user, "Logout", 0, self.accounts[self.current_user]["balance"])
        self.current_user = None
        self.create_login_screen()

# Main application execution
if __name__ == "__main__":
    root = tk.Tk()
    app = ATMApp(root)
    root.mainloop()
