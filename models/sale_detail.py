# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Salefleet(models.Model):
    _inherit = 'sale.order'

    transportista_id = fields.Many2one("res.partner", "Transportista", domain=[('transportista','=',True)])
    empleado_id = fields.Many2one("hr.employee", "Chofer",  domain=[('transportista','=',True)])
    es_flete_interno = fields.Boolean("Transportista externo", default=False)
    sale_line_fleet_ids = fields.One2many("sale.order.line.fleet", "sale_id", "Fletes")
    purchase_id = fields.Many2one("purchase.order", "Orde de compra", readonly=True)
    total_transportista = fields.Float("Costo de Transportista")

class Salefleetline(models.Model):
    _name="sale.order.line.fleet"
    _order = "sale_id asc"

    sale_id = fields.Many2one("sale.order", "# Orden de Venta")
    fecha = fields.Date("Fecha")
    purchase_id = fields.Many2one("purchase.order", "Factura de Flete")
    transportista_id = fields.Many2one("res.partner", "Transportista", domain=[('transportista', '=', True)])
    name = fields.Char("Descripcion", default="Flete", required=True)
    qty_galones = fields.Float("Cantidad")
    costo_galon = fields.Float("Costo por Galón")
    unidad_medida = fields.Many2one('product.uom', string='Unit of Measure', ondelete='set null', index=True)
    total = fields.Float("Monto total")
    product_id = fields.Many2one("product.product", "Producto", required=True, domain=[('purchase_ok', '=', True)])
    date = fields.Date("Fecha del Flete")
    state = fields.Selection([
            ('draft','Borrador'),
            ('open','Pendiente de Liquidar'),
            ('paid','Pagado'),
        ], string='Estado', index=True, default='draft', help="")
    type_anticipo = fields.Selection([('combustible', 'Combustible'), ('anticipo', 'Anticipo')], string='Tipo de anticipo', index=True)

