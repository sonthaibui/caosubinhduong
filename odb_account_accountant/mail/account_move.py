from odoo import models, fields, api,_

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        email_values = {
                'email_to': self.env.user.email,
                'email_cc': self.create_uid.email,
                'subject': self.name,
            }
        if self.state == 'draft':
            name = self.name
            res = super(AccountMove,self).action_post()
            name_after = self.name
            if self.move_type == 'in_invoice':
                if name != False and name_after != name:
                    template_id = self.env.ref('odb_account_accountant.bill_confirm_mail')
                    email_values.update({'subject':'BILL CONFIRM : %s' % (self.name)})
                    template_id.send_mail(self.id, email_values=email_values)
                    return res
                return res
            elif self.move_type == 'out_invoice':
                if (name != False and name_after != name) or (name != False and name_after == name and (name_after != '/' and name != '/')):
                    email_values.update({'subject':'INVOICE CONFIRM : %s' % (self.name)})
                    template_id = self.env.ref('odb_account_accountant.invoice_confirm_mail')
                    template_id.send_mail(self.id, email_values=email_values)
                    return res
                return res
        else:          
            return super(AccountMove,self).action_post()
