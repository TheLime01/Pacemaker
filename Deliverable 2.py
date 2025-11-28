
from tkinter import * #imports Tkiinter GUI classes/functions
import tkinter as tk 
from tkinter import ttk #imports some widgets(combobox)
import json #used for reading and writing files
from datetime import datetime #for timestamps in reports
import subprocess #allows launching Simulink
import serial #for serial communication
from serial.tools import list_ports #used to detect available COM ports
import time #for time delays 
import threading #for running background tasks
import struct #for packing and unpacking data (to send/receive info from pacemaker)
from collections import deque #buffer for incoming egram data
from matplotlib.figure import Figure #for creating the graphs
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os #used for file path creation 
from tkinter import font #used to change font sizes



'''
Off doesnt work properly doesnt save between uses
'''


'''
Parameters Name                              Range                     Increment

Lower Rate Limit                    [30, 60, 175, 60, 60]                  5                   
Upper Rate Limit                    [50, 120, 175, 120, 120]               5                   
Atrial Amplitude*                   [0.1, 5, 5, 5, 5]                     0.1                  
Atrial Pulse Width*                 [1, 1, 30, 1, 1]                       1                   
Ventricular Amplitude*              [0.1, 5, 5, 5, 5]                     0.1                  
Ventricular Pulse Width*            [1, 30, 1, 1, 1]                       1                   
VRP                                 [150, 320, 500, 320, 320]              10                  
ARP                                 [150, 250, 500, 250, 250]              10                  
Atrial Sensitivity**                [0, 0, 5, 0, 0]                       0.1                  
Ventricular Sensitivity**           [0, 0, 5, 0, 0]                       0.1                  



*adjusted for deliverable 2
**added for deliverable 2

AOO MODE 1 0 - STANDARD 1 - RATE ADAPTIVE - R
VOO MODE 2
VVI MODE 3
AAI MODE 4

'''

############################## Serial ##############################


class SerialMonitor:
    def __init__(self, param_mgr=None):
        self.lrl = "?"
        self.url = "?"
        self.atrial_amp = "?"
        self.atrial_pw = "?"
        self.ventricular_amp = "?"
        self.ventricular_pw = "?"
        self.vrp = "?"
        self.arp = "?"
        self.mode = "?"
        
        self.last_port = None  # Stores last connection
        self.Status = "Disconnected"  # Default status is disconnected
        self.Port_Description = "JLink CDC UART Port"  # Pacemaker description
        self.param_mgr = param_mgr  # <-- store reference

        # Start monitor thread (daemon so it won't block program exit)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.Monitor_ports, daemon=True)
        self.thread.start()

    def On_Connect(self, port):
        try:
            ser = serial.Serial(port, 115200, timeout=5)  # Connects serial
            print("Connected to", ser.name)
            ser.close()
        except serial.SerialException as e:
            print(f"Serial Port Error: {e}")
    
    def Monitor_ports(self):
        while not self.stop_event.is_set(): #Continuously checks
            ports = list(list_ports.comports()) #Collects and stores ports in a list
            pacemaker_port = None #Current pacemaker port set to none first

            #Looks only for the pacemaker device
            for p in ports:
                if self.Port_Description in p.description: #Checks each port description to see if there is a match
                    pacemaker_port = p.device #Stores the match
                    break

            #If Pacemaker is found
            if pacemaker_port:
                if pacemaker_port != self.last_port:  #Checks for new connection
                    try:
                        self.On_Connect(pacemaker_port) #Gets sent to serial
                        self.last_port = pacemaker_port #Stores the current port to check for changes
                    except Exception as e:
                        print("On_Connect error:", e)
                self.Status = "Connected"

            #If Pacemaker is not found
            else:
                if self.last_port is not None: #Checks if pacemaker was disconnected
                    print("Pacemaker disconnected")
                self.last_port = None
                self.Status = "Disconnected"
            time.sleep(1)

    def Write_Serial(self, param_mgr=None):
        pm = param_mgr or self.param_mgr  # <-- default to stored reference
        if pm is None:
            print("Write_Serial: No ParameterManager provided/attached.")
            return
        self.Packet_Serial(0x55, pm)
        try:
            ser = serial.Serial(self.last_port, 115200, timeout=1)
            time.sleep(2)
            ser.write(self.packet)
            ser.flush()
            print("Packet sent successfully.")
            ser.close()
        except serial.SerialException as e:
            print(f"Serial Port Error: {e}")
        

    def Packet_Serial(self, function_code, param_mgr=None):
        pm = param_mgr or self.param_mgr
        if pm is None:
            raise ValueError("Packet_Serial: ParameterManager is required")

        # Packet Parameters 
        self.Sync = 0x16
        self.FN_Code = function_code  # 0x55 setting params, 0x22 echo

        self.Lower_Rate_Limit = pm.parameter_values["Lower Rate Limit"][4]
        self.Upper_Rate_Limit = pm.parameter_values["Upper Rate Limit"][4]

        ################################################################### Off converts to 0 for pacemaker

        if pm.parameter_values["Atrial Amplitude"][5]:
            self.Atrial_Amplitude = 0.0

        else:
            self.Atrial_Amplitude = pm.parameter_values["Atrial Amplitude"][4]

            
        self.Atrial_Pulse_Width = pm.parameter_values["Atrial Pulse Width"][4]

        if pm.parameter_values["Ventricular Amplitude"][5]:
            self.Ventricular_Amplitude = 0.0

        else:
            self.Ventricular_Amplitude = pm.parameter_values["Ventricular Amplitude"][4]

        ############################################################################


        self.Ventricular_Pulse_Width = pm.parameter_values["Ventricular Pulse Width"][4]
        self.VRP = pm.parameter_values["VRP"][4]
        self.ARP = pm.parameter_values["ARP"][4]
        self.Atrial_Sensitivity    = pm.parameter_values["Atrial Sensitivity"][4]
        self.Ventricular_Sensitivity = pm.parameter_values["Ventricular Sensitivity"][4]
        
        self.actual_mode = pm.Mode[1]
        
        if self.actual_mode == "AOO":
            self.mode = 1
            self.adaptive_mode = 0
        elif self.actual_mode == "AOOR":
            self.mode = 1
            self.adaptive_mode = 1
        elif self.actual_mode == "VOO":
            self.mode = 2
            self.adaptive_mode = 0
        elif self.actual_mode == "VOOR":
            self.mode = 2
            self.adaptive_mode = 1
        elif self.actual_mode == "VVI":
            self.mode = 3
            self.adaptive_mode = 0
        elif self.actual_mode == "VVIR":
            self.mode = 3
            self.adaptive_mode = 1
        elif self.actual_mode == "AAI":
            self.mode = 4
            self.adaptive_mode = 0
        elif self.actual_mode == "AAIR":
            self.mode = 4
            self.adaptive_mode = 1


        # Build packet
        self.packet = struct.pack(
            "<BBdddddddddddd",
            int(self.Sync),
            int(self.FN_Code),
            float(self.Lower_Rate_Limit),
            float(self.Upper_Rate_Limit),
            float(self.Atrial_Amplitude),
            float(self.Atrial_Pulse_Width),
            float(self.Ventricular_Amplitude),
            float(self.Ventricular_Pulse_Width),
            float(self.VRP),
            float(self.ARP),
            float(self.Atrial_Sensitivity),
            float(self.Ventricular_Sensitivity),
            float(self.mode),
            float(self.adaptive_mode)
        )
        print(f"Packet ({len(self.packet)} bytes):", " ".join(f"{b:02X}" for b in self.packet))


    def Read_Device_Values(self):
        """
        Reads the current values from the pacemaker.
        Returns a dict with 12 fields (10 parameters + Atrial Data + Ventricle Data),
        or None if not connected or if the read fails.
        Does NOT update ParameterManager on its own.
        """
        if self.Status != "Connected" or self.last_port is None:
            print("Read_Device_Values: Device not connected.")
            return None

        # If device connected, attempt to read (reuse On_Connect logic)
        try:
            ser = serial.Serial(self.last_port, 115200, timeout=1)
            self.Packet_Serial(0x22, self.param_mgr)  # request current values
            ser.write(self.packet)
            ser.flush()
            #time.sleep(0.5)
           
            #Expect 96 bytes: 14 doubles => 10 params + atrial data + ventricle data
            response = ser.read(112)
            ser.close()
            if len(response) == 112:      
                unpacked = struct.unpack("<dddddddddddddd", response)
                (
                    mode,
                    ventricular_sens,
                    atrial_sens, 
                    vrp, 
                    arp,
                    ventricular_pw, 
                    atrial_pw,
                    ventricular_amp, 
                    atrial_amp,
                    url, 
                    lrl, 
                    adapt_data,
                    atrial_data, 
                    ventricle_data
                ) = unpacked

                return {
                    "Lower Rate Limit": lrl,
                    "Upper Rate Limit": url,
                    "Atrial Amplitude": atrial_amp,
                    "Atrial Pulse Width": atrial_pw,
                    "Ventricular Amplitude": ventricular_amp,
                    "Ventricular Pulse Width": ventricular_pw,
                    "VRP": vrp,
                    "ARP": arp,
                    "Atrial Sensitivity": atrial_sens,
                    "Ventricular Sensitivity": ventricular_sens,
                    "Atrial Data": atrial_data,
                    "Ventricle Data": ventricle_data,
                    "Mode": mode,
                    "Adaptive Data": adapt_data
                }
            else:
                print(f"Read_Device_Values: Incomplete response ({len(response)} bytes).")
                return None

        except serial.SerialException as e:
            print("Read_Device_Values Serial Error:", e)
            return None
        
    def stop(self):
        self.stop_event.set()




############################## Parameters / Data ##############################

class ParameterManager:


    def __init__(self, filename="parameters.json"):

        self.filename = os.path.join(os.path.dirname(__file__), "parameters.json") #file where parameter data is stored

        self.Device_model = "Pacemaker"
        self.Device_serial_number = "HOOO25"
        self.DCM_serial_number = "400325598"
        self.Model_number = "4230"
        self.Version_number = "1.0"

        # modes and each of their parameters
        self.Modes = ["AOO", "VOO", "AAI", "VVI", "AOOR", "VOOR", "AAIR", "VVIR"]
        self.Parameters_Units = [" ppm", " ppm", " V", " ms", " V", " ms", " ms", " ms", "mV", "mV"]
        self.mode_parameters = {
            "AOO": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width"],
            "VOO": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width"],
            "AAI": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width", "ARP", "Atrial Sensitivity"],
            "VVI": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "Ventricular Sensitivity"],
            "AOOR": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width"],
            "VOOR": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width"],
            "AAIR": ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude", "Atrial Pulse Width", "ARP", "Atrial Sensitivity"],
            "VVIR": ["Lower Rate Limit", "Upper Rate Limit", "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "Ventricular Sensitivity"]
        }

        # parameter values
        self.Mode = ["AOO", "AOO"]  #0=temporary paramater, 1=permanent parameter
        self.parameter_values = { #min, nominal, max, temp, permanent, toggle (false means on, true means off)
            "Lower Rate Limit": [30, 60, 175, 60, 60, False],
            "Upper Rate Limit": [50, 120, 175, 120, 120, False],
            "Atrial Amplitude": [0.1, 5, 5, 5, 5, False], ##############################
            "Atrial Pulse Width": [1, 1, 30, 1, 1, False],
            "Ventricular Amplitude": [0.1, 5, 5, 5, 5, False],
            "Ventricular Pulse Width": [1, 1, 30, 1, 1, False],
            "VRP": [150, 320, 500, 320, 320, False],
            "ARP": [150, 250, 500, 250, 250, False],
            "Atrial Sensitivity": [0, 0, 5, 0, 0, False],
            "Ventricular Sensitivity": [0, 0, 5, 0, 0, False]
        }

        self.load_parameters() #loads saved values


    def save_parameters_perm(self): #saves permanent programmable parameters and last saved mode between uses 

        print("Saving parameters to file...") #test to indicate saving

        data = { #data to save
            "last_mode": self.Mode[1], #permanent mode
            "parameter_values": self.parameter_values #parameter values
        }

        with open(self.filename, "w") as file: #writes parameters to JSON file
            json.dump(data, file, indent=4)

        print("Parameters saved to", self.filename) #test to confirm it saved


    def load_parameters(self): #loads previously saved parameters from JSON file
        
        if os.path.exists(self.filename): #if the file exists
            with open(self.filename, "r") as f: #load saved file
                data = json.load(f)
                
            if "last_mode" in data: #restore last mode
                self.Mode[0] = self.Mode[1] = data["last_mode"]

                
            if "parameter_values" in data: #restore last saved parameter values
                self.parameter_values = data["parameter_values"]

                for param, vals in self.parameter_values.items(): #goes through all the parameter values
                    if len(vals) < 6: #if the list has less than 6 elements
                        if "Amplitude" in param: #if it has Amplitude in the name
                            vals.append(True) #the toggle flag is set to true
                        else:
                            vals.append(False) #else false
                            
            print("Parameters loaded from", self.filename) #test to see if parameters are loaded in

        else: #if there is no previous saved file
            print("No parameters file found, using defaults.")

############################## User management ##############################

class UserManager:

    def __init__(self, filename="userdata.json"):
        self.filename = filename

    def userdata_exists(self):
        #check if userdata.json file exists, creates empty one if not
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"registered users": []}
            with open(self.filename, 'w') as file:
                json.dump(data, file, indent=4)

    def Verify_account(self, username, password):
        #Check if username and password is correct
        self.userdata_exists()
        with open(self.filename, "r") as file:
            data = json.load(file)
        for user in data['registered users']:
            if username.strip() == user['username'] and password.strip() == user['password']:
                return True
        return False

    def Add_new_user(self, username, password):
        #Checks sign up conditions and if it's all correct then signs up the user
        self.userdata_exists()
        with open(self.filename, "r") as file:
            data = json.load(file)

        if len(data['registered users']) > 9:  #checks if user list is full
            return False, "User list at capacity."
        new_user = {"username": username.strip(), "password": password.strip()}

        #checks username and password lengths
        if len(new_user['username']) < 6 or len(new_user['password']) < 6:
            return False, "Username & password must be at least 6 characters."
        elif len(new_user['username']) > 25 or len(new_user['password']) > 25:
            return False, "Username & password cannot exceed 25 characters."
        for user in data['registered users']:  #checks if username already exists
            if new_user['username'] == user['username']:
                return False, "Username already taken, please try again."

        #adds new user
        data["registered users"].append(new_user)
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)
            return True, "New user added, please sign in!"


############################## Egram Graphs ##############################

class EgramViewer(tk.Toplevel):

    def __init__(self, parent, time_data, voltageA_data, voltageV_data):
        super().__init__(parent)
        self.title("Egram Data Viewer")
        self.geometry("800x600")
        self.bg_colour = "#CBC3E3"
        self.config(background=self.bg_colour)
        try:
            self.iconphoto(True, PhotoImage(file="Pacemaker Logo.png"))
        except Exception:
            pass

        # max length for deques
        self.maxlen = 4000

        # initialize deques
        self.time_data = deque(time_data, maxlen=self.maxlen)
        self.voltageA_data = deque(voltageA_data, maxlen=self.maxlen)
        self.voltageV_data = deque(voltageV_data, maxlen=self.maxlen)

        # flags for showing graphs
        self.show_atrium = True
        self.show_ventricle = True

        # plot buttons
        button_frame = tk.Frame(self, bg=self.bg_colour)
        button_frame.pack(side=tk.TOP, pady=10)

        self.atrium_btn = tk.Button(button_frame, text="Toggle Atrium", command=self.toggle_atrium)
        self.atrium_btn.pack(side=tk.LEFT, padx=8)

        self.ventricle_btn = tk.Button(button_frame, text="Toggle Ventricle", command=self.toggle_ventricle)
        self.ventricle_btn.pack(side=tk.LEFT, padx=8)

        # figure and subplots
        self.fig = Figure(figsize=(8, 6), dpi=100, constrained_layout=True)
        self.axA = self.fig.add_subplot(211)
        self.axV = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.draw_graphs()

    def toggle_atrium(self):
        self.show_atrium = not self.show_atrium
        self.draw_graphs()

    def toggle_ventricle(self):
        self.show_ventricle = not self.show_ventricle
        self.draw_graphs()

    def draw_graphs(self):
        self.axA.clear()
        self.axV.clear()

        if len(self.time_data) == 0:
            self.canvas.draw()
            return

        # compute scrolling window edges
        last_time = self.time_data[-1]
        left_edge = last_time - (self.maxlen - 1)

        # atrium plot
        if self.show_atrium:
            self.axA.plot(self.time_data, self.voltageA_data, color="blue")
            self.axA.set_title("Atrium Signals")
            self.axA.set_xlabel("Time (ms)")
            self.axA.set_ylabel("Voltage (mV)")
            self.axA.grid(True)
            self.axA.set_xlim(left_edge, last_time)
            self.axA.set_visible(True)
        else:
            self.axA.set_visible(False)

        # ventricle plot
        if self.show_ventricle:
            self.axV.plot(self.time_data, self.voltageV_data, color="red")
            self.axV.set_title("Ventricle Signals")
            self.axV.set_xlabel("Time (ms)")
            self.axV.set_ylabel("Voltage (mV)")
            self.axV.grid(True)
            self.axV.set_xlim(left_edge, last_time)
            self.axV.set_visible(True)
        else:
            self.axV.set_visible(False)

        self.canvas.draw()

    def update_graph(self, new_time, new_voltageA=None, new_voltageV=None):
        if isinstance(new_time, list):
            self.time_data.extend(new_time)
            if new_voltageA is not None:
                self.voltageA_data.extend(new_voltageA)
            if new_voltageV is not None:
                self.voltageV_data.extend(new_voltageV)
        else:
            # Single sample
            self.time_data.append(new_time)
            if new_voltageA is not None:
                self.voltageA_data.append(new_voltageA)
            if new_voltageV is not None:
                self.voltageV_data.append(new_voltageV)
        
        self.draw_graphs()


############################## GUI ##############################

class PacemakerGUI:

    def __init__(self):
        self.param_mgr = ParameterManager() #initializes parameters
        self.serial_monitor = SerialMonitor(self.param_mgr) #sets up serial communication
        self.user_mgr = UserManager() #sets up user registration

        #sets up main window
        self.Window = Tk() #initiates a window
        self.Window.geometry("1080x1080") #sets size of the window
        self.Window.title("Pacemaker") #sets the title

        self.high_contrast = False #tracks current constrast mode

        try:
            Icon = PhotoImage(file="Pacemaker Logo.png") #sets the icon
            self.Window.iconphoto(True, Icon) #displays the icon
        except Exception:
            pass #if icon not found, ignore

        self.Window.config(background="#CBC3E3") #sets colour of background

        self.root = None  #will be created on successful login
        self.Status_button = None #shows connection status
        self.label = None
        self.combo_box = None #makes combobox
        self.sliders = {} #for storing slider widgets
        self.Status = self.serial_monitor.Status  #mirror serial status (kept in sync via update)

        self._create_login_widgets() #creates initial widgets


    ############################## Functions ##############################

    def About(self):
        About_window = Toplevel() #initiates about window
        About_window.geometry("360x180")
        About_window.title("About") #sets title

        Model_Number = Label(About_window, text="Model Number: " + self.param_mgr.Model_number, font=('Arial', 14), fg='black', bg="white") #sets text settings
        Model_Number.place(x=10, y=10) #displays model number text

        Software_Revision_Number = Label(About_window, text="Software Revision Number: Version " + self.param_mgr.Version_number, font=('Arial', 14), fg='black', bg="white") #sets text settings
        Software_Revision_Number.place(x=10, y=40) #displays software revision number text

        DCM_Serial_Number = Label(About_window, text="DCM Serial Number: " + self.param_mgr.DCM_serial_number, font=('Arial', 14), fg='black', bg="white") #sets text settings
        DCM_Serial_Number.place(x=10, y=70) #displays DCM serial number text

        Institution_Name = Label(About_window, text="Institution Name: McMaster University", font=('Arial', 14), fg='black', bg="white") #sets text settings
        Institution_Name.place(x=10, y=100) #displays institution name text


    def Get_input(self): #get username and password and returns it
        Username_input = self.Username_box.get()
        Password_input = self.Password_box.get()
        return Username_input, Password_input

    def Verify_account(self, username, password): #check if username and password is correct
        return self.user_mgr.Verify_account(username, password)

    def update_status_button(self):

        if self.Status_button:
            #read latest status from serial_monitor
            self.Status = self.serial_monitor.Status
            self.Status_button.config(text=self.Status)

        #schedule again
        try:
            self.root.after(100, self.update_status_button)
        except Exception:
            #If root was closed, ignore
            pass
        
    def Read_Pacemaker(self):
        self.Read_window = Toplevel() #opens a new window
        self.Read_window.geometry("300x380")
        self.Read_window.title("Pacemaker_Data") #sets title

        #reads
        values = self.serial_monitor.Read_Device_Values()

        #prepare display values
        if values is None:
            display_values = {
                "Lower Rate Limit": "?",
                "Upper Rate Limit": "?",
                "Atrial Amplitude": "?",
                "Atrial Pulse Width": "?",
                "Ventricular Amplitude": "?",
                "Ventricular Pulse Width": "?",
                "VRP": "?",
                "ARP": "?",
                "Atrial Sensitivity": "?",
                "Ventricular Sensitivity": "?",
                "Mode": "?",
                "Adaptive Data": "?"
            }
        else:
            display_values = {k: f"{v:.2f}" for k, v in values.items()}

        mode = display_values["Mode"]
        adaptive = display_values["Adaptive Data"]

        if mode == "1.00" and adaptive == "0.00":
            actual_mode = "AOO"
        elif mode == "1.00" and adaptive == "1.00":
            actual_mode = "AOOR"
        elif mode == "2.00" and adaptive == "0.00":
            actual_mode = "VOO"
        elif mode == "2.00" and adaptive == "1.00":
            actual_mode = "VOOR"
        elif mode == "3.00" and adaptive == "0.00":
            actual_mode = "VVI"
        elif mode == "3.00" and adaptive == "1.00":
            actual_mode = "VVIR"
        elif mode == "4.00" and adaptive == "0.00":
            actual_mode = "AAI"
        elif mode == "4.00" and adaptive == "1.00":
            actual_mode = "AAIR"
        else:
            actual_mode = "?"

        if display_values["Atrial Amplitude"] == "0.00":
            display_values["Atrial Amplitude"] = "Off"
        
        if display_values["Ventricular Amplitude"] == "0.00":
            display_values["Ventricular Amplitude"] = "Off"

        

        self.lrl_Label = Label(self.Read_window, text="Lower Rate Limit: " + display_values["Lower Rate Limit"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.lrl_Label.place(x=10, y=10)  

        self.url_Label = Label(self.Read_window, text="Upper Rate Limit: " + display_values["Upper Rate Limit"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.url_Label.place(x=10, y=40)  

        self.atrial_amp_Label = Label(self.Read_window, text="Atrial Amplitude: " + display_values["Atrial Amplitude"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.atrial_amp_Label.place(x=10, y=70)  

        self.atrial_pw_Label = Label(self.Read_window, text="Atrial Pulse Width: " + display_values["Atrial Pulse Width"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.atrial_pw_Label.place(x=10, y=100)

        self.ventricular_amp_Label = Label(self.Read_window, text="Ventricular Amplitude: " + display_values["Ventricular Amplitude"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.ventricular_amp_Label.place(x=10, y=130)

        self.ventricular_pw_Label = Label(self.Read_window, text="Ventricular Pulse Width: " + display_values["Ventricular Pulse Width"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.ventricular_pw_Label.place(x=10, y=160) 

        self.vrp_Label = Label(self.Read_window, text="VRP: " + display_values["VRP"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.vrp_Label.place(x=10, y=190) 

        self.vrp_Label = Label(self.Read_window, text="ARP: " + display_values["ARP"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.vrp_Label.place(x=10, y=220) 

        self.arp_Label = Label(self.Read_window, text="Atrial Sensitivity: " + display_values["Atrial Sensitivity"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.arp_Label.place(x=10, y=250) 

        self.arp_Label = Label(self.Read_window, text="Ventricular Sensitivity: " + display_values["Ventricular Sensitivity"], font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.arp_Label.place(x=10, y=280)

        self.mode_Label = Label(self.Read_window, text="Mode: " + actual_mode, font=('Arial', 14), fg='black', bg="white")  #Sets text settings
        self.mode_Label.place(x=10, y=310)  


    def Successful_login(self):  #Gives access to my account page

        self.Window.destroy(); #closes the login window
        self.root = tk.Tk() #opens a new window
        self.root.title("My Account")
        self.root.geometry("1080x1080")
        self.root.config(background="#CBC3E3") #sets colour of background

        #Fonts
        self.font_size = 14  #default size
        self.font_family = "Arial" #default font

        self.global_font = font.Font(family=self.font_family, size=self.font_size) #creates a font object for labels, buttons, and entries

        increase_btn = Button(self.root, text="A+", command=self.increase_font, font=self.global_font) #increase font
        increase_btn.place(x=870, y=20)

        decrease_btn = Button(self.root, text="A-", command=self.decrease_font, font=self.global_font)#decreases font
        decrease_btn.place(x=930, y=20)

        contrast_btn = Button(self.root, text="Toggle Contrast", command=self.toggle_contrast_logged_in, font=self.global_font) #toggles contrast
        contrast_btn.place(x=650, y=20)

        About_button = Button(self.root, text="About", font=self.global_font, fg='black', bg="white") #sets text settings
        About_button.place(x=15, y=15) #displays about button
        About_button.config(command=self.About) #sets button to about function

        Quit_button = Button(self.root, text="Quit", font=self.global_font, fg='black', bg="white") #sets text settings
        Quit_button.place(x=1000, y=20) #displays quit button
        Quit_button.config(command=self.Quit2) #sets button to quit function
        
        self.Status_button = Button(self.root, text=self.Status, font=self.global_font, fg='black', bg="white") #status button
        self.Status_button.place(x=15, y=725)

        self.combo_box_create()  #makes the drop-down menu to choose mode
        self.initializes_sliders()  #makes all the sliders

        self.param_mgr.load_parameters() #loads last saved values into sliders
        self.combo_box.set(self.param_mgr.Mode[1]) #set combo box to last saved mode
        self.select_mode(self.param_mgr.Mode[1]) #sets the starting mode (AOO)
        
        self.update_temp_values() #keeps updating the values in the sliders

        self.save_button = Button(self.root, text="Save Parameters", command=self.save_parameters, font=self.global_font) #save button
        self.save_button.place(x=450, y=300)

        self.Read_button = Button(self.root, text="Read Pacemaker", font=self.global_font) #read pacemaker button
        self.Read_button.place(x=450, y=350)
        self.Read_button.config(command=self.Read_Pacemaker)

        temp_report_button = Button(self.root, text="Temporary Report", command=lambda: self.export_report("Temporary"), font=self.global_font) #temporary report button
        temp_report_button.place(x=450, y=400)

        Bradycardia_report_button = Button(self.root, text="Bradycardia Report", command=lambda: self.export_report("Bradycardia"), font=self.global_font) # bradycardia report button
        Bradycardia_report_button.place(x=450, y=450)

        self.graph_button = Button(self.root, text="View Egram Graphs", command=self.open_graph_window, font=self.global_font)#egram graph button
        self.graph_button.place(x=450, y=500)

        self.update_status_button() #keeps the status button updated

    
    def open_graph_window(self):
        # disable combo box, save button, sliders and entry boxes
        self.combo_box.config(state="disabled")
        self.save_button.config(state="disabled")
        self.graph_button.config(state="disabled")
        self.Read_button.config(state="disabled")
        for param, (scale, entry, _, toggle, _) in self.sliders.items():
            scale.config(state="disabled")
            entry.config(state="disabled")
            if toggle:
                toggle.config(state="disabled")

        
        # setup graph window
        time_data = []
        voltageA_data = []
        voltageV_data = []
        graph_window = EgramViewer(self.root, time_data, voltageA_data, voltageV_data)

        # setup timing
        self.graph_loop_running = True
        start_time = time.time()

        batch_size = 24#51 for 10ms, 24 for 100ms  # adjust this
        buffer_time = []
        buffer_atr = []
        buffer_vent = []

        def poll_and_update():
            if not self.graph_loop_running:
                return
            vals = self.serial_monitor.Read_Device_Values()
            if vals is not None:
                elapsed_ms = (time.time() - start_time) * 1000
                a = (-5000/0.7)*vals.get("Atrial Data") + 5000
                v = (-5000/0.7)*vals.get("Ventricle Data") + 5000
                buffer_time.append(elapsed_ms)
                buffer_atr.append(a)
                buffer_vent.append(v)

                # Update graph only every batch_size samples
                if len(buffer_time) >= batch_size:
                    graph_window.update_graph(buffer_time, buffer_atr, buffer_vent)
                    buffer_time.clear()
                    buffer_atr.clear()
                    buffer_vent.clear()
            self.root.after(100, poll_and_update)

        poll_and_update()

        # When graph window closes, stop loop and re-enable sliders/buttons
        def on_close():
            self.graph_loop_running = False
            self.combo_box.config(state="readonly")
            self.save_button.config(state="normal")
            self.graph_button.config(state="normal")
            self.Read_button.config(state="normal")
            self.select_mode(self.combo_box.get())
            graph_window.destroy()

        graph_window.protocol("WM_DELETE_WINDOW", on_close)


    def combo_box_create(self):  #function to make dropdown menu
        self.root.title("Modes")
        self.label = tk.Label(self.root, text="Selected Mode: ", font=self.global_font, fg='black') #label to show current mode
        self.label.place(x=400, y=90)

        self.combo_box = ttk.Combobox(self.root, values=self.param_mgr.Modes, state='readonly', font=self.global_font)
        self.combo_box.place(x=400, y=130)

        self.combo_box.set("AOO")  #default state
        self.combo_box.bind("<<ComboboxSelected>>", self.select_mode) #bind selection change to update sliders based on selected mode

    def select_mode(self, event): #updates sliders - according to mode

        selected_mode = None
        
        try:
            #if called from bind, event will be passed; get current combo value
            selected_mode = self.combo_box.get() #get currently selected mode
        except Exception:
            #If called directly with a mode event will be a string
            if isinstance(event, str):
                selected_mode = event
            else: #use last known temporary mode
                selected_mode = self.param_mgr.Mode[0]

        self.label.config(text="Selected Mode: " + selected_mode) #update label to show currently selected mode

        self.root.focus() #ensure window focus

        allowed = self.param_mgr.mode_parameters[selected_mode]  #get the parameters that are relevent to the mode

        for param, (scale, entry, var, toggle, toggle_var) in self.sliders.items(): #enable sliders for allowed parameters, disable for others

            
            if param in allowed:  #if the parameter is in the current mode make available, else no
                scale.config(state="normal")
                entry.config(state="normal")

                saved_toggle = self.param_mgr.parameter_values[param][5]

                if toggle:
                    toggle_var.set(saved_toggle) #set checkbox state
                    toggle.config(state="normal") #make checkbox clickable
                    
                    if saved_toggle: #true = OFF
                        scale.config(state="disabled")
                        entry.config(state="disabled")
                        
                    else:  #false = ON
                        scale.config(state="normal")
                        entry.config(state="normal")
            else:
                #disable sliders and entries for parameters not allowed in this mode
                scale.config(state="disabled")
                entry.config(state="disabled")
                if toggle:
                    toggle_var.set(True)  # toggle OFF for disabled parameters
                    toggle.config(state="disabled")

                        

    def create_slider_with_entry(self, parent, label_text, from_, to, x, y, initial, has_toggle=False):
        
        var = tk.DoubleVar(value=initial) #creates a double int and initializes it to nominal value

        tk.Label(parent, text=label_text, font=self.global_font).place(x=x, y=y-10) #puts parameter name above the slider

        if label_text == "Atrial Amplitude" or label_text == "Ventricular Amplitude" or label_text == "Atrial Sensitivity" or label_text == "Ventricular Sensitivity":
            scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=0.1, variable=var, showvalue=False, length=150)

        elif label_text == "Atrial Pulse Width" or label_text == "Ventricular Pulse Width":
            scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=1, variable=var, showvalue=False, length=150)

        else:
            scale = tk.Scale(parent, from_=from_, to=to, orient='horizontal', resolution=0.01, variable=var, showvalue=False, length=150)
            
        # resolution - step size of decimal
        # variable=var - scale widget is linked to var, meaning moving the slider updates var automatically
        # length - of the slider
        
        scale.place(x=x, y=y + 20) #place slider on window

        #creates the box to type into
        entry = tk.Entry(parent, width=6, font=self.global_font)
        entry.place(x=x + 180, y=y + 30)
        entry.insert(0, str(initial)) #show the inital value

        #shows min and max values of the sliders
        min_label = tk.Label(parent, text=str(from_), font=self.global_font)
        min_label.place(x=x, y=y+40) #min
        
        max_label = tk.Label(parent, text=str(to), font=self.global_font)
        max_label.place(x=x + 130, y=y+40) #max

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
            entry.delete(0, tk.END)  #clears entry box
            entry.insert(0, str(round(var.get(), 2))) #inserts new number to 2 decimal places

        var.trace_add("write", update_from_scale)  #when sliders value changes - call function to update box


        if has_toggle:
            toggle_var = tk.BooleanVar(value=False) #true means slider disabled
            toggle = tk.Checkbutton(parent, text="Off", variable=toggle_var, font=self.global_font) #when this is checked/unchecked it toggle the Off state
            toggle.place(x=x-70, y=y + 20)
            

            def toggle_slider(): #enables/disables slider based on toggle state
                if toggle_var.get():#if true - disable 
                    scale.config(state="disabled")
                    entry.config(state="disabled")
                    
                else: #if false - enable
                    scale.config(state="normal")
                    entry.config(state="normal")


            toggle_var.trace_add("write", lambda *args: toggle_slider())

        else:
            toggle = None
            toggle_var = None

        
        return scale, entry, var, toggle, toggle_var  #return scale, entry box, shared value, toggle state

    def initializes_sliders(self):  #initializes all the sliders

        self.sliders = {} #to store parameters

        # (parent, label, min value, max value, x pos, y pos, nominal value)
        self.sliders["Lower Rate Limit"] = self.create_slider_with_entry(self.root, "Lower Rate Limit", 30, 180, 150, 150, 60)
        self.sliders["Upper Rate Limit"] = self.create_slider_with_entry(self.root, "Upper Rate Limit", 50, 200, 150, 250, 120)
        self.sliders["Atrial Amplitude"] = self.create_slider_with_entry(self.root, "Atrial Amplitude", 0.1, 5.0, 150, 350, 5, has_toggle=True)
        self.sliders["Atrial Pulse Width"] = self.create_slider_with_entry(self.root, "Atrial Pulse Width", 1, 30, 150, 450, 1)
        self.sliders["Atrial Sensitivity"] = self.create_slider_with_entry(self.root, "Atrial Sensitivity", 0, 5, 150, 550, 4) #new

        self.sliders["Ventricular Amplitude"] = self.create_slider_with_entry(self.root, "Ventricular Amplitude", 0.1, 5.0, 710, 150, 5, has_toggle=True)
        self.sliders["Ventricular Pulse Width"] = self.create_slider_with_entry(self.root, "Ventricular Pulse Width", 1, 30, 710, 250, 1)
        self.sliders["VRP"] = self.create_slider_with_entry(self.root, "VRP", 150, 500, 710, 350, 320)
        self.sliders["ARP"] = self.create_slider_with_entry(self.root, "ARP", 150, 500, 710, 450, 250)
        self.sliders["Ventricular Sensitivity"] = self.create_slider_with_entry(self.root, "Ventricular Sensitivity", 0, 5, 710, 550, 3.75) #new

        # Restore saved values from JSON
        for param, (scale, entry, var, toggle, toggle_var) in self.sliders.items():
            # Set slider to saved permanent value
            saved_value = self.param_mgr.parameter_values[param][4]  # permanent value
            var.set(saved_value)
            entry.delete(0, tk.END)
            entry.insert(0, str(saved_value))

            # Set toggle checkbox to saved state
            if toggle:
                saved_toggle = self.param_mgr.parameter_values[param][5]  # saved toggle
                toggle_var.set(saved_toggle)
                # Ensure slider/enabled state matches toggle
                if saved_toggle:
                    scale.config(state="disabled")
                    entry.config(state="disabled")
                else:
                    scale.config(state="normal")
                    entry.config(state="normal")


        


    def update_temp_values(self):

        for param, (scale, entry, var, toggle, toggle_var) in self.sliders.items(): #loops through all the sliders
            self.param_mgr.parameter_values[param][3] = var.get()  #gets current slider value and put it in temp place

        self.param_mgr.Mode[0] = self.combo_box.get() #update current slider value based on current combobox seleection

        try:
            self.root.after(500, self.update_temp_values) #continuously updates temp values
        except Exception:
            pass
        

    def save_parameters(self):
        
        for param in self.param_mgr.parameter_values:
            self.param_mgr.parameter_values[param][4] = self.param_mgr.parameter_values[param][3] #put temp values into permanent place

            if param in self.sliders:
                scale, entry, var, toggle, toggle_var = self.sliders[param]
                if toggle: #if toggle exists for parameter
                    print(f"Saving toggle for {param}: {toggle_var.get()}")
                    self.param_mgr.parameter_values[param][5] = toggle_var.get() #get state and stores it

        self.param_mgr.Mode[1] = self.combo_box.get() #save currenly selected mode

 
        self.param_mgr.save_parameters_perm() #write parameters to JSON file

 
        if self.serial_monitor.Status == "Connected": #if pacemaker connected - save values to pacemaker
            self.serial_monitor.Write_Serial(self.param_mgr)



    #creates a new report of the type given (Bradycardia or Temporary)
    def export_report(self, type: str):

        #saves current time and labels the output file
        current_datetime = datetime.now()
        file_name = type + "_Report-" + current_datetime.strftime("%Y-%m-%d-%H-%M-%S") + ".txt"

        #uses i to output temp or brady paramaters
        i = 3
        if type == "Bradycardia":
            i = 4

        param_str = "\n\tMode: " + self.param_mgr.Mode[i - 3] + "\n"
        for param in self.param_mgr.mode_parameters[self.param_mgr.Mode[i - 3]]:

            value = self.param_mgr.parameter_values[param][i]

            if param in self.sliders:
                _,_,_,_,toggle_var = self.sliders[param]

                if toggle_var is not None and toggle_var.get():
                    value = "Off"
            
            param_str += f"\t{param}: {value}\n"

        #writes report
        with open(file_name, 'w') as file:
            file.write(type + " Parameters Report" +
                       "\nDate: " + current_datetime.strftime("%Y-%m-%d %H:%M:%S") +
                       "\nDevice Model: " + self.param_mgr.Device_model +
                       "\nSerial Number: " + self.param_mgr.Device_serial_number +
                       "\nDCM Serial Number: " + self.param_mgr.DCM_serial_number +
                       "\nApplication Model: " + self.param_mgr.Model_number +
                       "\nVersion Number: " + self.param_mgr.Version_number +
                       "\n----------------------------------" + param_str
                       )

        subprocess.Popen(["notepad.exe", file_name])

    def userdata_exists(self):
        #check is userdata.json file exists, creates empty one if not
        try:
            with open("userdata.json", 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {
                "registered users": []
            }
            with open("userdata.json", 'w') as file:
                json.dump(data, file, indent=4)

    def Add_new_user(self, username, password):  #Checks sign up conditions and if it's all correct then signs up the user
        self.userdata_exists()
        with open("userdata.json", "r") as file:
            data = json.load(file)
        if len(data['registered users']) > 9:  #checks if user list is full
            return False, "User list at capacity."
        new_user = {
            "username": username.strip(),
            "password": password.strip()
        }

        #checks username and password lengths
        if len(new_user['username']) < 6 or len(new_user['password']) < 6:
            return False, "Username & password must be at least 6 characters."
        elif len(new_user['username']) > 25 or len(new_user['password']) > 25:
            return False, "Username & password cannot exceed 25 characters."
        for user in data['registered users']:  # checks if username already exists
            if new_user['username'] == user['username']:
                return False, "Username already taken, please try again."

        #adds new user
        data["registered users"].append(new_user)
        with open("userdata.json", "w") as file:
            json.dump(data, file, indent=4)
            return True, "New user added, please sign in!"

    def Sign_in(self):  #Gets username and password and verifies if it's correct
        Username_input, Password_input = self.Get_input()
        Verify = self.Verify_account(Username_input, Password_input)
        if (Verify == True):
            self.Successful_login()
        else:
            Sign_in_label = Label(self.Window, text="Incorrect username/password", font=('Arial', 14), fg='black', bg="#CBC3E3")  #Sets text settings
            Sign_in_label.place(x=395, y=425)  #Displays sign in text
            Sign_in_label.after(3000, Sign_in_label.destroy)  #Removes sign in text after some time

    def Sign_up(self):  #Gets username and password and verifies sign up conditions
        Username_input, Password_input = self.Get_input()
        Verify, Message = self.Add_new_user(Username_input, Password_input)

        Sign_up_label = Label(self.Window, text=Message, font=('Arial', 14), fg='black', bg="#CBC3E3")  # Sets text settings
        Sign_up_label.place(x=350, y=425)  # Displays sign up text

        Sign_up_label.after(3000, Sign_up_label.destroy)  # Removes sign up text after some time

    def Quit(self):
        self.serial_monitor.stop()
        self.Window.destroy()  #Quits window

    def Quit2(self):
        self.serial_monitor.stop()
        if self.root:
            self.root.destroy()  #Quits secondary window

    ############################## Widgets (login window) ##############################

    def _create_login_widgets(self):
        # Labels

        self.font_size = 14
        self.font_family = "Arial"
        self.global_font = font.Font(family=self.font_family, size=self.font_size)

        increase_btn = Button(self.Window, text="A+", command=self.increase_font, font=self.global_font)
        increase_btn.place(x=870, y=20)

        decrease_btn = Button(self.Window, text="A-", command=self.decrease_font, font=self.global_font)
        decrease_btn.place(x=930, y=20)

        toggle_btn = Button(self.Window, text="Toggle Contrast", command=self.toggle_contrast, font=self.global_font)
        toggle_btn.place(x=650, y=20)
        
        Username_label = Label(self.Window, text="Username", font=self.global_font, fg='black', bg="#CBC3E3")
        Username_label.place(x=345, y=500)

        Password_label = Label(self.Window, text="Password", font=self.global_font, fg='black', bg="#CBC3E3")
        Password_label.place(x=345, y=550)

        # Buttons
        Welcome_button = Button(self.Window, text="Welcome :)", font=('Arial', 40), fg='black', bg="white")
        Welcome_button.place(x=375, y=250)

        About_button = Button(self.Window, text="About", font=self.global_font, fg='black', bg="white")
        About_button.place(x=15, y=15)

        About_button.config(command=self.About)

        Sign_in_button = Button(self.Window, text="Sign In", font=self.global_font, fg='black', bg="white")
        Sign_in_button.place(x=625, y=495)

        Sign_in_button.config(command=self.Sign_in)

        Sign_up_button = Button(self.Window, text="Sign Up", font=self.global_font, fg='black', bg="white")
        Sign_up_button.place(x=620, y=545)

        Sign_up_button.config(command=self.Sign_up)

        Quit_button = Button(self.Window, text="Quit", font=self.global_font, fg='black', bg="white")
        Quit_button.place(x=1000, y=20)

        Quit_button.config(command=self.Quit)

        # Entry Boxes
        self.Username_box = Entry(self.Window)  #Box for username input
        self.Password_box = Entry(self.Window)  #Box for password input
        self.Username_box.place(x=470, y=505)  #Display username box
        self.Password_box.place(x=470, y=555)  #Display password box



    ######################### Acessibility #########################

    def increase_font(self):

        if self.font_size < 18: #prevent it from becoming to big
            self.font_size += 2  # increase size by 2
            self.global_font.config(size=self.font_size)

    def decrease_font(self):

        if self.font_size > 6:  # prevent it from becoming too small
            self.font_size -= 2
            self.global_font.config(size=self.font_size)


    def toggle_contrast(self): #for login-in window
        self.high_contrast = not self.high_contrast
        bg = "black" if self.high_contrast else "#CBC3E3"
        fg = "white" if self.high_contrast else "black"
        
        
        self.Window.config(bg=bg) # update window background
        
        
        for widget in self.Window.winfo_children(): #update all children widgets
            if isinstance(widget, tk.Label):
                widget.config(bg=bg, fg=fg)
            elif isinstance(widget, tk.Entry):
                widget.config(bg="white", fg="black") #keep entries white background and black text


    def toggle_contrast_logged_in(self): #for logged-in window

        self.high_contrast = not getattr(self, "high_contrast", False) #toggle contrast state

        #color scheme
        bg_color = "black" if self.high_contrast else "#CBC3E3"
        fg_color = "white" if self.high_contrast else "black"
        entry_bg = "black" if self.high_contrast else "white"
        entry_fg = "white" if self.high_contrast else "black"

        self.root.config(bg=bg_color) #set main window background

        def apply_contrast(widget):

            #skip widgets that are part of sliders
            if hasattr(widget, "is_slider_related") and widget.is_slider_related:
                return

            try:
                #normal Entry widgets (that aren't slider entries)
                if isinstance(widget, tk.Entry):
                    widget.config(bg=entry_bg, fg=entry_fg, insertbackground=fg_color)

                #skip all Scale widgets (sliders)
                elif isinstance(widget, tk.Scale):
                    return

                elif isinstance(widget, tk.Button):
                    return #skips buttons

                #frame or container: process children
                if hasattr(widget, "winfo_children"):
                    for child in widget.winfo_children():
                        apply_contrast(child)

            except tk.TclError:
                pass

        #apply to all children of root
        for widget in self.root.winfo_children():
            apply_contrast(widget)


############################## Run ##############################
    def run(self):
        self.Window.mainloop()


if __name__ == "__main__":
    app = PacemakerGUI()
    app.run()
