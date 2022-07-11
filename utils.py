from model import Items, Invoices, db


def check_if_item_exist(item_id, user):
    """
    Check if item exist in the database and if it belongs to the user
    """
    item = Items.query.filter_by(item_id=item_id).first()
    if item:
        if item.user == user:
            return True


def get_item_info(item_id):
    """
    Gets the name and the price of an item
    """
    item = Items.query.filter_by(item_id=item_id).first()
    item_info = [item.item_name, item.item_price]
    return item_info


def trigger_update_total(price, invoice_id):
    """
    Used to update the total amount of $ an invoice when invoice lines are created, updated or deleted.
    """
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    invoice.total = invoice.total + price
    db.session.commit()
