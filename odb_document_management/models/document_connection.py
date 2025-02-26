from odoo import fields, models,_
from smb.SMBConnection import SMBConnection

class DocumentConnection(models.Model):
    _name = 'document.connection'
    _description = "Document Connection"

    name = fields.Char('Name', required=True)
    username = fields.Char('UserName', required=True)
    password = fields.Char('PassWord', required=True)
    url_connection = fields.Char('Url Of Connection', required=True)
    type_connection = fields.Selection(
        string='Type Of Connection',
        selection=[('zshare', 'Z Share')],
        default="zshare"
    )
    ssl = fields.Boolean('SSL', default=False)
    
    def action_test_connection(self):
        server_ip = "172.16.0.100"
        server_name = 'D8'
        share_name = "backup"
        network_username = 'nguyen.tv@districteightdesign.com'
        network_password = 'D8company'
        machine_name = ''
        conn = SMBConnection(network_username, network_password, machine_name, server_name, use_ntlm_v2 = True)
        conn.connect(server_ip, 445)
        files = conn.listPath(share_name, "/04.Odoo/05.Backup/03.Demo14")
        for x in files:
            print(x)
        pass