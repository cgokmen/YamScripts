from yamsdaq_models import Company, Stock, ValuePoint
from controllers import transfer_account_money, get_account_balance, get_treasury_account
import settings

def getStockValueTaxAmount(value):
    return value * settings.STOCKTAX

def getCompanyFromCode(session, code):
    return session.query(Company).filter(Company.code == code).first()

def getCompanyCurrentPrice(session, company):
    return session.query(ValuePoint).filter(ValuePoint.company_code == company.code).order_by(ValuePoint.datetime.desc()).first().value

def getAccountStocks(session, account, company):
    companyStock = session.query(Stock).filter(Stock.company_code == company.code and Stock.owner_name == account.name).first()

    return companyStock

def addAccountStocks(session, account, company, count, price):
    # Find if the user owns any stocks in this company
    companyStock = getAccountStocks(session, account, company)

    # Create a stock obj if he doesnt
    if companyStock is None:
        companyStock = Stock(owner_number=account.number, company_code=company.code, count=0, value_per_stock_at_purchase=0)
        session.add(companyStock)
        session.commit()

    # What shall the value per stock be
    oldCount = companyStock.count
    oldValue = companyStock.value_per_stock_at_purchase

    addCount = count
    addValue = price

    totalCount = oldCount + addCount
    totalValue = (oldValue * oldCount + addValue * addCount) / float(totalCount)

    # Lets set the values
    companyStock.count = totalCount
    companyStock.value_per_stock_at_purchase = totalValue

def removeAccountStocks(session, account, company, count):
    # Find if the user owns any stocks in this company
    companyStock = getAccountStocks(session, account, company)

    if companyStock is None:
        # He does not, return false.
        raise ValueError("You do not have stocks in this company.")

    if companyStock.count < count:
        # Not enough stocks
        raise ValueError("You have fewer stocks in this company than the amount you wish to sell.")

    # Check if he is selling his entire stock
    if companyStock.count == count:
        # Then we just destroy the thing
        session.delete(companyStock)
    else:
        companyStock.count -= count

def buyAccountStocks(session, account, company, count):
    # Get stock value
    valuePerStock = getCompanyCurrentPrice(session, company)
    totalPrice = valuePerStock * count

    # Do the transaction
    transfer_account_money(session, account, get_treasury_account(session), totalPrice)
    addAccountStocks(session, account, company, count, valuePerStock)

def sellUserStocks(session, account, company, count):
    # Get stock value
    valuePerStock = getCompanyCurrentPrice(session, company)
    totalPrice = valuePerStock * count

    # Do the transaction
    treasury = get_treasury_account(session)
    if get_account_balance(treasury) > totalPrice:
        removeAccountStocks(session, account, company, count)
        transfer_account_money(session, treasury, account, totalPrice)
    else:
        raise ValueError("The Treasury does not have adequate funds to buy these stocks from you.")