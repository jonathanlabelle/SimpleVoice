from model import Items, Invoices, session, db


def check_if_item_exist(item_id, user):
    item = Items.query.filter_by(item_id=item_id).first()
    if item:
        if item.user == user:
            return True


def get_item_info(item_id):
    item = Items.query.filter_by(item_id=item_id).first()
    item_info = [item.item_name, item.item_price]
    return item_info


def trigger_update_total(price, invoice_id):
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    invoice.total = invoice.total + price
    db.session.commit()
