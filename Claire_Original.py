import json
from datetime import datetime
import subprocess

# programable paramters [0=lower limit, 1=nominal, 2=upper limit, 3=temporary paramater, 4=permanent parameter]
Lower_Rate_Limit = [30,60,175,60,60] #ppm
Upper_Rate_Limit = [50,120,175,120,120] #ppm
Atrial_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Atrial_Pulse_Width = [0.05,0.4,1.9,0.4,0.4] #ms
Ventricular_Amplitude = [0.5,3.5,7.0,3.5,3.5] #V
Ventricular_Pulse_Width = [0.05,0.4,1.9,0.4,0.4] #ms
VRP = [150,320,500,320,320] #ms
ARP = [150,250,500,250,250] #ms

# Consts
Device_model = "Pacemaker"
Device_serial_number = "HOOO25"
DCM_serial_number = "400325598"
Model_number = "ABCD"
Version_number = "0.2"

Modes = ["Off","AOO","VOO", "AAI", "VVI"]
Programable_Parameters = ["Lower Rate Limit", "Upper Rate Limit", "Atrial Amplitude","Atrial Pulse Width",
                         "Ventricular Amplitude", "Ventricular Pulse Width", "VRP", "ARP"]
Parameters_Units = [" ppm", " ppm", " V", " ms", " V", " ms", " ms", " ms"]
Mode_Parameters = [[False,False,False,False,False,False,False,False],
                   [True,True,True,True,False,False,False,False],
                   [True,True,False,False,True,True,False,False],
                   [True,True,True,True,False,False,False,True],
                   [True,True,False,False,True,True,True,False]]


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


# returns true if the username and password match a registered user, false otherwise
def login_request(username, password):
    userdata_exists()

    with open("userdata.json", "r") as file:
        data = json.load(file) 

    for user in data['registered users']:
        if username.strip() == user['username'] and password.strip() == user['password']:
            return True
        
    return False

#print(login_request('testuser4','123456')), returned False
#print(login_request('testuser4','654321')), returned True

# adds a new user to "userdata.json" 
def add_new_user(username, password):
    userdata_exists()

    with open("userdata.json", "r") as file:
        data = json.load(file) 

    # checks if user list already has 10 users
    if len(data['registered users']) > 10:
        return False, "User list at capacity."
    
    new_user = {
        "username": username.strip(),
        "password": password.strip()
    }

    # checks if username and password are within acceptable lengths
    if len(new_user['username']) < 6 or len(new_user['password']) < 6:
        return False, "Username and password must be at least 6 characters."
    elif len(new_user['username']) > 25 or len(new_user['password']) > 25:
        return False, "Username and password cannot exceede 25 characters."
    
    # checks if username is already in use
    for user in data['registered users']:
        if new_user['username'] == user['username']:
            return False, "Username already taken."

    # adds the new user
    data["registered users"].append(new_user)
    with open("userdata.json", "w") as file:
        json.dump(data, file, indent=4)
        return True, "User Added!"


#print(add_new_user("12345678901234567890123456","123456")), returned (False, 'Username and password cannot exceede 25 characters.')
#print(add_new_user("abcdef"," ")), returned (False, 'Username and password must be at least 6 characters.')
#print(add_new_user("abc","123456")), returned (False, 'Username and password must be at least 6 characters.')
#print(add_new_user("testuser6","123456")), returned (True, 'User Added!'), then (False, 'Username already taken.')


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
                    "\n"+ "\t" + Programable_Parameters[0]+ ": "+ str(Lower_Rate_Limit[i]) + Parameters_Units[0]+
                    "\n"+ "\t" + Programable_Parameters[1]+ ": "+ str(Upper_Rate_Limit[i]) + Parameters_Units[1]+
                    "\n"+ "\t" + Programable_Parameters[2]+ ": "+ str(Atrial_Amplitude[i]) + Parameters_Units[2]+
                    "\n"+ "\t" + Programable_Parameters[3]+ ": "+ str(Atrial_Pulse_Width[i]) + Parameters_Units[3]+
                    "\n"+ "\t" + Programable_Parameters[4]+ ": "+ str(Ventricular_Amplitude[i]) + Parameters_Units[4]+
                    "\n"+ "\t" + Programable_Parameters[5]+ ": "+ str(Ventricular_Pulse_Width[i]) + Parameters_Units[5]+
                    "\n"+ "\t" + Programable_Parameters[6]+ ": "+ str(VRP[i]) + Parameters_Units[6]+
                    "\n"+ "\t" + Programable_Parameters[7]+ ": "+ str(ARP[i]) + Parameters_Units[7]
      )
        
    subprocess.Popen(["notepad.exe",file_name])
    return file_name





