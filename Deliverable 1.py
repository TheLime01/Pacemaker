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

# Constants
Modes = ["Off", "AOO","VOO", "AAI", "VVI"]
Programmable_Parameters = ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude","Atrial Pules Width",
                         "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "ARP"]
Mode_Parameters = [[False,False,False,False,False,False,False,False],
                   [True,True,True,True,False,False,False,False],
                   [True,True,False,False,True,True,False,False],
                   [True,True,True,True,False,False,False,True],
                   [True,True,False,False,True,True,True,False]]

Parameters_Units = [" ppm", " ppm", " V", " ms", " V", " ms", " ms", " ms"]

mode_parameters = {
    "Off": [" "],
    "AOO": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Atrial_Amplitude", "Atrial_Pules_Width"],
    "VOO": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Ventricular_Amplitude", "Ventricular_Pulse_Width"],
    "AAI": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Atrial_Amplitude", "Atrial_Pules_Width", "ARP"],
    "VVI": ["Lower_Rate_Limit", "Upper_Rate_Limit", "Ventricular_Amplitude", "Ventricular_Pulse_Width", "VRP"]
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

    About_button = Button(root, text = "About", font = ('Arial', 16), fg = 'black', bg = "white") #Sets text settings
    About_button.place(x=15, y=15) #Displays about button
    About_button.config(command = About_2) #Sets button to about function

    combo_box_create()
    scales()
    parameters(Modes[0])
    update_temp_values()
    save_button = Button(root, text="Save", command=save_parameters)
    save_button.pack(pady=20)
    Button(root, text="Print Parameters", command=print_parameters).pack()
    temp_report_button = Button(root, text="Temporary Report", command=lambda:export_report("Temporary"))
    temp_report_button.pack(pady=20)
    Bradycardia_report_button = Button(root, text="Bradycardia Report", command=lambda:export_report("Bradycardia"))
    Bradycardia_report_button.pack(pady=20)
    
    root.mainloop()

def combo_box_create():
    root.title("Modes")
    global label
    label = tk.Label(root, text = "Selected Mode: ")
    label.pack(pady = 50)

    global combo_box
    combo_box = ttk.Combobox(root, values = Modes, state = 'readonly')
    combo_box.pack(pady = 10)

    combo_box.set("Off") #default state
    combo_box.bind("<<ComboboxSelected>>", select_mode) #allows user to select mode

def select_mode(event): #selects mode

    global selected_mode

    selected_mode = combo_box.get()
    label.config(text = "Selected Mode: " + selected_mode)
    parameters(selected_mode)

def scales():
    ##Making scales and setting it to default value

    #LowerRateLimit
    label_LowerRateLimit = Label(root, text = Programmable_Parameters[0]); 
    s_LowerRateLimit = Scale(root, from_=Lower_Rate_Limit[0], to=Lower_Rate_Limit[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_LowerRateLimit.set(Lower_Rate_Limit[1]); #sets lower rate limit to nominal value

    #UpperRateLimit
    label_UpperRateLimit = Label(root, text = Programmable_Parameters[1]); 
    s_UpperRateLimit = Scale(root, from_=Upper_Rate_Limit[0], to=Upper_Rate_Limit[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_UpperRateLimit.set(Upper_Rate_Limit[1]);

    #AtrialAmplitude
    label_AtrialAmplitude = Label(root, text = Programmable_Parameters[2]); 
    s_AtrialAmplitude = Scale(root, from_=Atrial_Amplitude[0], to=Atrial_Amplitude[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_AtrialAmplitude.set(Atrial_Amplitude[1]); 


    #AtrialPulesWidth
    label_AtrialPulesWidth = Label(root, text = Programmable_Parameters[3]); 
    s_AtrialPulesWidth = Scale(root, from_=Atrial_Pules_Width[0], to=Atrial_Pules_Width[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_AtrialPulesWidth.set(Atrial_Pules_Width[1]);

    #VentricularAmplitude
    label_VentricularAmplitude = Label(root, text = Programmable_Parameters[4]); 
    s_VentricularAmplitude = Scale(root, from_=Ventricular_Amplitude[0], to=Ventricular_Amplitude[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_VentricularAmplitude.set(Ventricular_Amplitude[1]);

    #VentricularPulseWidth
    label_VentricularPulseWidth = Label(root, text = Programmable_Parameters[5]); 
    s_VentricularPulseWidth = Scale(root, from_=Ventricular_Pulse_Width[0], to=Ventricular_Pulse_Width[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_VentricularPulseWidth.set(Ventricular_Pulse_Width[1]);

    #VRP
    label_VRP = Label(root, text = Programmable_Parameters[6]); 
    s_VRP = Scale(root, from_=VRP[0], to=VRP[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_VRP.set(VRP[1]);

    #ARP
    label_ARP = Label(root, text = Programmable_Parameters[7]); 
    s_ARP = Scale(root, from_=ARP[0], to=ARP[2], orient = HORIZONTAL); #creates scale from 0 to 100
    s_ARP.set(ARP[1]);

    #Puts scales into a list
    global sList
    sList = [s_LowerRateLimit, s_UpperRateLimit,s_AtrialAmplitude,s_AtrialPulesWidth,s_VentricularAmplitude,s_VentricularPulseWidth, s_VRP, s_ARP];

    #Puts labels into a list
    global lList
    lList = [label_LowerRateLimit, label_UpperRateLimit, label_AtrialAmplitude,label_AtrialPulesWidth,label_VentricularAmplitude, label_VentricularPulseWidth,
             label_VRP, label_ARP];
    
def parameters(selected_mode):

    match selected_mode:

        case "Off":
            mode = 0
        case "AOO":
            mode = 1

        case "VOO":
            mode = 2
        case "AAI":
            mode = 3
        case "VVI":
            mode = 4

    for i in range(8):
        if Mode_Parameters[mode][i]:
            sList[i].place(x=100, y=70+i*70)
            lList[i].place(x=100, y= 50+i*70)

        else:
            sList[i].place_forget()
            lList[i].place_forget()
            
def update_temp_values(): #updates value
    Lower_Rate_Limit[3] = sList[0].get()
    Upper_Rate_Limit[3] = sList[1].get()
    Atrial_Amplitude[3] = sList[2].get()
    Atrial_Pules_Width[3] = sList[3].get()
    Ventricular_Amplitude[3] = sList[4].get()
    Ventricular_Pulse_Width[3] = sList[5].get()
    VRP[3] = sList[6].get()
    ARP[3] = sList[7].get()

    root.after(500, update_temp_values); #updates every 0.5s

def save_parameters(): #saves parameters
    Lower_Rate_Limit[4] = Lower_Rate_Limit[3]
    Upper_Rate_Limit[4] = Upper_Rate_Limit[3]
    Atrial_Amplitude[4] = Atrial_Amplitude[3]
    Atrial_Pules_Width[4] = Atrial_Pules_Width[3]
    
    Ventricular_Amplitude[4] = Ventricular_Amplitude[3]
    Ventricular_Pulse_Width[4] = Ventricular_Pulse_Width[3]
    VRP[4] = VRP[3]
    ARP[4] = ARP[3]

def print_parameters():

    parameters = {
        "Lower_Rate_Limit": Lower_Rate_Limit[4],
        "Upper_Rate_Limit": Upper_Rate_Limit[4],
        "Atrial_Amplitude": Atrial_Amplitude[4],
        "Atrial_Pules_Width": Atrial_Pules_Width[4],
        "Ventricular_Amplitude": Ventricular_Amplitude[4],
        "Ventricular_Pulse_Width": Ventricular_Pulse_Width[4],
        "VRP": VRP[4],
        "ARP": ARP[4]

    }

    print(f"\nParameters for mode {selected_mode}:")
    for param in mode_parameters[selected_mode]:
        print(f"{param}: {parameters[param]}")

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






