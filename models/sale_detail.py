# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Salefleet(models.Model):
    _inherit = 'sale.order'

    transportista_id = fields.Many2one("res.partner", "Transportista", domain=[('transportista','=',True)])
    empleado_id = fields.Many2one("hr.employee", "Chofer",  domain=[('transportista','=',True)])
    es_flete_interno = fields.Boolean("Transportista externo", default=False)
    sale_line_fleet_ids = fields.One2many("sale.order.line.fleet", "sale_id", "Anticipo de combustible")
    fleet_anticipo_ids = fields.One2many("sale.order.line.fleet.anticipo", "sale_id", "Anticipo de transportistas")
    purchase_id = fields.Many2one("purchase.order", "Orde de compra", readonly=True)
    invoice_id = fields.Many2one("account.invoice","Liquidación de tranportista", readonly=True)
    total_transportista = fields.Float("Costo de Transportista")
    total_anticipo = fields.Float("Monto de anticipo")

    def action_button_confirm(self, cr, uid, ids, context=None):
        inh = super(Salefleet, self).action_button_confirm(cr, uid, ids, context=context)
        delivery_cost_obj = self.pool.get("sale.order.line.fleet")
        anticipo_obj = self.pool.get("sale.order.line.fleet.anticipo")
        vals = {}
        for order in self.browse(cr, uid, ids, context=context):
            vals = {
                'date': order.date_order,
                'sale_id': order.id,
                'transportista_id': order.transportista_id.id,
                'name': 'Orden de compra de combustible', 
                }
            delivery_cost_obj.create(cr, uid, vals,context)
            if order.es_flete_interno:
                valores = {
                'fecha': order.date_order,
                'sale_id': order.id,
                'transportista_id': order.transportista_id.id,
                'advance_account_id': order.transportista_id.property_account_supplier_advance.id
                'name': 'Anticipo de flete', 
                }
                anticipo_obj.create(cr, uid, valores,context)
        return inh

    def _choose_account_from_dilvery_line(self, line):
        property_obj = self.pool.get('ir.property')
        if line.product_id:
            acc_id = line.product_id.property_account_expense.id
            if not acc_id:
                acc_id = line.product_id.categ_id.property_account_expense_categ.id
            if not acc_id:
                raise except_orm(_('Error!'), _('Define an expense account for this product: "%s" (id:%d).') % (line.product_id.name,line.product_id.id,))
        else:
            acc_id = property_obj.get('property_account_expense_categ', 'product.category').id
        return acc_id

    @api.multi
    def create_purchase(self):
        delivery_line_obj= self.env["sale.order.line.fleet"]
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        values = {}
        vals = {}
        partner_id = 0
        purchase_id = 0
        sum_fleet = 0
        for order in self:
            for line in order.sale_line_fleet_ids:
                if line.id:
                    purchase_obj.search([('id', '=', line.id)]).unlink()
                    partner_id = 0
                type_obj = self.env['stock.picking.type']
                picking = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', order.company_id.id)], limit=1)
                location = self.env["stock.picking.type"].browse(picking.id)
                pricelist = self.env['res.partner'].search([('id', '=', line.proveedor_id.id)]).property_product_pricelist_purchase.id
                vals = {
                'partner_id': line.proveedor_id.id,
                'date_order': order.date_order,
                'picking_type_id': picking.id,
                'location_id': location.default_location_dest_id.id,
                'invoice_method': 'order',
                 'pricelist_id': pricelist,
                }
                purchase_id = purchase_obj.create(vals)

                if purchase_id:
                    acc_id = self._choose_account_from_dilvery_line(line)
                    values = {
                        'name': line.name,
                        'order_id': purchase_id.id,
                        'date_planned': order.date_order,
                        'account_id': acc_id,
                        'price_unit': line.total or 0.0,
                        'quantity': 1,#line.qty_galones,
                        'product_id': line.product_id.id or False,
                        # 'uos_id': False,
                        }
                    line.write({'purchase_id': purchase_id.id})
                    purchase_line_id = purchase_line_obj.create(values)

            if purchase_id:
                order.write({'purchase_id':purchase_id.id})
        return True

    #Crea Factura de Flete para transportista
    @api.multi
    def create_invoice(self):
        delivery_line_obj= self.env["sale.order.line.fleet.anticipo"]
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        values = {}
        vals = {}
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1).id
        partner_id = 0
        invoice_id = 0
        sum_fleet = 0
        for order in self:
            for line in order.fleet_anticipo_ids:
                if line.invoice_fleet_id.id:
                    inv_obj.search([('id', '=', line.invoice_fleet_id.id)]).unlink()
                    partner_id = 0

                if partner_id != line.transportista_id.id:
                    values = {
                        'partner_id': line.transportista_id.id,
                        'date_invoice': order.date_order,
                        'account_id': line.transportista_id.property_account_payable.id,
                        'type': 'in_invoice',
                        'journal_id': journal_id,
                        'origin': order.name,
                        }
                    partner_id = line.transportista_id.id
                    invoice_id = inv_obj.create(values)
                #Condicion para crear le objeto linea de factura account.invoice.line

                if invoice_id:
                    cuenta_anticipo = line.transportista_id.property_account_supplier_advance.id
                    if not cuenta_anticipo:
                          raise except_orm(_('Error!'), _('Defina una cuenta de anticipo de transportistas'))
                    # acc_id = self._choose_account_from_dilvery_line(line)
                    vals1 = {
                        'name': 'Valor de flete de transportista',
                        'invoice_id': invoice_id.id,
                        'account_id': cuenta_anticipo,
                        'price_unit': order.total_transportista or 0.0,
                        'quantity': 1,
                        }

                    vals = {
                        'name': line.name,
                        'invoice_id': invoice_id.id,
                        'account_id': cuenta_anticipo,
                        'price_unit': (line.total * -1) or 0.0,
                        'quantity': 1,
                        }
                    line.write({'invoice_fleet_id': invoice_id.id})
                    line.write({'state': 'open'})
                    inv_line_id1 = inv_line_obj.create(vals1)
                    inv_line_id = inv_line_obj.create(vals)
                    sum_fleet = line.total

            self.total_anticipo= sum_fleet
            if invoice_id:
                order.write({'invoice_id':invoice_id.id})

        return True

class Salefleetline(models.Model):
    _name="sale.order.line.fleet"
    _order = "sale_id asc"

    sale_id = fields.Many2one("sale.order", "# Orden de Venta")
    purchase_id = fields.Many2one("purchase.order", "Factura de Flete")
    transportista_id = fields.Many2one("res.partner", "Transportista", required=True, domain=[('transportista', '=', True)])
    name = fields.Char("Descripcion", default="Orden de compra de combustible")
    qty_galones = fields.Float("Cant")
    costo_galon = fields.Float("Costo por Galón")
    total = fields.Float("Monto total")
    product_id = fields.Many2one("product.product", "Producto", domain=[('purchase_ok', '=', True)])
    date = fields.Date("Fecha de Orden")
    proveedor_id = fields.Many2one("res.partner", "Proveedor", required=True, domain=[('supplier', '=', True)])

    @api.onchange("product_id")
    def onchangeproduct(self):
        if self.product_id.seller_ids:
            self.proveedor_id = self.product_id.seller_ids.name.id


class Salefleetline(models.Model):
    _name="sale.order.line.fleet.anticipo"

    sale_id = fields.Many2one("sale.order", "# Orden de Venta")
    fecha = fields.Date("Fecha de anticipo")
    invoice_fleet_id = fields.Many2one("account.invoice", "Liquidación de transportistas")
    transportista_id = fields.Many2one("res.partner", "Transportista", required=True, domain=[('transportista', '=', True)])
    name = fields.Char("Descripcion", default="Anticipo de flete", required=True)
    total = fields.Float("Monto de anticipo")
    state = fields.Selection([
            ('draft','Borrador'),
            ('open','Pendiente de Liquidar'),
            ('paid','Pagado'),
        ], string='Estado', index=True, default='draft', help="")
    advance_account_id = fields.Many2one('account.account', 'Cuenta de Anticipo', domain="[('type','!=','view')]")

