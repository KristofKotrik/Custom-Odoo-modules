from odoo import api, fields, models


class Type(models.Model):
    # Private attributes(_name, _description, _inherit, _sql_constraints, …)
    _name = "estate.property.type"
    _description = "Type of property"
    # TODO add constrains for remaining fields
    _sql_constraints = [
        ('check_type_name', 'UNIQUE(name)', 'Type with this name already exist!')
    ]
    _order = "sequence, name"

    # Default method and default_get
    #

    # Field declarations
    name = fields.Char(required=True)
    offer_count = fields.Integer(string='Count', compute='_compute_offer_count')
    property_count = fields.Char(string='# of properties', compute='_compute_property_count')
    sequence = fields.Integer(string='Sequence', default=2, help="Used to order property types. Lower is better.")

    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='offer')
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Property')

    # Compute, inverse and search methods in the same order as field declaration
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)

    # Selection method(methods used to return computed values for selection fields)
    #

    # Constrains methods ( @ api.constrains) and onchange methods ( @ api.onchange)
    #

    # CRUD methods (ORM overrides)
    #

    # Action methods
    def action_view_offers(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "estate.property.offer",
            "domain": [['property_type_id', '=', self.id]],
            "name": "Property Offers",
            'view_mode': 'tree,form',
            "target": 'new',
        }

    # Other business methods.
    #
