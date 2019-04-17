# **
# ** Author: Campbell Ong, Victoria Pruim
# ** Revision:
# ** Date: 6/7/18
# **
# ** Purpose: Reads in inventory from test.xlsm Excel sheet and creates/populates codb.db database and coData table
#       using SQL.
# **
# ** TO DO:
#       Don't read past row 1001 on Excel sheet
#       Test populate_sheet and create_db functions
#       Add item to table
#       Delete item from table
#       Read in multiple rooms and create/populate respective tables
#       ...and more

import openpyxl
import sqlite3
from sqlite3 import Error

coDict = {}


def create_connection(db_file):
    """
    create a database connection to the SQLite database specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def create_table(conn, create_table_sql):
    """
    create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def populate_table(conn, wb, sheet_name):  # This needs to be tested as a function (used to be in main)
    """
    populate a table by reading in Excel sheet data and using add_new_item() function
    :param conn: Connection object
    :param wb: selected Excel Workbook
    :param sheet_name: Excel sheet in wb Workbook desired to be read
    :return:
    """
    # Select desired worksheet
    ws = wb[sheet_name]

    # Read in and save to table
    try:
        rowCnt = 1
        for row in ws.rows:
            if rowCnt > 2:
                if row[0].value is not None:
                    status = 'OK'
                elif row[1].value is not None:
                    status = 'CVI'
                elif row[2].value is not None:
                    status = 'NIR'
                else:
                    status = 'NO STATUS'
                notes = row[3].value
                property_number = row[4].value
                component_type = row[5].value
                serial_number = row[6].value
                component_rev = row[7].value
                physical_location = row[8].value
                asset_number = row[9].value

                if serial_number is not None:
                    recordExists = coDict.get(serial_number, 0)
                    if recordExists:
                        coDict[serial_number] = [status, notes, property_number, component_type, serial_number,
                                                 component_rev, physical_location, asset_number]
                        add_new_item(conn, status, notes, property_number, component_type, serial_number, component_rev,
                                     physical_location, asset_number)
                    else:
                        print("Identical serial number on serial number " + serial_number + "Item skipped")

            rowCnt += 1
        conn.commit()

    except Exception as e:
        print("failure reading CO data")
        print(e)
        exit(-1)


def createDb():
    """
    connect (and create if non-existent) database
    :param:
    :return: connection or error
    """
    try:
        # absolute path of or to store database
        database = "/home/ksalvas/Documents/co/codb.db"

        # SQL statement to create coData table (parameters based on test.xlsm "codb" worksheet)
        sql_create_coData_table = """CREATE TABLE IF NOT EXISTS coData (
            status VARCHAR(5),
            notes TEXT,
            property_number VARCHAR(50) NOT NULL,
            component_type TEXT,
            serial_number VARCHAR(20) NOT NULL PRIMARY KEY,
            component_rev TEXT NOT NULL,
            physical_location TEXT NOT NULL,
            asset_number INT(15) NOT NULL
            );"""

        # create a database connection
        conn = create_connection(database)
        if conn is not None:
            # create coData table
            create_table(conn, sql_create_coData_table)
        else:
            print("Error! Cannot create the database connection.")

        return (conn)
    except Exception as e:
        print(e)


def add_new_item(conn, status, notes, property_number, component_type, serial_number, component_rev, physical_location,
                 asset_number):
    """
    add item to database
    :param conn: Connection object
    :param status: string ('OK', 'CVI', 'NIR', or None)
    :param notes: string
    :param property_number: string
    :param component_type: string
    :param serial_number: string
    :param component_rev: string
    :param physical_location: string
    :param asset_number: string
    :return: ...
    """
    conn.execute("INSERT OR REPLACE INTO coData VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                 .format(status, notes, property_number, component_type, serial_number, component_rev,
                         physical_location, asset_number))

    conn = conn.cursor()
    return conn.lastrowid


def select_item_by_serial_number(conn, serial_number):
    """
    print all info of item in database by searching serial_number using SQL
    :param conn: Connection object
    :param serial_number: string
    :return: 0 if no results
    """
    cur = conn.cursor()

    cur.execute("select * from coData where serial_number = '{}'".format(serial_number))

    rows = cur.fetchall()

    if len(rows) == 0:
        print("No rows to be displayed.")
        return 0
    else:
        # print("{} Result(s):".format(rows))
        for row in rows:
            print(row)


def print_inventory(conn, table):
    """
    print all items in table in numbered list
    :param conn: Connection object
    :param table: name of table
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM CoData")

    rows = cur.fetchall()
    num_rows = len(rows)
    item_num = 1

    print("{} Items in {} Inventory:".format(num_rows, table))
    for row in rows:
        print "{}".format(item_num),
        print(row)
        item_num += 1


def get_num_returned_rows(conn, sql_query_statement):
    """
    gets number of rows resulting from query
    :param conn: Connection object
    :param sql_query_statement: SQL query
    :return: number of rows
    """
    cur = conn.cursor()
    cur.execute("{}".format(sql_query_statement))
    num_rows = len(cur.fetchall())

    return num_rows


def get_status_str(new_status):
    """
    converts string of numeric menu option to new status
    :param new_status: string of numeric menu option
    :return: string of new status ("ERR" if invalid menu option)
    """
    if new_status == "1":
        stat_str = "OK"
    elif new_status == "2":
        stat_str = "CVI"
    elif new_status == "3":
        stat_str = "NIR"
    else:
        stat_str = "ERR"

    return stat_str


def edit_status(conn):
    """
    gets user input for item's serial number, prints current status, presents menu for new status,
    changes item's status in database
    :param: None
    :return: None
    """
    cur = conn.cursor()
    print("Updating Status")
    serial_number = input("Please enter serial number: ")

    # If serial_number is not in database, report error and ask user again
    status_query = "SELECT status FROM coData WHERE serial_number = '{}'".format(serial_number)
    cur.execute(status_query)

    # Get numbers of results
    num_rows = get_num_returned_rows(conn, status_query)

    # If 0 results, not in database; prompt user for valid serial_number
    while num_rows == 0:
        serial_number = input("Serial number '{}' is not in our database. "
                              "Please enter a valid serial number: ".format(serial_number))
        status_query = "SELECT status FROM coData WHERE serial_number = '{}'".format(serial_number)
        cur.execute(status_query)
        num_rows = get_num_returned_rows(conn, status_query)

    # If serial_number IS valid, update status
    else:
        # Save old status
        cur.execute("select status from coData where serial_number = '{}'".format(serial_number))

        # Fetches row and saves status string to oldS var
        oldS = cur.fetchone()[0]

        if oldS == 'NO STATUS':
            print("'{}' has {}.".format(serial_number, oldS))
        else:
            print("The current status for '{}' is {}".format(serial_number, oldS))

        # Update status
        message = "Please select one of the following numeric options for the new status: " \
                  "\n(1)\tOK" \
                  "\n(2)\tCVI" \
                  "\n(3)\tNIR\n"
        num_menu_option = input(message)
        new_status = get_status_str(num_menu_option)

        # Verify that user's chosen menu option is valid and that the new status is not the same as the old status
        while new_status is "ERR":
            num_menu_option = input("ERROR: Not a valid menu option. "
                                    "Please select (1), (2), or (3) to update status.\n"
                                    "{}".format(message))
            new_status = get_status_str(num_menu_option)
        else:
            while oldS == new_status:
                num_menu_option = input("ERROR: The status of serial number '{}' is already {}. "
                                        "Please select a different status.\n"
                                        "{}".format(serial_number, oldS, message))
                new_status = get_status_str(num_menu_option)
                # ^NOTE: can edit this while loop to state that no changes were made and simply exit
                #       exhibited in edit_note() function
            else:
                # If no errors, update status in database and output success message
                update_sql_statement = """update coData
                                           set status = '{}'
                                           where serial_number = '{}';""".format(new_status, serial_number)

                cur.execute(update_sql_statement)
                conn.commit()

                # Query new status to display; if matching old status, display error msg; display msg below otherwise
                cur.execute(status_query)
                newS = cur.fetchone()[0]

                print("The status of serial number '{}' was successfully changed from {} to {}".format(serial_number,
                                                                                                       oldS, newS))


def overwrite_note(conn):
    """
    gets user input for item's serial number, prints current notes, gets new notes in input,
    changes item's notes in database
    :param conn: Connection object
    :return: None
    """
    # NOTE: For GUI, can edit code so that user can truly edit notes, not just enter completely new notes

    cur = conn.cursor()
    print("Editing Notes")
    serial_number = input("Please enter serial number: ")

    # If serial_number is not in database, report error and ask user again
    status_query = "SELECT notes FROM coData WHERE serial_number = '{}'".format(serial_number)
    cur.execute(status_query)

    # Get numbers of results
    num_rows = get_num_returned_rows(conn, status_query)

    # If 0 results, not in database; prompt user for valid serial_number
    while num_rows == 0:
        serial_number = input("Serial number '{}' is not in our database. "
                              "Please enter a valid serial number: ".format(serial_number))
        status_query = "SELECT status FROM coData WHERE serial_number = '{}'".format(serial_number)
        cur.execute(status_query)
        num_rows = get_num_returned_rows(conn, status_query)

    # If serial_number IS valid, update status
    else:
        # Save old status
        cur.execute("select status from coData where serial_number = '{}'".format(serial_number))

        # Fetches row and saves status string to old_notes var
        old_notes = cur.fetchone()[0]

        if old_notes == 'NO STATUS':
            print("'{}' has {}.".format(serial_number, old_notes))
        else:
            print("The current status for '{}' is {}".format(serial_number, old_notes))

        # Update status
        message = "Please select one of the following numeric options for the notes change: " \
                  "\n(1)\tOK" \
                  "\n(2)\tCVI" \
                  "\n(3)\tNIR\n"
        num_menu_option = input(message)
        new_notes = get_status_str(num_menu_option)

        # Verify that user's chosen menu option is valid and that the new status is not the same as the old status
        while new_notes is "ERR":
            num_menu_option = input("ERROR: Not a valid menu option. "
                                    "Please select (1), (2), or (3) to update status.\n"
                                    "{}".format(message))
            new_notes = get_status_str(num_menu_option)
        else:
            while old_notes == new_notes:
                print("No changes made to the notes of '{}'.".format(serial_number))
                # ^NOTE: can edit this while loop to state that user must change the note and re-prompt until they do
                #       exhibited in edit_status() function
                break
            # else:
            #     # If no errors, update note in database and output success message
            #     update_sql_statement = """update coData
            #                                set status = '{}'
            #                                where serial_number = '{}';""".format(new_notes, serial_number)
            #
            #     cur.execute(update_sql_statement)
            #     conn.commit()
            #
            #     # Query new status to display; if matching old status, display error msg; display msg below otherwise
            #     cur.execute(status_query)
            #     newS = cur.fetchone()[0]
            #
            #     print(
            #         "The status of serial number '{}' was successfully changed from {} to {}".format(serial_number,
            #                                                                                          old_notes, newS))


def editing_menu(conn):
    """
    gives user menu for editing either Status or Notes
    calls either editStatus or editNote methods
    :param: None
    :return: None
    """
    message = "What would you like to edit?\n(1)\tStatus\n(2)\tNotes\n"
    user_choice = input(message)
    while user_choice not in "12":
        user_choice = input(message)
    if user_choice == "1":
        edit_status(conn)
    elif user_choice == "2":
        overwrite_note(conn)


def print_tables(conn):
    """
    queries database and prints out list of tables in database
    :param conn: Connection object
    :return:
    """
    cur = conn.cursor()

    cur.execute("select name from sqlite_master where type = 'table'")
    rows = cur.fetchall()
    num_rows = len(rows)
    item_num = 1

    print("{} Table(s) in Database".format(num_rows))
    for row in rows:
        print "{}".format(item_num),
        print(row[0])
        item_num += 1


def print_table_fields(conn, t_name):
    """
    queries database and prints out list of columns in table
    :param conn: Connection Object
    :param t_name: table name
    :return:
    """
    cur = conn.cursor()

    cur.execute("select * from {}".format(t_name))
    names = list(map(lambda x: x[0], cur.description))
    # print(names)
    num_rows = len(names)
    item_num = 1

    print("{} Column(s) in '{}' Table".format(num_rows, t_name))
    for name in names:
        print "{}\t".format(item_num),
        print(name)
        item_num += 1


def main():
    """
    read in data/items from Excel Worksheet and export to SQL database
    """
    codb_conn = createDb()

    # coFileName = "/home/ksalvas/Documents/co/coDocs/test_results.xlsm"
    # wb = openpyxl.load_workbook(coFileName, read_only=True, data_only=True)
    #
    # # Print name of sheets in workbook
    # sheetNameList = wb.sheetnames
    # print "Sheet names:",
    # for names in sheetNameList:
    #     print names,
    # print("\n")

    # sheet_name = "Room SGC"
    #
    # PROPERTY_NUMBER
    # HOSTNAME
    # COMPONENT_TYPE
    # MANUFACTURER
    # MODEL_NUMBER
    # SERIAL_NUMBER
    # COMPONENT_REV
    # PHYSICAL_LOCATION
    # ASSET_NUMBER
    #
    # # USE ONCE: Create and populate table to initialize database
    # create_table(codb_conn)
    # populate_table(codb_conn, wb, sheet_name)
    # INSERT status enum into table first

    try:  # test area

        # # Print out all items in room inventory
        # print_inventory(codb_conn, sheet_name)

        # # Print item info by searching serial_number 115
        # select_item_by_serial_number(codb_conn, '115')

        # overwrite_note(codb_conn)

        # print_table_fields(codb_conn, "coData")
        editing_menu(codb_conn)

        codb_conn.commit()
    except Exception as e:
        # print("failure reading CO data")
        print(e)
        exit(-1)


main()
