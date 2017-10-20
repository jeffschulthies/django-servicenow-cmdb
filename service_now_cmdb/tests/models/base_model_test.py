from service_now_cmdb.tests.base_test import BaseTest


class BaseModelTest(BaseTest):
    error_response = '{"error_description":"access_denied","error":"server_error"}'
    successful_response = '{"access_token":"sl6HfrB9Td5m4hy8MOwmzNV_NP4muV0zXLi-b3hQSxqHZuOnnXn53U8hiZpWk4_gP9rSzWzxm_uVnYnKEtNLJQ","refresh_token":"Qh2LwLUc-HXskeh58aQNCG_56yI3lPj_X8w9BU0rbwSNVmhiqfmG8hW8jBFap-6G5A_uDL8dJkIryrutniSzdw","scope":"useraccount","token_type":"Bearer","expires_in":1799}'
    access_token = "sl6HfrB9Td5m4hy8MOwmzNV_NP4muV0zXLi-b3hQSxqHZuOnnXn53U8hiZpWk4_gP9rSzWzxm_uVnYnKEtNLJQ"  # These tokens will be used to test the updating method
    refresh_token = "Qh2LwLUc-HXskeh58aQNCG_56yI3lPj_X8w9BU0rbwSNVmhiqfmG8hW8jBFap-6G5A_uDL8dJkIryrutniSzdw"

