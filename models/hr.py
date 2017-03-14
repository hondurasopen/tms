# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _


class hr_employee(models.Model):
    _description ='Employees'
    _name='hr.employee'
    _inherit='hr.employee'

    transportista = fields.Boolean("Transportista", default=False)