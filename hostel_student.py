from odoo import models, fields, api
from datetime import timedelta
from datetime import date
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import re
from odoo.osv import expression




class HostelStudent(models.Model):
    _name = 'hostel.student'
    _description = 'Hostel Student data'
    # This is the correct way to include mail.thread and rating.mixin
    _inherit = ['mail.thread', 'avatar.mixin','mail.activity.mixin']


    name = fields.Char(string="Student Name", required=True, tracking=True)
    room_no = fields.Char(string="Room Number", required=True, tracking=True)
    check_in_date = fields.Date(string="Check-In Date")
    check_out_date = fields.Date(string="Check-Out Date")

    # Many2One relationship (A student belongs to a hostel block)
    hostel_block_id = fields.Many2one('hostel.block', string="Hostel Block")

    # Many2Many relationship (A student can be enrolled in multiple activities)
    # activity_ids = fields.Many2many('hostel.activity', 'student_activity_rel', 'student_id', 'activity_id',
    #                                 string="Activities", )
    total_days = fields.Integer(string="Total Stay (Days)", compute="_compute_total_days",
                                inverse="_inverse_total_stay", readonly=False)

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)

    document = fields.Binary(string="Document")
    document_filename = fields.Char(string="Filename")

    # Existing fields
    student_count = fields.Integer(string="Total Students", compute='_compute_student_info')
    block_count = fields.Integer(string="Total Blocks", compute='_compute_student_info')


    @api.model
    def default_get(self, fields_list):

        defaults = super(HostelStudent, self).default_get(fields_list)

        # Set default check-in date to today if not set
        if 'check_in_date' in fields_list and not defaults.get('check_in_date'):
            defaults['check_in_date'] = fields.Date.today()

        # Set default check-out date to 7 days after check-in date if not set
        if 'check_out_date' in fields_list and not defaults.get('check_out_date'):
            defaults['check_out_date'] = fields.Date.today() + timedelta(days=7)

        return defaults

    # State field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', required=True)


    def action_check_in(self):
        self.write({'state': 'checked_in'})


    def action_check_out(self):
        self.write({'state': 'checked_out'})


    def action_cancel(self):
        self.write({'state': 'cancelled'})


    def action_reset_to_draft(self):
        self.write({'state': 'draft'})


    # read method
    def action_read_student(self):
        students = self.search([])
        student_data = students.read(['name', 'room_no'])
        print(student_data)
        return student_data

    def action_view_document(self):
        self.ensure_one()
        if not self.document:
            raise UserError("No document uploaded.")
    
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=hostel.student&id={self.id}&field=document&filename_field=document_filename&download=true',
            'target': 'new',
        }

    @api.depends()
    def _compute_student_info(self):
        student_model = self.env['hostel.student']
        block_model = self.env['hostel.block']

        for rec in self:
            rec.student_count = student_model.search_count([])
            rec.block_count = block_model.search_count([])


    # Button actions to open related models
    def action_show_students(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'hostel.student',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [],
        }


    def action_show_blocks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Blocks',
            'res_model': 'hostel.block',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [],
        }


    # server action
    def set_default_checkout_date(self):
        for student in self:
            if not student.check_out_date:
                # Set check-out date to 7 days after check-in date
                student.check_out_date = student.check_in_date + timedelta(days=7)


    _sql_constraints = [
        ('minimum_stay', 'CHECK ((check_out_date - check_in_date) >= 1)', 'Stay must be at least 1 day!')
    ]


    @api.constrains('room_no')
    def _check_room_number(self):
        pattern = re.compile(r'^[A-Z]-\d{3}$')  # Format: Letter-Digits (e.g., A-505)
        for record in self:
            if not pattern.match(record.room_no):
                raise ValidationError("Room Number must follow the format: 'A-505', 'B-203' (Letter-Digits).")


    def action_open_update_wizard(self):
        """ Opens the Update Check-Out Date Wizard """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Check-Out Date',
            'res_model': 'hostel.student.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_student_ids': [(6, 0, self.ids)]},  # Prefill students
        }


    @api.depends('check_in_date', 'check_out_date')
    def _compute_total_days(self):
        """ Compute total stay duration in days ,self represents multiple records in the model"""
        for record in self:
            if record.check_in_date and record.check_out_date:
                delta = record.check_out_date - record.check_in_date
                record.total_days = delta.days
            else:
                record.total_days = 0


    def _inverse_total_stay(self):
        for record in self:
            if record.total_days > 0:
                record.check_out_date = record.check_in_date + timedelta(days=record.total_days)


    @api.onchange('hostel_block_id')
    def _onchange_hostel_block(self):
        """ Auto-update room number based on the hostel block """
        if self.hostel_block_id:
            if "A" in self.hostel_block_id.name:
                self.room_no = "A-"
            elif "B" in self.hostel_block_id.name:
                self.room_no = "B-"

            else "c" in self .hostel_block_id.name:
                 self.room_no = "c-"


    # create method
    @api.model_create_multi
    def create(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()  # Convert name to uppercase before creating the record
        return super(HostelStudent, self).create(vals)


    # write method
    @api.model
    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].title()  # Convert name to uppercase before saving the record
        return super(HostelStudent, self).write(vals)


    # unlink method
    def unlink(self):
        for record in self:
            if record.state == 'checked_in':
                raise UserError("You cannot delete a checked-in record.")
        return super(HostelStudent, self).unlink()


    # copy method
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = f"{self.name} (Copy)"
        return super().copy(default)


    # browse method
    def browse_student(self):
        for student in self:
            print(" Browsed Student ")
            print(student)  # Output: hostel.student(ID)
            print(student.name if student else "No student found")  # Print name if available
        return True


    # search method
    def search_students(self):
        students = self.search([('state', '=', 'draft')])  # Returns a recordset
        for student in students:
            print(f"Student: {student.name}, Block: {student.hostel_block_id.name}")
        return students


    # group by
    def group_by_hostel_block(self):
        result = self.env['hostel.student'].read_group(
            domain=[],  # No filter
            fields=['hostel_block_id', 'id:count'],  # Group by department_id, count employees
            groupby=['hostel_block_id']
        )
        print(result)  # Output: [{'department_id': (3, 'IT Department'), 'id_count': 5}, {...}]
        return result


    # search_read method
    def action_search_read_student(self):
        self.ensure_one()  # Ensures the method is called for a single record

        students = self.search_read(
            [('name', 'ilike', self.name)],
            ['name', 'room_no', 'activity_ids']
        )

        if not students:
            raise models.ValidationError("No student found with this name.")

        # Log results in Odoo console
        for stu in students:
            print(f"Student Found: {stu}")

        # Show results in a new window
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Search Results',
            'view_mode': 'list,form',
            'res_model': 'hostel.student',
            'domain': [('name', 'ilike', self.name)],
            'target': 'current',
        }


    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.name} ({rec.room_no})"
            result.append((rec.id, name))
        print(result)
        return result
