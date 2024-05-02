# -*- coding: utf-8 -*-from fastapi import APIRouter
from fastapi import APIRouter
from integrations.sageoneclient import SageOneAPIClient
from integrations.investec import InvestecAPIClient
from utils import get_config
import dateutil.parser
import datetime
import re

router = APIRouter()

@router.get("/companies")
def get_sage_companies() -> list:
    """
    Retrieves the companies in Sage One
    """
    config = get_config() # Get the config
    sage_client = SageOneAPIClient(config.get("sageone", "url"), config.get("sageone", "api_key"), config.get("sageone", "username"), config.get("sageone", "password"))
    return sage_client.get_companies()

@router.get("/bankaccounts")
def get_sage_bank_accounts(company_id: int) -> list:
    """
    Retrieves the bank accounts for a company in Sage One

    **company_id** The Company ID
    """
    config = get_config() # Get the config
    sage_client = SageOneAPIClient(config.get("sageone", "url"), config.get("sageone", "api_key"), config.get("sageone", "username"), config.get("sageone", "password"))
    return sage_client.get_company_bank_accounts(company_id)

@router.post("/syncallbankaccounts")
def import_investec_transactions(from_date: datetime.date, to_date: datetime.date) -> dict:
    config = get_config() # Get the config
    sage_client = SageOneAPIClient(config.get("sageone", "url"), config.get("sageone", "api_key"), config.get("sageone", "username"), config.get("sageone", "password"))
    investec_client = InvestecAPIClient(config.get("investec", "client_id"), config.get("investec", "secret"), config.get("investec", "api_key"))

    # Get all the investec bank accounts
    investec_bank_accounts = dict()
    investec_resp = investec_client.get_accounts()
    for rr in investec_resp:
        investec_bank_accounts[rr["accountNumber"]] = rr

    bank_accounts_found = list()
    bank_accounts_notfound = list()

    # Get all the companies in Sage
    companies = sage_client.get_companies()
    for c in companies:
        company_id = c["ID"]
        company_name = c["Name"]

        # Get the bank accounts
        sage_bank_accounts = sage_client.get_company_bank_accounts(company_id)
        for b in sage_bank_accounts:
            bank_account_id = b["ID"]
            bank_account_number = b["AccountNumber"]
            bank_account_name = b["Name"]
            bank_name = b["BankName"]

            report_data = dict(sage=b, investec=dict())
            if bank_account_number in investec_bank_accounts:
                investec_bank_details = investec_bank_accounts[bank_account_number]
                report_data["investec"] = investec_bank_details
                bank_accounts_found.append(report_data)
                # merge the transactions
                import_investec_transactions(company_id, bank_account_id, investec_bank_details["accountId"], from_date, to_date)
            else:
                bank_accounts_notfound.append(report_data)
    return dict(matched=bank_accounts_found, not_matched=bank_accounts_notfound)

@router.post("/synctransactions")
def import_investec_transactions(sage_company_id: int, sage_bank_account_id: int, investec_bank_account_id: int, from_date: datetime.date, to_date: datetime.date) -> int:
    """
    Import transaction from Investec to Sage One for a certain date period.

    **sage_company_id** The company ID

    **sage_bank_account_id** The Sage bank account ID to import the transactions into

    **investec_bank_account_id** The Investec bank account ID to export the transactions from

    **from_date** Import from this date (inclusive)

    **to_date** Import to this date (inclusive)

    **returns** The total number of transactions imported into Sage One
    """
    config = get_config() # Get the config
    sage_client = SageOneAPIClient(config.get("sageone", "url"), config.get("sageone", "api_key"), config.get("sageone", "username"), config.get("sageone", "password"))
    investec_client = InvestecAPIClient(config.get("investec", "client_id"), config.get("investec", "secret"), config.get("investec", "api_key"))
    # Get the default account types to assign to income and expenses
    accounts = sage_client.get_company_unallocated_accounts(sage_company_id)
    unallocated_income_id =  accounts["Income"]["ID"]
    unallocated_expense_id =  accounts["Expenses"]["ID"]
    # Get the txt types
    tax_types = sage_client.get_company_tax_types(sage_company_id)
    # Get a list of the transactions already in Sage
    imported_transactions = list()
    manual_transactions = list()
    sage_transactions = sage_client.get_company_bank_account_transactions(sage_company_id, sage_bank_account_id, from_date, to_date)
    valid_sha256 = re.compile(r"^[a-f0-9]{64}(:.+)?$", re.IGNORECASE)
    for st in sage_transactions:
        bank_identifier = st.get("BankUniqueIdentifier")
        if bank_identifier and valid_sha256.match(bank_identifier):
            imported_transactions.append(st["BankUniqueIdentifier"])
        else:
            manual_transactions.append(st)
    transactions = investec_client.get_account_transactions(investec_bank_account_id, from_date, to_date)
    new_transactions = list()
    total_imported = 0
    for trx in transactions:
        trx_type = trx["type"]
        trx_exclusive = trx["amount"]
        trx_description = trx["description"]
        trx_transaction_date = trx["postingDate"]
        if trx_type == "DEBIT":
            trx_exclusive *= -1
        trx_tax = 0.00
        trx_total = trx_exclusive + trx_tax
        hex_digest = trx["transactionHash"]
        if hex_digest in imported_transactions:
            continue # Already imported
        transaction_date = dateutil.parser.isoparse(trx_transaction_date).strftime("%Y-%m-%dT00:00:00Z")
        t_data = {
            "ID": 0,
            "Date": transaction_date,
            "BankAccountId": sage_bank_account_id,
            "Type": 1, # Account
            "SelectionId": unallocated_expense_id if trx_type == "DEBIT" else unallocated_income_id,
            "Description": trx_description,
            "TaxTypeId": 0,
            "Exclusive": trx_exclusive,
            "Tax": trx_tax,
            "Total": trx_total,
            "Reconciled": True,
            "BankUniqueIdentifier": hex_digest,
            "Editable": True,
            "Accepted": False
        }
        # Check if there is a manually captured transaction that matches this one
        for m in manual_transactions:
            if m["Date"] == transaction_date and m["Total"] == trx_total:
                m["BankUniqueIdentifier"] = hex_digest
                t_data = m
                break
        else:
            total_imported += 1
        new_transactions.append(t_data)
        if len(new_transactions) == 100:
            sage_client.save_company_bank_account_transactions(sage_company_id, new_transactions)
            new_transactions = list()
    if new_transactions:
        sage_client.save_company_bank_account_transactions(sage_company_id, new_transactions)
    return total_imported
