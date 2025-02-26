# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

class CustomModel(models.Model):
    _name = 'xview.model'
    _description = 'X-View'

    @api.model
    def fetchData(self, model, field_related=None, field_parent_id=None, domain=[]):
        res = []
        if domain != []:
            domain =  expression.normalize_domain(domain)
        if field_parent_id != None:
            if field_related == None: #case: only focus to 1 model
                model_pool = self.env[model].search(domain)
                for rec in model_pool:
                    res.append({
                        'id': rec.id,
                        'name': rec.name,
                        'pId':rec[field_parent_id]['id'],
                        'open':False,
                        'model': model
                    })
                return res
            else: #case: focus to 2 model
                model_pool = self.env[model]
                model_related_pool = model_pool[field_related]
                parent = model_related_pool.search([(field_parent_id, '=', False)], limit=1)
                if parent:
                    for rec in model_related_pool.search([]):
                        if rec[field_parent_id]['id'] == False:
                            res.append({
                                'id': rec.id,
                                'name': rec.name,
                                'children':[],
                                'open':False,
                                'model': model_related_pool._name
                            })
                            for item in model_pool.search(domain):
                                if item[field_related]['id'] == rec.id:
                                    res.append({
                                        'id': item.id,
                                        'name': item.name,
                                        'pId':rec.id,
                                        'open':False,
                                        'model': model
                                })
                else:
                    model_pool_search = model_pool.search(domain)
                    mark = []
                    for rec in model_pool_search:
                        res.append({
                            'id': rec.id,
                            'name': rec.name,
                            'pId': rec[field_related]['id'],
                            'open':False,
                            'model': model_pool._name
                        })
                        if rec[field_related]['id'] not in mark:
                            related = model_related_pool.browse(rec[field_related]['id'])
                            res.append({
                                'id':rec[field_related]['id'],
                                'name': related.name,
                                'children':[],
                                'open':False,
                                'model': related._name
                            })
                            mark.append(rec[field_related]['id'])             
                return res    
        else:#case: focus to 1 model but missing paramater field_parent_id
            raise ValidationError(_('Missing paramater parent_id !'))

    @api.model
    def beforeExpandData(self, id, model,field_related, field_parent_id, domain=[]):
        if domain != []:
            domain =  expression.normalize_domain(domain)
        model_pool = self.env[model]
        model_related_pool = model_pool[field_related]
        res = []
        model_related_pool_search = model_related_pool.search([(field_parent_id,'=',id)])
        for rec in model_related_pool_search:
            res.append({
                'id': rec.id,
                'name': rec.name,
                'children':[],
                'pId':id,
                'open':False,
                'model': model_related_pool._name
            })
        model_pool_search = model_pool.search([(field_related,'=',id)] + domain)
        for item in model_pool_search:
            res.append({
                'id': item.id,
                'name': item.name,
                'pId': item[field_related]['id'],
                'open': False,
                'model': model
            })
        return res
      