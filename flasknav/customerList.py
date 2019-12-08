# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 20:23:57 2019

@author: 014892317
"""
import dbtasks

# Call function in dbtasks file to return all student files.
customers = dbtasks.getCustomers()

if isinstance(customers, str):
    print('Error Occured. ' + customers)
else:
    for customer in customers:
        print(customer['cusId'], customer['cusFname'], customer['cusLname'], customer['cusState'], customer['cusSalesYTD'], customer['cusSalesPrev'])



        

