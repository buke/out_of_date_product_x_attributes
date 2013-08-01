# -*- coding: utf-8 -*-
##############################################################################
#
#    Product X Attributes
#    Copyright 2013 wangbuke <wangbuke@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from tools.translate import _
from lxml import etree

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'attribute_group_ids': fields.many2many('attribute.group', 'categ_attr_grp_rel', 'categ_id', 'grp_id', 'Attribute Groups'),
        }


class product_product(osv.osv):
    _inherit = "product.product"

    def _attr_grp_ids(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        for pid in ids:
            cr.execute( 'SELECT  attribute_group.id \
                    FROM attribute_group \
                    JOIN categ_attr_grp_rel \
                    ON categ_attr_grp_rel.grp_id = attribute_group.id  \
                    JOIN product_category \
                    ON product_category.id = categ_attr_grp_rel.categ_id  \
                    JOIN product_template \
                    ON product_template.categ_id = product_category.id  \
                    JOIN product_product \
                    ON product_product.product_tmpl_id = product_template.id  \
                    WHERE product_product.id=%s',(pid,))
            grp_ids = [rid for (rid,) in cr.fetchall() ]

            cr.execute( 'SELECT  attribute_group.id \
                    FROM attribute_group \
                    JOIN categ_attr_grp_rel \
                    ON categ_attr_grp_rel.grp_id = attribute_group.id  \
                    JOIN product_category \
                    ON product_category.id = categ_attr_grp_rel.categ_id  \
                    JOIN product_categ_rel \
                    ON product_categ_rel.categ_id = product_category.id  \
                    JOIN product_product \
                    ON product_product.id = product_categ_rel.product_id  \
                    WHERE product_product.id=%s',(pid,))
            grp_ids2 = [rid for (rid,) in cr.fetchall() ]

            res[pid] = list(set(grp_ids+grp_ids2))

        return res

    _columns = {
        #'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'attribute_group_ids': fields.function(_attr_grp_ids, type='one2many',
        relation='attribute.group', string='Groups')
    }

    def _fix_size_bug(self, cr, uid, result, context=None):
    #When created a field text dynamicaly, its size is limited to 64 in the view.
    #The bug is fixed but not merged
    #https://code.launchpad.net/~openerp-dev/openerp-web/6.1-opw-579462-cpa/+merge/128003
    #TO remove when the fix will be merged
        for field in result['fields']:
            if result['fields'][field]['type'] == 'text':
                if 'size' in result['fields'][field]: del result['fields'][field]['size']
        return result

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        result = super(product_product, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and context.get('attribute_group_ids'):
            eview = etree.fromstring(result['arch'])
            attributes_notebook, toupdate_fields = self.pool.get('attribute.attribute')._build_attributes_notebook(cr, uid, context['attribute_group_ids'], context=context)
            result['fields'].update(self.fields_get(cr, uid, toupdate_fields, context))
            main_page = etree.Element('page', string=_('Custom Attributes'))
            main_page.append(attributes_notebook)
            #info_page = eview.xpath("//page[@string='%s']" % (_('Information'),))[0]
            info_page = eview.xpath("//page")[0]# buke just put it in second page
            info_page.addnext(main_page)
            result['arch'] = etree.tostring(eview, pretty_print=True)
            result = self._fix_size_bug(cr, uid, result, context=context)
        return result

    def browse(self, cr, uid, select, context=None, list_class=None, fields_process=None):
        result = super(product_product, self).browse(cr, uid, select, context=context, list_class=list_class, fields_process=fields_process)
        return result

    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        result = super(product_product, self).read(cr, user, ids, fields=fields, context=context, load=load)

        if result and len(result) < 2: # just for form view
            result[0]['attribute_group_ids'] = self._attr_grp_ids(cr, user, ids, 'attribute_group_ids')[result[0]['id']]

        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
