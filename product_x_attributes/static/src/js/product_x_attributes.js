/*##############################################################################
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
##############################################################################*/

openerp.product_x_attributes = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt;

    instance.web.FormView = instance.web.FormView.extend({
        reload_form_view: function(data) {
            var self = this;
            var $dest = this.$el.hasClass("oe_form_container") ? this.$el : this.$el.find('.oe_form_container');
            $dest.empty();
            self.$sidebar.remove();
            self.$buttons.remove();
            self.load_form(data);
        },

        load_record: function(record) {
            var self = this, set_values = [];
            var $dest = this.$el.hasClass("oe_form_container") ? this.$el : this.$el.find('.oe_form_container');
            /** buke **/
            if (self.model=='product.product' && record.id && !record.reload_fields_view){
                $dest.find('.oe_form').hide();
                self.dataset._model._context.attribute_group_ids = record.attribute_group_ids;
                var view_loaded_def = instance.web.fields_view_get({
                    "model": self.dataset._model,
                    "view_id": self.view_id,
                    "view_type": self.view_type,
                    "toolbar": !!self.options.$sidebar,
                    "context": self.dataset.get_context(),
                });

                return view_loaded_def.then(function(fields_view) {
                    self.fields_view = fields_view;
                    return $.when(self.dataset.read_ids([record.id], self.fields_view.fields, self.dataset)).then(function(record_ids) {
                        self.reload_form_view(fields_view); 
                        record_ids[0].reload_fields_view = true;
                        self.trigger('load_record', record_ids[0]);
                    });
                });
            }
            $dest.find('.oe_form').show();
            /** buke **/
            if (!record) {
                this.set({ 'title' : undefined });
                this.do_warn(_t("Form"), _t("The record could not be found in the database."), true);
                return $.Deferred().reject();
            }
            this.datarecord = record;
            this._actualize_mode();

            if (self.model=='product.product' && record.id){
                self.to_view_mode();//buke
            }

            this.set({ 'title' : record.id ? record.display_name : _t("New") });

            _(this.fields).each(function (field, f) {
                field._dirty_flag = false;
                field._inhibit_on_change_flag = true;
                var result = field.set_value(self.datarecord[f] || false);
                field._inhibit_on_change_flag = false;
                set_values.push(result);
            });
            return $.when.apply(null, set_values).then(function() {
                if (!record.id) {
                    // New record: Second pass in order to trigger the onchanges
                    // respecting the fields order defined in the view
                    _.each(self.fields_order, function(field_name) {
                        if (record[field_name] !== undefined) {
                            var field = self.fields[field_name];
                            field._dirty_flag = true;
                            self.do_onchange(field);
                        }
                    });
                }
                self.on_form_changed();
                self.rendering_engine.init_fields();
                self.is_initialized.resolve();
                self.do_update_pager(record.id == null);
                if (self.sidebar) {
                   self.sidebar.do_attachement_update(self.dataset, self.datarecord.id);
                }
                if (record.id) {
                    self.do_push_state({id:record.id});
                } else {
                    self.do_push_state({});
                }
                self.$el.add(self.$buttons).removeClass('oe_form_dirty');
                self.autofocus();
            });
        },

    });
};

