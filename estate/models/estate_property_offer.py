import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Offer(models.Model):
    # Private attributes(_name, _description, _inherit, _sql_constraints, …)
    _name = "estate.property.offer"
    _description = "Property offers"
    # TODO set constraints for remaining fields
    # FIXED constraint not having an effect
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'Offer price must be positive value!')
    ]
    _order = "price desc"

    # Default method and default_get
    #

    # Field declarations
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    price = fields.Float(required=True)
    status = fields.Selection(copy=False, readonly="True", selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    validity = fields.Integer(default=7)

    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    # Compute, inverse and search methods in the same order as field declaration
    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + datetime.timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Datetime.today() + datetime.timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        d = datetime.datetime
        for record in self:
            record.validity = (d.combine(record.date_deadline, d.min.time()) - fields.Datetime.today()).days

    # Selection method(methods used to return computed values for selection fields)
    #

    # Constrains methods ( @ api.constrains) and onchange methods ( @ api.onchange)
    # FIXED cannot refuse offer that are under 90% of expected price
    @api.constrains('status')
    def _check_price_height(self):
        for record in self:
            if record.price < record.property_id.expected_price * 9 / 10 and record.status != 'refused':
                raise ValidationError("The selling price must be at least 90% of the expected price!")

    # CRUD methods (ORM overrides)
    @api.model
    def create(self, vals):
        prop = self.env["estate.property"].browse(vals["property_id"])
        if vals["price"] > prop.best_price:
            prop.state = 'received'
        else:
            raise UserError("Offered price must be higher that the best offer!")
        return super().create(vals)

    # Action methods
    # FIXED after an offer is accepted you can create new offer which can be accepted too
    def action_accept_offer(self):
        for record in self:
            if record.status != 'refused':
                record.status = 'accepted'
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
                record.property_id.refuse_all_offers()
            else:
                # redundant after adding conditions to buttons in views
                raise UserError("Cannot accept refused offer!")
        return True

    def action_refuse_offer(self):
        for record in self:
            if record.status != 'accepted':
                record.status = 'refused'
            else:
                # redundant after adding conditions to buttons in views
                raise UserError("Cannot refuse accepted offer!")
        return True

    # Other business methods.
    #
