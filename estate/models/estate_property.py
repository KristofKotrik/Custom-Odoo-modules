from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class Property(models.Model):

    # Private attributes
    _name = "estate.property"
    _description = "Properties that are being sold"
    # TODO set constraints for remaining fields
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'Expected price must be positive value!'),
        ('check_selling_price', 'CHECK(selling_price > 0)', 'Selling price must be positive value!')
    ]
    _order = "id desc"

    # Default methods
    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)

    # Field declarations
    active = fields.Boolean(default=True)
    bedrooms = fields.Integer(default=2)
    best_price = fields.Float(compute='_compute_highest_offer')
    # FIXED behavior of computing date_availability - sets +3 months with any action
    date_availability = fields.Date(copy=False, default=lambda self: self._default_date_availability())
    description = fields.Text()
    expected_price = fields.Float(required=True)
    facades = fields.Integer()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('east', 'East'), ('south', 'South'), ('west', 'West')]
    )
    garage = fields.Boolean()
    living_area = fields.Integer(string='Living Area (sqm)')
    name = fields.Char(required=True, string='Title')
    postcode = fields.Char()
    selling_price = fields.Float(readonly=True, copy=False)
    # FIXED change status to Offer accepted and Offer received
    # TODO change state to New if there is no active offer
    state = fields.Selection(copy=False, required=True, default='new', string='Status', readonly=True,
                             selection=[
                                 ('new', 'New'),
                                 ('received', 'Offer Received'),
                                 ('accepted', 'Offer Accepted'),
                                 ('sold', 'Sold'),
                                 ('canceled', 'Canceled')
                             ]
                             )
    total_area = fields.Integer(compute='_compute_area_sum')

    # foreign values
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False, readonly=True)
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offer')
    property_type_id = fields.Many2one('estate.property.type', string='Property type')
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tags')

    # TODO deleting a property deletes all offers first

    # Compute, inverse and search methods
    @api.depends('living_area', 'garden_area')
    def _compute_area_sum(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_highest_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

    # Constrains and onchange methods
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    # CRUD methods
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        for record in self:
            if record.state != 'new' and record.state != 'cancelled':
                raise UserError("Cannot delete property that is not new or cancelled!")

    # Action methods
    def action_state_canceled(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'canceled'
            else:
                # redundant after addition of states property to view buttons
                raise UserError("Sold property cannot be canceled!")
        return True

    # DONE add logic that limits selling property only if there is an offer accepted
    def action_state_sold(self):
        for record in self:
            if record.state == 'accepted':
                record.state = 'sold'
            else:
                if record.state != 'canceled':
                    raise UserError("Accept an offer first!")
                else:
                    # redundant after addition of states property to view buttons
                    raise UserError("Canceled property cannot be sold!")
        return True

    # Other business logic
    def refuse_all_offers(self):
        if self.offer_ids:
            self.state = 'accepted'
            for offer in self.offer_ids:
                if offer.status != 'accepted':
                    offer.status = 'refused'
