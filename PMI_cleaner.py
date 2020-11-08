import sqlite3
import pandas
import calendar
from time import strptime

def execute(path):
    Actual_Y = "Actual_Y_IPMIM"
    Actual_M = "Actual_M_IPMIM"
    Actual_D = "Actual_D_IPMIM"
    Release_Y = "Release_Y_IPMIM"
    Release_M = "Release_M_IPMIM"
    Release_D = "Release_D_IPMIM"
    Release_Date = "Release_Date_IPMIM"
    Actual_Date = "Actual_Date_IPMIM"
    Prev = "Prev_IPMIM"

    # Detect in which row the mistmatch is
    table = pandas.read_csv(filepath_or_buffer=path, index_col= 0)
    for i, elem in enumerate(pandas.isnull(table["Prev"])):
        if elem == True:
            init_pos = i
            break

    # Trasnform previous months names
    table[Release_M] = table[Release_M].apply(lambda x: strptime(x, '%b').tm_mon).astype('uint8')
    table[Actual_M] = table[Actual_M][0:init_pos].apply(lambda x: strptime(x, '%b').tm_mon)

    #print(table["Actual_M"][0:init_pos])

    # Move all involved cols from specified row
    for i in range(init_pos, len(table[Prev])):
        table.iat[i, -1] = table.iat[i, -2]
        table.iat[i, -2] = table.iat[i, -3]
        table.iat[i, -3] = table.iat[i, -4]
        table.iat[i, -4] = table.iat[i, -5]
        prev_release_m = table.at[i-1, Release_M]
        prev_actual_m = table.at[i-1, Actual_M]
        if prev_release_m == prev_actual_m:     #Association Release-Actual month
            if prev_actual_m == 1:
                table.at[i, Actual_M] = 12
            else:
                table.at[i, Actual_M] = prev_actual_m - 1
        else:
            table.at[i, Actual_M] = prev_actual_m

    table[Actual_M] = table[Actual_M].astype('uint8')
    #print(table["Release_M"], table["Actual_M"])

    # Actual_Y logic
    table.insert(loc=0, column=Actual_Y, value=table[Release_Y])
    for i in range(0, len(table[Actual_M])):
        if table.at[i, Actual_M] > table.at[i, Release_M]:
            table.at[i, Actual_Y] = table.at[i, Release_Y] - 1

    #print(table["Release_Y"]-table["Actual_Y"])

    # Join Release_Y-Release_M-Release_D
    table.insert(loc=0, column=Release_Date, value='None')
    table.insert(loc=0, column=Actual_Date, value='None')
    table[Release_Date] = table[Release_Y].astype(str) + "-" + table[Release_M].astype(str) + "-" + table[Release_D].astype(str)

    # Join Actual_Y-Actual_M
    table[Actual_Date] = table[Actual_Y].astype(str) + "-" + table[Actual_M].astype(str)
    #table.to_csv("data/IPMIM.csv")
    con = sqlite3.connect("data/db/economic_data.sqlite")
    table.to_sql(name="IPMIM", con=con)

if __name__ == "__main__":
    execute("data/IPMIM.csv")