# Analyzer to clean up Telemetry data and compare it to the Dozee and EarlySense devices

import csv
import pandas as pd
import matplotlib.pyplot as plt

def clean(filename, new_filename):
    """Arguments: 
        filename: original data file
        new_filename: name of new file to write to
    
    Returns: the new file that contains only the columns 
    that we wanted from the original file
    """

    data = pd.read_csv(filename) # make file usable in python
    headers = data.columns
    tele = "TELEMETRY"
    dozee = "DOZEE"
    es = "ES"
    new_file = new_filename # create new file to write to
    with open(new_file, 'w', newline="") as file: # write to new file
        csvwriter = csv.writer(file)
        for header in headers:
            if tele in filename: # if the file is telemetry
                headers = ["Time", "ECG_HR", "CO2_RR"]
                csvwriter.writerow(headers) # write the headers to the file
                if (header == "Time" or header == "ECG_HR" or header == "CO2_RR"):
                    csvwriter.writerows(data.header) # write the data for headers we wanted
            elif dozee in filename: # if the file is Dozee
                headers = ["Time", "Heart Rate", "Breath Rate"]
                csvwriter.writerow(headers)
                if (header == "Time" or header == "Heart Rate" or header == "Breath Rate"):
                    csvwriter.writerows(data.header)
            elif es in filename: # if the file is EarlySense
                headers = ["Clock", "Hr avg", "Rr avg"]
                csvwriter.writerow(headers)
                if (header == "Clock" or header == "Hr avg" or header == "Rr avg"):
                    csvwriter.writerows(data.header)
    return new_file


def colon_split(string):
    """Cleans the time format to include only hours and minutes
    
    Arguments: 
        string: the time as a string
    
    Returns: a string representing the time with only hours and minutes
    """

    if string.count(":") == 1: # if there is only one colon, return the same string
        return string
        # string.split(":")[0]
    return ":".join(string.split(":", 2)[:2]) # return everything before the second colon (HR:MM:SS -> HR:MM)


def clean_tele(new_filename):
    """Averages the heart rate and respiratory rate for each minute
    for the telemetry data and rewrites it to the file
    
    Arguments: 
        new_filename: the new file with only the heart rate and respiratory
        rate columns that we cleaned using clean() 
    
    Returns: the new, rewritten telemetry file with the averages for
    each minute instead of data points for every 5 seconds
    """

    data = pd.read_csv(new_filename)
    time = data.Time.split(" ")[1] # separate the date from the time
    hr = data.ECG_HR
    rr = data.CO2_RR
    total_hr = 0
    total_rr = 0
    count = 0
    averages = []
    for i in range(1, len(time)):
        j = colon_split(time[i]) # take the seconds out of the time
        k = colon_split(time[i - 1])
        if j == k: # if the min is the same as the next min, add the values and increase count
            total_hr += hr[i]
            total_rr += rr[i]
            count += 1
        averages.append([(total_hr / count), (total_rr / count)]) # append the averages for each min in a new list
    
    new_file = new_filename # rewrite the file
    with open(new_file, 'w', newline="") as file:
        csvwriter = csv.writer(file) 
        csvwriter.writerow(data.columns)
        csvwriter.writerows(averages)
    return new_file
    

def timepoints(filename):
    """Takes a file of cleaned data and counts how many evaluable minutes of 
    data are in the file.
    
    Arguments:
        filename: file with cleaned data
        
    Returns: an int representing the number of evaluable minutes in the file 
    """

    points = 0
    data = pd.read_csv(filename)
    headers = data.columns
    for i in range(len(data)):
        if (data.headers[1][i] == 0 or data.headers[1][i].isnull() or 
                data.headers[2][i] == 0 or data.headers[2][i]): 
            points += 1
    return points


def plot(tele, es, dozee):
    """Takes the cleaned data files for the Telemetry, EarlySense, and Dozee
    and creates two line graphs to compare values for each minute
    
    Arguments:
        tele: cleaned Telemetry data
        es: cleaned EarlySense data
        Dozee: cleaned Dozee data
    
    Returns: two color-coordinated line graphs that represents the data points
    for each minute for each of the data sets (heart rate and respiratory rate)
    """
    tele_rows = []
    with open(tele, 'r') as file:
        csvreader = csv.reader(file)
        tele_header = next(csvreader)
        for row in csvreader:
            tele_rows.append(row)
    
    es_rows = []
    with open(es, 'r') as file:
        csvreader = csv.reader(file)
        es_header = next(csvreader)
        for row in csvreader:
            es_rows.append(row)

    dozee_rows = []
    with open(dozee, 'r') as file:
        csvreader = csv.reader(file)
        dozee_header = next(csvreader)
        for row in csvreader:
            dozee_rows.append(row)

    tele_hr_x = []
    tele_hr_y = []
    for row in tele_rows:
        tele_hr_x.append(row[0])
        tele_hr_y.append(row[1])
    plt.plot(tele_hr_x, tele_hr_y, label = "Telemetry Heart Rate")

    es_hr_x = []
    es_hr_y = []
    for row in es_rows:
        es_hr_x.append(row[0])
        es_hr_y.append(row[1])
    plt.plot(es_hr_x, es_hr_y, label = "EarlySense Heart Rate")

    dozee_hr_x = []
    dozee_hr_y = []
    for row in es_rows:
        dozee_hr_x.append(row[0])
        dozee_hr_y.append(row[1])
    plt.plot(dozee_hr_x, dozee_hr_y, label = "Dozee Heart Rate")

    plt.xlabel("Time (HH:MM)")
    plt.ylabel("Heart Rate")
    plt.title("Heart Rate Comparison")
    plt.legend()
    plt.show()

    tele_rr_x = []
    tele_rr_y = []
    for row in tele_rows:
        tele_rr_x.append(row[0])
        tele_rr_y.append(row[2])
    plt.plot(tele_rr_x, tele_rr_y, label = "Telemetry Respiratory Rate")

    es_rr_x = []
    es_rr_y = []
    for row in es_rows:
        es_rr_x.append(row[0])
        es_rr_y.append(row[2])
    plt.plot(es_rr_x, es_rr_y, label = "EarlySense Respiratory Rate")

    dozee_rr_x = []
    dozee_rr_y = []
    for row in es_rows:
        dozee_rr_x.append(row[0])
        dozee_rr_y.append(row[1])
    plt.plot(dozee_rr_x, dozee_rr_y, label = "Dozee Respiratory Rate")

    plt.xlabel("Time (HH:MM)")
    plt.ylabel("Respiratory Rate")
    plt.title("Respiratory Rate Comparison")
    plt.legend()
    plt.show()

    
def main():
    """"""


if __name__ == "__main__":
    main()