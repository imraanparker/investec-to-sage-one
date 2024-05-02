# -*- coding: utf-8 -*-
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import datetime


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SageOneAPIClient(object):
    """
    Wrapper class for the Sage One South African API
    """

    def __init__(self, api_url, api_key, sage_email, sage_password, version="2.0.0", default_timeout=30):
        """
        Initialise the API. Creates a session to handle the HTTP calls efficiently
        """
        self.requests_sess = requests.Session()
        self.requests_sess.auth = (sage_email, sage_password)
        self.requests_sess.verify = False
        self.api_key = api_key
        self.api = "%s/api/%s" % (api_url, version)
        self.timeout = default_timeout

    def _call(self, service_url: str, method: str, params: dict=None, body: dict=None) -> dict:
        """
        Helper function to call the API

        :param service_url: The service to call
        :param method: The HTTP verb (get or post)
        :param params: The query parameters to send
        :param body: The payload to send
        :returns: The result
        """
        if not params:
            params = dict()
        params["apiKey"] = self.api_key
        request = getattr(self.requests_sess, method)
        headers = {"Accept": "application/json"}
        if method == "post":
            headers["Content-Type"] = "application/json; charset=utf-8"
        response = request("%s/%s" % (self.api, service_url), params=params, json=body, headers=headers, timeout=self.timeout)
        if not response.ok:
            requests.exceptions.HTTPError(response.status_code, response.content)
        response.raise_for_status()
        content = response.json()
        if "data" in content:
            return content["data"]
        return content

    def get_companies(self) -> list:
        """
        Get a list of active companies

        :returns: The active companies for the user
        """
        data = self._call("Company/Get", "get", params={"$filter": "Active eq true", "$select": "ID,Name", "$orderby": "Name"})
        return data["Results"]

    def get_company_unallocated_accounts(self, company_id: int) -> dict:
        """
        Get the unallocated accounts for use in creation of bank transactions

        :param company_id: The company
        :returns: The ID and Name for the unallocated accounts ('Unallocated Income' and 'Unallocated Expense')
        """
        params = {
            "CompanyID": company_id,
            "$filter": "Name eq 'Unallocated Expense' or Name eq 'Unallocated Income'",
            "$select": "ID,Name", "$orderby": "Name"
        }
        data = self._call("Account/Get", "get", params=params)
        results = {"Income": dict(), "Expenses": dict()}
        for d in data["Results"]:
            if "Expense" in d["Name"]:
                results["Expenses"] = {"ID": d["ID"], "Name": d["Name"]}
            elif "Income" in d["Name"]:
                results["Income"] = {"ID": d["ID"], "Name": d["Name"]}
        return results

    def get_company_tax_types(self, company_id: int) -> list:
        """
        Get a list of tax types for a company

        :param company_id: The company
        :returns: The tax types for the company
        """
        params = {
            "CompanyID": company_id,
            "$filter": "Active eq true",
            "$select": "ID,Name,Percentage,IsDefault",
            "$orderby": "Name"
        }
        data = self._call("TaxType/Get", "get", params=params)
        return data["Results"]

    def get_company_bank_accounts(self, company_id: int) -> list:
        """
        Get a list of active bank accounts

        :param company_id: The company
        :returns: The bank accounts for the company
        """
        params = {
            "CompanyID": company_id,
            "$filter": "Active eq true",
            "$select": "ID,Name,BankName,AccountNumber",
            "$orderby": "Name"
        }
        data = self._call("BankAccount/Get", "get", params=params)
        return data["Results"]

    def get_company_bank_account_transactions(self, company_id: int, bank_account_id: int, from_date: datetime=None, to_date: datetime=None) -> list:
        """
        Get a list of transactions for a bank account

        :param company_id: The company that owns the bank account
        :param bank_account_id: The bank account
        :param from_date: Only get transactions from this date (inclusive)
        :param to_date: Only get transactions to this date (inclusive)
        :returns: The bank account transactions
        """
        params = {"CompanyId": company_id, "$orderby": "Date"}
        filters = ["BankAccountId eq %s" % bank_account_id]
        if from_date:
            from_date = from_date - datetime.timedelta(days=1)
            filters.append("Date gt DateTime'%s'" % from_date.strftime("%Y-%m-%d"))
        if to_date:
            to_date = to_date + datetime.timedelta(days=1)
            filters.append("Date lt DateTime'%s'" % to_date.strftime("%Y-%m-%d"))
        if filters:
            params["$filter"] = " and ".join(filters)
        records = list()
        while True:
            data = self._call("BankTransaction/Get", "get", params=params)
            records.extend(data["Results"])
            if len(records) == data["TotalResults"]:
                break
            params["$skip"] = len(records)
        return records

    def save_company_bank_account_transaction(self, company_id: int, transaction: dict) -> dict:
        """
        Saves a bank account transaction

        :param company_id: The company that owns the bank account
        :param transaction: The transaction to save
        :returns: The saved transaction
        """
        params = {"CompanyId": company_id}
        data = self._call("BankTransaction/Save", "post", params=params, body=transaction)
        return data

    def save_company_bank_account_transactions(self, company_id: int, transactions: list) -> list:
        """
        Creates bank transactions (Bulk)

        :param company_id: The company that owns the bank account
        :param transaction: The transactions to save
        :returns: The saved transactions
        """
        params = {"CompanyId": company_id}
        data = self._call("BankTransaction/SaveBatch", "post", params=params, body=transactions)
        return data

