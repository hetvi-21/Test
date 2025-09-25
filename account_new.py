from odoo import models, fields

class SaleOrder(models.Model):
    _inherit='account.move'
    description = "inherit account.move to add custom fields"

    custom_field = fields.Char(string="Custom Field")
    name =  fields.char(stirng ="customer name")

