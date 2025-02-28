from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberSalary(models.Model):
    _name = "rubber.salary"
    _description = "Rubber Salary"
    _rec_name = 'name'

    to = fields.Many2one('hr.department', required=True, string='Tổ')
    to_name = fields.Char(string='Tên Tổ', related='to.name')
    to_name1 = fields.Char('Tổ Tên', compute='_compute_toname')
    ref = fields.Char('Reference', compute='_compute_ref')
    employee_id = fields.Many2one('hr.employee', string='Công nhân', required=True)
    empname = fields.Char('CN', compute='_compute_empname')
    empname1 = fields.Char('CN1', compute='_compute_empname')
    bymonth = fields.Boolean('By Month', default=False, readonly=False)
    sttcn = fields.Char('STT CN')
    name = fields.Char('name', related='employee_id.name')
    company_id = fields.Many2one('res.company', store=True, copy=False,
        string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
        related='company_id.currency_id')
    active = fields.Boolean('Active', default=True)
    thang = fields.Selection([
        ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'),
        ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', default=str(fields.Datetime.now().strftime('%m')), required=True) 
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    namkt = fields.Char('Năm khai thác', compute='_compute_plt')
    thangkt = fields.Char('Tháng khai thác', compute='_compute_plt')
    textthang = fields.Char('Tháng', default='Bảng tính lương tháng')
    textnam = fields.Char('Năm', default='Năm')
    empty = fields.Char('Empty')
    quykho = fields.Float('Tổng quy khô', digits='One Decimal', compute='_compute_khotien')
    tiennuoc = fields.Float('tiennuoc', digits='Product Price', compute='_compute_khotien')
    tienday = fields.Float('tienday', digits='Product Price', compute='_compute_khotien')
    tiendong = fields.Float('tiendong', digits='Product Price', compute='_compute_khotien')
    tienchen = fields.Float('tienchen', digits='Product Price', compute='_compute_khotien')
    phucap1 = fields.Float('phucap1', digits='Product Price', compute='_compute_khotien')
    tongtien = fields.Monetary('Tổng cộng', compute='_compute_khotien')
    rubber_line_ids = fields.One2many('rubber', 'rubbersalary_id', string='Sản lượng mũ cạo', domain=[('bymonth', '=', True)]) # hàm on change bên dưới để set những rubber nào có bymonth = True
    reward_line_ids = fields.One2many('reward', 'rubbersalary_id', string='Thuong', domain=[('bymonth', '=', True)])
    reward_id = fields.Many2one('reward', string='Reward', readonly=True)
    tongtien_reward = fields.Monetary('Tiền thưởng năm', compute='_compute_thuong')
    tienung = fields.Float('Trừ tiền ưng', compute='_compute_phucap', digits='Product Price')
    tiendao = fields.Float('Tiền dao', compute='_compute_phucap', digits='Product Price')
    boithuoc = fields.Float('Bôi thuốc', compute='_compute_phucap', digits='Product Price')
    boikeo = fields.Float('Bôi keo', compute='_compute_phucap', digits='Product Price')
    giacomang = fields.Float('Gia cố máng', compute='_compute_phucap', digits='Product Price')
    chuyencan = fields.Float('Chuyên cần', compute='_compute_phucap', digits='Product Price')
    thuongsl = fields.Float('Thưởng sản lượng', compute='_compute_phucap', digits='Product Price')
    ngaylam = fields.Char('Ngày vắng', compute='_compute_phucap')
    phucap = fields.Float('Phụ cấp', compute='_compute_phucap', digits='Product Price')
    quykho1 = fields.Float('Quy khô tương đương 1 phần', compute='_compute_phucap', digits='One Decimal')
    sophan = fields.Float('Số phần', default='1.0', compute='_compute_phucap', digits='One Decimal')
    caochoang = fields.Float('Cạo choàng', compute='_compute_phucap', digits='Product Price')
    duongxau = fields.Float('Đường xấu', compute='_compute_phucap', digits='Product Price')
    dixa = fields.Float('Đi xa', compute='_compute_phucap', digits='Product Price')
    itmu = fields.Float('Ít mũ', compute='_compute_phucap', digits='Product Price')
    ttmang = fields.Float('Thanh toán máng', digits='Product Price', compute='_compute_phucap')
    tienmuon = fields.Float('Trừ tiền mượn', compute='_compute_phucap', digits='Product Price')
    tienbh = fields.Float('Tiền BH', compute='_compute_phucap', digits='Product Price')
    luongthangtruoc = fields.Float('Lương tháng trước', digits='Product Price', compute='_compute_phucap')
    caoxa = fields.Float('Cạo xả', compute='_compute_phucap', digits='Product Price')
    bdgv = fields.Float('Buộc đá, gắn váy', digits='Product Price', compute='_compute_phucap')
    bdgvmu = fields.Float('Buộc đá, gắn váy miệng úp', digits='Product Price', compute='_compute_phucap')
    bddm = fields.Float('Bắn dây dẫn mũ', compute='_compute_phucap', digits='Product Price')
    mmcn = fields.Float('Mở miệng cạo ngửa', compute='_compute_phucap', digits='Product Price')
    mmcu = fields.Float('Mở miệng cạo úp', compute='_compute_phucap', digits='Product Price')
    bkrtgn = fields.Float('Buộc kiềng, rãi tô, gắn nắp', compute='_compute_phucap', digits='Product Price')
    tienphan = fields.Float('Tiền phân', compute='_compute_phucap', digits='Product Price')
    rmdm = fields.Float('Rong mương, đóng máng', compute='_compute_phucap', digits='Product Price')
    rct = fields.Float('Rập cờ, thước', compute='_compute_phucap', digits='Product Price')
    bkrtmn = fields.Float('Buộc kiềng, rãi tô, miệng ngửa', compute='_compute_phucap', digits='Product Price')
    xdn = fields.Float('Xỏ dây nắp', compute='_compute_phucap', digits='Product Price')
    tbm = fields.Float('Tiền bấm máng', compute='_compute_phucap', digits='Product Price')
    chiendo = fields.Float('Chiên độ', compute='_compute_phucap', digits='Product Price')
    tienvattu = fields.Float('Tiền gom tô, nắp kiềng, váy', compute='_compute_phucap', digits='Product Price')
    tienvattu1 = fields.Float('Tiền giữ vật tư (-)', compute='_compute_phucap', digits='Product Price')
    tiencuoinam = fields.Float('Tiền thưởng cuối năm', compute='_compute_phucap', digits='Product Price')
    tiengomto = fields.Float('Tiền giữ gom tô', compute='_compute_phucap', digits='Product Price')
    tamvong = fields.Float('Tầm vong', compute='_compute_phucap', digits='Product Price')
    truidao = fields.Float('Trui dao', compute='_compute_phucap', digits='Product Price')
    bandao = fields.Float('Bán dao', compute='_compute_phucap', digits='Product Price')
    ghichu = fields.Char('Ghi chú', compute='_compute_phucap', digits='Product Price')
    banlinhtinh = fields.Float('Bán vật tư', compute='_compute_phucap', digits='Product Price')
    tientangdg = fields.Float('Tiền tăng đơn giá', compute='_compute_khotien', digits='Product Price')
    ngaycao = fields.Integer('Ngày cạo', compute='_compute_khotien')
    tongtienr = fields.Monetary('Còn lại làm tròn', readonly=True)
    tongluong = fields.Monetary('Tổng lương', readonly=True)
    conlai = fields.Monetary('Còn lại', readonly=True)
    # Phuc loi
    pl2 = fields.Boolean('pl0', default=True)
    pl13 = fields.Boolean('pl1', default=True)
    pl14 = fields.Boolean('pl2', default=True)
    pl3 = fields.Boolean('pl3', default=True)
    pl4 = fields.Boolean('pl4', default=True)
    pl5 = fields.Boolean('pl5', default=True)
    pl6 = fields.Boolean('pl6', default=True)
    pl7 = fields.Boolean('pl7', default=True)
    pl8 = fields.Boolean('pl8', default=True)
    pl9 = fields.Boolean('pl9', default=True)
    pl10 = fields.Boolean('pl10', default=True)
    pl11 = fields.Boolean('pl11', default=True)
    pl12 = fields.Boolean('pl12', default=True)
    rb2 = fields.Boolean('rb0', default=True)
    rb13 = fields.Boolean('rb1', default=True)
    rb14 = fields.Boolean('rb2', default=True)
    rb3 = fields.Boolean('rb3', default=True)
    rb4 = fields.Boolean('rb4', default=True)
    rb5 = fields.Boolean('rb5', default=True)
    rb6 = fields.Boolean('rb6', default=True)
    rb7 = fields.Boolean('rb7', default=True)
    rb8 = fields.Boolean('rb8', default=True)
    rb9 = fields.Boolean('rb9', default=True)
    rb10 = fields.Boolean('rb10', default=True)
    rb11 = fields.Boolean('rb11', default=True)
    rb12 = fields.Boolean('rb12', default=True)
    dt2 = fields.Boolean('dt0', default=True)
    dt13 = fields.Boolean('dt1', default=True)
    dt14 = fields.Boolean('dt2', default=True)
    dt3 = fields.Boolean('dt3', default=True)
    dt4 = fields.Boolean('dt4', default=True)
    dt5 = fields.Boolean('dt5', default=True)
    dt6 = fields.Boolean('dt6', default=True)
    dt7 = fields.Boolean('dt7', default=True)
    dt8 = fields.Boolean('dt8', default=True)
    dt9 = fields.Boolean('dt9', default=True)
    dt10 = fields.Boolean('dt10', default=True)
    dt11 = fields.Boolean('dt11', default=True)
    dt12 = fields.Boolean('dt12', default=True)
    tg2 = fields.Boolean('tg0', default=True)
    tg13 = fields.Boolean('tg1', default=True)
    tg14 = fields.Boolean('tg2', default=True)
    tg3 = fields.Boolean('tg3', default=True)
    tg4 = fields.Boolean('tg4', default=True)
    tg5 = fields.Boolean('tg5', default=True)
    tg6 = fields.Boolean('tg6', default=True)
    tg7 = fields.Boolean('tg7', default=True)
    tg8 = fields.Boolean('tg8', default=True)
    tg9 = fields.Boolean('tg9', default=True)
    tg10 = fields.Boolean('tg10', default=True)
    tg11 = fields.Boolean('tg11', default=True)
    tg12 = fields.Boolean('tg12', default=True)
    rtt2 = fields.Boolean('rtt0', default=True)
    rtt13 = fields.Boolean('rtt1', default=True)
    rtt14 = fields.Boolean('rtt2', default=True)
    rtt3 = fields.Boolean('rtt3', default=True)
    rtt4 = fields.Boolean('rtt4', default=True)
    rtt5 = fields.Boolean('rtt5', default=True)
    rtt6 = fields.Boolean('rtt6', default=True)
    rtt7 = fields.Boolean('rtt7', default=True)
    rtt8 = fields.Boolean('rtt8', default=True)
    rtt9 = fields.Boolean('rtt9', default=True)
    rtt10 = fields.Boolean('rtt10', default=True)
    rtt11 = fields.Boolean('rtt11', default=True)
    rtt12 = fields.Boolean('rtt12', default=True)
    tt2 = fields.Boolean('tt0', default=True)
    tt13 = fields.Boolean('tt1', default=True)
    tt14 = fields.Boolean('tt2', default=True)
    tt3 = fields.Boolean('tt3', default=True)
    tt4 = fields.Boolean('tt4', default=True)
    tt5 = fields.Boolean('tt5', default=True)
    tt6 = fields.Boolean('tt6', default=True)
    tt7 = fields.Boolean('tt7', default=True)
    tt8 = fields.Boolean('tt8', default=True)
    tt9 = fields.Boolean('tt9', default=True)
    tt10 = fields.Boolean('tt10', default=True)
    tt11 = fields.Boolean('tt11', default=True)
    tt12 = fields.Boolean('tt12', default=True)
    conlaipl = fields.Boolean('conlaipl', default=True, compute='_compute_conlaipl')
    conlaitt = fields.Boolean('tconlaittt12', default=True, compute='_compute_conlaitt')
    plt2 = fields.Monetary(' ', default=0, compute='_compute_plt')
    plt13 = fields.Float('Tháng 1', default=0, compute='_compute_plt', digits='Product Price')
    plt14 = fields.Float('Tháng 2', default=0, compute='_compute_plt', digits='Product Price')
    plt3 = fields.Float('Tháng 3', default=0, compute='_compute_plt', digits='Product Price')
    plt4 = fields.Float('Tháng 4', default=0, compute='_compute_plt', digits='Product Price')
    plt5 = fields.Float('Tháng 5', default=0, compute='_compute_plt', digits='Product Price')
    plt6 = fields.Float('Tháng 6', default=0, compute='_compute_plt', digits='Product Price')
    plt7 = fields.Float('Tháng 7', default=0, compute='_compute_plt', digits='Product Price')
    plt8 = fields.Float('Tháng 8', default=0, compute='_compute_plt', digits='Product Price')
    plt9 = fields.Float('Tháng 9', default=0, compute='_compute_plt', digits='Product Price')
    plt10 = fields.Float('Tháng 10', default=0, compute='_compute_plt', digits='Product Price')
    plt11 = fields.Float('Tháng 11', default=0, compute='_compute_plt', digits='Product Price')
    plt12 = fields.Float('Tháng 12', default=0, compute='_compute_plt', digits='Product Price')
    rbt2 = fields.Float('Còn lại', default=0, compute='_compute_plt', digits='Product Price')
    rbt13 = fields.Float('Rút bớt tháng 1', default=0, compute='_compute_plt', digits='Product Price')
    rbt14 = fields.Float('Rút bớt tháng 2', default=0, compute='_compute_plt', digits='Product Price')
    rbt3 = fields.Float('Rút bớt tháng 3', default=0, compute='_compute_plt', digits='Product Price')
    rbt4 = fields.Float('Rút bớt tháng 4', default=0, compute='_compute_plt', digits='Product Price')
    rbt5 = fields.Float('Rút bớt tháng 5', default=0, compute='_compute_plt', digits='Product Price')
    rbt6 = fields.Float('Rút bớt tháng 6', default=0, compute='_compute_plt', digits='Product Price')
    rbt7 = fields.Float('Rút bớt tháng 7', default=0, compute='_compute_plt', digits='Product Price')
    rbt8 = fields.Float('Rút bớt tháng 8', default=0, compute='_compute_plt', digits='Product Price')
    rbt9 = fields.Float('Rút bớt tháng 9', default=0, compute='_compute_plt', digits='Product Price')
    rbt10 = fields.Float('Rút bớt tháng 10', default=0, compute='_compute_plt', digits='Product Price')
    rbt11 = fields.Float('Rút bớt tháng 11', default=0, compute='_compute_plt', digits='Product Price')
    rbt12 = fields.Float('Rút bớt tháng 12', default=0, compute='_compute_plt', digits='Product Price')
    dtt2 = fields.Float('Đóng thêm', default=0, compute='_compute_plt', digits='Product Price')
    dtt13 = fields.Float('Đóng thêm tháng 1', default=0, compute='_compute_plt', digits='Product Price')
    dtt14 = fields.Float('Đóng thêm tháng 2', default=0, compute='_compute_plt', digits='Product Price')
    dtt3 = fields.Float('Đóng thêm tháng 3', default=0, compute='_compute_plt', digits='Product Price')
    dtt4 = fields.Float('Đóng thêm tháng 4', default=0, compute='_compute_plt', digits='Product Price')
    dtt5 = fields.Float('Đóng thêm tháng 5', default=0, compute='_compute_plt', digits='Product Price')
    dtt6 = fields.Float('Đóng thêm tháng 6', default=0, compute='_compute_plt', digits='Product Price')
    dtt7 = fields.Float('Đóng thêm tháng 7', default=0, compute='_compute_plt', digits='Product Price')
    dtt8 = fields.Float('Đóng thêm tháng 8', default=0, compute='_compute_plt', digits='Product Price')
    dtt9 = fields.Float('Đóng thêm tháng 9', default=0, compute='_compute_plt', digits='Product Price')
    dtt10 = fields.Float('Đóng thêm tháng 10', default=0, compute='_compute_plt', digits='Product Price')
    dtt11 = fields.Float('Đóng thêm tháng 11', default=0, compute='_compute_plt', digits='Product Price')
    dtt12 = fields.Float('Đóng thêm tháng 12', default=0, compute='_compute_plt', digits='Product Price')
    rbtt2 = fields.Float('Còn lại', default=0, compute='_compute_plt', digits='Product Price')
    rbtt13 = fields.Float('Rút tiền thưởng tháng 1', default=0, compute='_compute_plt', digits='Product Price')
    rbtt14 = fields.Float('Rút tiền thưởng tháng 2', default=0, compute='_compute_plt', digits='Product Price')
    rbtt3 = fields.Float('Rút tiền thưởng tháng 3', default=0, compute='_compute_plt', digits='Product Price')
    rbtt4 = fields.Float('Rút tiền thưởng tháng 4', default=0, compute='_compute_plt', digits='Product Price')
    rbtt5 = fields.Float('Rút tiền thưởng tháng 5', default=0, compute='_compute_plt', digits='Product Price')
    rbtt6 = fields.Float('Rút tiền thưởng tháng 6', default=0, compute='_compute_plt', digits='Product Price')
    rbtt7 = fields.Float('Rút tiền thưởng tháng 7', default=0, compute='_compute_plt', digits='Product Price')
    rbtt8 = fields.Float('Rút tiền thưởng tháng 8', default=0, compute='_compute_plt', digits='Product Price')
    rbtt9 = fields.Float('Rút tiền thưởng tháng 9', default=0, compute='_compute_plt', digits='Product Price')
    rbtt10 = fields.Float('Rút tiền thưởng tháng 10', default=0, compute='_compute_plt', digits='Product Price')
    rbtt11 = fields.Float('Rút tiền thưởng tháng 11', default=0, compute='_compute_plt', digits='Product Price')
    rbtt12 = fields.Float('Rút tiền thưởng tháng 12', default=0, compute='_compute_plt', digits='Product Price')
    tgtt2 = fields.Float('Còn lại', default=0, compute='_compute_plt', digits='Product Price')
    tgtt13 = fields.Float('Tiền thưởng tăng/giảm tháng 1', default=0, compute='_compute_plt', digits='Product Price')
    tgtt14 = fields.Float('Tiền thưởng tăng/giảm tháng 2', default=0, compute='_compute_plt', digits='Product Price')
    tgtt3 = fields.Float('Tiền thưởng tăng/giảm tháng 3', default=0, compute='_compute_plt', digits='Product Price')
    tgtt4 = fields.Float('Tiền thưởng tăng/giảm tháng 4', default=0, compute='_compute_plt', digits='Product Price')
    tgtt5 = fields.Float('Tiền thưởng tăng/giảm tháng 5', default=0, compute='_compute_plt', digits='Product Price')
    tgtt6 = fields.Float('Tiền thưởng tăng/giảm tháng 6', default=0, compute='_compute_plt', digits='Product Price')
    tgtt7 = fields.Float('Tiền thưởng tăng/giảm tháng 7', default=0, compute='_compute_plt', digits='Product Price')
    tgtt8 = fields.Float('Tiền thưởng tăng/giảm tháng 8', default=0, compute='_compute_plt', digits='Product Price')
    tgtt9 = fields.Float('Tiền thưởng tăng/giảm tháng 9', default=0, compute='_compute_plt', digits='Product Price')
    tgtt10 = fields.Float('Tiền thưởng tăng/giảm tháng 10', default=0, compute='_compute_plt', digits='Product Price')
    tgtt11 = fields.Float('Tiền thưởng tăng/giảm tháng 11', default=0, compute='_compute_plt', digits='Product Price')
    tgtt12 = fields.Float('Tiền thưởng tăng/giảm tháng 12', default=0, compute='_compute_plt', digits='Product Price')
    pldg13 = fields.Char(' ', default="", compute='_compute_plt')
    pldg14 = fields.Char(' ', default="", compute='_compute_plt')
    pldg3 = fields.Char(' ', default="", compute='_compute_plt')
    pldg4 = fields.Char(' ', default="", compute='_compute_plt')
    pldg5 = fields.Char(' ', default="", compute='_compute_plt')
    pldg6 = fields.Char(' ', default="", compute='_compute_plt')
    pldg7 = fields.Char(' ', default="", compute='_compute_plt')
    pldg8 = fields.Char(' ', default="", compute='_compute_plt')
    pldg9 = fields.Char(' ', default="", compute='_compute_plt')
    pldg10 = fields.Char(' ', default="", compute='_compute_plt')
    pldg11 = fields.Char(' ', default="", compute='_compute_plt')
    pldg12 = fields.Char(' ', default="", compute='_compute_plt')
    ttt2 = fields.Monetary(' ', default=0, compute='_compute_plt')
    ttt13 = fields.Float('Tháng 1', default=0, compute='_compute_plt', digits='Product Price')
    ttt14 = fields.Float('Tháng 2', default=0, compute='_compute_plt', digits='Product Price')
    ttt3 = fields.Float('Tháng 3', default=0, compute='_compute_plt', digits='Product Price')
    ttt4 = fields.Float('Tháng 4', default=0, compute='_compute_plt', digits='Product Price')
    ttt5 = fields.Float('Tháng 5', default=0, compute='_compute_plt', digits='Product Price')
    ttt6 = fields.Float('Tháng 6', default=0, compute='_compute_plt', digits='Product Price')
    ttt7 = fields.Float('Tháng 7', default=0, compute='_compute_plt', digits='Product Price')
    ttt8 = fields.Float('Tháng 8', default=0, compute='_compute_plt', digits='Product Price')
    ttt9 = fields.Float('Tháng 9', default=0, compute='_compute_plt', digits='Product Price')
    ttt10 = fields.Float('Tháng 10', default=0, compute='_compute_plt', digits='Product Price')
    ttt11 = fields.Float('Tháng 11', default=0, compute='_compute_plt', digits='Product Price')
    ttt12 = fields.Float('Tháng 12', default=0, compute='_compute_plt', digits='Product Price')
    rutbot = fields.Float('Rút bớt', digits='Product Price', compute='_compute_plt')
    ruttt = fields.Float('Rút tiền thưởng', digits='Product Price', compute='_compute_plt')
    dongthem = fields.Float('Đóng thêm', digits='Product Price', compute='_compute_plt')
    plconlai = fields.Monetary('PL Năm trước', compute='_compute_plt')
    plconlai_hf = fields.Boolean(default=False)

    @api.constrains('employee_id','thang','nam')
    def _check_rubbersalary_unique(self):
        allowancebymonth_counts = self.search_count([('employee_id','=',self.employee_id.id),('thang','=',self.thang),('nam','=',self.nam),('id','!=',self.id)])
        if allowancebymonth_counts > 0:
            raise ValidationError(_("Phiếu lương công nhân" + self.employee_id.name.lower() + " tháng " + self.thang + "/" + self.nam + " đã tồn tại."))

    @api.depends('rb13','rb14','rb3','rb4','rb5','rb6','rb7','rb8','rb9','rb10','rb11','rb12','dt13','dt14','dt3','dt4','dt5','dt6','dt7','dt8','dt9','dt10','dt11','dt12')
    def _compute_conlaipl(self):
        for rec in self:
            if rec.rb13 == True or rec.rb14 == True or rec.rb3 == True or rec.rb4 == True or rec.rb5 == True or rec.rb6 == True or rec.rb7 == True or rec.rb8 == True or rec.rb9 == True or rec.rb10 == True or rec.rb11 == True or rec.rb12 == True or rec.dt13 == True or rec.dt14 == True or rec.dt3 == True or rec.dt4 == True or rec.dt5 == True or rec.dt6 == True or rec.dt7 == True or rec.dt8 == True or rec.dt9 == True or rec.dt10 == True or rec.dt11 == True or rec.dt12 == True:
                rec.conlaipl = True
            else:
                rec.conlaipl = False

    @api.depends('rtt13','rtt14','rtt3','rtt4','rtt5','rtt6','rtt7','rtt8','rtt9','rtt10','rtt11','rtt12','tg13','tg14','tg3','tg4','tg5','tg6','tg7','tg8','tg9','tg10','tg11','tg12')
    def _compute_conlaitt(self):
        for rec in self:
            if rec.rtt13 == True or rec.rtt14 == True or rec.rtt3 == True or rec.rtt4 == True or rec.rtt5 == True or rec.rtt6 == True or rec.rtt7 == True or rec.rtt8 == True or rec.rtt9 == True or rec.rtt10 == True or rec.rtt11 == True or rec.rtt12 == True or rec.tg13 == True or rec.tg14 == True or rec.tg3 == True or rec.tg4 == True or rec.tg5 == True or rec.tg6 == True or rec.tg7 == True or rec.tg8 == True or rec.tg9 == True or rec.tg10 == True or rec.tg11 == True or rec.tg12 == True:
                rec.conlaitt = True
            else:
                rec.conlaitt = False

    @api.depends('to')
    def _compute_ref(self):
        for rec in self:
            rec.ref = 'To' + rec.to.name[3:6]

    @api.depends('employee_id','thang','nam')
    def _compute_plt(self):
        for rec in self:
            rec.plt2 = 0
            rec.plt13 = 0
            rec.plt14 = 0
            rec.plt3 = 0
            rec.plt4 = 0
            rec.plt5 = 0
            rec.plt6 = 0
            rec.plt7 = 0
            rec.plt8 = 0
            rec.plt9 = 0
            rec.plt10 = 0
            rec.plt11 = 0
            rec.plt12 = 0
            rec.rbt13 = 0
            rec.rbt14 = 0
            rec.rbt3 = 0
            rec.rbt4 = 0
            rec.rbt5 = 0
            rec.rbt6 = 0
            rec.rbt7 = 0
            rec.rbt8 = 0
            rec.rbt9 = 0
            rec.rbt10 = 0
            rec.rbt11 = 0
            rec.rbt12 = 0
            rec.dtt13 = 0
            rec.dtt14 = 0
            rec.dtt3 = 0
            rec.dtt4 = 0
            rec.dtt5 = 0
            rec.dtt6 = 0
            rec.dtt7 = 0
            rec.dtt8 = 0
            rec.dtt9 = 0
            rec.dtt10 = 0
            rec.dtt11 = 0
            rec.dtt12 = 0
            rec.rbtt2 = 0
            rec.rbtt13 = 0
            rec.rbtt14 = 0
            rec.rbtt3 = 0
            rec.rbtt4 = 0
            rec.rbtt5 = 0
            rec.rbtt6 = 0
            rec.rbtt7 = 0
            rec.rbtt8 = 0
            rec.rbtt9 = 0
            rec.rbtt10 = 0
            rec.rbtt11 = 0
            rec.rbtt12 = 0
            rec.tgtt13 = 0
            rec.tgtt14 = 0
            rec.tgtt3 = 0
            rec.tgtt4 = 0
            rec.tgtt5 = 0
            rec.tgtt6 = 0
            rec.tgtt7 = 0
            rec.tgtt8 = 0
            rec.tgtt9 = 0
            rec.tgtt10 = 0
            rec.tgtt11 = 0
            rec.tgtt12 = 0
            rec.pldg13 = ""
            rec.pldg14 = ""
            rec.pldg3 = ""
            rec.pldg4 = ""
            rec.pldg5 = ""
            rec.pldg6 = ""
            rec.pldg7 = ""
            rec.pldg8 = ""
            rec.pldg9 = ""
            rec.pldg10 = ""
            rec.pldg11 = ""
            rec.pldg12 = ""
            rec.ttt2 = 0
            rec.ttt13 = 0
            rec.ttt14 = 0
            rec.ttt3 = 0
            rec.ttt4 = 0
            rec.ttt5 = 0
            rec.ttt6 = 0
            rec.ttt7 = 0
            rec.ttt8 = 0
            rec.ttt9 = 0
            rec.ttt10 = 0
            rec.ttt11 = 0
            rec.ttt12 = 0
            rec.plconlai = 0
            rec.rutbot = 0
            rec.ruttt = 0
            rec.dongthem = 0
            rec.namkt = ''
            rec.thangkt = ''
            namkt = ''
            thangkt = ''
            if int(rec.thang) >= 3:
                namkt = rec.nam
                thangkt = rec.thang
            else:
                namkt = str(int(rec.nam) - 1)
                if int(rec.thang) == 1:
                    thangkt = '13'
                elif int(rec.thang) == 2:
                    thangkt = '14'
            rec.namkt = namkt
            rec.thangkt = thangkt
            rwbs = self.env['reward'].search([('namkt','=',str(int(rec.namkt) - 1)),('employee_id','=',rec.employee_id.id)])
            if len(rwbs) > 0:
                rec.plconlai_hf = True
                conlai = 0
                for rwb in rwbs:
                    conlai += rwb.phucloitln
                rec.plconlai = conlai
            else:
                rec.plconlai_hf = False
                rec.plconlai = 0
            rws = self.env['reward'].search([('employee_id','=',rec.employee_id.id),('namkt','=',rec.namkt)])
            if len(rws) > 0:
                for rw in rws:
                    rec['plt' + str(int(rw.thangkt))] = rw.phucloi
                    rec['rbt' + str(int(rw.thangkt))] = rw.rutbot
                    rec['dtt' + str(int(rw.thangkt))] = rw.dongthem
                    rec['rbtt' + str(int(rw.thangkt))] = rw.ruttt
                    rec['tgtt' + str(int(rw.thangkt))] = rw.ttth
                    rec['pldg' + str(int(rw.thangkt))] = rw.pltext
                    rec['ttt' + str(int(rw.thangkt))] = rw.tongtien
                    if rw.thangkt == rec.thangkt:
                        rec.plt2 = rw.phucloitl
                        rec.rbt2 = rw.phucloitln
                        rec.ttt2 = rw.tongtientl
                        rec.rbtt2 = rw.tongtientln
                        rec.rutbot = rw.rutbot
                        rec.ruttt = rw.ruttt
                        rec.dongthem = rw.dongthem
            for x in range(2, 15):
                if x > int(rec.thangkt):
                    rec['pl' + str(x)] = False
                else:
                    rec['pl' + str(x)] = True
                    if rec['plt' + str(x)] == 0:
                        rec['pl' + str(x)] = False
            for z in range(2, 15):
                if z > int(rec.thangkt):
                    rec['rb' + str(z)] = False
                    rec['dt' + str(z)] = False
                    rec['rtt' + str(z)] = False
                    rec['tg' + str(z)] = False
                else:
                    rec['rb' + str(z)] = True
                    rec['dt' + str(z)] = True
                    rec['rtt' + str(z)] = True
                    rec['tg' + str(z)] = True
                    if rec['rbt' + str(z)] == 0:
                        rec['rb' + str(z)] = False
                    if rec['dtt' + str(z)] == 0:
                        rec['dt' + str(z)] = False
                    if rec['rbtt' + str(z)] == 0:
                        rec['rtt' + str(z)] = False
                    if rec['tgtt' + str(z)] == 0:
                        rec['tg' + str(z)] = False
            for y in range(2, 15):
                if y > int(rec.thangkt):
                    rec['tt' + str(y)] = False
                else:
                    rec['tt' + str(y)] = True
                    if rec['ttt' + str(y)] == 0:
                        rec['tt' + str(y)] = False

    @api.depends('to')
    def _compute_toname(self):
        for rec in self:
            rec.to_name1 = rec.to.name.replace('TỔ','Tổ')

    @api.depends('employee_id')
    def _compute_sttcn(self):
        plant = self.env['plantation'].search([('to', '=', self.employee_id.id),('lo', '=', 'a')])
        for rec in self:
            rec.sttcn = plant.sttcn

    @api.depends('employee_id')   
    def _compute_empname(self):
        for rec in self:
            rec.empname = rec.employee_id.name.split('-')[0]
            rec.empname1 = rec.employee_id.name.split('-')[0].replace(' ', '_')
                   
    @api.depends('employee_id', 'thang', 'nam')
    def _compute_phucap(self):
        for rec in self:
            alw = rec.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=',rec.thang),('nam','=',rec.nam)])
            if len(rec.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=',rec.thang),('nam','=',rec.nam)])) == 1:
                als = rec.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=',rec.thang),('nam','=',rec.nam)])
                rec.boithuoc = als[0].boithuoc
                rec.boikeo = als[0].boikeo
                rec.ghichu = als[0].ghichu
                rec.giacomang = als[0].giacomang
                rec.chuyencan = als[0].chuyencan
                rec.thuongsl = als[0].thuong_sl
                rec.ngaylam = als[0].ngaylam
                rec.phucap = als[0].phucap
                rec.sophan = als[0].sophan
                rec.quykho1 = als[0].quykho
                rec.caochoang = als[0].caochoang
                rec.duongxau = als[0].duongxau
                rec.tienvattu = als[0].tienvattu
                rec.tienbh = als[0].tienbh
                rec.itmu = als[0].itmu
                rec.tiencuoinam = als[0].tiencuoinam
                rec.mmcn = als[0].mmcn
                rec.mmcu = als[0].mmcu
                rec.bkrtgn = als[0].bkrtgn
                rec.tienphan = als[0].tienphan
                rec.luongthangtruoc = als[0].luongthangtruoc
                rec.bkrtmn = als[0].bkrtmn
                rec.bdgv = als[0].bdgv
                rec.bdgvmu = als[0].bdgvmu
                rec.rct = als[0].rct
                rec.rmdm = als[0].rmdm
                rec.xdn = als[0].xdn
                rec.ttmang = als[0].ttmang
                rec.caoxa = als[0].caoxa
                rec.bddm = als[0].bddm
                rec.tongluong = rec.tongtien + rec.boithuoc + rec.boikeo + rec.giacomang + rec.chuyencan + rec.thuongsl + rec.phucap + rec.caochoang + rec.duongxau + rec.itmu + rec.tienvattu + rec.mmcn + rec.mmcu + rec.bkrtgn + rec.bkrtmn + rec.rct + rec.rmdm + rec.xdn + rec.ttmang + rec.bddm + rec.caoxa + rec.bdgv + rec.bdgvmu + rec.luongthangtruoc + rec.tienphan + rec.rutbot - rec.dongthem + rec.ruttt
                rec.tienvattu1 = als[0].tienvattu1
                rec.tienung = als[0].tienung + als[0].ungtien 
                rec.tienmuon = als[0].tienmuon
                rec.tiendao = als[0].tiendao
                rec.chiendo = als[0].chiendo
                rec.tiengomto = als[0].tiengomto
                rec.tbm = als[0].tbm
                rec.tamvong = als[0].tamvong
                rec.truidao = als[0].truidao
                rec.bandao = als[0].bandao
                rec.banlinhtinh = als[0].banlinhtinh
                rec.conlai = rec.tongluong - rec.tienvattu1  - rec.tienung - rec.tiendao - rec.chiendo - rec.tiengomto - rec.tbm - rec.tamvong - rec.truidao - rec.bandao - rec.banlinhtinh - rec.tienmuon - rec.tienbh - rec.tiencuoinam
                mod = rec.conlai % 10000
                if mod >= 5000:
                    rec.tongtienr = rec.conlai - mod + 10000
                else:
                    rec.tongtienr = rec.conlai - mod
            elif len(rec.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=',rec.thang),('nam','=',rec.nam)])) == False:
                rec.tienung = 0
                rec.tiendao = 0
                rec.boithuoc = 0
                rec.boikeo = 0
                rec.ghichu = ''
                rec.giacomang = 0
                rec.chuyencan = 0
                rec.thuongsl = 0
                rec.ngaylam = ""
                rec.phucap = 0
                rec.sophan = 0
                rec.quykho1 = 0
                rec.caochoang = 0
                rec.duongxau = 0
                rec.itmu = 0
                rec.chiendo = 0
                rec.tienvattu = 0
                rec.tienvattu1 = 0
                rec.tienbh = 0
                rec.tiencuoinam = 0
                rec.tiengomto = 0
                rec.tongtienr = 0
                rec.luongthangtruoc = 0
                rec.mmcn = 0
                rec.mmcu = 0
                rec.bkrtgn = 0
                rec.tienphan = 0
                rec.bkrtmn = 0
                rec.bdgv = 0
                rec.bdgvmu = 0
                rec.ttmang = 0
                rec.caoxa = 0
                rec.tienmuon = 0
                rec.bddm = 0
                rec.rct = 0
                rec.rmdm = 0
                rec.xdn = 0
                rec.tbm = 0
                rec.tamvong = 0
                rec.truidao = 0
                rec.bandao = 0
                rec.banlinhtinh = 0
                rec.tongluong = 0
                rec.conlai = 0

    #Tìm những rubber nào có cùng tháng, năm, employee_id với tháng, năm, employee_id của rubber salary, thêm điều kiện là phải có giá trị cộng, mũ đay, mũ đông, mũ chèn, phụ cấp > 0 thì bymonth = True, ngược lại bymonth = False)
    #Sau đó cho hiện những rubber có bymonth = True trong phiếu lương
    #Phải thêm đk cùng tổ nữa vì năm nay có trường hợp 1 công nhân làm 2 tổ trong tháng 1 như tổ 70
    @api.onchange('thang', 'nam')
    def _onchange_thang(self):
        if self.thang and self.nam:  
            if self.env['rubber'].search([('rubbersalary_id.employee_id','=', self.name)]):
                rbs = self.env['rubber'].search([('rubbersalary_id.employee_id','=', self.name)])
                for rb in rbs:                               
                    if rb.thang == self.thang and rb.nam == self.nam and rb.to ==self.to_name and (rb.cong > 0 or rb.muday > 0 or rb.mudong > 0 or rb.muchen > 0 or rb.phucap >0):                    
                        rb.bymonth = True   
                    else:
                        rb.bymonth = False
            """ if self.env['reward'].search([('employee_id','=', self.name)]):             
                rrs = self.env['reward'].search([('employee_id','=', self.name)])          
                for rr in rrs:                                                  
                    if rr.namkt == self.namkt:                    
                        rr.bymonth = True                           
                    else:                        
                        rr.bymonth = False  """           

    @api.depends('rubber_line_ids')
    def _compute_khotien(self):
        for rec in self:
            if rec.rubber_line_ids:
                for line in rec.rubber_line_ids:
                    if line.bymonth == True:
                        rec.quykho += line.quykho
                        rec.tongtien += line.tongtien
                        rec.tientangdg += line.tientangdg
                        rec.tiennuoc += line.tiennuoc
                        rec.tienday += line.tienday
                        rec.tiendong += line.tiendong
                        rec.tienchen += line.tienchen
                        rec.phucap1 += line.phucap
                        rec.ngaycao += 1
            else:
                rec.quykho = 0
                rec.tongtien = 0
                rec.tientangdg = 0
                rec.tiennuoc = 0
                rec.tienday = 0
                rec.tiendong = 0
                rec.tienchen = 0
                rec.phucap1 = 0
                rec.ngaycao = 0
        """ if self.rubber_line_ids:
            for line in self.rubber_line_ids:
                if line.bymonth == True:
                    self.quykho += line.quykho
                    self.tongtien += line.tongtien
                    self.tientangdg += line.tientangdg
                    self.tiennuoc += line.tiennuoc
                    self.tienday += line.tienday
                    self.tiendong += line.tiendong
                    self.tienchen += line.tienchen
                    self.ngaycao += 1
        else:
            self.quykho = 0
            self.tongtien = 0
            self.tientangdg = 0
            self.tiennuoc = 0
            self.tienday = 0
            self.tiendong = 0
            self.tienchen = 0
            self.ngaycao = 0 """

    @api.depends('rubber_line_ids')
    def _compute_thuong(self):
        for rec in self:
            if rec.env['reward'].search([('employee_id','=', rec.name),('thang','=', rec.thang)]):            
                rec.tongtien_reward = rec.env['reward'].search([('employee_id','=', rec.name),('thang','=', rec.thang)]).tongtien_luyke
            else:
                rec.tongtien_reward = 0
