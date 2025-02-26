from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    def prepare_list_mail(self):
        self.ensure_one()
        group_account_invoice= self.env.ref('account.group_account_invoice')
        emails_group_account = group_account_invoice.users.filtered(lambda x: x.email).mapped('email')
        sale_person = self.sale_id.user_id
        if sale_person.email:
            list_mail = emails_group_account + [sale_person.email,self.create_uid.email]
        else:
            list_mail = emails_group_account + [self.create_uid.email]
        if sale_person.employee_id.parent_id.work_email:
            list_mail += [sale_person.employee_id.parent_id.work_email]
        return list(set(list_mail))

    def action_post(self):
        email_cc = self.prepare_list_mail()
        if self.state == 'draft':
            email_values = {
                'email_to': self.env.user.email,
                'email_cc': ",".join(email_cc),
                'subject': self.name,
            }
            name = self.name
            res = super(AccountPayment, self).action_post()
            name_after = self.name
            template_id = self.env.ref('odb_account_accountant.payment_confirm_mail')
            if self.partner_type == 'customer':
                if (name != False and name_after != name) or (name != False and name_after == name and (name_after != '/' and name != '/')):
                    email_values.update(
                        {'subject': 'CUSTOMER PAYMENT CONFIRM : %s' % (self.name)})
                    template_id.send_mail(self.id, email_values=email_values)
                    return res
                return res
            elif self.partner_type == 'supplier':
                if (name != False and name_after != name) or (name != False and name_after == name and (name_after != '/' and name != '/')):
                    email_values.update(
                        {'subject': 'VENDOR PAYMENT CONFIRM : %s' % (self.name)})
                    template_id.send_mail(self.id, email_values=email_values)
                    return res
                return res
        return super(AccountPayment,self).action_post()
