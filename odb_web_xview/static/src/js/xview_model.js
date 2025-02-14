odoo.define('odb_web_xview.Model', function(require) {
    "use strict";

    var AbstractModel = require('web.AbstractModel');

    var XViewModel = AbstractModel.extend({

        get: function() {
            return this.data;
        },
       
        load: function(params) {
            this.modelName = params.modelName;
            this.domain = params.domain || [];
            this.fields = params.fields;
            this.viewFields = params.viewFields;

            this.field_related = params.field_related;
            this.parent_id = params.parent_id;
            
            return this._fetchData();
        },
        
        reload: function(handle, params) {
            if ('domain' in params) {
                this.domain = params.domain;
            }
            return this._fetchData();
        },

        _fetchData: function() {
            var self = this;
            var params = Array.prototype.slice.call(arguments);
            var defs = [
                this._rpc({
                    model: 'xview.model',
                    method: 'fetchData',
                    args: [this.modelName, this.field_related || undefined, this.parent_id, this.domain]
                })
            ];
            return $.when.apply($, defs, ).then(function() {
                var results = Array.prototype.slice.call(arguments);
                self.data = {
                    "xViewNodes": results[0],
                };

            });
        },
        itemExist:function(arr, item){
            var flag = false
            for(var i = 0;i<arr.length;i++){
                if(item.id == arr[i].id){
                    flag = true;
                    break;
                }
            }
            return flag
        },
        _beforeExpandData: function(node_id,id,model) {
            var self = this;
            if (this.field_related !== undefined){
                var defs = [
                    this._rpc({
                        model: 'xview.model',
                        method: 'beforeExpandData',
                        args: [id, this.modelName,this.field_related, this.parent_id, this.domain]
                    })
                ];
                return $.when.apply($, defs, ).then(function() {
                    var results = Array.prototype.slice.call(arguments);
                    var record = results[0]
                    var treeObj = $.fn.zTree.getZTreeObj("xview_tree");
                    for (var i = 0; i< record.length; i++){
                        if(!self.itemExist(self.data.xViewNodes, record[i])){
                            self.data.xViewNodes.push(record[i])
                            treeObj.addNodes(treeObj.getNodeByTId(node_id.split('_switch')[0]), record[i])
                        }
                    }
                })
            }
            else{
                return $.when()
            }
           
         },
    
    });
    return XViewModel;
});