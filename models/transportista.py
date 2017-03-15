# -*- encoding: utf-8 -*-
from openerp import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    transportista = fields.Boolean("Transportista", default=False)
    property_account_supplier_advance = fields.Many2one('account.account', string="Cuenta anticipo proveedores", domain="[('type','!=','view')]",
    	help="This account will be used for advance payment of suppliers")
