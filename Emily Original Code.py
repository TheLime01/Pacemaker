from tkinter import *

############################## Setup ##############################

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

    Model_Number = Label(About_window, text = "Model Number: ABCD", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Model_Number.place(x=10, y=10) #Displays model number text
    Software_Revision_Number = Label(About_window, text = "Software Revision Number: Version 1.0", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Software_Revision_Number.place(x=10, y=40) #Displays software revision number text
    DCM_Serial_Number = Label(About_window, text = "DCM Serial Number: ABCD", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    DCM_Serial_Number.place(x=10, y=70) #Displays DCM serial number text
    Institution_Name = Label(About_window, text = "Institution Name: McMaster University", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Institution_Name.place(x=10, y=100) #Displays institution name text

    About_window.mainloop() #Displays the about window
    
def Sign_in():
    Sign_in_label = Label(Window, text = "Incorrect username/password", font = ('Arial', 14), fg = 'black', bg = "#CBC3E3") #Sets text settings
    Sign_in_label.place(x=395, y=425) #Displays sign in text
    Sign_in_label.after(3000, Sign_in_label.destroy) #Removes sign in text after some time

def Sign_up():
    Sign_up_label = Label(Window, text = "Account created, sign in now", font = ('Arial', 14), fg = 'black', bg = "#CBC3E3") #Sets text settings
    Sign_up_label.place(x=400, y=425) #Displays sign up text
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
