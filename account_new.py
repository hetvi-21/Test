from odoo import models, fields

class SaleOrder(models.Model):
    _inherit='account.move'

    custom_field = fields.Char(string="Custom Field")
