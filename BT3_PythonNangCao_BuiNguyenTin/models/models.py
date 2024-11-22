# models/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import db  # Import db từ models/__init__.py

class ChuyenNganh(db.Model):  # Kế thừa từ db.Model
    __tablename__ = 'ChuyenNganhs'
    ChuyenNganhID = Column(String(20), primary_key=True)
    TenChuyenNganh = Column(String(100), nullable=False)
    
    sinh_viens = relationship("SinhVien", back_populates="chuyen_nganh")

class SinhVien(db.Model):  # Kế thừa từ db.Model
    __tablename__ = 'SinhViens'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Ten = Column(String(100), nullable=False)
    Tuoi = Column(Integer, nullable=False)
    GioiTinh = Column(Boolean, nullable=False)
    ChuyenNganhID = Column(String(20), ForeignKey('ChuyenNganhs.ChuyenNganhID'), nullable=False)
    
    chuyen_nganh = relationship("ChuyenNganh", back_populates="sinh_viens")

class User(db.Model):  # Kế thừa từ db.Model
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
