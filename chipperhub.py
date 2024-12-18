from tkinter import *
from tkinter import messagebox
import customtkinter as ctk
import pyperclip
import mysql.connector
from mysql.connector import errors
import bcrypt  
import re
import os
import socket
import subprocess
import nmap



font1 = ('Helvetica', 23, 'bold')
font2 = ('Helvetica', 11)
font3 = ('Helvetica', 9)

#SQL
def initialize_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root"
	    
        )

        cursor = conn.cursor()
        create_database(cursor)
        create_table(cursor)

        return conn, cursor
    except mysql.connector.Error as e:
        print(f"Error during database connection: {e}")
        messagebox.showerror("Database Connection Error", "Unable to connect to the database.")
        return None, None

def create_database(cursor):
    try:
        cursor.execute("SHOW DATABASES")
        temp = cursor.fetchall()
        databases = [item[0] for item in temp]

        if "pbl_kel10" not in databases:
            cursor.execute("CREATE DATABASE pbl_kel10")
        cursor.execute("USE pbl_kel10")
    except mysql.connector.Error as e:
        print(f"Error creating database: {e}")
        messagebox.showerror("Creating Database Error", "Unable to create the database.")

def create_table(cursor):
    cursor.execute("SHOW TABLES")
    temp = cursor.fetchall()
    tables = [item[0] for item in temp]

    if "users" not in tables:
        cursor.execute("""CREATE TABLE users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(21) UNIQUE,
            password VARCHAR(60),
            fullName VARCHAR(50)
        )""")

def login(cursor, data):
    cursor.execute("SELECT password FROM users WHERE username = %s", (data["username"],))
    result = cursor.fetchone()

    if result is not None and bcrypt.checkpw(data["password"].encode('utf-8'), result[0].encode('utf-8')):
        return True 
    else:
        return False  

def register(cursor, conn, data):
    hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password, fullName) VALUES (%s, %s, %s)", 
                   (data["username"], hashed_password.decode('utf-8'), data["fullName"]))
    conn.commit()

#GUI
class StartScreen:
    def __init__(self, master):
        self.master = master
        self.master.title('Lobby [PBL-RKSA_KEL10]')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=500, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Welcome to', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=120, y=50)
        self.heading = Label(self.frame, text='Chipperhub', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=120, y=100)

        Button(self.frame, width=14, pady=7, text='Start', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.open_login_app).place(x=155, y=240)
        Button(self.frame, width=14, pady=7, text='About Us', bg='#ff69b4', fg='white', cursor='hand2',border=0, command=self.about_us_page).place(x=155, y=320)

    def open_login_app(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        LoginPage(self.master)

    def about_us_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        AboutUs(self.master)

class LoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title('Login')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Login', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=135, y=50)

        self.username_entry = Entry(self.frame, width=21, fg='black', border=0, bg="white", font=font2)
        self.username_entry.place(x=115, y=150)
        self.username_entry.insert(0, 'Username')
        self.username_entry.bind('<FocusIn>', self.on_enter)
        self.username_entry.bind('<FocusOut>', self.on_leave)

        Frame(self.frame, width=180, height=2, bg='black').place(x=115, y=175)

        self.password_entry = Entry(self.frame, width=21, fg='black', border=0, bg="white", font=font2)
        self.password_entry.place(x=115, y=205)
        self.password_entry.insert(0, 'Password')
        self.password_entry.bind('<FocusIn>', self.on_enter)
        self.password_entry.bind('<FocusOut>', self.on_leave)

        Frame(self.frame, width=180, height=2, bg='black').place(x=115, y=230)

        Button(self.frame, width=14, pady=7, text='Login', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.signin).place(x=150, y=290)
        Button(self.frame, width=17, pady=7, text='Back to Lobby', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.back_to_lobby).place(x=140, y=380)

        label = Label(self.frame, text="Don't have an account?", fg='black', bg='white')
        label.place(x=115, y=340)

        sign_up = Button(self.frame, width=6, text='Register', border=0, bg='white', cursor='hand2', fg='blue', command=self.open_register_page)
        sign_up.place(x=242, y=340)

    def on_enter(self, event):
        if event.widget.get() in ['Username', 'Password']:
            event.widget.delete(0, 'end')
            event.widget.config(fg='black', show='*' if event.widget == self.password_entry else '')

    def on_leave(self, event):
        if not event.widget.get():
            event.widget.insert(0, 'Username' if event.widget == self.username_entry else 'Password')
            event.widget.config(fg='grey', show='' if event.widget == self.password_entry else '')

    def signin(self):
        data = {}
        data["username"] = self.username_entry.get()
        data["password"] = self.password_entry.get()
        
        entered_username = self.username_entry.get().strip()
        entered_password = self.password_entry.get().strip()

        if not entered_username or not entered_password:
            messagebox.showerror("Login Failed", "Please fill a valid username and password.")
            self.open_login_page()  # Reopen the login page
            return

        if entered_username == 'Username' or entered_password == 'Password':
            messagebox.showerror("Login Failed", "Please fill a valid username and password.")
            return

        data = {"username": entered_username, "password": entered_password}
        result = login(cursor, data)

        if result:
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.frame.destroy()
            HomePage(self.master, username=entered_username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")

            self.open_login_page()

    def open_login_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        LoginPage(self.master)


    def open_register_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        RegisterPage(self.master)
    
    def back_to_lobby(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        StartScreen(self.master)        

class RegisterPage:
    def __init__(self, master):
        self.master = master
        self.master.title('Register Here')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)
        
        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Register', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=135, y=50)

        self.username_entry = Entry(self.frame, width=21, fg='black', border=0, bg="white", font=font2)
        self.username_entry.place(x=115, y=150)
        self.username_entry.insert(0, 'Create Username')
        self.username_entry.bind('<FocusIn>', self.on_enter)
        self.username_entry.bind('<FocusOut>', self.on_leave)

        Frame(self.frame, width=180, height=2, bg='black').place(x=115, y=175)

        self.password_entry = Entry(self.frame, width=21, fg='black', border=0, bg="white", font=font2)
        self.password_entry.place(x=115, y=205)
        self.password_entry.insert(0, 'Create Password')
        self.password_entry.bind('<FocusIn>', self.on_enter)
        self.password_entry.bind('<FocusOut>', self.on_leave)

        Frame(self.frame, width=180, height=2, bg='black').place(x=115, y=230)

        self.fullname_entry = Entry(self.frame, width=21, fg='black', border=0, bg="white", font=font2)
        self.fullname_entry.place(x=115, y=260)
        self.fullname_entry.insert(0, 'Enter Full Name')
        self.fullname_entry.bind('<FocusIn>', self.on_enter)
        self.fullname_entry.bind('<FocusOut>', self.on_leave)

        Frame(self.frame, width=180, height=2, bg='black').place(x=115, y=285)

        Button(self.frame, width=14, pady=7, text='Register', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.register).place(x=150, y=315)

        label = Label(self.frame, text="Already have an account?", fg='black', bg='white')
        label.place(x=113, y=365)

        sign_in = Button(self.frame, width=6, text='Login', border=0, bg='white', cursor='hand2', fg='blue', command=self.open_login_page)
        sign_in.place(x=251, y=365)

        self.username_entry.default_text = 'Create Username'
        self.password_entry.default_text = 'Create Password'
        self.fullname_entry.default_text = 'Enter Full Name'

    def on_enter(self, event):
        if event.widget.get() in ['Create Username', 'Create Password', 'Enter Full Name']:
            event.widget.delete(0, 'end')
            event.widget.config(fg='black', show='*' if event.widget == self.password_entry else '')

    def on_leave(self, event):
        if not event.widget.get():
            default_text = 'Create Username' if event.widget == self.username_entry else 'Create Password' if event.widget == self.password_entry else 'Enter Full Name'
            event.widget.insert(0, default_text)
            event.widget.config(fg='grey', show='' if event.widget == self.password_entry else '')

    def open_login_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        LoginPage(self.master)
    
    def open_register_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        RegisterPage(self.master)    

    def validate_password(self, password):
        # Buat cek pw ny 8 krkter ap g
        if len(password) < 8:
            return False, "Password harus memiliki setidaknya 8 karakter."

        # eini buat biar cek pw setidakny 1 angka
        if not re.search(r"\d", password):
            return False, "Password harus mengandung setidaknya satu angka."

        # ini cek stidknya pw 1 huruf
        if not re.search(r"[A-Za-z]", password):
            return False, "Password harus mengandung setidaknya satu huruf."

        # cek setidakny pw 1 krkter khusus
        if not re.search(r"[@$!%*?&]", password):
            return False, "Password harus mengandung setidaknya satu karakter khusus (@, $, !, %, *, ?, &)."

        # cek pw gbole ada spasii
        if " " in password:
            return False, "Password tidak boleh mengandung spasi."

        return True, "Password valid."

    def register(self):
        data = {}
        data["username"] = self.username_entry.get()
        data["password"] = self.password_entry.get()
        data["fullName"] = self.fullname_entry.get()

        default_username = self.username_entry.default_text
        default_password = self.password_entry.default_text
        default_fullname = self.fullname_entry.default_text

        entered_username = self.username_entry.get().strip()
        entered_password = self.password_entry.get().strip()
        entered_fullname = self.fullname_entry.get().strip()

        if not all([entered_username, entered_password, entered_fullname]) or \
           entered_username == default_username or entered_password == default_password or entered_fullname == default_fullname:
            messagebox.showerror("Registration Failed", "Please fill in all fields.")
            self.open_register_page()
            return

        # Validate password strength
        is_valid, message = self.validate_password(entered_password)
        if not is_valid:
            messagebox.showerror("Registration Failed", message)
            return

        try:
            data = {"username": entered_username, "password": entered_password, "fullName": entered_fullname}
            register(cursor, conn, data)

            messagebox.showinfo("Registration Successful", "Account has been successfully registered!")

            self.open_login_page()

        except errors.IntegrityError as e:
            if e.errno == 1062:  # MySQL error code for duplicate entry
                messagebox.showerror("Registration Failed", "Username already exists. Please choose another username.")
                self.open_register_page()

            else:
                messagebox.showerror("Registration Failed", f"An error occurred during registration: {e}")
        except Exception as e:
            messagebox.showerror("Registration Failed", f"An unexpected error occurred: {e}")

class HomePage:
    def __init__(self, master, username):
        self.master = master
        self.master.title('Home')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)
        self.username = username  # Store the username as an instance variable

        full_name = self.get_full_name()

        self.create_widgets(full_name)

    def create_widgets(self, full_name):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Welcome Home!', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=95, y=30)
        
        self.heading = Label(self.frame, text=f'Hello,', fg='#ff69b4', bg='white', font=font2)
        self.heading.place(x=20, y=110)
        self.heading = Label(self.frame, text=f'{full_name}!', bg='white', font=font2)
        self.heading.place(x=70, y=110)
        self.heading = Label(self.frame, text='Choose your options:', fg='#ff69b4', bg='white', font=font2)
        self.heading.place(x=20, y=150)

        Button(self.frame, width=14, pady=7, text='Tools', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.open_tools_page).place(x=155, y=200)
        Button(self.frame, width=14, pady=7, text='Exit', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.Exit).place(x=155, y=360)

    def open_tools_page(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        ToolsPage(self.master, username=self.username)

    def Exit(self):
        confirm = messagebox.askyesno("Exit Confirmation", "Are you sure want to Exit?")
        
        if confirm:
            messagebox.showinfo("Exit", "You have been successfully Exit.")
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.frame.destroy()
            LoginPage(self.master)

    def get_full_name(self):
        cursor.execute(f"SELECT fullName FROM users WHERE username = '{self.username}'")
        result = cursor.fetchone()
        return result[0] if result else "User"

class ToolsPage:
    def __init__(self, master, username):
        self.master = master
        self.master.title('Tools')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)
        self.username = username  # Store the username as an instance variable

        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Tools', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=160, y=50)

        # Tombol untuk Port Scanner
        Button(self.frame, width=16, pady=7, text='Port Scanner', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.open_port_scanner).place(x=147, y=140)

        # Tombol untuk Vulnerability Check
        Button(self.frame, width=16, pady=7, text='Vulnerability Check(under construction)', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.open_vulnerability_check).place(x=147, y=200)

        # Tombol untuk Substitution Chipper
        Button(self.frame, width=16, pady=7, text='Substitution Chipper', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.open_substitution_chipper).place(x=147, y=260)

        Button(self.frame, width=14, pady=7, text='Back', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.back_to_home).place(x=153, y=340)

    def back_to_home(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        HomePage(self.master, username=self.username)

    def open_port_scanner(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        PortScanner(self.master, username=self.username)

    def open_vulnerability_check(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        VulnerabilityCheck(self.master, username=self.username)

    def open_substitution_chipper(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        SubstitutionCipher(self.master, username=self.username)  # Pastikan Anda memiliki kelas SubstitutionChipper

class SubstitutionCipher:
    def __init__(self, master, username):
        self.master = master
        self.master.title('[Tools] Substitution Cipher')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)
        self.username = username

        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Substitution Cipher', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=40, y=20)

        Label(self.frame, text="Enter the text:", bg='white', font=font2).place(x=27, y=80)
        self.text_frame = Frame(self.frame, width=280, height=90, bg='black')
        self.text_frame.place(x=30, y=110)
        self.text_box = Text(self.text_frame, width=45, height=4, wrap=WORD, fg='black', borderwidth=2, relief="solid", bg="white", font=font2)
        self.paste_button = Button(self.frame, text="Paste", bg='white', fg='blue', cursor='hand2', border=0, command=self.paste_from_clipboard)
        self.paste_button.place(x=355, y=162)
        self.text_box.pack()

        Label(self.frame, text="Enter the shift value:", bg='white', font=font2).place(x=27, y=200)
        self.shift_frame = Frame(self.frame, width=180, height=30, bg='black')
        self.shift_frame.place(x=30, y=230)
        self.shift_box = Text(self.shift_frame, width=10, height=1, wrap=WORD, fg='black', borderwidth=2, relief="solid", bg="white", font=font2)
        self.shift_box.pack()

        Button(self.frame, width=14, pady=7, text='Encrypt', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.encrypt_text).place(x=30, y=270)
        Button(self.frame, width=14, pady=7, text='Clear', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.reset_fields).place(x=160, y=270)
        Button(self.frame, width=14, pady=7, text='Decrypt', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.decrypt_text).place(x=290, y=270)
        Button(self.frame, width=14, pady=7, text='Back', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.back_to_tools).place(x=160, y=445)

        Label(self.frame, text="Result:", bg='white', font=font2).place(x=27, y=320)
        self.result_frame = Frame(self.frame, width=280, height=90, bg='black')
        self.result_frame.place(x=30, y=350)
        self.result_box = Text(self.result_frame, width=45, height=4, wrap=WORD, fg='black', borderwidth=2, relief="solid", bg="white", font=font2)
        self.copy_button = Button(self.frame, text="Copy", bg='white', fg='blue', cursor='hand2', border=0, command=self.copy_to_clipboard)
        self.copy_button.place(x=357, y=402)
        self.result_box.pack()
        self.result_box.config(state=DISABLED)  # Make the result box read-only

    def paste_from_clipboard(self):
            clipboard_text = pyperclip.paste()
            self.text_box.delete(1.0, END)
            self.text_box.insert(END, clipboard_text)

    def copy_to_clipboard(self):
        # Copy text from the "Result:" text box to the clipboard.
        result_text = self.result_box.get("1.0", END)
        self.master.clipboard_clear()
        self.master.clipboard_append(result_text)
        self.master.update()  # Update the clipboard content

        if result_text.strip():  # Check if there is text to copy
            pyperclip.copy(result_text)
            messagebox.showinfo("Copy Successful", "Text copied to clipboard.")
        else:
            messagebox.showwarning("Copy Failed", "No text to copy.")

    def back_to_tools(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        ToolsPage(self.master, username=self.username)

    def reset_fields(self):
        #Reset the text fields for "Enter the text:" and "Results:".
        self.text_box.delete("1.0", END)
        self.shift_box.delete("1.0", END)
        self.result_box.config(state=NORMAL)
        self.result_box.delete("1.0", END)
        self.result_box.config(state=DISABLED)

    def reset_shift_field(self):
        self.shift_box.config(state=NORMAL)
        self.shift_box.delete(1.0, END)

    def encrypt_text(self):
        plaintext = self.text_box.get("1.0", "end-1c")  # Get the text from the text box
        
        if not plaintext:
            messagebox.showwarning("Encrypt Failed", "Please enter text to encrypt.")
            self.reset_shift_field()
            return

        shift = self.get_shift_value()

        if plaintext and shift is not None:
            encrypted_text = self.sub_encrypt(plaintext, shift)
            self.result_box.config(state=NORMAL)  # Enable editing temporarily
            self.result_box.delete(1.0, END)
            self.result_box.insert(END, encrypted_text)
            self.result_box.config(state=DISABLED)  # Make the result box read-only

    def decrypt_text(self):
        ciphertext = self.text_box.get("1.0", "end-1c")  # Get the text from the text box
        
        if not ciphertext:
            messagebox.showwarning("Decrypt Failed", "Please enter text to decrypt.")
            self.reset_shift_field()
            return
        
        shift = self.get_shift_value()

        if ciphertext and shift is not None:
            decrypted_text = self.sub_decrypt(ciphertext, shift)
            self.result_box.config(state=NORMAL)  # Enable editing temporarily
            self.result_box.delete(1.0, END)
            self.result_box.insert(END, decrypted_text)
            self.result_box.config(state=DISABLED)  # Make the result box read-only

    def get_shift_value(self):
        try:
            shift = int(self.shift_box.get("1.0", "end-1c"))  # Get the text from the text box
            return shift
        except ValueError:
            messagebox.showerror("Error", "Invalid shift value. Please enter a valid integer.")
            self.reset_shift_field()

    def sub_encrypt(self, plaintext, shift):
        encrypted_text = ''.join(self.shift_char(char, shift) for char in plaintext)
        return encrypted_text

    def sub_decrypt(self, ciphertext, shift):
        decrypted_text = ''.join(self.shift_char(char, -shift) for char in ciphertext)
        return decrypted_text

    def shift_char(self, char, shift):
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            return chr((ord(char) - start + shift) % 26 + start)
        else:
            return char
        
import nmap
from tkinter import *
from tkinter import messagebox

class PortScanner:
    def __init__(self, master, username):
        self.master = master
        self.master.title('[Tools] Port Scanner')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)
        self.username = username

        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Port Scanner', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=120, y=20)

        Label(self.frame, text="Enter the IP Address:", bg='white', font=font2).place(x=27, y=80)
        self.ip_entry = Entry(self.frame, width=30, fg='black', bg='white', font=font2)
        self.ip_entry.place(x=30, y=110)

        Button(self.frame, width=14, pady=7, text='Scan Ports', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.scan_ports).place(x=160, y=150)

        Label(self.frame, text="Results:", bg='white', font=font2).place(x=27, y=200)
        self.result_frame = Frame(self.frame, width=280, height=150, bg='black')
        self.result_frame.place(x=30, y=230)
        self.result_box = Text(self.result_frame, width=45, height=8, wrap=WORD, fg='black', 
                               borderwidth=2, relief="solid", bg="white", font=font2)
        self.result_box.pack()
        self.result_box.config(state=DISABLED)

        Button(self.frame, width=14, pady=7, text='Back', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.back_to_tools).place(x=160, y=400)

    def scan_ports(self):
        ip_address = self.ip_entry.get().strip()
        if not ip_address:
            messagebox.showerror("Error", "Please enter a valid IP address.")
            return

        self.result_box.config(state=NORMAL)
        self.result_box.delete(1.0, END)

        # Menggunakan nmap untuk memindai port
        nm = nmap.PortScanner()
        try:
            nm.scan(ip_address, '1-1024')  # Memindai port dari 1 hingga 1024
            open_ports = [port for port in nm[ip_address]['tcp'] if nm[ip_address]['tcp'][port]['state'] == 'open']
            
            if open_ports:
                result_text = f"Open ports on {ip_address}:\n" + "\n".join(map(str, open_ports))
            else:
                result_text = f"No open ports found on {ip_address}."
        except Exception as e:
            result_text = f"Error scanning ports: {str(e)}"

        self.result_box.insert(END, result_text)
        self.result_box.config(state=DISABLED)

    def back_to_tools(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        ToolsPage(self.master, username=self.username)


class VulnerabilityCheck:
    def __init__(self, master, username):
        self.master = master
        self.master.title('[Tools] Vulnerability Check')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)
        self.username = username

        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='Vulnerability Check', fg='#ff69b4', bg='white', font=font1)
        self.heading.place(x=80, y=20)

        Label(self.frame, text="Enter the IP Address:", bg='white', font=font2).place(x=27, y=80)
        self.ip_entry = Entry(self.frame, width=30, fg='black', bg='white', font=font2)
        self.ip_entry.place(x=30, y=110 )

        Button(self.frame, width=16, pady=7, text='Check Vulnerabilities', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.check_vulnerabilities).place(x=130, y=150)

        Label(self.frame, text="Results:", bg='white', font=font2).place(x=27, y=200)
        self.result_frame = Frame(self.frame, width=280, height=150, bg='black')
        self.result_frame.place(x=30, y=230)
        self.result_box = Text(self.result_frame, width=45, height=8, wrap=WORD, fg='black', 
                               borderwidth=2, relief="solid", bg="white", font=font2)
        self.result_box.pack()
        self.result_box.config(state=DISABLED)

        Button(self.frame, width=14, pady=7, text='Back', bg='#ff69b4', fg='white', 
               cursor='hand2', border=0, command=self.back_to_tools).place(x=160, y=400)

    def check_vulnerabilities(self):
        ip_address = self.ip_entry.get().strip()
        if not ip_address:
            messagebox.showerror("Error", "Please enter a valid IP address.")
            return

        self.result_box.config(state=NORMAL)
        self.result_box.delete(1.0, END)

        # Menggunakan nmap untuk memeriksa kerentanan
        nm = nmap.PortScanner()
        try:
            nm.scan(ip_address, arguments='--script=vuln')  # Menggunakan skrip Nmap untuk memeriksa kerentanan
            vulnerabilities = []
            for host in nm.all_hosts():
                for proto in nm[host]['tcp']:
                    if 'script' in nm[host]['tcp'][proto]:
                        vulnerabilities.append(nm[host]['tcp'][proto]['script'])

            if vulnerabilities:
                result_text = f"Vulnerabilities found on {ip_address}:\n" + "\n".join(vulnerabilities)
            else:
                result_text = f"No vulnerabilities found on {ip_address}."
        except Exception as e:
            result_text = f"Error checking vulnerabilities: {str(e)}"

        self.result_box.insert(END, result_text)
        self.result_box.config(state=DISABLED)

    def back_to_tools(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        ToolsPage(self.master, username=self.username)


class AboutUs:
    def __init__(self, master):
        self.master = master
        self.master.title('About Us')
        self.master.geometry('425x500+550+100')
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        self.frame = Frame(self.master, width=425, height=500, bg="white")
        self.frame.place(x=0, y=0)

        self.heading = Label(self.frame, text='PBL-RKSA_KEL10', bg='white', font=font1)
        self.heading.place(x=9, y=20)
        self.heading = Label(self.frame, text='Muhammad Rizqy Nur Faiz (4332401025)', bg='white', font=font2)
        self.heading.place(x=10, y=70)
        self.heading = Label(self.frame, text='Devi Natalya (4332401002) ', bg='white', font=font2)
        self.heading.place(x=10, y=100)
        self.heading = Label(self.frame, text='Gina Thasafiya (4332401003)', bg='white', font=font2)
        self.heading.place(x=10, y=130)
        self.heading = Label(self.frame, text='Nursyafika Wahyuni (4332401007)', bg='white', font=font2)
        self.heading.place(x=10, y=160)
        

        Button(self.frame, width=14, pady=7, text='Back', bg='#ff69b4', fg='white', cursor='hand2', border=0, command=self.back_to_start).place(x=155, y=320)

    def back_to_start(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
        StartScreen(self.master)

if __name__ == "__main__":
    try:
        conn, cursor = initialize_connection()
        root = Tk()
        app = StartScreen(root)
        root.mainloop()
    except Exception as e:
        print(f"Unexpected error: {e}")
        messagebox.showerror("Error", "An unexpected error occurred. Please check the logs.")
