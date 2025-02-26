from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _check_email_already_exists(self):
        group_purchase_manager_ids = self.env.ref('purchase.group_purchase_manager')
        puchase_manager_emails = group_purchase_manager_ids.users.filtered(lambda x: x.email).mapped('email')
        if self.env.user.email in puchase_manager_emails:
            puchase_manager_emails.remove(self.env.user.email)
            return puchase_manager_emails
        return puchase_manager_emails

    def button_confirm(self):
        subject = 'PURCHASE ORDER CONFIRM : %s' % (self.name)
        email_values = {
            'email_to': self.env.user.email,
            'email_cc': ",".join(self._check_email_already_exists()),
            'subject': subject,
        }
        template_id = self.env.ref('odb_purchase_management.purchase_order_confirm_mail')
        template_id.send_mail(self.id, email_values=email_values)
        return super(PurchaseOrder,self).button_confirm()
