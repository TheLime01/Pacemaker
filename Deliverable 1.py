#make it a bit more user friendly - look wise - spacing, font sizing
# bradycardia report- shows mode and only parameters that apply
#save button saves new mode too

from tkinter import *
import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import subprocess

############################## Variables ##############################

Device_model = "Pacemaker"
Device_serial_number = "HOOO25"
DCM_serial_number = "400325598"
Model_number = "ABCD"
Version_number = "1.0"

# programable paramters [1=lower limit, 2=nominal, 3=upper limit, 4=temporary paramater, 5=permanent parameter]
Lower_Rate_Limit = [30,60,175,60,60] #ppm
Upper_Rate_Limit = [50,120,175,120,120] #ppm
Atrial_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Atrial_Pules_Width = [0.05,0.4,1.9,0.4,0.4] #ms
Ventricular_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Ventricular_Pulse_Width = [0.05,0.4,1.9,0.4,0.4] #ms
VRP = [150,320,500,320,320] #ms
ARP = [150,250,500,250,250] #ms


parameter_values = {
    "Lower Rate Limit": [30, 60, 175, 60, 60],
    "Upper Rate Limit": [50, 120, 175, 120, 120],
    "Atrial Amplitude": [0.5, 3.5, 7.0, 3.5, 3.5],
    "Atrial Pules Width": [0.05, 0.4, 1.9, 0.4, 0.4],
    "Ventricular Amplitude": [0.5, 3.5, 7.0, 3.5, 3.5],
    "Ventricular Pulse Width": [0.05, 0.4, 1.9, 0.4, 0.4],
    "VRP": [150, 320, 500, 320, 320],
    "ARP": [150, 250, 500, 250, 250]
}


# Constants
Modes = ["AOO","VOO", "AAI", "VVI"]
Programmable_Parameters = ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude","Atrial Pules Width",
                         "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "ARP"]

Mode_Parameters = [[True,True,True,True,False,False,False,False],
                   [True,True,False,False,True,True,False,False],
                   [True,True,True,True,False,False,False,True],
                   [True,True,False,False,True,True,True,False]]

Parameters_Units = [" ppm", " ppm", " V", " ms", " V", " ms", " ms", " ms"]

mode_parameters = {
    "AOO": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pules Width"],
    "VOO": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width"],
    "AAI": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pules Width", "ARP"],
    "VVI": ["Lower Rate_Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse_Width", "VRP"]
    }




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
    Software_Revision_Number = Label(About_window, text = "Software Revision Number: Version " + Version_number, font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Software_Revision_Number.place(x=10, y=40) #Displays software revision number text
    DCM_Serial_Number = Label(About_window, text = "DCM Serial Number: " + DCM_serial_number, font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    DCM_Serial_Number.place(x=10, y=70) #Displays DCM serial number text
    Institution_Name = Label(About_window, text = "Institution Name: McMaster University", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Institution_Name.place(x=10, y=100) #Displays institution name text

    About_window.mainloop() #Displays the about window

def About_2():
    About_window = Toplevel() #Initiates about window
    About_window.geometry("360x180")
    About_window.title("About") #Sets title

    Model_Number = Label(About_window, text = "Model Number: " + Model_number, font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Model_Number.place(x=10, y=10) #Displays model number text
    Software_Revision_Number = Label(About_window, text = "Software Revision Number: Version " + Version_number, font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Software_Revision_Number.place(x=10, y=40) #Displays software revision number text
    DCM_Serial_Number = Label(About_window, text = "DCM Serial Number: " + DCM_serial_number, font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    DCM_Serial_Number.place(x=10, y=70) #Displays DCM serial number text
    Institution_Name = Label(About_window, text = "Institution Name: McMaster University", font = ('Arial', 14), fg = 'black', bg = "white") #Sets text settings
    Institution_Name.place(x=10, y=100) #Displays institution name text

    About_window.mainloop() #Displays the about window

def Get_input(): #Get username and password and returns it
    Username_input = Username_box.get()
    Password_input = Password_box.get()
    return Username_input, Password_input

def Verify_account(username, password): #Check if username and password is correct
    userdata_exists()
    with open("userdata.json", "r") as file:
        data = json.load(file) 
    for user in data['registered users']:
        if username.strip() == user['username'] and password.strip() == user['password']:
            return True
    return False

def Successful_login(): #Gives access to my account page
    Window.destroy(); #Close main window
    global root
    root = tk.Tk() #Open new window
    root.title("My Account")
    root.geometry("1080x1080")
    root.config(background = "#CBC3E3") #Sets colour of background

    About_button = Button(root, text = "About", font = ('Arial', 16), fg = 'black', bg = "white") #Sets text settings
    About_button.place(x=15, y=15) #Displays about button
    About_button.config(command = About_2) #Sets button to about function

    combo_box_create() #makes the drop-down menu to choose mode
    initializes_sliders() #makes all the sliders
    select_mode(None) #sets the starting mode (AOO) with correct states of sliders
    update_temp_values() #keeps updating the values in the slides

    save_button = Button(root, text="Save", command=save_parameters)
    save_button.place(x=525, y=300)
    Button(root, text="Print Parameters", command=print_parameters).place(x=495, y=350)
    temp_report_button = Button(root, text="Temporary Report", command=lambda:export_report("Temporary"))
    temp_report_button.place(x=490, y=400)
    Bradycardia_report_button = Button(root, text="Bradycardia Report", command=lambda:export_report("Bradycardia"))
    Bradycardia_report_button.place(x=490, y=450)

def combo_box_create(): #function to make dropdown menu
    
    root.title("Modes")
    global label
    label = tk.Label(root, text = "Selected Mode: ", font = ('Arial', 14), fg = 'black')
    label.place(x=450, y=90)

    global combo_box 
    combo_box = ttk.Combobox(root, values = Modes, state = 'readonly', font = ('Arial', 11)) #fills combo box with mode, and user can read only 
    combo_box.place(x=450, y=130)

    combo_box.set("AOO") #default state
    
    combo_box.bind("<<ComboboxSelected>>", select_mode) #when user selects a mode - select mode is called, which updates the sliders



def select_mode(event): #updates sliders - according to mode
    
    global selected_mode
    
    selected_mode = combo_box.get() #gets current mode from combo box
    
    label.config(text="Selected Mode: " + selected_mode)

    allowed = mode_parameters[selected_mode] #get the parameters that are relevent to the mode

    for param, (scale, entry, var) in sliders.items():
        if param in allowed: # if the parameter is in the current mode make available, else no
            scale.config(state="normal")
            entry.config(state="normal")
        else:
            scale.config(state="disabled")
            entry.config(state="disabled")



def create_slider_with_entry(parent, label, from_, to, x, y, initial): #can type in entry for slider

    var = tk.DoubleVar(value=initial) #creates a double int and initializes it to nominal value

    tk.Label(parent, text=label).place(x=x, y=y) #puts parameter name above the slider

    scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=0.01, variable=var, showvalue=False, length=150)
    #resolution - step size of decimal
    #variable=var --> scale widget is linked to var, meaning moving the slider updates var automatically
    #hides the default value display
    #pixel length of the slider
    scale.place(x=x, y=y+20)

    #creates the box to type into
    entry = tk.Entry(parent, width=6)
    entry.place(x=x+180, y=y+30)
    entry.insert(0, str(initial)) #show the inital value

    #shows min and max values of the sliders
    tk.Label(parent, text=str(from_)).place(x=x, y=y+40) #min
    tk.Label(parent, text=str(to)).place(x=x+130, y=y+40) #max


    #when user types number into box
    def update_from_entry(event):
        try:
            val = float(entry.get()) #try coverting the text to number
            if from_ <= val <= to: #can only be within the range
                var.set(val) #update value
            else:
                print("Error")
            
            
        except ValueError:
            print("Error")

    #when user hits enter or clicks out - updates slider
    entry.bind("<Return>", update_from_entry)
    entry.bind("<FocusOut>", update_from_entry)


    #when slider moves - update box to show current value
    def update_from_scale(*args): #called whenever the slider's value changes
        entry.delete(0, tk.END) #clears entry box
        entry.insert(0, str(round(var.get(), 2)))  #inserts new number to 2 decimal places

    var.trace_add("write", update_from_scale) #when sliders value changes - call function to update box

    return scale, entry, var #return scale, entry box and the shared value


def initializes_sliders(): #initializes all the sliders

    global sliders 

    sliders = {}

    #(parent, label, min value, max value, x pos, y pos, nominal value)
    sliders["Lower Rate Limit"] = create_slider_with_entry(root, "Lower Rate Limit", 30, 180, 150, 220, 60)
    sliders["Upper Rate Limit"] = create_slider_with_entry(root, "Upper Rate Limit", 50, 200, 150, 300, 120)
    sliders["Atrial Amplitude"] = create_slider_with_entry(root, "Atrial Amplitude", 0.5, 5.0, 150, 380, 3.5)
    sliders["Atrial Pules Width"] = create_slider_with_entry(root, "Atrial Pules Width", 0.05, 1.9, 150, 460, 0.4)
    sliders["Ventricular Amplitude"] = create_slider_with_entry(root, "Ventricular Amplitude", 0.5, 5.0, 710, 220, 3.5)
    sliders["Ventricular Pulse Width"] = create_slider_with_entry(root, "Ventricular Pulse Width", 0.05, 1.9, 710, 300, 0.4)
    sliders["VRP"] = create_slider_with_entry(root, "VRP", 150, 500, 710, 380, 320)
    sliders["ARP"] = create_slider_with_entry(root, "ARP", 150, 500, 710, 460, 250)


def update_temp_values():
    for param, (scale, entry, var) in sliders.items(): #loop through sliders
        parameter_values[param][3] = var.get() #get the value for slider and put it in the temp place
        
    root.after(500, update_temp_values) #continuously calls this function to update temp values

def save_parameters():
    for param in parameter_values:
        parameter_values[param][4] = parameter_values[param][3]  #save temp as permanent

def print_parameters():
    print(f"\nParameters for mode {selected_mode}:")
    for param in mode_parameters[selected_mode]:
        print(f"{param}: {parameter_values[param][4]}")

# creates a new report of the type given (Bradycardia or Temporary)
def export_report(type: str):

    # saves current time and labels the output file
    current_datetime = datetime.now()
    file_name = type + "_Report-" + current_datetime.strftime("%Y-%m-%d-%H-%M-%S") + ".txt"

    # uses i to output temp or brady paramaters
    i = 3
    if type == "Bradycardia":
        i = 4

    # writes report
    with open(file_name, 'w') as file:
        file.write(type + " Parameters Report"+
                   "\nDate: " + current_datetime.strftime("%Y/%M/%D %H:%M:%S")+
                   "\nDevice Model: "+ Device_model+
                    "\nSerial Number: "+ Device_serial_number+
                    "\nDCM Serial Number: "+ DCM_serial_number+
                    "\nApplication Model: "+ Model_number+
                    "\nVersion Number: "+ Version_number+
                    "\n----------------------------------"
                    "\n"+ type + " Parameters: "+
                    "\n"+ "\t" + Programmable_Parameters[0]+ ": "+ str(Lower_Rate_Limit[i]) + Parameters_Units[0]+
                    "\n"+ "\t" + Programmable_Parameters[1]+ ": "+ str(Upper_Rate_Limit[i]) + Parameters_Units[1]+
                    "\n"+ "\t" + Programmable_Parameters[2]+ ": "+ str(Atrial_Amplitude[i]) + Parameters_Units[2]+
                    "\n"+ "\t" + Programmable_Parameters[3]+ ": "+ str(Atrial_Pules_Width[i]) + Parameters_Units[3]+
                    "\n"+ "\t" + Programmable_Parameters[4]+ ": "+ str(Ventricular_Amplitude[i]) + Parameters_Units[4]+
                    "\n"+ "\t" + Programmable_Parameters[5]+ ": "+ str(Ventricular_Pulse_Width[i]) + Parameters_Units[5]+
                    "\n"+ "\t" + Programmable_Parameters[6]+ ": "+ str(VRP[i]) + Parameters_Units[6]+
                    "\n"+ "\t" + Programmable_Parameters[7]+ ": "+ str(ARP[i]) + Parameters_Units[7]
      )
        
    subprocess.Popen(["notepad.exe",file_name])
    #return file_name

# check is userdata.json file exists, creates empty one f not
def userdata_exists():
    try:
        with open("userdata.json", 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {
            "registered users": []
            }  
        with open("userdata.json", 'w') as file:
            json.dump(data, file, indent=4)

def Add_new_user(username, password): #Checks sign up conditions and if it's all correct then signs up the user
    userdata_exists()
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
    
def Sign_in(): #Gets username and password and verifies if it's correct
    Username_input, Password_input = Get_input()
    Verify = Verify_account(Username_input, Password_input)
    if (Verify == True):
        Successful_login()
    else:
        Sign_in_label = Label(Window, text = "Incorrect username/password", font = ('Arial', 14), fg = 'black', bg = "#CBC3E3") #Sets text settings
        Sign_in_label.place(x=395, y=425) #Displays sign in text
        Sign_in_label.after(3000, Sign_in_label.destroy) #Removes sign in text after some time

def Sign_up(): #Gets username and password and verifies sign up conditions
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
