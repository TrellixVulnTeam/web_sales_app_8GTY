import sqlite3
import csv

# Hard coded database name.  Real-world, use a config file
dbname = 'customers.db'
con = sqlite3.connect(dbname)


def getCustomers():
    """ Function will return all customers in the database """
    sqlCmd = 'SELECT * FROM customer'

    con = sqlite3.connect(dbname)
    con.row_factory = sqlite3.Row
    curs = con.cursor()

    try:
        curs.execute(sqlCmd)
        records = curs.fetchall()
    except Exception as e:
        return ('Error ' + str(e))
    else:
        return records
    finally:
        con.close()


def totRecords():
    # Assume no errors, can add try except blocks
    con = sqlite3.connect(dbname)
    curs = con.cursor()
    curs.execute('SELECT COUNT(*) FROM customer')
    record = curs.fetchall()
    con.close()
    return record[0][0]


def findCustomers(pDict):
    # This is vulnerable to sql injection attacks
    sqlCmd = "1 = 1"
    if pDict['cusId'] != '':
        sqlCmd += " and cusId = " + pDict['cusId'].upper()
    if pDict['cusFname'] != '':
        sqlCmd += " and upper(cusFname) like '" + pDict['cusFname'].upper() + "%'"
    if pDict['cusLname'] != '':
        sqlCmd += " and upper(cusLname) like '" + pDict['cusLname'].upper() + "%'"
    if pDict['cusState'] != '':
        sqlCmd += " and upper(cusState) like '" + pDict['cusState'].upper() + "%'"
    if pDict['cusSalesYTD'] != '':
        sqlCmd += ' and cusSalesYTD >= ' + pDict['cusSalesYTD']
    if pDict['cusSalesPrev'] != '':
        sqlCmd += ' and cusSalesPrev >= ' + pDict['cusSalesPrev']

    sqlCmd = 'SELECT * FROM customer WHERE ' + sqlCmd

    con = sqlite3.connect(dbname)
    con.row_factory = sqlite3.Row
    curs = con.cursor()
    try:
        curs.execute(sqlCmd)
        record = curs.fetchall()
        return record
    except Exception as e:
        return 'Error ' + str(e)
    finally:
        con.close()


def findCustomerById(cId):
    sqlCmd = 'SELECT * FROM customer WHERE cusId = ?'

    con = sqlite3.connect(dbname)
    con.row_factory = sqlite3.Row
    curs = con.cursor()
    try:
        curs.execute(sqlCmd, (cId,))
        record = curs.fetchall()
    except Exception as e:
        return ('Error ' + str(e))
    else:
        return record
    finally:
        con.close()


def deleteCustomerById(cId):
    sqlCmd = 'DELETE FROM customer WHERE cusId = ?'
    con = sqlite3.connect(dbname)
    con.row_factory = sqlite3.Row
    curs = con.cursor()
    try:
        curs.execute(sqlCmd, (cId,))
        rowcount = curs.rowcount
        con.commit()
    except Exception as e:
        return ('Error ' + str(e))
    else:
        return rowcount
    finally:
        con.close()


def updateCustomer(pDict):
    con = sqlite3.connect(dbname)
    curs = con.cursor()
    try:
        sqlCmd = """UPDATE Customer 
                    SET cusFname = ?, cusLname = ?, cusState = ?, cusSalesYTD = ?, cusSalesPrev = ?
                    WHERE cusId = ?"""
        curs.execute(sqlCmd, (pDict['cusFname'], pDict['cusLname'], pDict['cusState'], float(pDict['cusSalesYTD']),
                              float(pDict['cusSalesPrev']), int(pDict['cusId'])))
        rowcount = curs.rowcount
        con.commit()
    except Exception as e:
        return ('Error ' + str(e))
    else:
        return rowcount
    finally:
        con.close()


def insertCustomer(pDict):
    con = sqlite3.connect(dbname)
    curs = con.cursor()
    try:
        sqlCmd = """INSERT INTO customer
                    (cusId, cusFname, cusLname, cusState, cusSalesYTD, cusSalesPrev) 
                    VALUES(?, ?, ?, ?, ?, ?)"""
        curs.execute(sqlCmd,
                     (pDict['cusId'], pDict['cusFname'], pDict['cusLname'], pDict['cusState'],
                      float(pDict['cusSalesYTD']),
                      float(pDict['cusSalesPrev'])))
        con.commit()
    except Exception as e:
        return 'Error ' + str(e)
    else:
        return 1
    finally:
        con.close()


def reports(id):
    if id == '1':
        sqlCmd = """ SELECT *
                     FROM customer 
                     ORDER BY cusLname, cusFname"""
    if id == '2':
        sqlCmd = """ SELECT *
                     FROM customer 
                     ORDER BY cusSalesYTD DESC"""
    if id == '3':
        sqlCmd = """ SELECT *
                     FROM customer
                     ORDER BY RANDOM() LIMIT 3"""

    con = sqlite3.connect(dbname)
    con.row_factory = sqlite3.Row
    curs = con.cursor()

    try:
        curs.execute(sqlCmd)
        records = curs.fetchall()

    except Exception as e:
        return 'error ' + str(e)

    else:
        return records

    finally:
        con.close()


def sql_insert_customer(collection, errfile):
    # Create cursor and execute insert statement
    con = sqlite3.connect(dbname)
    curs = con.cursor()
    # Use exception handling
    totRecInserted = 0
    for row in collection:
        try:
            curs.execute(
                'INSERT INTO customer(cusId, cusFname, cusLname, cusState, cusSalesYTD, cusSalesPrev) '
                'VALUES(?, ?, ?, ?, ?, ?)', row)
            con.commit()
            totRecInserted += 1
        except sqlite3.IntegrityError as e:
            with open(errfile, mode='a') as errorfile:
                print(row, 'Error: ' + str(e), end='\n', file=errorfile)
        except Exception as e:
            print('exception', str(e))
            return 'Error' + str(e)

    return totRecInserted


def export_file(filename):
    con = sqlite3.connect(dbname)
    db_records = getCustomers()
    totRec = totRecords()

    with open(filename, mode='w') as export_file:
        export_writer = csv.writer(export_file, delimiter=' ')
        for record in db_records:
            export_writer.writerow(record)

    return totRec
