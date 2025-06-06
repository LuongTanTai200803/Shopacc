from odoo import fields, models, api

class HrEmployeeSkillLevel(models.Model):
    _inherit = 'hr.employee.skill.level'

    minimum_required = fields.Boolean(
        string="Minimum Required",
        default=False
    )

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    has_skill_below_standard = fields.Boolean(
        string="Has Skill Below Standard",
        store=True
    )

    def _compute_has_skill_below_standard(self):
        for employee in self:
            below_standard = any(
                skill.level_id.minimum_required and skill.level_progress < 100
                for skill in employee.employee_skill_ids
            )
            employee.has_skill_below_standard = below_standard

    def get_skills_below_standard(self):
        self.ensure_one()
        return self.employee_skill_ids.filtered(
            lambda skill: skill.level_id.minimum_required and skill.level_progress < 100
        )

    def action_check_skills(self):
        self._compute_has_skill_below_standard()
        return True

    # action send mail
    def action_send_skill_alert(self):
        self.ensure_one()
        if self.has_skill_below_standard:
            template = self.env.ref('hr_skill_alert.email_template_skill_alert')
            template.send_mail(self.id, force_send=True)

<odoo>
    <data>

        <record id="email_template_skill_alert" model="mail.template">
            <field name="name">Skill Alert Notification</field>
            <field name="model_id" ref="hr.model_hr_employee"/>  <!-- Gửi từ model hr.employee -->
            <field name="subject">[Thông báo] Nhân viên có kỹ năng chưa đạt chuẩn</field>
            <field name="email_to">${object.department_id.manager_id.work_email or 'hr@example.com'}</field>
            <field name="email_from">${user.email or 'noreply@example.com'}</field>
            <field name="auto_delete" eval="True"/>
            <field name="body_html" type="html">
                <![CDATA[
                <p>Chào HR,</p>

                <p>Nhân viên <strong>${object.name}</strong> có một số kỹ năng chưa đạt chuẩn:</p>

                <ul>
                % for skill in object.skill_ids:
                    % if skill.level < skill.standard_level:
                        <li>
                            <strong>${skill.skill_id.name}</strong> - Mức hiện tại: ${skill.level} / Chuẩn: ${skill.standard_level}
                        </li>
                    % endif
                % endfor
                </ul>

                <p>Vui lòng xem xét để có phương án đào tạo phù hợp.</p>

                <p>Trân trọng,<br/>Hệ thống Odoo</p>
                ]]>
            </field>
        </record>

    </data>
</odoo>


<form>
    ...
    <header>
        <button name="action_check_skills"
                type="object"
                string="Kiểm tra kỹ năng"
                class="btn-secondary"/>
        <button name="action_send_skill_alert"
                type="object"
                string="Gửi cảnh báo"
                class="btn-primary"
                attrs="{'invisible': [('has_skill_below_standard', '=', False)]}" />
    </header>
    ...
</form>

import pytest
from odoo.tests.common import TransactionCase


@pytest.mark.usefixtures("setup_hr_skill")
class TestEmployeeSkillAlert(TransactionCase):

    def setUp(self):
        super().setUp()

        # Tạo đối tượng level: đạt chuẩn và chưa đạt
        SkillLevel = self.env['hr.employee.skill.level']
        self.level_standard = SkillLevel.create({
            'name': 'Standard Level',
            'minimum_required': True,
        })
        self.level_non_required = SkillLevel.create({
            'name': 'Optional Level',
            'minimum_required': False,
        })

        # Tạo skill
        self.skill = self.env['hr.skill'].create({
            'name': 'Python',
            'skill_type_id': self.env.ref('hr_skills.skill_type_technical').id,
        })

        # Tạo nhân viên
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })

        # Thêm kỹ năng chưa đạt chuẩn (progress < 100)
        self.skill_line = self.env['hr.employee.skill'].create({
            'employee_id': self.employee.id,
            'skill_id': self.skill.id,
            'level_id': self.level_standard.id,
            'level_progress': 75,
        })

    def test_compute_has_skill_below_standard(self):
        self.employee._compute_has_skill_below_standard()
        assert self.employee.has_skill_below_standard is True

    def test_get_skills_below_standard(self):
        skills = self.employee.get_skills_below_standard()
        assert self.skill_line in skills
        assert all(skill.level_progress < 100 for skill in skills)

    def test_send_skill_alert_triggers_email(self):
        # Kích hoạt lại tính toán
        self.employee._compute_has_skill_below_standard()

        # Lấy email template (đảm bảo template tồn tại trong XML)
        template = self.env.ref('hr_skill_alert.email_template_skill_alert')

        # Theo dõi số email được gửi
        initial_mails = self.env['mail.mail'].search_count([])

        # Gửi
        self.employee.action_send_skill_alert()

        # Kiểm tra có thêm email được gửi
        new_mails = self.env['mail.mail'].search_count([])
        assert new_mails > initial_mails
