from odoo import fields, models


# does it neet to have the same class name as the inherited class?
class Users(models.Model):

    _inherit = "res.users"

    property_ids = fields.One2many('estate.property',
                                   'salesperson_id',
                                   string='Properties',
                                   domain=['|', ('state', '=', 'new'), ('state', '=', 'received')]
                                   )
