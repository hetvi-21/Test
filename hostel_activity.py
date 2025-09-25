from odoo import models, fields

class HostelActivity(models.Model):
    _name = 'hostel.activity'
    _description = 'Hostel Activity'

    name = fields.Char(string="sports Name", required=True)
    student_ids = fields.Many2many('hostel.student', 'student_activity_rel', 'activity_id', 'student_id', string="Students")


# --addons-path=addons,../enterprise_18,../custom/Hostel_Management --db-filter=odoo-test -c ../odoo.conf --dev xml