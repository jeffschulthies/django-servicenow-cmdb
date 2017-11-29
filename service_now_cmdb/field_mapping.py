"""
This module contains the function code applied to models to facilitate the ServiceNow Integration.
Be careful when editing this. SNCMBD Handler references function names.

When adding new functions follow this naming convention

------------------
Naming Convention
------------------
Model name + ServiceNow Field

Example:
class IPAddress:
    fieldOne
    fieldTwo
    fieldThree

To create a function for the first field. Define the field in this file.

def ip_address_field_one(model):
    # Some processing
    return val

For readibility, if when adding a new model add the following comment,

# ------------------
# Model Name
# ------------------
"""

