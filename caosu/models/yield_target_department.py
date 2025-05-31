from odoo import api, fields, models
from odoo.exceptions import UserError

class YieldTargetDepartment(models.Model):
    _name = "yield.target.department"
    _description = "Yield Target Department"

    department_id = fields.Many2one('hr.department', string='Department', required=True)
    namkt = fields.Char('Year of Harvest', required=True)
    quykho_drc_target = fields.Float('Quy kho DRC Target', digits='Product Price', required=True)
    yield_target_ids = fields.One2many('yield.target', 'yield_target_id', string='Yield Targets')
    yield_distribution_ids = fields.One2many('yield.distribution', 'yield_target_department_id', string='Yield Distributions')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(YieldTargetDepartment, self).create(vals_list)
        for record in records:
            # Get all plantations in the department
            plantations = self.env['plantation'].search([('to', '=', record.department_id.id)])
            yield_targets = []
            for plantation in plantations:
                yield_targets.append({
                    'yield_target_id': record.id,
                    'department_id': record.department_id.id,
                    'plantation_id': plantation.id,
                    'namkt': record.namkt,
                    'quykho_drc_target': record.quykho_drc_target,
                })
            self.env['yield.target'].create(yield_targets)
        return records   

    def write(self, vals):
        res = super(YieldTargetDepartment, self).write(vals)
        # Check if quykho_drc_target is updated
        if 'quykho_drc_target' in vals:
            for record in self:
                # Find related yield.target records
                targets = self.env['yield.target'].search([('yield_target_id', '=', record.id)])
                # Update monthly targets based on the new yearly target and distribution proportions
                for target in targets:
                    distribution = self.env['yield.distribution'].search([
                        ('yield_target_department_id', '=', record.id),
                        ('namkt', '=', record.namkt)
                    ])
                    if distribution:
                        target.quykho_drc_target_t1 = record.quykho_drc_target * distribution.t1
                        target.quykho_drc_target_t2 = record.quykho_drc_target * distribution.t2
                        target.quykho_drc_target_t3 = record.quykho_drc_target * distribution.t3
                        target.quykho_drc_target_t4 = record.quykho_drc_target * distribution.t4
                        target.quykho_drc_target_t5 = record.quykho_drc_target * distribution.t5
                        target.quykho_drc_target_t6 = record.quykho_drc_target * distribution.t6
                        target.quykho_drc_target_t7 = record.quykho_drc_target * distribution.t7
                        target.quykho_drc_target_t8 = record.quykho_drc_target * distribution.t8
                        target.quykho_drc_target_t9 = record.quykho_drc_target * distribution.t9
                        target.quykho_drc_target_t10 = record.quykho_drc_target * distribution.t10
                        target.quykho_drc_target_t11 = record.quykho_drc_target * distribution.t11
                        target.quykho_drc_target_t12 = record.quykho_drc_target * distribution.t12
                        target.quykho_drc_target_t13 = record.quykho_drc_target * distribution.t13
                        target.quykho_drc_target_t14 = record.quykho_drc_target * distribution.t14
        return res
class YieldTarget(models.Model):
    _name = "yield.target"
    _description = "Yield Target"

    yield_target_id = fields.Many2one('yield.target.department', string='Department', required=True, ondelete='cascade')
    plantation_id = fields.Many2one('plantation', string='Plantation', required=True)
    department_id = fields.Many2one('hr.department', string='Department', related='yield_target_id.department_id', store=True)
    namkt = fields.Char('Year of Harvest', required=True)
    quykho_drc_target = fields.Float('Quy kho DRC Target', digits='Product Price', required=True)

    # Fields for each month's target (1-14)
    quykho_drc_target_t1 = fields.Float('quykho t1', digits='Product Price')
    quykho_drc_target_t2 = fields.Float('quykho t2', digits='Product Price')
    quykho_drc_target_t3 = fields.Float('quykho t3', digits='Product Price')
    quykho_drc_target_t4 = fields.Float('quykho t4', digits='Product Price')
    quykho_drc_target_t5 = fields.Float('quykho t5', digits='Product Price')
    quykho_drc_target_t6 = fields.Float('quykho t6', digits='Product Price')
    quykho_drc_target_t7 = fields.Float('quykho t7', digits='Product Price')
    quykho_drc_target_t8 = fields.Float('quykho t8', digits='Product Price')
    quykho_drc_target_t9 = fields.Float('quykho t9', digits='Product Price')
    quykho_drc_target_t10 = fields.Float('quykho t10', digits='Product Price')
    quykho_drc_target_t11 = fields.Float('quykho t11', digits='Product Price')
    quykho_drc_target_t12 = fields.Float('quykho t12', digits='Product Price')
    quykho_drc_target_t13 = fields.Float('quykho t13', digits='Product Price')
    quykho_drc_target_t14 = fields.Float('quykho t14', digits='Product Price')

    def write(self, vals):
        res = super(YieldTarget, self).write(vals)
        # Check if quykho_drc_target is updated
        if 'quykho_drc_target' in vals:
            for record in self:
                # Find the distribution proportions for the department
                distribution = self.env['yield.distribution'].search([
                    ('yield_target_department_id', '=', record.yield_target_id.id),
                    ('namkt', '=', record.namkt)
                ])
                if distribution:
                    # Update monthly targets based on the new yearly target and distribution proportions
                    record.quykho_drc_target_t1 = record.quykho_drc_target * distribution.t1
                    record.quykho_drc_target_t2 = record.quykho_drc_target * distribution.t2
                    record.quykho_drc_target_t3 = record.quykho_drc_target * distribution.t3
                    record.quykho_drc_target_t4 = record.quykho_drc_target * distribution.t4
                    record.quykho_drc_target_t5 = record.quykho_drc_target * distribution.t5
                    record.quykho_drc_target_t6 = record.quykho_drc_target * distribution.t6
                    record.quykho_drc_target_t7 = record.quykho_drc_target * distribution.t7
                    record.quykho_drc_target_t8 = record.quykho_drc_target * distribution.t8
                    record.quykho_drc_target_t9 = record.quykho_drc_target * distribution.t9
                    record.quykho_drc_target_t10 = record.quykho_drc_target * distribution.t10
                    record.quykho_drc_target_t11 = record.quykho_drc_target * distribution.t11
                    record.quykho_drc_target_t12 = record.quykho_drc_target * distribution.t12
                    record.quykho_drc_target_t13 = record.quykho_drc_target * distribution.t13
                    record.quykho_drc_target_t14 = record.quykho_drc_target * distribution.t14

        # Check if any quykho_drc_target_t* fields are updated
        if any(f'quykho_drc_target_t{i}' in vals for i in range(1, 15)):
            # Find related rewards and update their quykho_drc_target field
            rewards = self.env['reward'].search([('employee_id', 'in', self.mapped('plantation_id.employee_id.id'))])
            for reward in rewards:
                # Sum up all quykho_drc_target_t* values across plantations with the same employee_id
                plantations = self.env['plantation'].search([('employee_id', '=', reward.employee_id.id)])
                targets = self.env['yield.target'].search([('plantation_id', 'in', plantations.ids)])
                total = 0.0
                for target in targets:
                    thang_num = int(reward.thang)
                    field_name = f'quykho_drc_target_t{thang_num}'
                    total += getattr(target, field_name, 0.0)
                reward.quykho_drc_target = total
        return res
class YieldDistribution(models.Model):
    _name = "yield.distribution"
    _description = "Yield Distribution"

    yield_target_department_id = fields.Many2one('yield.target.department', string='Yield Target Department', required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    namkt = fields.Char('Year of Harvest', required=True)
    t1 = fields.Float('T1 %', digits=(5, 2), default=0.0, store=True)
    t2 = fields.Float('T2 %', digits=(5, 2), default=0.0, store=True)
    t3 = fields.Float('T3 %', digits=(5, 2), default=0.0, store=True)
    t4 = fields.Float('T4 %', digits=(5, 2), default=0.0, store=True)
    t5 = fields.Float('T5 %', digits=(5, 2), default=0.0, store=True)
    t6 = fields.Float('T6 %', digits=(5, 2), default=0.0, store=True)
    t7 = fields.Float('T7 %', digits=(5, 2), default=0.0, store=True)
    t8 = fields.Float('T8 %', digits=(5, 2), default=0.0, store=True)
    t9 = fields.Float('T9 %', digits=(5, 2), default=0.0, store=True)
    t10 = fields.Float('T10 %', digits=(5, 2), default=0.0, store=True)
    t11 = fields.Float('T11 %', digits=(5, 2), default=0.0, store=True)
    t12 = fields.Float('T12 %', digits=(5, 2), default=0.0, store=True)
    t13 = fields.Float('T13 %', digits=(5, 2), default=0.0, store=True)
    t14 = fields.Float('T14 %', digits=(5, 2), default=0.0, store=True)

    def write(self, vals):
        res = super(YieldDistribution, self).write(vals)
        # Check if any t* fields are updated
        if any(f't{i}' in vals for i in range(1, 15)):
            # Find related yield.target records and update their monthly targets
            targets = self.env['yield.target'].search([
                ('yield_target_id', '=', self.yield_target_department_id.id),
                ('namkt', '=', self.namkt)
            ])
            for target in targets:
                target.quykho_drc_target_t1 = target.quykho_drc_target * self.t1
                target.quykho_drc_target_t2 = target.quykho_drc_target * self.t2
                target.quykho_drc_target_t3 = target.quykho_drc_target * self.t3
                target.quykho_drc_target_t4 = target.quykho_drc_target * self.t4
                target.quykho_drc_target_t5 = target.quykho_drc_target * self.t5
                target.quykho_drc_target_t6 = target.quykho_drc_target * self.t6
                target.quykho_drc_target_t7 = target.quykho_drc_target * self.t7
                target.quykho_drc_target_t8 = target.quykho_drc_target * self.t8
                target.quykho_drc_target_t9 = target.quykho_drc_target * self.t9
                target.quykho_drc_target_t10 = target.quykho_drc_target * self.t10
                target.quykho_drc_target_t11 = target.quykho_drc_target * self.t11
                target.quykho_drc_target_t12 = target.quykho_drc_target * self.t12
                target.quykho_drc_target_t13 = target.quykho_drc_target * self.t13
                target.quykho_drc_target_t14 = target.quykho_drc_target * self.t14
        return res