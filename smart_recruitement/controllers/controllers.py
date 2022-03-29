# -*- coding: utf-8 -*-
# from odoo import http


# class SmartRecruitement(http.Controller):
#     @http.route('/smart_recruitement/smart_recruitement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smart_recruitement/smart_recruitement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('smart_recruitement.listing', {
#             'root': '/smart_recruitement/smart_recruitement',
#             'objects': http.request.env['smart_recruitement.smart_recruitement'].search([]),
#         })

#     @http.route('/smart_recruitement/smart_recruitement/objects/<model("smart_recruitement.smart_recruitement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smart_recruitement.object', {
#             'object': obj
#         })
