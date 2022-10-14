from odoo import fields, models


class Tags(models.Model):
    # Private attributes(_name, _description, _inherit, _sql_constraints, …)
    _name = "estate.property.tags"
    _description = "Property tags"
    _sql_constraints = [
        ('check_tag_name', 'UNIQUE(name)', 'Tag with this name already exist!')
    ]
    _order = "name"

    # Default method and default_get
    #

    # Field declarations
    color = fields.Integer()
    name = fields.Char(required=True, default="New Tag")

    # Compute, inverse and search methods in the same order as field declaration
    #

    # Selection method(methods used to return computed values for selection fields)
    #

    # Constrains methods ( @ api.constrains) and onchange methods ( @ api.onchange)
    #

    # CRUD methods (ORM overrides)
    #

    # Action methods
    #

    # Other business methods.
    #
