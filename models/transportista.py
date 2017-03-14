# -*- encoding: utf-8 -*-
from openerp import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    transportista = fields.Boolean("Transportista", default=False)
