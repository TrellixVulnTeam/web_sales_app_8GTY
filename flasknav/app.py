from flask import Flask, render_template, request
from flasknav import dbtasks
from datetime import datetime
import csv
import os

UPLOAD_FOLDER = os.getcwd() + "/uploads/"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/testing', methods=['POST', 'GET'])
def test():
    myDict = {'a': 'apple', 'b': 'banana'}
    # return (myDict)
    return render_template('testing.html', myDict=myDict)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/customer', methods=['POST', 'GET'])
def customer():
    if request.method == 'GET':
        totRec = dbtasks.totRecords()
        # Empty customers dictionary for GET
        customer = {}
        return render_template('manage_customers.html', totRec=totRec, customer=customer)

    if request.method == 'POST':
        source = 'POST'
        totRec = dbtasks.totRecords()
        customer = request.form
        cusRecords = dbtasks.findCustomers(customer)

        # return (cusRecords)
        return render_template('manage_customers.html', totRec=totRec, customer=customer, cusRecords=cusRecords,
                               source=source)


@app.route('/delete/<cusId>', methods=['POST', 'GET'])
def delete(cusId):
    if request.method == 'GET':
        # Retrieve customer information and send to delete form
        customer = dbtasks.findCustomerById(cusId)
        return render_template('delete.html', customer=customer)

    if request.method == 'POST':
        customer = request.form
        msg = dbtasks.deleteCustomerById(cusId)
        if msg == 1:
            message = 'Customer Deleted Successfully'
        else:
            message = 'Error Deleting Customer.  Error: ' + msg

        return render_template('message.html', message=message)


@app.route('/update/<cusId>', methods=['POST', 'GET'])
def update(cusId):
    if request.method == 'GET':
        # Retrieve customer information and send to update form
        source = 'GET'
        customer = dbtasks.findCustomerById(cusId)
        return render_template('update.html', source=source, customer=customer)

    if request.method == 'POST':
        source = 'POST'
        customer = request.form
        msg = dbtasks.updateCustomer(customer)
        if msg == 1:
            message = 'Customer Updated Successfully'
            return render_template('message.html', message=message, customer=customer)
        else:
            message = 'Error Updating Customer.  Message: ' + msg
            return render_template('update.html', message=message, customer=customer)


@app.route('/newcustomer', methods=['POST', 'GET'])
def newcustomer():
    if request.method == 'GET':
        return render_template('newcustomer.html')

    # if it's not a GET request then it must be a POST
    # get the data from the form and check required fields
    customer = request.form
    message = ""
    valid_data = True

    # if required fields are blank return an appropriate message
    if not request.form.get("cusId"):
        valid_data = False
        message += "".join('You must enter a customer ID. | ')
    if not request.form.get("cusFname"):
        valid_data = False
        message += "".join('You must enter a first name. | ')
    if not request.form.get("cusLname"):
        valid_data = False
        message += "".join('You must enter a last name.')

    if not valid_data:
        return render_template('newcustomer.html', message=message, customer=customer)

    # they filled out at least the required fields now check to
    # see if the customer that they're adding already exists
    cusRecords = dbtasks.findCustomers(customer)

    # if we found the customer it's a duplicate and we shouldn't add it
    if cusRecords:
        message = 'Customer Record Already Exists.'
        return render_template('newcustomer.html', message=message, customer=customer)

    # else we attempt to add the record to the db
    else:
        msg = dbtasks.insertCustomer(customer)
        if msg == 1:
            message = 'Customer Record Added Successfully.'
            return render_template('newcustomer.html', message=message, customer=customer)
        else:
            message = 'Error Adding Customer Record.  Message: ' + msg
            return render_template('newcustomer.html', message=message, customer=customer)


# return (cusRecords) return render_template('manage_customers.html', totRec=totRec, customer=customer,
# cusRecords=cusRecords, source=source)

@app.route('/import_file', methods=['GET', 'POST'])
def import_file():
    if request.method == 'POST':
        file = request.files['txtfile']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with open(app.config['UPLOAD_FOLDER'] + filename) as import_file:
            collection = [tuple(line) for line in csv.reader(import_file, delimiter=" ")]

        totRecProcessed = len(collection)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        errfile = filename[: -4] + "_errors_" + now + ".txt"

        totRecInserted = dbtasks.sql_insert_customer(collection, errfile)
        totRec = dbtasks.totRecords()

        return render_template("import_file.html", filename=filename, totRec=totRec,
                               totRecProcessed=totRecProcessed, totRecInserted=totRecInserted)

    if request.method == 'GET':
        totRec = dbtasks.totRecords()
        return render_template('import_file.html', totRec=totRec)





@app.route('/export')
def export():
    return render_template('export.html')


@app.route('/reports', methods=['POST', 'GET'])
def reports():
    if request.method == 'GET':
        source = 'GET'
        totRec = dbtasks.totRecords()
        return render_template('reports.html', source=source, totRec=totRec)

    if request.method == 'POST':
        source = 'POST'
        report = request.form
        result = dbtasks.reports(report['report'])
        # return render_template('reports.html', msg=msg, totRec=totRec, status=status, file=file)
        return render_template('reports.html', source=source, result=result)


# @app.route('/inputfilenames')
# def input_filenames():
#     return render_template('input_filenames.html')


# @app.route('/result_fileprocess', methods=['POST', 'GET'])
# def result_fileprocess():
#     if request.method == 'POST':
#         files = request.form
#         txtfile = files['txtfile']
#         dbfile = files['dbfile']
#         errorfile = 'input_error.txt'
#         status = 'Success'
#
#         with open(txtfile, mode='r') as stufile:
#             for record in stufile:
#                 rec = record.split()
#                 msg = sql_insert_customer(rec, errorfile)
#                 if msg != 'Success':
#                     status = msg
#         return render_template('result_fileprocess.html', status=status, errorfile=errorfile)


# @app.route('/customerresult', methods=['POST', 'GET'])
# def customerresult():
#     if request.method == 'POST':
#         customer = request.form
#         return render_template("customerresult.html", customer=customer)


if __name__ == '__main__':
    app.run(debug=True)
