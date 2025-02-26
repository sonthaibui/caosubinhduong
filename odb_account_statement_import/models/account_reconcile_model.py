# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, tools, _
from collections import defaultdict


class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    # overite function odoo return matched_candidates_values (open_balance_vals)
    
    # def _get_invoice_matching_rule_result(self, st_line, candidates, aml_ids_to_exclude, reconciled_amls_ids, partner):
    #     new_reconciled_aml_ids = set()
    #     new_treated_aml_ids = set()
    #     candidates, priorities = self._filter_candidates(candidates, aml_ids_to_exclude, reconciled_amls_ids)

    #     st_line_currency = st_line.foreign_currency_id or st_line.currency_id
    #     candidate_currencies = set(candidate['aml_currency_id'] for candidate in candidates)
    #     kept_candidates = candidates
    #     if candidate_currencies == {st_line_currency.id}:
    #         kept_candidates = []
    #         sum_kept_candidates = 0
    #         for candidate in candidates:
    #             candidate_residual = candidate['aml_amount_residual_currency']

    #             if st_line_currency.compare_amounts(candidate_residual, -st_line.amount_residual) == 0:
    #                 # Special case: the amounts are the same, submit the line directly.
    #                 kept_candidates = [candidate]
    #                 break

    #             elif st_line_currency.compare_amounts(abs(sum_kept_candidates), abs(st_line.amount_residual)) < 0:
    #                 # Candidates' and statement line's balances have the same sign, thanks to _get_invoice_matching_query.
    #                 # We hence can compare their absolute value without any issue.
    #                 # Here, we still have room for other candidates ; so we add the current one to the list we keep.
    #                 # Then, we continue iterating, even if there is no room anymore, just in case one of the following candidates
    #                 # is an exact match, which would then be preferred on the current candidates.
    #                 kept_candidates.append(candidate)
    #                 sum_kept_candidates += candidate_residual

    #     # It is possible kept_candidates now contain less different priorities; update them
    #     kept_candidates_by_priority = self._sort_reconciliation_candidates_by_priority(kept_candidates, aml_ids_to_exclude, reconciled_amls_ids)
    #     priorities = set(kept_candidates_by_priority.keys())

    #     # We check the amount criteria of the reconciliation model, and select the
    #     # kept_candidates if they pass the verification.
    #     matched_candidates_values = self._process_matched_candidates_data(st_line, kept_candidates)
    #     status = self._check_rule_propositions(matched_candidates_values)
    #     if 'rejected' in status:
    #         rslt = None
    #     else:
    #         rslt = {
    #             'model': self,
    #             'aml_ids': [candidate['aml_id'] for candidate in kept_candidates],
    #         }
    #         new_treated_aml_ids = set(rslt['aml_ids'])

    #         # Create write-off lines (in company's currency).
    #         if 'allow_write_off' in status:
    #             residual_balance_after_rec = matched_candidates_values['residual_balance_curr'] + matched_candidates_values['candidates_balance_curr']
    #             writeoff_vals_list = self._get_write_off_move_lines_dict(
    #                 st_line,
    #                 matched_candidates_values['balance_sign'] * residual_balance_after_rec,
    #                 partner.id,
    #             )
    #             if writeoff_vals_list:
    #                 rslt['status'] = 'write_off'
    #                 rslt['write_off_vals'] = writeoff_vals_list
    #         else:
    #             writeoff_vals_list = []

    #         # Reconcile.
    #         if 'allow_auto_reconcile' in status:

    #             # Process auto-reconciliation. We only do that for the first two priorities, if they are not matched elsewhere.
    #             aml_ids = [candidate['aml_id'] for candidate in kept_candidates]
    #             lines_vals_list = [{'id': aml_id} for aml_id in aml_ids]

    #             if lines_vals_list and priorities & {1, 3} and self.auto_reconcile:

    #                 # Ensure this will not raise an error if case of missing account to create an open balance.
    #                 dummy, open_balance_vals = st_line._prepare_reconciliation(lines_vals_list + writeoff_vals_list)

    #                 if not open_balance_vals or open_balance_vals.get('account_id'):

    #                     if not st_line.partner_id and partner:
    #                         st_line.partner_id = partner

    #                     st_line.reconcile(lines_vals_list + writeoff_vals_list, allow_partial=True)

    #                     rslt['status'] = 'reconciled'
    #                     rslt['reconciled_lines'] = st_line.line_ids
    #                     new_reconciled_aml_ids = new_treated_aml_ids

    #     return rslt, new_reconciled_aml_ids, new_treated_aml_ids,matched_candidates_values


    # def _apply_rules(self, st_lines, excluded_ids=None, partner_map=None):
    #     ''' Apply criteria to get candidates for all reconciliation models.

    #     This function is called in enterprise by the reconciliation widget to match
    #     the statement lines with the available candidates (using the reconciliation models).

    #     :param st_lines:        Account.bank.statement.lines recordset.
    #     :param excluded_ids:    Account.move.lines to exclude.
    #     :param partner_map:     Dict mapping each line with new partner eventually.
    #     :return:                A dict mapping each statement line id with:
    #         * aml_ids:      A list of account.move.line ids.
    #         * model:        An account.reconcile.model record (optional).
    #         * status:       'reconciled' if the lines has been already reconciled, 'write_off' if the write-off must be
    #                         applied on the statement line.
    #     '''
    #     # This functions uses SQL to compute its results. We need to flush before doing anything more.
    #     for model_name in ('account.bank.statement', 'account.bank.statement.line', 'account.move', 'account.move.line', 'res.company', 'account.journal', 'account.account'):
    #         self.env[model_name].flush(self.env[model_name]._fields)

    #     results = {line.id: {'aml_ids': []} for line in st_lines}

    #     available_models = self.filtered(lambda m: m.rule_type != 'writeoff_button').sorted()
    #     aml_ids_to_exclude = set() # Keep track of already processed amls.
    #     reconciled_amls_ids = set() # Keep track of already reconciled amls.

    #     # First associate with each rec models all the statement lines for which it is applicable
    #     lines_with_partner_per_model = defaultdict(lambda: [])
    #     for st_line in st_lines:

    #         # Statement lines created in old versions could have a residual amount of zero. In that case, don't try to
    #         # match anything.
    #         if not st_line.amount_residual:
    #             continue

    #         mapped_partner = (partner_map and partner_map.get(st_line.id) and self.env['res.partner'].browse(partner_map[st_line.id])) or st_line.partner_id

    #         for rec_model in available_models:
    #             partner = mapped_partner or rec_model._get_partner_from_mapping(st_line)

    #             if rec_model._is_applicable_for(st_line, partner):
    #                 lines_with_partner_per_model[rec_model].append((st_line, partner))

    #     # Execute only one SQL query for each model (for performance)
    #     matched_lines = self.env['account.bank.statement.line']
    #     for rec_model in available_models:

    #         # We filter the lines for this model, in case a previous one has already found something for them
    #         filtered_st_lines_with_partner = [x for x in lines_with_partner_per_model[rec_model] if x[0] not in matched_lines]

    #         if not filtered_st_lines_with_partner:
    #             # No unreconciled statement line for this model
    #             continue

    #         all_model_candidates = rec_model._get_candidates(filtered_st_lines_with_partner, excluded_ids)

    #         for st_line, partner in filtered_st_lines_with_partner:
    #             candidates = all_model_candidates[st_line.id]
    #             if candidates:
    #                 model_rslt, new_reconciled_aml_ids, new_treated_aml_ids,matched_candidates_values = rec_model._get_rule_result(st_line, candidates, aml_ids_to_exclude, reconciled_amls_ids, partner)

    #                 if model_rslt:
    #                     # We inject the selected partner (possibly coming from the rec model)
    #                     model_rslt['partner']= partner

    #                     results[st_line.id] = model_rslt
    #                     results['matched_candidates_values'] = matched_candidates_values
    #                     reconciled_amls_ids |= new_reconciled_aml_ids
    #                     aml_ids_to_exclude |= new_treated_aml_ids
    #                     matched_lines += st_line

    #     return results 