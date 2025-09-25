cooma to covert odoo to foycom
 python3.10 odoo_to_foycom.py /home/silent/Workspace_17/17_repo/wms-kpcloseout /home/silent/Workspace_17/wms_foycom/wms-foycom-kpcloseout


live pdf and html view
http://localhost:8059/report/pdf/account.account_invoices/2?debug=assets


js code for page for detect last page in invoice
<!--<template>-->
        <template id="minimal_layout" inherit_id="web.minimal_layout" priority="100">
        <script t-if="subst" position="inside">
<!--            <script type="text/javascript" t-if="subst">-->
            console.log('this',this);
           var operations = {
    'last-page': function (elt) { elt.style.visibility = (vars.page === vars.topage) ? "visible" : "hidden"; },
};

for (var klass in operations) {
    var y = document.getElementsByClassName(klass);
    for (var j=0; j&lt;y.length; ++j) operations[klass](y[j]);
}
        </script>
    </template>
module : report_qweb_element_page_visibility  (present in odoo 17 wms_kpcloseout)



ssh:
git clone ssh://git@gitlab.silentinfotech.com:2222/training/training-project.git




  if 'groups_id' in vals:
            commands = vals.get('groups_id')
            # commands is a list like [(6, 0, [ids])] or [(4, id), (3, id), etc.]
            for cmd in commands:
                if cmd[0] in (4, 6):  # 4=add, 6=replace
                    if cmd[0] == 4:
                        # add one group id
                        group_id = cmd[1]
                        changes_id_true.append(group_id)
                    elif cmd[0] == 6:
                        # replace with list of groups
                        group_ids = cmd[2]
                        changes_id_true.extend(group_ids)
                elif cmd[0] == 3:  # remove group id
                    group_id = cmd[1]
                    changes_id_false.append(group_id)

