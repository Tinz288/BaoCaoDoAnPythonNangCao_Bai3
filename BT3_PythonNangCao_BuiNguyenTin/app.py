from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db
from models.models import SinhVien, ChuyenNganh, User
from config import Config
import os

class App:
    def __init__(self):
        """Khởi tạo Flask app và cấu hình ứng dụng"""
        self.app = Flask(__name__)  # Tạo đối tượng Flask
        self.app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
        self.app.secret_key = 'secretkey'  # Dùng cho flash messages
        db.init_app(self.app)  # Khởi tạo DB với app

    def get_app(self):
        """Trả về Flask app đã cấu hình"""
        return self.app

    def init_routes(self):
        """Khởi tạo các routes cho Flask app"""
        # Route trang chủ với form đăng nhập và đăng ký
        @self.app.route('/')
        def index():
            mode = request.args.get('mode', 'login')  # 'login' hoặc 'register'
            return render_template('index.html', mode=mode)
        @self.app.route('/register', methods=['POST'])
        def register():
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            # Kiểm tra mật khẩu và xác nhận mật khẩu
            if password != confirm_password:
                flash("Mật khẩu và xác nhận mật khẩu không khớp!", "error")
                return redirect(url_for('index', mode='register'))

            # Kiểm tra xem tên người dùng đã tồn tại chưa
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Tên người dùng đã tồn tại!", "error")
                return redirect(url_for('index', mode='register'))

            # Tạo tài khoản mới
            hashed_password = password
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash("Đăng ký thành công! Hãy đăng nhập.", "success")
            return redirect(url_for('index', mode='login'))

        # Route đăng nhập
        @self.app.route('/login', methods=['POST'])
        def login():
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                session['user_id'] = user.id  # Lưu id người dùng vào session
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Tên người dùng hoặc mật khẩu không đúng!', 'error')
                return redirect(url_for('index'))

        # Route giao diện chính (Dashboard)
        @self.app.route('/dashboard')
        def dashboard():
            if 'user_id' not in session:
                flash('Vui lòng đăng nhập!', 'error')
                return redirect(url_for('index'))
            sinh_viens = SinhVien.query.all()  # Lấy tất cả sinh viên
            return render_template('dashboard.html', sinh_viens=sinh_viens)  # Đây là giao diện chính khi người dùng đăng nhập

        # Route logout
        @self.app.route('/logout')
        def logout():
            session.pop('user_id', None)
            flash('Đăng xuất thành công!', 'success')
            return redirect(url_for('index'))


        @self.app.route('/add_sinh_vien', methods=['GET', 'POST'])
        def add_sinh_vien():
            if request.method == 'POST':
                ten = request.form['ten']
                tuoi = int(request.form['tuoi'])
                gioi_tinh = True if request.form['gioi_tinh'] == 'Nam' else False
                chuyen_nganh_id = request.form['chuyen_nganh_id']

                new_sinh_vien = SinhVien(Ten=ten, Tuoi=tuoi, GioiTinh=gioi_tinh, ChuyenNganhID=chuyen_nganh_id)
                db.session.add(new_sinh_vien)
                db.session.commit()
                flash('Thêm sinh viên thành công!', 'success')
                return redirect(url_for('dashboard'))

            chuyen_nganhs = ChuyenNganh.query.all()  # Lấy tất cả chuyên ngành để chọn
            return render_template('sinhvien_form.html', chuyen_nganhs=chuyen_nganhs)

        @self.app.route('/delete_sinh_vien/<int:id>')
        def delete_sinh_vien(id):
            sinh_vien = SinhVien.query.get(id)
            if sinh_vien:
                db.session.delete(sinh_vien)
                db.session.commit()
                flash('Xóa sinh viên thành công!', 'success')
            else:
                flash('Không tìm thấy sinh viên!', 'error')
            return redirect(url_for('dashboard'))

        @self.app.route('/update_sinh_vien/<int:id>', methods=['GET', 'POST'])
        def update_sinh_vien(id):
            sinh_vien = SinhVien.query.get(id)
            if not sinh_vien:
                flash('Sinh viên không tồn tại!', 'error')
                return redirect(url_for('dashboard'))

            if request.method == 'POST':
                sinh_vien.Ten = request.form['ten'] if request.form['ten'] else sinh_vien.Ten
                sinh_vien.Tuoi = int(request.form['tuoi']) if request.form['tuoi'] else sinh_vien.Tuoi
                sinh_vien.GioiTinh = True if request.form['gioi_tinh'] == 'Nam' else False
                sinh_vien.ChuyenNganhID = request.form['chuyen_nganh_id'] if request.form['chuyen_nganh_id'] else sinh_vien.ChuyenNganhID
                db.session.commit()
                flash('Cập nhật sinh viên thành công!', 'success')
                return redirect(url_for('dashboard'))

            chuyen_nganhs = ChuyenNganh.query.all()  # Lấy tất cả chuyên ngành để chọn
            return render_template('sinhvien_form.html', sinh_vien=sinh_vien, chuyen_nganhs=chuyen_nganhs)

        @self.app.route('/add_chuyen_nganh', methods=['GET', 'POST'])
        def add_chuyen_nganh():
            if request.method == 'POST':
                ma_chuyen_nganh = request.form['ma_chuyen_nganh']
                ten_chuyen_nganh = request.form['ten_chuyen_nganh']

                # Kiểm tra nếu mã chuyên ngành đã tồn tại
                existing_chuyen_nganh = ChuyenNganh.query.filter_by(ChuyenNganhID=ma_chuyen_nganh).first()
                if existing_chuyen_nganh:
                    flash('Mã chuyên ngành đã tồn tại!', 'error')
                    return redirect(url_for('add_chuyen_nganh'))

                # Thêm chuyên ngành mới
                new_chuyen_nganh = ChuyenNganh(ChuyenNganhID=ma_chuyen_nganh, TenChuyenNganh=ten_chuyen_nganh)
                db.session.add(new_chuyen_nganh)
                db.session.commit()
                flash('Thêm chuyên ngành thành công!', 'success')
                return redirect(url_for('dashboard'))

            return render_template('add_chuyen_nganh.html')  # Hiển thị form thêm chuyên ngành

# Chạy ứng dụng
if __name__ == "__main__":
    app_instance = App()
    app_instance.init_routes()
    app = app_instance.get_app()
    app.run(debug=True)
