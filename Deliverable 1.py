from tkinter import *
import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import subprocess

############################## Variables ##############################

Model_number = "ABCD"
DCM_serial_number = "400325598"

############################## Setup ##################################

Window = Tk() #Initiates a window
Window.geometry("1080x1080") #Sets size of the window
Window.title("Pacemaker") #Sets the title
Icon = PhotoImage(file = "C:/Users/emily/Downloads/Pacemaker Logo.png") #Sets the icon
Window.iconphoto(True, Icon) #Displays the icon
Window.config(background = "#CBC3E3") #Sets colour of background

############################## Functions ##############################

def About():
    About_window = Toplevel() #Initiates about window
    About_window.geometry("360x180")
    About_window.title("About") #Sets title

    Model_Number = Label(About_window, text = "Model Number: " + Model_number, font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Model_Number.place(x=10, y=10) #Displays model number text
    Software_Revision_Number = Label(About_window, text = "Software Revision Number: Version 1.0", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Software_Revision_Number.place(x=10, y=40) #Displays software revision number text
    DCM_Serial_Number = Label(About_window, text = "DCM Serial Number: " + DCM_serial_number, font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    DCM_Serial_Number.place(x=10, y=70) #Displays DCM serial number text
    Institution_Name = Label(About_window, text = "Institution Name: McMaster University", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Institution_Name.place(x=10, y=100) #Displays institution name text

    About_window.mainloop() #Displays the about window

def Get_input():
    Username_input = Username_box.get()
    Password_input = Password_box.get()
    return Username_input, Password_input

def Verify_account(username, password):
    with open("userdata.json", "r") as file:
        data = json.load(file) 
    for user in data['registered users']:
        if username.strip() == user['username'] and password.strip() == user['password']:
            return True
    return False

def Successful_login(): #function
    Window.destroy(); #close main window
    login = tk.Tk();
    login.title("My Account");
    login.geometry("1080x1080");
    login.mainloop();
    
def Add_new_user(username, password):
    with open("userdata.json", "r") as file:
        data = json.load(file) 
    if len(data['registered users']) > 10:
        return False, "User list at capacity."
    new_user = {
        "username": username.strip(),
        "password": password.strip()
    }
    if len(new_user['username']) < 6 or len(new_user['password']) < 6:
        return False, "Username & password must be at least 6 characters."
    elif len(new_user['username']) > 25 or len(new_user['password']) > 25:
        return False, "Username & password cannot exceed 25 characters."
    for user in data['registered users']:
        if new_user['username'] == user['username']:
            return False, "Username already taken, please try again."
    data["registered users"].append(new_user)
    with open("userdata.json", "w") as file:
        json.dump(data, file, indent=4)
        return True, "New user added, please sign in!"
    
def Sign_in():
    Username_input, Password_input = Get_input()
    Verify = Verify_account(Username_input, Password_input)
    if (Verify == True):
        Successful_login()
    else:
        Sign_in_label2 = Label(Window, text = "Incorrect username/password", font = ('Arial', 14), fg = 'black', bg = "#CBC3E3") #Sets text settings
        Sign_in_label2.place(x=395, y=425) #Displays sign in text
    #Sign_in_label = Label(Window, text = "Incorrect username/password", font = ('Arial', 14), fg = 'black', bg = "#CBC3E3") #Sets text settings
    #Sign_in_label.place(x=395, y=425) #Displays sign in text
    #Sign_in_label.after(3000, Sign_in_label.destroy) #Removes sign in text after some time

def Sign_up():
    Username_input, Password_input = Get_input()
    Verify, Message = Add_new_user(Username_input, Password_input)
    Sign_up_label = Label(Window, text = Message, font = ('Arial', 14), fg = 'black', bg = "#CBC3E3") #Sets text settings
    Sign_up_label.place(x=350, y=425) #Displays sign up text
    Sign_up_label.after(3000, Sign_up_label.destroy) #Removes sign up text after some time

def Connected():
    Not_Connected_button.after(10, Not_Connected_button.destroy)
    Connected_button = Button(Window, text = "Connected", font = ('Arial', 16), fg = 'black', bg = "white") #Sets button settings
    Connected_button.place(x=15, y=725) #Displays button
    Connected_button.config(command = Not_Connected) #Sets button to not connected function

def Not_Connected():
    Connected_button.after(10, Connected_button.destroy)
    Not_Connected_button = Button(Window, text = "Not Connected", font = ('Arial', 16), fg = 'black', bg = "white") #Sets button settings
    Not_Connected_button.place(x=15, y=725) #Displays button
    Not_Connected_button.config(command = Connected) #Sets button to connected function
    
def Quit():
    Window.destroy() #Quits window

############################## Widgets ##############################

#### Labels ####

Username_label = Label(Window, text = "Username", font = ('Arial', 16), fg = 'black', bg = "#CBC3E3") #Sets text settings
Username_label.place(x=345, y=500) #Displays username text
Password_label = Label(Window, text = "Password", font = ('Arial', 16), fg = 'black', bg = "#CBC3E3") #Sets text settings
Password_label.place(x=345, y=550) #Displays password text

#### Buttons ####

Welcome_button = Button(Window, text = "Welcome :)", font = ('Arial', 40), fg = 'black', bg = "white") #Sets text settings
Welcome_button.place(x=375, y=250) #Displays welcome text

About_button = Button(Window, text = "About", font = ('Arial', 16), fg = 'black', bg = "white") #Sets text settings
About_button.place(x=15, y=15) #Displays about button
About_button.config(command = About) #Sets button to about function

Sign_in_button = Button(Window, text = "Sign In", font = ('Arial', 14), fg = 'black', bg = "white") #Sets button settings
Sign_in_button.place(x=625, y=495) #Displays button
Sign_in_button.config(command = Sign_in) #Sets button to sign in function

Sign_up_button = Button(Window, text = "Sign Up", font = ('Arial', 14), fg = 'black', bg = "white") #Sets button settings
Sign_up_button.place(x=620, y=545) #Displays button
Sign_up_button.config(command = Sign_up) #Sets button to sign up function

Not_Connected_button = Button(Window, text = "Not Connected", font = ('Arial', 16), fg = 'black', bg = "white") #Sets button settings
Not_Connected_button.place(x=15, y=725) #Displays button
Not_Connected_button.config(command = Connected) #Sets button to connected function

Connected_button = Button(Window, text = "Connected", font = ('Arial', 16), fg = 'black', bg = "white") #Sets button settings

Quit_button = Button(Window, text = "Quit", font = ('Arial', 16), fg = 'black', bg = "white") #Sets text settings
Quit_button.place(x=1010, y=15) #Displays quit button
Quit_button.config(command = Quit) #Sets button to quit function

#### Entry Boxes ####

Username_box = Entry(Window); #Box for username input
Password_box = Entry(Window);  #Box for password input
Username_box.place(x=470, y=505); #Display username box
Password_box.place(x=470, y=555); #Display password box

############################## Main ##############################

Window.mainloop() #Displays the window
