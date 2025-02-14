from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_email_already_exists(self):
        group_sale_manager_ids = self.env.ref('sales_team.group_sale_manager')
        sale_manager_emails = group_sale_manager_ids.users.filtered(lambda x: x.email).mapped('email')
        if self.env.user.email in sale_manager_emails:
            sale_manager_emails.remove(self.env.user.email)
            return sale_manager_emails
        return sale_manager_emails

    def action_request(self):
        subject = 'ORDER CONFIRMATION SUCESSFUL : %s' % (self.name)
        email_values = {
            'email_to': self.env.user.email,
            'email_cc': ",".join(self._check_email_already_exists()),
            'subject': subject,
        }
        template_id = self.env.ref('odb_sale_management.order_confirmation_successful_mail')
        template_id.send_mail(self.id, email_values=email_values)
        return super(SaleOrder,self).action_request()