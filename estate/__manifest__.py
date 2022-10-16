# noinspection PyStatementEffect
{
    'name': 'estate',
    'depends': [
        'base',
    ],
    'category': 'Real Estate/Brokerage',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'views/res_users_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tags_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml'
    ],
    'application': True,
    'license': 'LGPL-3',
}
