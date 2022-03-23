from datetime import datetime
from dateparser import parse
import csv

filename = "input.csv"
input_list = []
input_2d = []
utc_list = []
ldn_list = []
nyc_list = []
tko_list = []
hkg_list = []
accepted = []
utc1d = []
suffix = []
bbg_ldn = ['8:00 LDN', '9:00 LDN', '10:00 LDN', '13:00 LDN', '16:00 LDN']
bbg_nyc = ['6:00 NYC', '7:00 NYC', '8:00 NYC', '9:00 NYC', '10:00 NYC', '11:00 NYC', '12:00 NYC', 
           '13:00 NYC', '14:00 NYC', '15:00 NYC', '16:00 NYC']
bbg_tko = ['9:00 TKO', '10:00 TKO', '10:30 TKO', '11:00 TKO', '11:30 TKO', '12:00 TKO', '12:30 TKO',
           '13:00 TKO', '14:00 TKO', '15:00 TKO', '15:30 TKO', '16:30 TKO', '18:00 TKO', '19:00 TKO', '20:00 TKO']
bbg_hkg = ['15:00 HKG', '16:00 HKG']
timezones = {'EU': 'CET', 'LDN': 'GB', 'NYC': 'EST5EDT', 'TKO': 'Japan', 'HKG': 'Hongkong',
             'SYD': 'Australia/Canberra', 'AUK':'Pacific/Auckland'}



cross = []
side = []
notional = []
ccy = []
date = []


with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)
    data.pop(0) #removes the first row that is just column headings, since we already know which columns we want to extract

#reads csv file and extracts our relavent data into input_list

for i in range(len(data)):
    input_list.append(data[i][6])
    input_list.append(data[i][7])
    cross.append(data[i][1])
    side.append(data[i][2])
    notional.append(data[i][3])
    ccy.append(data[i][4])
    date.append(data[i][8])
    
for i in range(len(cross)):
    one = f"{cross[i][:3]}"
    two = f"{cross[i][3:]}"
    cross[i] = (one + " " + two)


#formatting input_list into a 2d list
input_2d = [input_list[i:i+2] for i in range(0, int(len(input_list)), 2)]

#changing the timezone to one that is accepted by dateparser (EU -> CET)
#These timezones are the same, EU just isn't recognized by dateparser
#for the rest of them see the timezones dictionary

for i in range(len(input_2d)):
    repl = input_2d[i][1]
    #print(repl)
    if input_2d[i][1] in timezones:
        input_2d[i][1]= timezones[repl]

utc_list = input_2d
#Convert input times to UTC
for i in range(len(input_2d)):
    TIMEZONE = input_2d[i][1]
    processed = parse(input_2d[i][0], settings ={ 'TIMEZONE': TIMEZONE, 'TO_TIMEZONE': 'UTC'})
    processed = datetime.strftime(processed, '%H:%M')
    utc_list[i][0] = processed
    utc_list[i][1] = 'UTC'
    utc1d.append(processed)

accepted = utc1d    



# acceptd BBG timezones are LDN NYC TKO HGK 
for i in range(len(utc_list)):
    processed = parse(utc_list[i][0], settings ={ 'TIMEZONE': 'UTC', 'TO_TIMEZONE': 'GB'})
    processed = datetime.strftime(processed, '%H:%M') + ' LDN'
    ldn_list.append(processed)
     
for i in range(len(utc_list)):
    processed = parse(utc_list[i][0], settings ={ 'TIMEZONE': 'UTC', 'TO_TIMEZONE': 'EST5EDT'})
    processed = datetime.strftime(processed, '%H:%M') + ' NYC'
    nyc_list.append(processed)

for i in range(len(utc_list)):
    processed = parse(utc_list[i][0], settings ={ 'TIMEZONE': 'UTC', 'TO_TIMEZONE': 'Japan'})
    processed = datetime.strftime(processed, '%H:%M') + ' TKO'
    tko_list.append(processed)

for i in range(len(utc_list)):
    processed = parse(utc_list[i][0], settings ={ 'TIMEZONE': 'UTC', 'TO_TIMEZONE': 'Hongkong'})
    processed = datetime.strftime(processed, '%H:%M') + ' HKG'
    hkg_list.append(processed)

    
    
for i in range(len(utc1d)):
    if nyc_list[i] in bbg_nyc:
        accepted[i] = nyc_list[i]
        
    elif ldn_list[i] in bbg_ldn:
        accepted[i] = ldn_list[i]
        
    elif tko_list[i] in bbg_tko:
        accepted[i] = tko_list[i]
        
    elif hkg_list[i] in bbg_hkg:
        accepted[i] = hkg_list[i]
        
    else:
        accepted[i] = "NA"
#print(accepted)  

for i in range(len(accepted)):
    suffix.append(accepted[i].split(" "))
    #print(accepted[i])
#print(suffix)
    
for i in range(len(suffix)):
    front = f"{suffix[i][0][:-3]}"
    front = int(front)
    back = f"{suffix[i][0][2:]}"
    if back == ":00":
        if front < 12:
            suffix[i][0] = str(front) + "AM"
        elif front == 12:
            suffix[i][0] = str(front) + "PM"
        else:
            suffix[i][0] = str(front - 12) + "PM"
    else:
        if front < 12:
            suffix[i][0] = str(front) + back + "AM"
        elif front == 12:
            suffix[i][0] = str(front) + back + "PM"
        else:
            suffix[i][0] = str(front - 12) + back + "PM"
    accepted[i] = "BBG " + suffix[i][0] + " " + suffix[i][1]
    

header = ["Cross", "Side", "Notional", "CCY", "Fix Type", "Date"]
rows = zip(cross, side, notional, ccy, accepted, date)


with open('result.csv', 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

