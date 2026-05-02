"""
融鑫CRM后端服务 - Python FastAPI + SQLite
运行方式: python backend/main.py
访问地址: http://localhost:8080
"""

import os
import re
import json
import hashlib
import secrets
from datetime import datetime, timedelta, date
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Text, DateTime, DECIMAL, ForeignKey, JSON, Index, UniqueConstraint, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base

# ===================== 配置 =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "crm.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"
SECRET_KEY = "rongxin-crm-secret-key-2026-lan-v1"
ALGORITHM = "HS256"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ===================== 数据模型 =====================

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(BigInteger, default=0)
    level = Column(Integer, default=3)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


    def to_dict(self):
        return {"id": self.id, "name": self.name, "parent_id": self.parent_id,
                "level": self.level, "sort_order": self.sort_order, "created_at": self.created_at}

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    real_name = Column(String(50), nullable=False)
    role = Column(Integer, default=1)  # 1顾问 2主管 3管理员
    dept_id = Column(BigInteger, ForeignKey("departments.id"), nullable=True)
    daily_quota = Column(Integer, default=50)
    accept_new_data = Column(Integer, default=1)
    hidden_columns = Column(JSON, default=list)  # 隐藏的客户列表字段
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)

    assignments = relationship("CustomerAssignment", back_populates="advisor")
    remarks = relationship("CustomerRemark", back_populates="advisor")
    loan_cases = relationship("LoanCase", back_populates="advisor")


    def to_dict(self):
        return {"id": self.id, "username": self.username, "real_name": self.real_name,
                "role": self.role, "dept_id": self.dept_id, "daily_quota": self.daily_quota,
                "accept_new_data": self.accept_new_data, "hidden_columns": self.hidden_columns,
                "status": self.status, "created_at": self.created_at}

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), nullable=False)
    phone_hash = Column(String(64), nullable=False, index=True)
    name = Column(String(50))
    gender = Column(Integer, default=0)  # 0未知 1男 2女
    city = Column(String(50))
    age = Column(Integer)
    source = Column(String(100))
    loan_type = Column(Integer, default=1)  # 1信用贷 2车抵贷 3房抵贷 4保单贷 5学历贷 6抵押贷
    apply_amount = Column(DECIMAL(10, 2), default=0)
    status = Column(Integer, default=0)  # 0待跟进，见STATUS_MAP
    star_level = Column(Integer, default=0)  # 0-6星
    is_blacklisted = Column(Integer, default=0)
    is_locked = Column(Integer, default=0)
    is_important = Column(Integer, default=0)
    last_remark_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    qualifications = Column(JSON, default=dict)

    assignments = relationship("CustomerAssignment", back_populates="customer", cascade="all, delete-orphan")
    remarks = relationship("CustomerRemark", back_populates="customer", cascade="all, delete-orphan", order_by="desc(CustomerRemark.created_at)")
    loan_cases = relationship("LoanCase", back_populates="customer")
    reminders = relationship("CustomerReminder", cascade="all, delete-orphan")
    tag_assignments = relationship("CustomerTagAssignment", cascade="all, delete-orphan", single_parent=True)


    def to_dict(self):
        return {"id": self.id, "phone": self.phone, "phone_hash": self.phone_hash,
                "name": self.name, "gender": self.gender, "city": self.city, "age": self.age,
                "source": self.source, "loan_type": self.loan_type, "apply_amount": self.apply_amount,
                "status": self.status, "star_level": self.star_level, "is_blacklisted": self.is_blacklisted,
                "is_locked": self.is_locked, "is_important": self.is_important,
                "last_remark_at": self.last_remark_at, "created_at": self.created_at,
                "updated_at": self.updated_at, "qualifications": self.qualifications}

class CustomerAssignment(Base):
    __tablename__ = "customer_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    advisor_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    pool_type = Column(Integer, default=1)  # 1=我的客户 2=再分配 3=公共池 4=必跟进
    assigned_at = Column(DateTime, default=datetime.now)
    assigned_by = Column(BigInteger, default=0)
    status = Column(Integer, default=1)  # 1有效 0失效

    customer = relationship("Customer", back_populates="assignments")
    advisor = relationship("User", back_populates="assignments")


    def to_dict(self):
        return {"id": self.id, "customer_id": self.customer_id, "advisor_id": self.advisor_id,
                "pool_type": self.pool_type, "assigned_at": self.assigned_at,
                "assigned_by": self.assigned_by, "status": self.status}

class CustomerRemark(Base):
    __tablename__ = "customer_remarks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    advisor_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    remark_type = Column(Integer, default=0)  # 0跟进 1主管点评 2备忘
    status_at_remark = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer", back_populates="remarks")
    advisor = relationship("User", back_populates="remarks")


    def to_dict(self):
        return {"id": self.id, "customer_id": self.customer_id, "advisor_id": self.advisor_id,
                "content": self.content, "remark_type": self.remark_type,
                "status_at_remark": self.status_at_remark, "created_at": self.created_at}

class CustomerReminder(Base):
    __tablename__ = "customer_reminders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    advisor_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    reminder_at = Column(DateTime, nullable=False)  # 提醒时间
    is_done = Column(Integer, default=0)  # 0未完成 1已完成
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer", back_populates="reminders")
    advisor = relationship("User")

    def to_dict(self):
        return {"id": self.id, "customer_id": self.customer_id, "advisor_id": self.advisor_id,
                "content": self.content, "reminder_at": self.reminder_at.isoformat() if self.reminder_at else None,
                "is_done": self.is_done, "created_at": self.created_at.isoformat() if self.created_at else None}

class LoanCase(Base):
    __tablename__ = "loan_cases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    advisor_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    dept_id = Column(BigInteger)
    bank_name = Column(String(100))
    bank_manager = Column(String(50))
    apply_amount = Column(DECIMAL(10, 2))
    fee_rate = Column(DECIMAL(5, 4))
    stage = Column(Integer, default=1)  # 1审核 2批款 3收款 4拒批 5违约
    approve_amount = Column(DECIMAL(10, 2))
    approve_at = Column(DateTime)
    collection_amount = Column(DECIMAL(10, 2))
    collection_at = Column(DateTime)
    submit_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer", back_populates="loan_cases")
    advisor = relationship("User", back_populates="loan_cases")


    def to_dict(self):
        return {"id": self.id, "customer_id": self.customer_id, "advisor_id": self.advisor_id,
                "dept_id": self.dept_id, "bank_name": self.bank_name, "bank_manager": self.bank_manager,
                "apply_amount": self.apply_amount, "fee_rate": self.fee_rate, "stage": self.stage,
                "approve_amount": self.approve_amount, "approve_at": self.approve_at,
                "collection_amount": self.collection_amount, "collection_at": self.collection_at,
                "submit_at": self.submit_at, "created_at": self.created_at}

class PerformanceTarget(Base):
    __tablename__ = "performance_targets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    target_type = Column(String(20))  # 进件数/放款额/客户数
    target_value = Column(Integer, default=0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "target_type": self.target_type,
                "target_value": self.target_value, "start_date": self.start_date,
                "end_date": self.end_date, "created_at": self.created_at}


class Notice(Base):
    __tablename__ = "notices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    notice_type = Column(Integer, default=1)  # 1公告 2滚动条
    is_visible = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "content": self.content,
                "notice_type": self.notice_type, "is_visible": self.is_visible,
                "created_by": self.created_by,
                "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None}


class CallRecord(Base):
    """通话记录"""
    __tablename__ = "call_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    advisor_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    call_type = Column(Integer, default=1)  # 1呼出 2呼入
    call_result = Column(Integer, default=0)  # 0未接 1接通 2占线 3关机 4空号 5拒接
    duration = Column(Integer, default=0)  # 通话时长(秒)
    call_at = Column(DateTime, default=datetime.now)
    note = Column(Text, default="")  # 通话备注
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer")
    advisor = relationship("User")

    def to_dict(self):
        return {"id": self.id, "customer_id": self.customer_id, "advisor_id": self.advisor_id,
                "call_type": self.call_type, "call_result": self.call_result,
                "duration": self.duration, "call_at": self.call_at.isoformat() if self.call_at else None,
                "note": self.note, "created_at": self.created_at.isoformat() if self.created_at else None}


class CustomerTag(Base):
    """客户标签定义（预定义静态标签）"""
    __tablename__ = "customer_tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)   # 标签维度：费用/房产/婚姻等
    tag_name = Column(String(100), nullable=False)  # 标签名称
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {"id": self.id, "category": self.category,
                "tag_name": self.tag_name, "sort_order": self.sort_order}


class CustomerTagAssignment(Base):
    """客户-标签关联表（每个客户最多一个标签）"""
    __tablename__ = "customer_tag_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    tag_id = Column(BigInteger, ForeignKey("customer_tags.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.now)
    assigned_by = Column(BigInteger, default=0)

    customer = relationship("Customer")
    tag = relationship("CustomerTag")

    def to_dict(self):
        return {"id": self.id, "customer_id": self.customer_id, "tag_id": self.tag_id,
                "assigned_at": self.assigned_at, "assigned_by": self.assigned_by,
                "tag_name": self.tag.tag_name if self.tag else "",
                "category": self.tag.category if self.tag else ""}

# ===================== 角色枚举 =====================
ROLE_MAP = {
    0: "负责人",
    1: "区长",
    2: "部长",
    3: "二级主管",
    4: "主管",
    5: "顾问",
    6: "学徒",
}
ROLE_TEXT = {
    0: "负责人", 1: "区长", 2: "部长",
    3: "二级主管", 4: "主管", 5: "顾问", 6: "学徒"
}

# 权限判断辅助函数
def is_boss(user): return user.role == 0        # 负责人
def is_district_manager(user): return user.role <= 1  # 负责人+区长
def is_dept_head(user): return user.role <= 2    # 负责人+区长+部长
def is_manager(user): return user.role <= 4       # 负责人+区长+部长+二级主管+主管
def is_advisor(user): return user.role >= 5      # 顾问+学徒

# ===================== 客户标签体系（10维度60+标签）=====================
TAG_CATEGORIES = {
    "费用": {
        "label": "费用", "icon": "PriceTag",
        "options": ["2%", "3%", "4%", "5%", "6%", "7%", "8%", "10%", "12%", "15%"]
    },
    "营业执照": {
        "label": "营业执照", "icon": "Document",
        "options": ["有限公司", "个体工商户"]
    },
    "经营情况": {
        "label": "经营情况", "icon": "Shop",
        "options": ["真实经营（银联收款）", "真实经营（无收款）", "无实际经营"]
    },
    "需求时间": {
        "label": "需求时间", "icon": "Clock",
        "options": ["1个月内", "2个月", "3个月", "6个月", "一年以上"]
    },
    "开票纳税": {
        "label": "开票纳税", "icon": "Money",
        "options": ["0", "3万以下", "3-10万", "10-30万", "30-50万", "50-100万", "100万以上"]
    },
    "工薪族": {
        "label": "工薪族", "icon": "Briefcase",
        "options": ["代发10000+", "代发5000-10000", "代发5000以下", "现金发放", "半年内新入职"]
    },
    "房产": {
        "label": "房产", "icon": "House",
        "options": ["全款红本", "按揭中", "按揭已清", "外地名下杭州购", "杭州户籍外地购", "安置房/宅基地", "自建房", "父母名下"]
    },
    "车产": {
        "label": "车产", "icon": "Van",
        "options": ["全款", "按揭中", "按揭已清", "公司户"]
    },
    "保单": {
        "label": "保单", "icon": "DocumentChecked",
        "options": ["有商业保单（可贷）"]
    },
    "婚姻": {
        "label": "婚姻", "icon": "User",
        "options": ["已婚有孩", "已婚无孩", "离异"]
    },
}


# ===================== 状态枚举 =====================
STATUS_MAP = {
    0: "待跟进", 1: "有意向", 2: "未接通", 3: "预约上门",
    4: "已上门", 5: "已受理", 6: "待签约", 7: "已签约",
    8: "银行已放款", 9: "银行已拒绝", 10: "审核中", 11: "无意向",
    12: "贷款资质不符", 13: "捣乱申请", 14: "重复申请",
    15: "外地申请", 16: "停机", 17: "空号", 18: "外地号码"
}

STATUS_EDITABLE = [5, 6, 8, 0, 4, 15, 16, 17]  # 编辑时可设置的状态

GENDER_MAP = {0: "未知", 1: "男", 2: "女"}
LOAN_TYPE_MAP = {1: "信用贷", 2: "车抵贷", 3: "房抵贷", 4: "保单贷", 5: "学历贷", 6: "抵押贷"}
MARITAL_STATUS_MAP = {0: "未婚", 1: "已婚有孩", 2: "已婚无孩", 3: "离异"}

QUICK_REMARKS = [
    "未接", "不需要了", "通话中", "拒接", "接了就挂", "无法接通",
    "用户正忙", "贷款即挂", "空号", "停机", "关机", "外地号码",
    "现在不方便接听", "不是本人申请", "微信待通过", "已发短信", "已加微信"
]

REMARK_HINT = "1、户籍地在哪 2、上班还是做生意 3、工资多少/营业执照多长时间 4、是否有社保和公积金 5、自己和配偶是否有房车和保单 6、负债和征信情况 7、初步判断可以做哪些银行 8、预约什么时候上门"

# ===================== 辅助函数 =====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_phone(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()[:64]


def mask_phone(phone: str) -> str:
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]


def verify_password(plain: str, hashed: str) -> bool:
    import bcrypt
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    import bcrypt
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def create_token(user_id: int) -> str:
    from jose import jwt as jwt_lib
    payload = {"user_id": user_id, "exp": datetime.now() + timedelta(hours=48)}
    return jwt_lib.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    # 优先从 Authorization header 读取（前端axios自动加 Bearer 前缀）
    auth_token = authorization if authorization else token
    if not auth_token:
        raise HTTPException(401, "未登录或登录已失效")
    # 去掉 Bearer 前缀
    if auth_token.startswith("Bearer "):
        auth_token = auth_token[7:]
    from jose import jwt as jwt_lib
    try:
        payload = jwt_lib.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.status == 0:
            raise HTTPException(401, "登录已失效")
        return user
    except jwt_lib.ExpiredSignatureError:
        raise HTTPException(401, "登录已过期")
    except:
        raise HTTPException(401, "登录已失效")


def require_manager(user: User = Depends(get_current_user)):
    """主管及以上权限（role <= 4）"""
    if user.role > 4:
        raise HTTPException(403, "权限不足，需要主管及以上权限")
    return user


def require_boss(user: User = Depends(get_current_user)):
    """负责人权限（role == 0）"""
    if user.role != 0:
        raise HTTPException(403, "权限不足，仅负责人可用")
    return user


def customer_to_dict(c, user=None, include_options=False):
    quals = c.qualifications or {}
    re = quals.get("real_estate", {})
    ve = quals.get("vehicle", {})
    ins = quals.get("insurance", {})
    cr = quals.get("credit", {})
    li = quals.get("liabilities", {})
    result = {
        "id": c.id, "phone": mask_phone(c.phone) if user and user.role >= 5 else c.phone,
        "name": c.name or "", "gender": c.gender, "genderText": GENDER_MAP.get(c.gender, "未知"),
        "city": c.city or "", "age": c.age or 0, "source": c.source or "",
        "loan_type": c.loan_type, "loanTypeText": LOAN_TYPE_MAP.get(c.loan_type, "信用贷"),
        "apply_amount": float(c.apply_amount or 0),
        "status": c.status, "statusText": STATUS_MAP.get(c.status, "待跟进"),
        "star_level": c.star_level, "is_blacklisted": c.is_blacklisted,
        "is_locked": c.is_locked, "is_important": c.is_important,
        "last_remark_at": c.last_remark_at.isoformat() if c.last_remark_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        # 资质字段（扁平化，方便前端读取）
        "qualifications": {
            # 身份信息
            "marriage": quals.get("marriage", ""),
            "education": quals.get("education", ""),
            "edu_type": quals.get("edu_type", ""),
            "occupation": quals.get("occupation", ""),
            "salary_issue": quals.get("salary_issue", ""),
            "biz_years": quals.get("biz_years", ""),
            # 房产
            "has_house": re.get("has_house", 0),
            "house_type": re.get("house_type", ""),
            "house_province": re.get("house_province", ""),
            "house_mortgage": re.get("house_mortgage", ""),
            "house_loan": re.get("house_loan", 0),
            # 车产
            "has_car": ve.get("has_car", 0),
            "car_type": ve.get("car_type", ""),
            "car_loan": ve.get("car_loan", 0),
            "car_years": ve.get("car_years", ""),
            "car_value": ve.get("car_value", ""),
            # 保单
            "has_insurance": ins.get("has_insurance", 0),
            "insurance_company": ins.get("insurance_company", ""),
            "insurance_status": ins.get("insurance_status", ""),
            # 社保公积金
            "social_security": quals.get("social_security", 0),
            "housing_fund": quals.get("housing_fund", 0),
            # 企业主
            "has_enterprise": quals.get("has_enterprise", 0),
            # 信用
            "weilidai": cr.get("weilidai", ""),
            "credit_query": cr.get("credit_query", ""),
            "loan_count": cr.get("loan_count", ""),
            "credit_card": cr.get("credit_card", ""),
            "credit_level": cr.get("credit_level", ""),
            "zhima_score": cr.get("zhima_score", ""),
            # 负债
            "debt_house": li.get("house", 0),
            "debt_car": li.get("car", 0),
            "debt_net": li.get("net", 0),
            "debt_other": li.get("other", 0),
            # 需求
            "loan_use": quals.get("loan_use", ""),
            "loan_term": quals.get("loan_term", ""),
            "urgency": quals.get("urgency", ""),
            "need_desc": quals.get("need_desc", ""),
            # 原始嵌套（保留兼容性）
            "real_estate": re, "vehicle": ve, "insurance": ins,
            "credit": cr, "liabilities": li,
        }
    }
    if include_options:
        result["_statusMap"] = STATUS_MAP
        result["_loanTypeMap"] = LOAN_TYPE_MAP
        result["_sources"] = ["BXMJ-excel", "T+1-excel", "有钱花", "分期乐", "豆豆钱",
                              "钱袋子", "桔多多", "宜融推单", "优乐推", "千橙广告", "其他"]
        # 标签信息
        if c.tag_assignments:
            ta = c.tag_assignments[0]
            result["tag"] = ta.tag.to_dict() if ta.tag else None
            result["tag_category"] = ta.tag.category if ta.tag else None
        else:
            result["tag"] = None
            result["tag_category"] = None
    return result


# ===================== Pydantic模型 =====================
class LoginIn(BaseModel):
    username: str
    password: str


class CustomerIn(BaseModel):
    phone: str
    name: str = ""
    gender: int = 0
    city: str = ""
    age: int = 0
    source: str = ""
    loan_type: int = 1
    apply_amount: float = 0
    qualifications: dict = {}


class CustomerUpd(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[int] = None
    city: Optional[str] = None
    age: Optional[int] = None
    loan_type: Optional[int] = None
    apply_amount: Optional[float] = None
    status: Optional[int] = None
    star_level: Optional[int] = None
    is_locked: Optional[int] = None
    is_important: Optional[int] = None
    qualifications: Optional[dict] = None


class RemarkIn(BaseModel):
    content: str
    remark_type: int = 0
    new_status: Optional[int] = None  # 提交备注同时变更客户状态


class LoanCaseIn(BaseModel):
    customer_id: int
    bank_name: str = ""
    bank_manager: str = ""
    apply_amount: float = 0
    fee_rate: float = 0


# ===================== 初始化数据库 =====================

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(User).count() == 0:
            # 创建默认部门（3级）
            dept = Department(name="融鑫汇公司", level=1)
            db.add(dept)
            db.flush()
            dept2 = Department(name="杭州一区", parent_id=dept.id, level=2)
            db.add(dept2)
            db.flush()
            dept3 = Department(name="一区二部2", parent_id=dept2.id, level=3)
            db.add(dept3)
            db.flush()

            # 创建负责人账号（role=0）
            boss = User(
                username="admin", password_hash=hash_password("admin123"),
                real_name="系统管理员", role=0, dept_id=dept3.id
            )
            db.add(boss)
            db.flush()

            # 创建测试顾问（role=5）
            for i in range(1, 4):
                u = User(
                    username=f"test{i}", password_hash=hash_password("123456"),
                    real_name=f"顾问{i}号", role=5, dept_id=dept3.id
                )
                db.add(u)
            db.commit()

            # 初始化标签数据
            init_tags(db)
            db.commit()
            print("[OK] 数据库初始化完成！默认账号: admin/admin123（负责人）")
        else:
            # 确保标签数据存在
            if db.query(CustomerTag).count() == 0:
                init_tags(db)
                db.commit()
            print("[OK] 数据库已是最新")
            # 迁移旧角色数据（role 1→5顾问, 2→4主管, 3→0负责人）
            _migrate_old_roles(db)
    finally:
        db.close()


def init_tags(db):
    """初始化客户标签数据（10维度）"""
    tag_data = [
        # 费用
        ("费用", "2%"), ("费用", "3%"), ("费用", "4%"), ("费用", "5%"),
        ("费用", "6%"), ("费用", "7%"), ("费用", "8%"),
        ("费用", "10%"), ("费用", "12%"), ("费用", "15%"),
        # 营业执照
        ("营业执照", "有限公司"), ("营业执照", "个体工商户"),
        # 经营情况
        ("经营情况", "真实经营（银联收款）"), ("经营情况", "真实经营（无收款）"), ("经营情况", "无实际经营"),
        # 需求时间
        ("需求时间", "1个月内"), ("需求时间", "2个月"), ("需求时间", "3个月"),
        ("需求时间", "6个月"), ("需求时间", "一年以上"),
        # 开票纳税
        ("开票纳税", "0"), ("开票纳税", "3万以下"), ("开票纳税", "3-10万"),
        ("开票纳税", "10-30万"), ("开票纳税", "30-50万"),
        ("开票纳税", "50-100万"), ("开票纳税", "100万以上"),
        # 工薪族
        ("工薪族", "代发10000+"), ("工薪族", "代发5000-10000"),
        ("工薪族", "代发5000以下"), ("工薪族", "现金发放"), ("工薪族", "半年内新入职"),
        # 房产
        ("房产", "全款红本"), ("房产", "按揭中"), ("房产", "按揭已清"),
        ("房产", "外地名下杭州购"), ("房产", "杭州户籍外地购"),
        ("房产", "安置房/宅基地"), ("房产", "自建房"), ("房产", "父母名下"),
        # 车产
        ("车产", "全款"), ("车产", "按揭中"), ("车产", "按揭已清"), ("车产", "公司户"),
        # 保单
        ("保单", "有商业保单（可贷）"),
        # 婚姻
        ("婚姻", "已婚有孩"), ("婚姻", "已婚无孩"), ("婚姻", "离异"),
    ]
    for i, (cat, name) in enumerate(tag_data):
        existing = db.query(CustomerTag).filter(
            CustomerTag.category == cat, CustomerTag.tag_name == name
        ).first()
        if not existing:
            tag = CustomerTag(category=cat, tag_name=name, sort_order=i)
            db.add(tag)
    print(f"[OK] 标签初始化完成，共 {len(tag_data)} 个标签")


def _migrate_old_roles(db):
    """迁移旧角色数据：1顾问→5顾问，2主管→4主管，3管理员→0负责人"""
    migration_map = {1: 5, 2: 4, 3: 0}
    migrated = 0
    for old_role, new_role in migration_map.items():
        db.query(User).filter(User.role == old_role).update({"role": new_role})
        migrated += 1
    if migrated > 0:
        db.commit()
        print(f"[OK] 角色迁移完成（顾问1→5，主管2→4，管理员3→0）")


# ===================== FastAPI 应用 =====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[CRM] 融鑫CRM启动中...")
    init_db()
    yield
    print("[BYE] 融鑫CRM已关闭")

app = FastAPI(title="融鑫CRM", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ===================== 登录接口 =====================

@app.post("/api/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "账号或密码错误")
    if user.status == 0:
        raise HTTPException(401, "账号已被禁用")
    token = create_token(user.id)
    return {
        "token": token,
        "user": user.to_dict()
    }


@app.get("/api/auth/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user.to_dict()


@app.post("/api/auth/password")
def change_password(old: str = Form(), new: str = Form(...), user: User = Depends(get_current_user)):
    if not verify_password(old, user.password_hash):
        raise HTTPException(400, "原密码错误")
    user.password_hash = hash_password(new)
    return {"msg": "密码修改成功"}


# ===================== 用户/部门接口 =====================

@app.get("/api/departments")
def get_depts(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        depts = db.query(Department).order_by(Department.level).all()
        return [{"id": d.id, "name": d.name, "parent_id": d.parent_id, "level": d.level} for d in depts]
    finally:
        db.close()


@app.get("/api/departments/{dept_id}/members")
def get_dept_members(dept_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取部门下的所有成员"""
    users = db.query(User).filter(User.dept_id == dept_id, User.status == 1).all()
    return {"members": [{"id": u.id, "real_name": u.real_name, "username": u.username} for u in users]}


@app.get("/api/users")
def get_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).filter(User.status == 1).all()
    return [u.to_dict() for u in users]


@app.get("/api/users/team")
def get_team(user: User = Depends(require_manager), db: Session = Depends(get_db)):
    users = db.query(User).filter(
        User.dept_id == user.dept_id, User.id != user.id
    ).all()
    return [u.to_dict() for u in users]


@app.put("/api/users/{uid}")
def update_user(uid: int, body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新用户个人信息（姓名、手机等），仅允许本人修改"""
    target = db.query(User).filter(User.id == uid).first()
    if not target:
        raise HTTPException(404, "用户不存在")
    # 顾问只能修改自己的信息，主管可以修改下属
    if uid != user.id and user.role >= 5:
        raise HTTPException(403, "无权修改他人信息")
    if body.get("real_name"):
        target.real_name = body["real_name"]
    if body.get("phone"):
        # 检查手机号是否被占用
        existing = db.query(User).filter(User.username == body["phone"], User.id != uid).first()
        if existing:
            raise HTTPException(400, "该手机号已被其他账号使用")
        target.username = body["phone"]
    if body.get("daily_quota") is not None and user.role <= 4:
        target.daily_quota = body["daily_quota"]
    db.commit()
    return target.to_dict()


@app.post("/api/users")
def create_user(body: dict, user: User = Depends(require_manager), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.get("username")).first():
        raise HTTPException(400, "账号已存在")
    u = User(
        username=body["username"], password_hash=hash_password(body.get("password", "123456")),
        real_name=body.get("real_name", ""), role=body.get("role", 1),
        dept_id=body.get("dept_id") or user.dept_id
    )
    db.add(u)
    db.commit()
    return u.to_dict()


@app.put("/api/users/{uid}/quota")
def set_quota(uid: int, daily_quota: int = Form(...), user: User = Depends(require_manager), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == uid, User.dept_id == user.dept_id).first()
    if not u:
        raise HTTPException(404, "用户不存在")
    u.daily_quota = daily_quota
    db.commit()
    return {"msg": "设置成功"}


# ===================== 客户搜索接口 =====================

@app.get("/api/customers")
def get_customers(
    keyword: str = Query(""), kw_type: str = Query(""),
    status: int = Query(-1), status_list: str = Query(""),
    star: int = Query(-1), star_list: str = Query(""),
    loan_type: int = Query(-1),
    locked: int = Query(-1), important: int = Query(-1),
    source: str = Query(""), sources: str = Query(""),
    city: str = Query(""),
    age_min: int = Query(0), age_max: int = Query(0),
    marital_status: int = Query(-1),
    start_date: str = Query(""), end_date: str = Query(""),
    remark_keyword: str = Query(""),
    no_remark_days: int = Query(0),
    time_type: str = Query("created"),
    data_type: int = Query(0),
    pool_type: int = Query(-1),
    remark_count_min: int = Query(0),
    remark_count_max: int = Query(0),
    remark_history: int = Query(-1),
    dept_id: int = Query(-1),
    other_condition: int = Query(-1),
    has_house: int = Query(-1),
    has_car: int = Query(-1),
    has_social_security: int = Query(-1),
    has_housing_fund: int = Query(-1),
    has_enterprise: int = Query(-1),
    has_salary_payment: int = Query(-1),
    has_insurance: int = Query(-1),
    has_credit_card: int = Query(-1),
    qual_keyword: str = Query(""),
    tag: str = Query(""),
    repay_status: int = Query(-1),
    page: int = Query(1), page_size: int = Query(20),
    sort_field: str = Query("created_at"), sort_order: str = Query("desc"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # 顾问只能看自己的客户
    q = db.query(Customer).join(
        CustomerAssignment,
        and_(CustomerAssignment.customer_id == Customer.id, CustomerAssignment.advisor_id == user.id)
    ).filter(CustomerAssignment.pool_type.in_([1, 2, 4]))

    # 数据类型筛选：原始数据(1) / 再分配(2)
    if data_type == 1:
        q = q.filter(CustomerAssignment.pool_type == 1)
    elif data_type == 2:
        q = q.filter(CustomerAssignment.pool_type == 2)

    # 入池类型筛选（来自公共池筛选）
    if pool_type >= 0:
        q = q.filter(CustomerAssignment.pool_type == pool_type)

    # 关键词搜索（支持按类型区分）
    if keyword:
        if kw_type == "phone":
            q = q.filter(Customer.phone.like(f"%{keyword}%"))
        elif kw_type == "name":
            q = q.filter(Customer.name.like(f"%{keyword}%"))
        elif kw_type == "id":
            if keyword.lstrip('-').isdigit():
                q = q.filter(Customer.id == int(keyword))
        else:
            q = q.filter(or_(
                Customer.name.like(f"%{keyword}%"),
                Customer.phone.like(f"%{keyword}%")
            ))

    # 多状态筛选（逗号分隔）
    if status_list:
        statuses = []
        for s in status_list.split(","):
            s = s.strip()
            if s and s.lstrip('-').isdigit():
                statuses.append(int(s))
        if statuses:
            q = q.filter(Customer.status.in_(statuses))

    if status >= 0:
        q = q.filter(Customer.status == status)
    if star >= 0:
        q = q.filter(Customer.star_level == star)
    # 星级多选（逗号分隔）
    if star_list:
        stars = []
        for s in star_list.split(","):
            s = s.strip()
            if s.lstrip('-').isdigit():
                stars.append(int(s))
        if stars:
            q = q.filter(Customer.star_level.in_(stars))
    if loan_type > 0:
        q = q.filter(Customer.loan_type == loan_type)
    if locked >= 0:
        q = q.filter(Customer.is_locked == locked)
    if important >= 0:
        q = q.filter(Customer.is_important == important)
    if source:
        q = q.filter(Customer.source == source)
    # 来源多选
    if sources:
        src_list = [s.strip() for s in sources.split(",") if s.strip()]
        if src_list:
            q = q.filter(Customer.source.in_(src_list))
    # 城市筛选
    if city:
        q = q.filter(Customer.city.like(f"%{city}%"))

    # 时间范围（按不同时间类型）
    if start_date or end_date:
        if time_type == "remark":
            col = Customer.last_remark_at
        elif time_type == "apply":
            # 实际申请时间：按进件提交时间 LoanCase.submit_at 筛选
            # 先找出符合条件的客户ID，再做时间筛选
            loan_q = db.query(LoanCase.customer_id, func.min(LoanCase.submit_at).label("apply_time")).filter(
                LoanCase.submit_at != None
            ).group_by(LoanCase.customer_id)
            if start_date:
                loan_q = loan_q.filter(LoanCase.submit_at >= start_date)
            if end_date:
                loan_q = loan_q.filter(LoanCase.submit_at <= end_date + " 23:59:59")
            apply_customer_ids = [r[0] for r in loan_q.all()]
            # 如果有结果才筛选，否则返回空
            if apply_customer_ids:
                q = q.filter(Customer.id.in_(apply_customer_ids))
            else:
                q = q.filter(Customer.id == -1)  # 无结果
        else:
            col = Customer.created_at
        if time_type != "apply" and (start_date or end_date):
            if start_date:
                q = q.filter(col >= start_date)
            if end_date:
                q = q.filter(col <= end_date + " 23:59:59")

    # 未备注超过N天筛选
    if no_remark_days > 0:
        cutoff = datetime.now() - timedelta(days=no_remark_days)
        q = q.filter(or_(
            Customer.last_remark_at < cutoff,
            Customer.last_remark_at == None
        ))

    if remark_keyword:
        q = q.filter(Customer.remarks.any(CustomerRemark.content.like(f"%{remark_keyword}%")))

    # 年龄范围筛选（SQL级）
    if age_min > 0:
        q = q.filter(Customer.age >= age_min)
    if age_max > 0:
        q = q.filter(Customer.age <= age_max)

    # 城市筛选
    if city:
        q = q.filter(Customer.city.like(f"%{city}%"))

    # 资质字段筛选（应用层过滤，SQLite JSON查询有限制）
    all_items = q.all()
    filtered = []
    for c in all_items:
        quals = c.qualifications or {}
        real_estate = quals.get("real_estate", {}) or {}
        vehicle = quals.get("vehicle", {}) or {}
        social_security = quals.get("social_security", 0)
        housing_fund = quals.get("housing_fund", 0)
        enterprise = quals.get("enterprise", 0)

        if has_house >= 0:
            has = bool(real_estate.get("property_type"))
            if has != bool(has_house):
                continue
        if has_car >= 0:
            has = bool(vehicle.get("car_type"))
            if has != bool(has_car):
                continue
        if has_social_security >= 0:
            has = bool(social_security > 0)
            if has != bool(has_social_security):
                continue
        if has_housing_fund >= 0:
            has = bool(housing_fund > 0)
            if has != bool(has_housing_fund):
                continue
        if has_enterprise >= 0:
            has = bool(enterprise > 0)
            if has != bool(has_enterprise):
                continue
        # 代发工资筛选
        if has_salary_payment >= 0:
            salary_payment = quals.get("salary_payment", 0) or 0
            has = bool(salary_payment > 0)
            if has != bool(has_salary_payment):
                continue
        # 婚姻状况筛选
        if marital_status >= 0:
            marriage = quals.get("marriage", 0) or 0
            if marriage != marital_status:
                continue
        # 保单筛选
        if has_insurance >= 0:
            insurance = quals.get("insurance", 0) or 0
            has = bool(insurance > 0)
            if has != bool(has_insurance):
                continue
        # 信用卡筛选
        if has_credit_card >= 0:
            credit_card = quals.get("credit_card", 0) or 0
            has = bool(credit_card > 0)
            if has != bool(has_credit_card):
                continue
        # 资质关键词搜索（在 qualifications JSON 各字段中搜索）
        if qual_keyword:
            quals_str = json.dumps(quals, ensure_ascii=False)
            if qual_keyword not in quals_str:
                continue
        # 按标签名称筛选
        if tag:
            found = False
            for ta in c.tag_assignments:
                if ta.tag and ta.tag.tag_name == tag:
                    found = True
                    break
            if not found:
                continue
        # 还款状态筛选（应用层）
        if repay_status >= 0:
            loan = db.query(LoanCase).filter(LoanCase.customer_id == c.id).first()
            if repay_status == 0:
                if loan:
                    continue
            elif repay_status == 1:
                if not loan or loan.stage == 3:
                    continue
            elif repay_status == 2:
                if not loan or loan.stage != 3:
                    continue
        # 备注次数范围筛选
        if remark_count_min > 0 or remark_count_max > 0:
            remark_count = len(c.remarks) if hasattr(c, 'remarks') else db.query(CustomerRemark).filter(CustomerRemark.customer_id == c.id).count()
            if remark_count_min > 0 and remark_count < remark_count_min:
                continue
            if remark_count_max > 0 and remark_count > remark_count_max:
                continue
        # 备注历史筛选（最近N天有备注）
        if remark_history >= 0:
            now = datetime.now()
            all_remarks = db.query(CustomerRemark).filter(CustomerRemark.customer_id == c.id).order_by(CustomerRemark.created_at.desc()).all()
            if remark_history == 0:
                # 今天
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                has_recent = any(r.created_at >= today for r in all_remarks)
                if not has_recent: continue
            else:
                cutoff = now - timedelta(days=remark_history)
                has_recent = any(r.created_at >= cutoff for r in all_remarks)
                if not has_recent: continue
        # 所属部门筛选
        if dept_id >= 0:
            matched = False
            for a in c.assignments:
                if a.status == 1:
                    advisor = db.query(User).filter(User.id == a.advisor_id).first()
                    if advisor and advisor.dept_id == dept_id:
                        matched = True
                        break
            if not matched: continue
        # 其他条件筛选
        if other_condition >= 0:
            if other_condition == 1:
                # 第一个备注顾问 - 保留所有（前端按备注历史筛选）
                pass
            elif other_condition == 2:
                # 第一次跟进时间 - 跳过没有跟进过的
                first_remark = db.query(CustomerRemark).filter(CustomerRemark.customer_id == c.id).order_by(CustomerRemark.created_at.asc()).first()
                if not first_remark: continue
            elif other_condition == 3:
                # 第一次贷款申请时间
                first_loan = db.query(LoanCase).filter(LoanCase.customer_id == c.id, LoanCase.submit_at != None).order_by(LoanCase.submit_at.asc()).first()
                if not first_loan: continue
        filtered.append(c)

    # 排序
    col = getattr(Customer, sort_field, Customer.created_at)
    filtered.sort(key=lambda c: getattr(c, sort_field) or datetime.min, reverse=(sort_order == "desc"))

    total = len(filtered)
    items = filtered[(page - 1) * page_size: page * page_size]
    return {"total": total, "items": [customer_to_dict(c, user) for c in items]}


@app.get("/api/customers/my-count")
def get_my_customer_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前顾问的客户数量（含上限信息）"""
    count = db.query(CustomerAssignment).filter(
        CustomerAssignment.advisor_id == user.id,
        CustomerAssignment.status == 1
    ).count()
    # 不同角色上限不同
    if user.role <= 2:
        limit = 1000  # 负责人/区长/部长无限制
    elif user.role == 3:
        limit = 800   # 二级主管
    elif user.role == 4:
        limit = 600   # 主管
    else:
        limit = 400   # 顾问/学徒
    return {"count": count, "limit": limit, "near_limit": count >= limit * 0.9, "at_limit": count >= limit, "role": user.role, "roleText": ROLE_TEXT.get(user.role, "未知")}


@app.get("/api/customers/all-options")
def get_all_options():
    return {
        "statusMap": STATUS_MAP,
        "statusEditable": STATUS_EDITABLE,
        "loanTypeMap": LOAN_TYPE_MAP,
        "maritalStatusMap": MARITAL_STATUS_MAP,
        "roleMap": ROLE_TEXT,
        "quickRemarks": QUICK_REMARKS,
        "remarkHint": REMARK_HINT,
        "sources": ["BXMJ-excel", "T+1-excel", "有钱花", "分期乐", "豆豆钱", "钱袋子",
                    "桔多多", "宜融推单", "优乐推", "千橙广告", "PA-excel", "其他"],
        "tagCategories": TAG_CATEGORIES,
    }


@app.get("/api/customers/{cid}")
def get_customer(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "客户不存在")
    # 检查权限
    assignment = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == cid,
        CustomerAssignment.advisor_id == user.id,
        CustomerAssignment.status == 1
    ).first()
    if not assignment and user.role >= 5:
        raise HTTPException(403, "无权访问此客户")
    return customer_to_dict(c, user, include_options=True)


@app.get("/api/customers/{cid}/assign-history")
def get_customer_assign_history(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取客户分配历史"""
    assignments = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == cid
    ).order_by(CustomerAssignment.assigned_at.desc()).limit(50).all()
    items = []
    for a in assignments:
        from_user = db.query(User).filter(User.id == (a.assigned_by or 0)).first()
        to_user = db.query(User).filter(User.id == a.advisor_id).first()
        items.append({
            "id": a.id,
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            "from_name": from_user.real_name if from_user else "系统",
            "to_name": to_user.real_name if to_user else "未知",
            "pool_type": a.pool_type,
            "status": a.status,
        })
    return {"items": items}


@app.post("/api/customers")
def create_customer(body: CustomerIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 查重
    ph = hash_phone(body.phone)
    existing = db.query(Customer).filter(Customer.phone_hash == ph).first()
    if existing:
        raise HTTPException(400, f"手机号已存在（客户ID: {existing.id}）")
    c = Customer(
        phone=body.phone, phone_hash=ph, name=body.name, gender=body.gender,
        city=body.city, age=body.age, source=body.source,
        loan_type=body.loan_type, apply_amount=body.apply_amount,
        qualifications=body.qualifications
    )
    db.add(c)
    db.flush()

    # 分配给当前顾问
    assign = CustomerAssignment(customer_id=c.id, advisor_id=user.id, pool_type=1)
    db.add(assign)
    db.commit()
    return customer_to_dict(c, user)


@app.get("/api/customers/all-options")
def get_all_options(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取客户相关下拉选项"""
    # 获取所有标签名称列表
    tags = db.query(CustomerTag).all()
    tag_list = sorted(set([t.tag_name for t in tags if t.tag_name]))
    # 如果没有标签，返回预定义标签
    if not tag_list:
        tag_list = [
            # 费用
            "2%", "3%", "4%", "5%", "6%", "7%", "8%", "10%", "12%", "15%",
            # 工薪族
            "代发10000+", "代发5000-10000", "代发5000以下", "现金发放", "半年内新入职",
            # 房产
            "全款红本", "按揭中", "按揭已清", "外地名下杭州购", "安置房/宅基地",
            # 车产
            "全款", "按揭中", "按揭已清", "公司户",
            # 婚姻
            "已婚有孩", "已婚无孩", "离异",
            # 保单
        "有商业保单（可贷）",
    ]
    # 查询城市列表（去重）
    cities = db.query(Customer.city).filter(Customer.city != None, Customer.city != "").distinct().all()
    city_list = sorted(set([c[0] for c in cities if c[0]]))
    # 查询来源列表（去重，合并预定义）
    srcs = db.query(Customer.source).filter(Customer.source != None, Customer.source != "").distinct().all()
    src_list = sorted(set([s[0] for s in srcs if s[0]]))
    default_srcs = ["BXMJ-excel", "T+1-excel", "有钱花", "分期乐", "豆豆钱", "钱袋子",
                   "桔多多", "宜融推单", "优乐推", "千橙广告", "PA-excel", "YYDL-excel",
                   "ZX-excel", "ZY-excel", "融信用", "宜融钱包", "#全部流量客户#", "其他"]
    for ds in default_srcs:
        if ds not in src_list:
            src_list.append(ds)
    src_list = sorted(src_list)
    return {
        "statusMap": STATUS_MAP,
        "loanTypeMap": LOAN_TYPE_MAP,
        "maritalStatusMap": MARITAL_STATUS_MAP,
        "sources": src_list,
        "cityList": city_list,
        "tagList": tag_list,
    }


@app.get("/api/customers/check-phone")
def check_phone(phone: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """检查手机号是否已存在，返回已有客户信息"""
    ph = hash_phone(phone)
    c = db.query(Customer).filter(Customer.phone_hash == ph).first()
    if c:
        return {"exists": True, "customer_id": c.id, "customer_name": c.name, "status": c.status}
    return {"exists": False}


@app.put("/api/customers/{cid}")
def update_customer(cid: int, body: CustomerUpd, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "客户不存在")

    # 如果要更新手机号，先检查重复
    if body.phone is not None and body.phone != c.phone:
        ph = hash_phone(body.phone)
        dup = db.query(Customer).filter(Customer.phone_hash == ph, Customer.id != cid).first()
        if dup:
            raise HTTPException(400, f"手机号已存在（客户ID: {dup.id}）")
        c.phone = body.phone
        c.phone_hash = ph

    data = body.model_dump(exclude_none=True)
    # phone已在上面直接更新，从data中移除避免重复赋值
    if "phone" in data:
        del data["phone"]
    if "qualifications" in data:
        quals = {**(c.qualifications or {}), **data.pop("qualifications")}
        c.qualifications = quals

    for k, v in data.items():
        setattr(c, k, v)
    db.commit()
    return customer_to_dict(c, user)


@app.delete("/api/customers/{cid}")
def delete_customer(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "客户不存在")
    db.query(CustomerAssignment).filter(CustomerAssignment.customer_id == cid).delete()
    db.delete(c)
    db.commit()
    return {"msg": "删除成功"}


# ===================== 备注接口 =====================

@app.get("/api/customers/{cid}/remarks")
def get_remarks(cid: int, page: int = Query(1), page_size: int = Query(50),
                 user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(CustomerRemark, User).join(User, User.id == CustomerRemark.advisor_id).filter(CustomerRemark.customer_id == cid)
    total = q.count()
    rows = q.order_by(CustomerRemark.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [{
            "id": r.id, "content": r.content, "remark_type": r.remark_type,
            "remark_type_text": ["跟进记录", "主管点评", "备忘"][r.remark_type] if r.remark_type <= 2 else "备忘",
            "status_at_remark": r.status_at_remark,
            "statusText": STATUS_MAP.get(r.status_at_remark, ""),
            "created_at": r.created_at.isoformat() if r.created_at else "",
            "advisor_id": r.advisor_id,
            "advisor_name": u.real_name if u else ""
        } for r, u in rows]
    }


@app.post("/api/customers/{cid}/remarks")
def add_remark(cid: int, body: RemarkIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "客户不存在")

    r = CustomerRemark(
        customer_id=cid, advisor_id=user.id, content=body.content,
        remark_type=body.remark_type, status_at_remark=c.status
    )
    db.add(r)
    c.last_remark_at = datetime.now()
    # 如果同时传了新状态，则更新客户状态
    if body.new_status is not None and body.new_status >= 0:
        c.status = body.new_status
        r.status_at_remark = body.new_status
    db.commit()
    return {"id": r.id, "created_at": r.created_at.isoformat()}


# ===================== 提醒接口 =====================

class ReminderIn(BaseModel):
    customer_id: int
    content: str
    reminder_at: str  # ISO format datetime string


@app.post("/api/reminders")
def create_reminder(body: ReminderIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """创建提醒"""
    from datetime import datetime
    ra = datetime.fromisoformat(body.reminder_at)
    r = CustomerReminder(customer_id=body.customer_id, advisor_id=user.id, content=body.content, reminder_at=ra)
    db.add(r)
    db.commit()
    return r.to_dict()


@app.get("/api/reminders/upcoming")
def get_upcoming_reminders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户今日及过期的提醒"""
    from datetime import datetime
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    reminders = db.query(CustomerReminder).filter(
        CustomerReminder.advisor_id == user.id,
        CustomerReminder.is_done == 0,
        CustomerReminder.reminder_at <= today.replace(hour=23, minute=59, second=59)
    ).order_by(CustomerReminder.reminder_at.asc()).limit(50).all()
    items = []
    for r in reminders:
        customer = db.query(Customer).filter(Customer.id == r.customer_id).first()
        items.append({**r.to_dict(), "customer_name": customer.name if customer else "未知"})
    return {"items": items}


@app.put("/api/reminders/{rid}/done")
def mark_reminder_done(rid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """标记提醒为已完成"""
    r = db.query(CustomerReminder).filter(CustomerReminder.id == rid, CustomerReminder.advisor_id == user.id).first()
    if not r:
        raise HTTPException(404, "提醒不存在")
    r.is_done = 1
    db.commit()
    return {"ok": True}


@app.delete("/api/reminders/{rid}")
def delete_reminder(rid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.query(CustomerReminder).filter(CustomerReminder.id == rid, CustomerReminder.advisor_id == user.id).first()
    if not r:
        raise HTTPException(404, "提醒不存在")
    db.delete(r)
    db.commit()
    return {"ok": True}


# ===================== 客户池操作 =====================

@app.post("/api/customers/{cid}/to-pool")
def to_pool(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """加入公共池"""
    assignment = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == cid, CustomerAssignment.advisor_id == user.id,
        CustomerAssignment.status == 1
    ).first()
    if assignment:
        assignment.status = 0
    pool = CustomerAssignment(customer_id=cid, advisor_id=user.id, pool_type=3, assigned_by=user.id)
    db.add(pool)
    db.commit()
    return {"msg": "已加入公共池"}


@app.post("/api/customers/{cid}/to-must-follow")
def to_must_follow(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """加入必跟进"""
    assignment = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == cid, CustomerAssignment.advisor_id == user.id,
        CustomerAssignment.status == 1
    ).first()
    if assignment:
        assignment.status = 0
    pool = CustomerAssignment(customer_id=cid, advisor_id=user.id, pool_type=4, assigned_by=user.id)
    db.add(pool)
    db.commit()
    return {"msg": "已加入必跟进"}


@app.post("/api/customers/{cid}/from-pool")
def from_pool(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """从公共池取出"""
    # 检查是否已被其他人取走
    existing = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == cid, CustomerAssignment.pool_type.in_([1, 2]),
        CustomerAssignment.status == 1
    ).first()
    if existing and existing.advisor_id != user.id:
        raise HTTPException(400, "此客户已被其他顾问领取")

    # 停用公共池分配记录
    old_pool = db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == cid,
        CustomerAssignment.pool_type == 3,
        CustomerAssignment.status == 1
    ).first()
    if old_pool:
        old_pool.status = 0

    assignment = CustomerAssignment(customer_id=cid, advisor_id=user.id, pool_type=1, assigned_by=user.id)
    db.add(assignment)
    db.commit()
    return {"msg": "领取成功"}


@app.post("/api/customers/{cid}/lock")
def lock_customer(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "客户不存在")
    c.is_locked = 1 if c.is_locked == 0 else 0
    db.commit()
    return {"msg": "锁定成功" if c.is_locked else "解锁成功"}


@app.post("/api/customers/{cid}/important")
def mark_important(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "客户不存在")
    c.is_important = 1 if c.is_important == 0 else 0
    db.commit()
    return {"msg": "标为重要" if c.is_important else "取消重要"}


@app.post("/api/customers/{cid}/blacklist")
def blacklist(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(404, "客户不存在")
    c.is_blacklisted = 1 if c.is_blacklisted == 0 else 0
    db.commit()
    return {"msg": "已拉黑" if c.is_blacklisted else "已移除黑名单"}


# ===================== 公共池接口 =====================

@app.get("/api/pool")
def get_pool(
    keyword: str = Query(""), kw_type: str = Query(""),
    status: int = Query(-1), status_list: str = Query(""),
    star: int = Query(-1), star_list: str = Query(""),
    loan_type: int = Query(-1),
    locked: int = Query(-1), important: int = Query(-1),
    source: str = Query(""), sources: str = Query(""),
    city: str = Query(""),
    age_min: int = Query(0), age_max: int = Query(0),
    marital_status: int = Query(-1),
    has_insurance: int = Query(-1),
    has_credit_card: int = Query(-1),
    # 新增字段
    pool_type: int = Query(-1),
    time_type: int = Query(-1),
    no_remark_days: int = Query(0),
    remark_keyword: str = Query(""),
    remark_count_min: int = Query(0),
    remark_count_max: int = Query(0),
    remark_history: int = Query(-1),
    dept_id: int = Query(-1),
    other_condition: int = Query(-1),
    quals_keyword: str = Query(""),
    page: int = Query(1), page_size: int = Query(20),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # 基础查询：公共池（pool_type=3）
    q = db.query(Customer).join(
        CustomerAssignment,
        and_(CustomerAssignment.customer_id == Customer.id, CustomerAssignment.pool_type == 3,
             CustomerAssignment.status == 1)
    )

    # 入池类型（assignment的pool_type：2=再分配 3=公共池 4=转介）
    # 注意：外层JOIN条件固定pool_type=3，但如果筛选其他类型需要用子查询
    if pool_type >= 0:
        # 重新筛选：改为直接JOIN不限制pool_type，由pool_type过滤
        q = db.query(Customer).join(
            CustomerAssignment,
            and_(CustomerAssignment.customer_id == Customer.id,
                 CustomerAssignment.pool_type == pool_type,
                 CustomerAssignment.status == 1)
        )

    # 关键词搜索方式
    if keyword:
        if kw_type == "phone":
            q = q.filter(Customer.phone.like(f"%{keyword}%"))
        elif kw_type == "name":
            q = q.filter(Customer.name.like(f"%{keyword}%"))
        elif kw_type == "id":
            if keyword.lstrip('-').isdigit():
                q = q.filter(Customer.id == int(keyword))
        else:
            q = q.filter(or_(Customer.name.like(f"%{keyword}%"), Customer.phone.like(f"%{keyword}%")))

    # 状态多选
    if status_list:
        slist = []
        for s in status_list.split(","):
            s = s.strip()
            if s.lstrip('-').isdigit():
                slist.append(int(s))
        if slist:
            q = q.filter(Customer.status.in_(slist))
    elif status >= 0:
        q = q.filter(Customer.status == status)

    # 星级多选
    if star_list:
        slist = []
        for s in star_list.split(","):
            s = s.strip()
            if s.lstrip('-').isdigit():
                slist.append(int(s))
        if slist:
            q = q.filter(Customer.star_level.in_(slist))
    elif star >= 0:
        q = q.filter(Customer.star_level == star)

    if loan_type >= 0:
        q = q.filter(Customer.loan_type == loan_type)
    if locked >= 0:
        q = q.filter(Customer.is_locked == (1 if locked else 0))
    if important >= 0:
        q = q.filter(Customer.is_important == (1 if important else 0))

    # 来源多选
    if sources:
        src_list = [s.strip() for s in sources.split(",") if s.strip()]
        if src_list:
            q = q.filter(Customer.source.in_(src_list))
    elif source:
        q = q.filter(Customer.source == source)

    if city:
        q = q.filter(Customer.city.like(f"%{city}%"))
    if age_min > 0:
        q = q.filter(Customer.age >= age_min)
    if age_max > 0:
        q = q.filter(Customer.age <= age_max)

    # 时间类型排序：1=按入池时间 2=按创建时间
    order_col = CustomerAssignment.assigned_at if (time_type == 1 or time_type < 0) else Customer.created_at

    # 应用层过滤：资质字段（JSON列）、备注相关、所属部门、资质关键词
    needs_app_filter = (
        marital_status >= 0 or has_insurance >= 0 or has_credit_card >= 0
        or no_remark_days > 0 or remark_keyword or remark_count_min > 0 or remark_count_max > 0
        or remark_history >= 0 or dept_id >= 0 or quals_keyword
    )

    if needs_app_filter:
        # 获取所有数据后在Python层过滤
        from sqlalchemy.orm import joinedload
        all_q = db.query(Customer).options(joinedload(Customer.assignments))
        # 重新应用JOIN条件
        if pool_type >= 0:
            all_q = all_q.join(CustomerAssignment,
                and_(CustomerAssignment.customer_id == Customer.id,
                     CustomerAssignment.pool_type == pool_type,
                     CustomerAssignment.status == 1))
        else:
            all_q = all_q.join(CustomerAssignment,
                and_(CustomerAssignment.customer_id == Customer.id,
                     CustomerAssignment.pool_type == 3,
                     CustomerAssignment.status == 1))
        # 应用SQL层过滤
        if keyword:
            if kw_type == "phone":
                all_q = all_q.filter(Customer.phone.like(f"%{keyword}%"))
            elif kw_type == "name":
                all_q = all_q.filter(Customer.name.like(f"%{keyword}%"))
            elif kw_type == "id" and keyword.lstrip('-').isdigit():
                all_q = all_q.filter(Customer.id == int(keyword))
            else:
                all_q = all_q.filter(or_(Customer.name.like(f"%{keyword}%"), Customer.phone.like(f"%{keyword}%")))
        if status_list:
            slist = [int(s.strip()) for s in status_list.split(",") if s.strip().lstrip('-').isdigit()]
            if slist: all_q = all_q.filter(Customer.status.in_(slist))
        elif status >= 0:
            all_q = all_q.filter(Customer.status == status)
        if star_list:
            slist = [int(s.strip()) for s in star_list.split(",") if s.strip().lstrip('-').isdigit()]
            if slist: all_q = all_q.filter(Customer.star_level.in_(slist))
        elif star >= 0:
            all_q = all_q.filter(Customer.star_level == star)
        if loan_type >= 0: all_q = all_q.filter(Customer.loan_type == loan_type)
        if locked >= 0: all_q = all_q.filter(Customer.is_locked == (1 if locked else 0))
        if important >= 0: all_q = all_q.filter(Customer.is_important == (1 if important else 0))
        if sources:
            src_list = [s.strip() for s in sources.split(",") if s.strip()]
            if src_list: all_q = all_q.filter(Customer.source.in_(src_list))
        elif source:
            all_q = all_q.filter(Customer.source == source)
        if city: all_q = all_q.filter(Customer.city.like(f"%{city}%"))
        if age_min > 0: all_q = all_q.filter(Customer.age >= age_min)
        if age_max > 0: all_q = all_q.filter(Customer.age <= age_max)

        all_custs = all_q.all()
        filtered = []

        now = datetime.now()
        for c in all_custs:
            # 资质字段过滤
            if marital_status >= 0 or has_insurance >= 0 or has_credit_card >= 0:
                quals = c.qualifications or {}
                if marital_status >= 0:
                    marriage = quals.get("marriage", 0) or 0
                    if marriage != marital_status: continue
                if has_insurance >= 0:
                    has = bool((quals.get("has_insurance", 0) or 0) > 0)
                    if has != bool(has_insurance): continue
                if has_credit_card >= 0:
                    has = bool((quals.get("credit_card", 0) or 0) > 0)
                    if has != bool(has_credit_card): continue

            # 备注相关过滤
            remarks = db.query(CustomerRemark).filter(CustomerRemark.customer_id == c.id).order_by(CustomerRemark.created_at.asc()).all()
            remark_count = len(remarks)

            if remark_count_min > 0 and remark_count < remark_count_min: continue
            if remark_count_max > 0 and remark_count > remark_count_max: continue

            if remark_keyword:
                found = any(remark_keyword in (r.content or '') for r in remarks)
                if not found: continue

            if remark_history >= 0:
                if remark_count == 0:
                    # 无备注，则按入池时间判断
                    last_remark_time = None
                    for a in c.assignments:
                        if a.assigned_at:
                            last_remark_time = a.assigned_at
                            break
                else:
                    last_remark_time = remarks[-1].created_at
                if last_remark_time:
                    days_diff = (now - last_remark_time).days
                    if days_diff > remark_history: continue
                # 如果remark_history=0（今天），且无备注，跳过
                if remark_count == 0 and remark_history == 0: continue

            if no_remark_days > 0:
                if remark_count == 0:
                    # 从入池时间算起
                    last_time = None
                    for a in c.assignments:
                        if a.assigned_at:
                            last_time = a.assigned_at
                            break
                    if last_time and (now - last_time).days > no_remark_days: pass
                    else: continue
                else:
                    last_time = remarks[-1].created_at
                    if (now - last_time).days > no_remark_days: pass
                    else: continue

            # 所属部门过滤
            if dept_id >= 0:
                # 查找当前有效分配的顾问部门
                matched = False
                for a in c.assignments:
                    if a.status == 1:
                        advisor = db.query(User).filter(User.id == a.advisor_id).first()
                        if advisor and advisor.dept_id == dept_id:
                            matched = True
                            break
                if not matched: continue

            # 资质关键词过滤
            if quals_keyword:
                quals = c.qualifications or {}
                quals_str = json.dumps(quals, ensure_ascii=False)
                if quals_keyword not in quals_str: continue

            filtered.append(c)

        total = len(filtered)
        # 排序
        if time_type == 2:
            filtered.sort(key=lambda c: c.created_at or datetime.min, reverse=True)
        else:
            # 按入池时间（取最近一次入池时间）
            filtered.sort(key=lambda c: max((a.assigned_at or datetime.min) for a in c.assignments if a.status == 1) if c.assignments else datetime.min, reverse=True)
        start = (page - 1) * page_size
        end = start + page_size
        items = filtered[start:end]
        return {"total": total, "items": [customer_to_dict(c, user) for c in items]}

    total = q.count()
    items = q.order_by(order_col.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "items": [customer_to_dict(c, user) for c in items]}


@app.get("/api/pool/count")
def pool_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(CustomerAssignment).filter(
        CustomerAssignment.pool_type == 3, CustomerAssignment.status == 1
    ).count()
    return {"count": count}


# ===================== 转移记录接口 =====================

@app.get("/api/transfer-history")
def get_transfer_history(
    page: int = Query(1), page_size: int = Query(50),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取当前用户的客户转移记录（所有下属客户的分配历史）"""
    # 主管看团队，顾问只看自己
    if user.role <= 4:
        team_ids = [u.id for u in db.query(User).filter(User.dept_id == user.dept_id).all()]
        if not team_ids:
            team_ids = [user.id]
        q = db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id.in_(team_ids)
        )
    else:
        q = db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == user.id
        )

    total = q.count()
    rows = q.order_by(CustomerAssignment.assigned_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    items = []
    for a in rows:
        customer = db.query(Customer).filter(Customer.id == a.customer_id).first()
        from_user = db.query(User).filter(User.id == (a.assigned_by or 0)).first()
        to_user = db.query(User).filter(User.id == a.advisor_id).first()
        items.append({
            "id": a.id,
            "customer_id": a.customer_id,
            "customer_name": customer.name if customer else "未知",
            "customer_phone": mask_phone(customer.phone) if customer else "",
            "from_name": from_user.real_name if from_user else "系统",
            "to_name": to_user.real_name if to_user else "未知",
            "pool_type": a.pool_type,
            "pool_type_text": {1: "我的客户", 2: "再分配", 3: "公共池", 4: "必跟进"}.get(a.pool_type, "未知"),
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            "status": a.status,
        })

    return {"total": total, "items": items}


# ===================== 必跟进池 =====================

@app.get("/api/important-pool")
def get_important_pool(
    keyword: str = Query(""), status: int = Query(-1), star: int = Query(-1),
    loan_type: int = Query(-1),
    page: int = Query(1), page_size: int = Query(20),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """必跟进客户：超过7天未备注的客户（可搜索/筛选）"""
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=7)
    q = db.query(Customer).join(
        CustomerAssignment,
        and_(CustomerAssignment.customer_id == Customer.id, CustomerAssignment.advisor_id == user.id)
    ).filter(
        CustomerAssignment.pool_type.in_([1, 4]),
        CustomerAssignment.status == 1,
        or_(Customer.last_remark_at < cutoff, Customer.last_remark_at == None)
    )

    if keyword:
        q = q.filter(or_(
            Customer.name.like(f"%{keyword}%"),
            Customer.phone.like(f"%{keyword}%")
        ))
    if status >= 0:
        q = q.filter(Customer.status == status)
    if star >= 0:
        q = q.filter(Customer.star_level == star)
    if loan_type > 0:
        q = q.filter(Customer.loan_type == loan_type)

    total = q.count()
    items = q.order_by(Customer.last_remark_at.asc().nullsfirst()).offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "items": [customer_to_dict(c, user) for c in items]}


# ===================== 在审件接口 =====================

@app.get("/api/loan-cases")
def get_loan_cases(
    stage: int = Query(-1), keyword: str = Query(""),
    page: int = Query(1), page_size: int = Query(20),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    q = db.query(LoanCase).filter(LoanCase.advisor_id == user.id)
    if stage >= 0:
        q = q.filter(LoanCase.stage == stage)
    if keyword:
        q = q.filter(LoanCase.customer_id == int(keyword) if keyword.isdigit() else 0)

    total = q.count()
    items = q.order_by(LoanCase.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    STAGE_MAP = {1: "审核中", 2: "已批款", 3: "已收款", 4: "已拒批", 5: "已违约"}
    result = []
    for lc in items:
        c = db.query(Customer).filter(Customer.id == lc.customer_id).first()
        result.append({
            "id": lc.id, "customer_id": lc.customer_id,
            "customer_name": c.name if c else "未知",
            "customer_phone": mask_phone(c.phone) if c else "",
            "bank_name": lc.bank_name, "bank_manager": lc.bank_manager,
            "apply_amount": float(lc.apply_amount or 0),
            "fee_rate": float(lc.fee_rate or 0),
            "stage": lc.stage, "stageText": STAGE_MAP.get(lc.stage, "审核中"),
            "approve_amount": float(lc.approve_amount or 0),
            "collection_amount": float(lc.collection_amount or 0),
            "submit_at": lc.submit_at.isoformat() if lc.submit_at else None,
            "approve_at": lc.approve_at.isoformat() if lc.approve_at else None,
            "collection_at": lc.collection_at.isoformat() if lc.collection_at else None,
            "created_at": lc.created_at.isoformat() if lc.created_at else None,
        })
    return {"total": total, "items": result}


@app.post("/api/loan-cases")
def create_loan_case(body: LoanCaseIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lc = LoanCase(
        customer_id=body.customer_id, advisor_id=user.id, dept_id=user.dept_id,
        bank_name=body.bank_name, bank_manager=body.bank_manager,
        apply_amount=body.apply_amount, fee_rate=body.fee_rate
    )
    db.add(lc)
    db.commit()
    return {"id": lc.id}


@app.put("/api/loan-cases/{lid}/stage")
def update_case_stage(lid: int, stage: int = Form(...), amount: float = Form(0),
                      user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lc = db.query(LoanCase).filter(LoanCase.id == lid, LoanCase.advisor_id == user.id).first()
    if not lc:
        raise HTTPException(404, "在审件不存在")
    lc.stage = stage
    if stage == 2:
        lc.approve_amount = amount
        lc.approve_at = datetime.now()
    elif stage == 3:
        lc.collection_amount = amount
        lc.collection_at = datetime.now()
    db.commit()
    return {"msg": "更新成功"}


class LoanCaseUpdate(BaseModel):
    bank_name: Optional[str] = None
    bank_manager: Optional[str] = None
    apply_amount: Optional[float] = None
    fee_rate: Optional[float] = None
    submit_at: Optional[str] = None

@app.put("/api/loan-cases/{lid}")
def update_loan_case(lid: int, body: LoanCaseUpdate,
                     user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """编辑进件基本信息"""
    lc = db.query(LoanCase).filter(LoanCase.id == lid).first()
    if not lc:
        raise HTTPException(404, "在审件不存在")
    if lc.advisor_id != user.id and user.role < 2:
        raise HTTPException(403, "无权限")
    if body.bank_name is not None:
        lc.bank_name = body.bank_name
    if body.bank_manager is not None:
        lc.bank_manager = body.bank_manager
    if body.apply_amount is not None:
        lc.apply_amount = body.apply_amount
    if body.fee_rate is not None:
        lc.fee_rate = body.fee_rate
    if body.submit_at:
        try:
            lc.submit_at = datetime.fromisoformat(body.submit_at)
        except:
            pass
    db.commit()
    return {"msg": "更新成功"}


# ===================== 统计接口 =====================

@app.get("/api/stats/dashboard")
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    month_start = today.replace(day=1)

    my_ids = [a.id for a in db.query(CustomerAssignment.id).filter(
        CustomerAssignment.advisor_id == user.id, CustomerAssignment.status == 1,
        CustomerAssignment.pool_type.in_([1, 2, 4])
    ).all()]

    total = len(my_ids) if my_ids else 0
    if not my_ids:
        my_ids = [0]

    # 今日新增
    today_new = db.query(Customer).filter(
        Customer.id.in_(my_ids), func.date(Customer.created_at) == today
    ).count()

    # 今日备注
    today_remark = db.query(CustomerRemark).filter(
        CustomerRemark.advisor_id == user.id,
        func.date(CustomerRemark.created_at) == today
    ).count()

    # 本月在审件
    month_cases = db.query(LoanCase).filter(
        LoanCase.advisor_id == user.id,
        LoanCase.submit_at >= month_start
    ).count()

    # 今日进件
    today_cases = db.query(LoanCase).filter(
        LoanCase.advisor_id == user.id,
        func.date(LoanCase.submit_at) == today
    ).count()

    # 星级分布
    star_dist = db.query(Customer.star_level, func.count()).filter(
        Customer.id.in_(my_ids)
    ).group_by(Customer.star_level).all()
    star_data = [{"name": f"{s}星", "value": c} for s, c in star_dist]

    # 状态分布
    status_dist = db.query(Customer.status, func.count()).filter(
        Customer.id.in_(my_ids)
    ).group_by(Customer.status).all()
    status_data = [{"name": STATUS_MAP.get(s, "未知"), "value": c} for s, c in status_dist]

    # 公共池数量
    pool_count = db.query(CustomerAssignment).filter(
        CustomerAssignment.pool_type == 3, CustomerAssignment.status == 1
    ).count()

    return {
        "total": total, "todayNew": today_new, "todayRemark": today_remark,
        "monthCases": month_cases, "todayCases": today_cases,
        "poolCount": pool_count,
        "starDist": star_data, "statusDist": status_data
    }


@app.get("/api/stats/monthly")
def get_monthly_stats(month: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not month:
        month = date.today().strftime("%Y-%m")
    from calendar import monthrange
    y, m = int(month[:4]), int(month[5:7])
    _, last_day = monthrange(y, m)
    start = f"{y}-{m:02d}-01"
    end = f"{y}-{m:02d}-{last_day}"

    my_ids = [a.customer_id for a in db.query(CustomerAssignment).filter(
        CustomerAssignment.advisor_id == user.id, CustomerAssignment.status == 1,
        CustomerAssignment.pool_type.in_([1, 2, 4])
    ).all()]
    if not my_ids:
        my_ids = [0]

    new_count = db.query(func.count()).select_from(Customer).filter(
        Customer.id.in_(my_ids),
        Customer.created_at >= start, Customer.created_at <= end + " 23:59:59"
    ).scalar()

    remark_count = db.query(func.count()).select_from(CustomerRemark).filter(
        CustomerRemark.advisor_id == user.id,
        CustomerRemark.created_at >= start, CustomerRemark.created_at <= end + " 23:59:59"
    ).scalar()

    case_count = db.query(func.count()).select_from(LoanCase).filter(
        LoanCase.advisor_id == user.id,
        LoanCase.submit_at >= start, LoanCase.submit_at <= end + " 23:59:59"
    ).scalar()

    approve_count = db.query(func.count()).select_from(LoanCase).filter(
        LoanCase.advisor_id == user.id,
        LoanCase.stage == 2,
        LoanCase.approve_at >= start, LoanCase.approve_at <= end + " 23:59:59"
    ).scalar()

    collection_count = db.query(func.count()).select_from(LoanCase).filter(
        LoanCase.advisor_id == user.id,
        LoanCase.stage == 3,
        LoanCase.collection_at >= start, LoanCase.collection_at <= end + " 23:59:59"
    ).scalar()

    approve_amount_row = db.query(func.sum(LoanCase.approve_amount)).filter(
        LoanCase.advisor_id == user.id,
        LoanCase.stage >= 2,
        LoanCase.approve_at >= start, LoanCase.approve_at <= end + " 23:59:59"
    ).scalar()

    return {
        "month": month, "newCount": new_count or 0, "remarkCount": remark_count or 0,
        "caseCount": case_count or 0, "approveCount": approve_count or 0,
        "collectionCount": collection_count or 0,
        "approveAmount": float(approve_amount_row or 0)
    }


# ===================== 团队管理接口 =====================

@app.get("/api/team/customers")
def team_customers(
    keyword: str = Query(""), page: int = Query(1), page_size: int = Query(20),
    advisor_id: int = Query(None),
    user: User = Depends(require_manager), db: Session = Depends(get_db)
):
    """主管查看所有下属客户"""
    sub_ids = [u.id for u in db.query(User).filter(User.dept_id == user.dept_id).all()]
    if not sub_ids:
        sub_ids = [user.id]

    q = db.query(Customer, CustomerAssignment, User).join(
        CustomerAssignment, CustomerAssignment.customer_id == Customer.id
    ).join(
        User, User.id == CustomerAssignment.advisor_id
    ).filter(
        CustomerAssignment.advisor_id.in_(sub_ids),
        CustomerAssignment.pool_type.in_([1, 2, 4]),
        CustomerAssignment.status == 1
    )

    if advisor_id:
        q = q.filter(CustomerAssignment.advisor_id == advisor_id)
    if keyword:
        q = q.filter(or_(
            Customer.name.like(f"%{keyword}%"), Customer.phone.like(f"%{keyword}%")
        ))

    total = q.count()
    rows = q.order_by(CustomerAssignment.assigned_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    items = []
    for c, a, u in rows:
        item = customer_to_dict(c, user)
        item["advisor_name"] = u.real_name
        items.append(item)

    return {"total": total, "items": items}


@app.post("/api/team/assign")
def team_assign(customer_id: int = Form(...), to_user_id: int = Form(...),
                user: User = Depends(require_manager), db: Session = Depends(get_db)):
    """主管分配客户给顾问"""
    to_user = db.query(User).filter(User.id == to_user_id, User.dept_id == user.dept_id).first()
    if not to_user:
        raise HTTPException(400, "目标顾问不存在")

    # 失效旧分配
    db.query(CustomerAssignment).filter(
        CustomerAssignment.customer_id == customer_id, CustomerAssignment.status == 1,
        CustomerAssignment.pool_type.in_([1, 2])
    ).update({"status": 0})

    # 新分配
    assign = CustomerAssignment(customer_id=customer_id, advisor_id=to_user_id, pool_type=2, assigned_by=user.id)
    db.add(assign)
    db.commit()
    return {"msg": "分配成功"}


# ===================== 设置接口 =====================

@app.get("/api/settings")
def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "accept_new_data": user.accept_new_data,
        "hidden_columns": user.hidden_columns or []
    }


@app.put("/api/settings")
def update_settings(
    accept_new_data: int = Form(None), hidden_columns: str = Form(""),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if accept_new_data is not None:
        user.accept_new_data = accept_new_data
    if hidden_columns:
        user.hidden_columns = json.loads(hidden_columns)
    db.commit()
    return {"msg": "保存成功"}


# ===================== 绩效统计接口 =====================

@app.get("/api/stats/performance")
def get_performance(month: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取绩效目标"""
    if not month:
        from datetime import date
        month = date.today().strftime("%Y-%m")

    # 获取当前用户目标
    targets = db.query(PerformanceTarget).filter(
        PerformanceTarget.user_id == user.id
    ).all()

    from calendar import monthrange
    y, m = int(month[:4]), int(month[5:7])
    _, last_day = monthrange(y, m)
    start = f"{y}-{m:02d}-01"
    end = f"{y}-{m:02d}-{last_day}"

    my_ids = [a.customer_id for a in db.query(CustomerAssignment).filter(
        CustomerAssignment.advisor_id == user.id, CustomerAssignment.status == 1
    ).all()]
    if not my_ids:
        my_ids = [0]

    new_count = db.query(func.count()).select_from(Customer).filter(
        Customer.id.in_(my_ids),
        Customer.created_at >= start, Customer.created_at <= end + " 23:59:59"
    ).scalar() or 0

    remark_count = db.query(func.count()).select_from(CustomerRemark).filter(
        CustomerRemark.advisor_id == user.id,
        CustomerRemark.created_at >= start, CustomerRemark.created_at <= end + " 23:59:59"
    ).scalar() or 0

    case_count = db.query(func.count()).select_from(LoanCase).filter(
        LoanCase.advisor_id == user.id,
        LoanCase.submit_at >= start, LoanCase.submit_at <= end + " 23:59:59"
    ).scalar() or 0

    result = []
    for t in targets:
        completed = 0
        if t.target_type == "新增客户":
            completed = new_count
        elif t.target_type == "跟进次数":
            completed = remark_count
        elif t.target_type == "进件数":
            completed = case_count
        result.append({
            "id": t.id,
            "target_type": t.target_type,
            "target_value": t.target_value,
            "completed": completed,
            "start_date": t.start_date.isoformat() if t.start_date else None,
            "end_date": t.end_date.isoformat() if t.end_date else None
        })

    # 如果没有目标，返回默认目标
    if not result:
        result = [
            {"id": 1, "target_type": "进件数", "target_value": 20, "completed": case_count, "start_date": start, "end_date": end},
            {"id": 2, "target_type": "新增客户", "target_value": 50, "completed": new_count, "start_date": start, "end_date": end},
            {"id": 3, "target_type": "跟进次数", "target_value": 100, "completed": remark_count, "start_date": start, "end_date": end},
        ]

    return {"targets": result}


@app.get("/api/stats/remarks")
def get_remarks_log(
    page: int = Query(1), page_size: int = Query(20),
    advisor_id: int = Query(None), start_date: str = Query(""), end_date: str = Query(""),
    remark_type: int = Query(None),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取跟进日志（带顾问信息）"""
    q = db.query(CustomerRemark, Customer, User).join(
        Customer, Customer.id == CustomerRemark.customer_id
    ).join(
        User, User.id == CustomerRemark.advisor_id
    )

    # 非管理员只看自己部门的
    if user.role >= 5:
        q = q.filter(CustomerRemark.advisor_id == user.id)
    elif user.role <= 4:
        team_ids = [u.id for u in db.query(User).filter(User.dept_id == user.dept_id).all()]
        if team_ids:
            q = q.filter(CustomerRemark.advisor_id.in_(team_ids))

    if advisor_id:
        q = q.filter(CustomerRemark.advisor_id == advisor_id)
    if remark_type is not None:
        q = q.filter(CustomerRemark.remark_type == remark_type)
    if start_date:
        q = q.filter(CustomerRemark.created_at >= start_date)
    if end_date:
        q = q.filter(CustomerRemark.created_at <= end_date + " 23:59:59")

    total = q.count()
    items = q.order_by(CustomerRemark.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "items": [{
            "id": r[0].id,
            "content": r[0].content,
            "remark_type": r[0].remark_type,
            "status_at_remark": r[0].status_at_remark,
            "created_at": r[0].created_at.isoformat() if r[0].created_at else "",
            "advisor_name": r[2].real_name,
            "customer_id": r[1].id,
            "customer_name": r[1].name or "未知",
            "customer_phone": mask_phone(r[1].phone)
        } for r in items]
    }


# ===================== Excel 导入接口 =====================

@app.post("/api/customers/import-file")
async def import_file(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Excel批量导入客户数据"""
    import openpyxl
    from io import BytesIO

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "仅支持 xlsx/xls 格式")

    content = await file.read()
    try:
        wb = openpyxl.load_workbook(BytesIO(content))
    except Exception:
        raise HTTPException(400, "文件格式错误，无法读取")

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        raise HTTPException(400, "Excel文件数据为空")

    headers = [str(h).strip() if h else '' for h in rows[0]]
    data_rows = rows[1:]

    # 列索引映射
    def col(name):
        for i, h in enumerate(headers):
            if name in h:
                return i
        return -1

    phone_i = col('手机')
    name_i = col('姓名')
    gender_i = col('性别')
    city_i = col('城市')
    age_i = col('年龄')
    amount_i = col('额度')
    loan_type_i = col('贷款类型')
    source_i = col('来源')

    GENDER_MAP_R = {'男': 1, '女': 2, '未知': 0}
    LOAN_TYPE_MAP_R = {'信用贷': 1, '车抵贷': 2, '房抵贷': 3, '保单贷': 4, '学历贷': 5, '抵押贷': 6, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6}

    count = 0
    errors = []
    for i, row in enumerate(data_rows, 2):
        try:
            phone = str(row[phone_i]).strip() if phone_i >= 0 else ''
            if not phone or phone in ('None', ''):
                continue
            phone = ''.join(c for c in phone if c.isdigit())
            if len(phone) < 11:
                continue

            ph = hash_phone(phone)
            existing = db.query(Customer).filter(Customer.phone_hash == ph).first()
            if existing:
                continue

            gender = GENDER_MAP_R.get(str(row[gender_i]).strip() if gender_i >= 0 else '', 0)
            loan_type = LOAN_TYPE_MAP_R.get(str(row[loan_type_i]).strip() if loan_type_i >= 0 else '1', 1)

            try:
                amount = float(row[amount_i]) if amount_i >= 0 and row[amount_i] else 0
            except:
                amount = 0

            try:
                age = int(row[age_i]) if age_i >= 0 and row[age_i] else 0
            except:
                age = 0

            c = Customer(
                phone=phone, phone_hash=ph,
                name=str(row[name_i]).strip() if name_i >= 0 else '',
                gender=gender,
                city=str(row[city_i]).strip() if city_i >= 0 else '',
                age=age,
                loan_type=loan_type,
                apply_amount=amount,
                source=str(row[source_i]).strip() if source_i >= 0 else 'BXMJ-excel'
            )
            db.add(c)
            db.flush()

            assign = CustomerAssignment(customer_id=c.id, advisor_id=user.id, pool_type=1)
            db.add(assign)
            count += 1
        except Exception as e:
            errors.append(f"行{i}: {str(e)}")

    db.commit()
    return {"count": count, "errors": errors[:10]}


# ===================== 系统信息 =====================

@app.get("/api/system/info")
def system_info():
    return {
        "name": "融鑫CRM",
        "version": "1.0.0",
        "description": "贷款行业客户管理系统"
    }


# ===================== 离职人员管理 =====================

@app.get("/api/team/offboard")
def get_offboard_users(user: User = Depends(require_manager), db: Session = Depends(get_db)):
    """获取离职（禁用）员工及其客户数量"""
    offboard = db.query(User).filter(User.status == 0, User.dept_id == user.dept_id).all()
    result = []
    for u in offboard:
        count = db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == u.id,
            CustomerAssignment.pool_type.in_([1, 2]),
            CustomerAssignment.status == 1
        ).count()
        d = u.to_dict()
        d["customer_count"] = count
        result.append(d)
    return result


@app.post("/api/team/reassign-all")
def reassign_all_customers(
    from_user_id: int = Form(...), to_user_id: int = Form(...),
    user: User = Depends(require_manager), db: Session = Depends(get_db)
):
    """将某员工所有客户批量转移给另一员工"""
    to_user = db.query(User).filter(User.id == to_user_id, User.dept_id == user.dept_id).first()
    if not to_user:
        raise HTTPException(400, "目标顾问不存在")

    # 获取来源用户的所有有效分配
    assignments = db.query(CustomerAssignment).filter(
        CustomerAssignment.advisor_id == from_user_id,
        CustomerAssignment.pool_type.in_([1, 2]),
        CustomerAssignment.status == 1
    ).all()

    count = 0
    for a in assignments:
        # 失效旧分配
        a.status = 0
        # 新建分配给目标顾问
        new_assign = CustomerAssignment(
            customer_id=a.customer_id, advisor_id=to_user_id,
            pool_type=2, assigned_by=user.id, status=1
        )
        db.add(new_assign)
        count += 1

    db.commit()
    return {"msg": f"已转移 {count} 名客户", "count": count}


@app.put("/api/users/{uid}/status")
def set_user_status(uid: int, status: int = Form(...), user: User = Depends(require_manager), db: Session = Depends(get_db)):
    """启用/禁用员工（离职处理）"""
    u = db.query(User).filter(User.id == uid, User.dept_id == user.dept_id).first()
    if not u:
        raise HTTPException(404, "用户不存在")
    if uid == user.id:
        raise HTTPException(400, "不能禁用自己")
    u.status = status
    db.commit()
    return {"msg": "操作成功", "status": u.status}


# ===================== 团队统计（日志页用）=====================

@app.get("/api/stats/team-daily")
def get_team_daily(
    target_date: str = Query(""),
    user: User = Depends(require_manager), db: Session = Depends(get_db)
):
    """团队当日/某日跟进统计"""
    if not target_date:
        target_date = date.today().isoformat()

    team_ids = [u.id for u in db.query(User).filter(User.dept_id == user.dept_id, User.status == 1).all()]
    if not team_ids:
        team_ids = [user.id]

    # 按顾问统计当日备注数
    rows = db.query(User, func.count(CustomerRemark.id)).join(
        CustomerRemark, CustomerRemark.advisor_id == User.id, isouter=True
    ).filter(
        User.id.in_(team_ids),
        func.date(CustomerRemark.created_at) == target_date
    ).group_by(User.id).all()

    total_remarks = sum(cnt for _, cnt in rows)

    return {
        "date": target_date,
        "total_remarks": total_remarks,
        "advisors": [{
            "advisor_name": u.real_name,
            "advisor_id": u.id,
            "remark_count": cnt
        } for u, cnt in rows]
    }


# ===================== 客户来源分布 =====================

@app.get("/api/stats/source-dist")
def get_source_dist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """客户来源分布"""
    if user.role >= 5:
        # 顾问只看自己的
        my_cids = [a.customer_id for a in db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == user.id, CustomerAssignment.status == 1,
            CustomerAssignment.pool_type.in_([1, 2, 4])
        ).all()]
        q = db.query(Customer.source, func.count()).filter(Customer.id.in_(my_cids or [0]))
    else:
        # 主管看团队
        team_ids = [u.id for u in db.query(User).filter(User.dept_id == user.dept_id).all()]
        cids = [a.customer_id for a in db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id.in_(team_ids), CustomerAssignment.status == 1
        ).all()]
        q = db.query(Customer.source, func.count()).filter(Customer.id.in_(cids or [0]))

    dist = q.group_by(Customer.source).all()
    return [{"name": src or "未知", "value": cnt} for src, cnt in dist]


@app.get("/api/stats/status-dist")
def get_status_dist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """客户状态分布"""
    if user.role >= 5:
        my_cids = [a.customer_id for a in db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == user.id, CustomerAssignment.status == 1,
            CustomerAssignment.pool_type.in_([1, 2, 4])
        ).all()]
        q = db.query(Customer.status, func.count()).filter(Customer.id.in_(my_cids or [0]))
    else:
        team_ids = [u.id for u in db.query(User).filter(User.dept_id == user.dept_id).all()]
        cids = [a.customer_id for a in db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id.in_(team_ids), CustomerAssignment.status == 1
        ).all()]
        q = db.query(Customer.status, func.count()).filter(Customer.id.in_(cids or [0]))

    dist = q.group_by(Customer.status).all()
    return [{"name": STATUS_MAP.get(s, "未知"), "value": cnt, "status": s} for s, cnt in dist]


# ===================== 标签API =====================

@app.get("/api/tags")
def get_tags(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取所有标签（按维度分组）"""
    tags = db.query(CustomerTag).order_by(CustomerTag.sort_order).all()
    # 按维度分组
    grouped = {}
    for t in tags:
        if t.category not in grouped:
            grouped[t.category] = {"category": t.category, "tags": []}
        grouped[t.category]["tags"].append(t.to_dict())
    return list(grouped.values())


@app.get("/api/tags/categories")
def get_tag_categories():
    """获取标签维度定义（不含具体标签）"""
    return [{"key": k, "label": v["label"], "icon": v["icon"]} for k, v in TAG_CATEGORIES.items()]


@app.get("/api/customers/{cid}/tag")
def get_customer_tag(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取客户的标签"""
    assignment = db.query(CustomerTagAssignment).filter(
        CustomerTagAssignment.customer_id == cid
    ).first()
    if assignment:
        return assignment.to_dict()
    return None


@app.post("/api/customers/{cid}/tag")
def set_customer_tag(
    cid: int,
    tag_id: int = Form(...),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """为客户设置标签（替换式：同一维度只能有一个标签）"""
    # 删除该客户已有标签
    db.query(CustomerTagAssignment).filter(
        CustomerTagAssignment.customer_id == cid
    ).delete()

    tag = db.query(CustomerTag).filter(CustomerTag.id == tag_id).first()
    if not tag:
        raise HTTPException(404, "标签不存在")

    # 同一维度只能有一个标签（删除同维度旧标签）
    db.query(CustomerTagAssignment).filter(
        CustomerTagAssignment.customer_id == cid,
        CustomerTagAssignment.tag_id.in_(
            db.query(CustomerTag.id).filter(CustomerTag.category == tag.category)
        )
    ).delete(synchronize_session=False)

    assignment = CustomerTagAssignment(
        customer_id=cid, tag_id=tag_id, assigned_by=user.id
    )
    db.add(assignment)
    db.commit()
    return assignment.to_dict()


@app.delete("/api/customers/{cid}/tag")
def remove_customer_tag(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """删除客户标签"""
    db.query(CustomerTagAssignment).filter(
        CustomerTagAssignment.customer_id == cid
    ).delete()
    db.commit()
    return {"ok": True}


# ===================== 日志导出 =====================

@app.get("/api/stats/remarks/export")
def export_remarks(
    advisor_id: int = Query(None), start_date: str = Query(""), end_date: str = Query(""),
    user: User = Depends(require_manager), db: Session = Depends(get_db)
):
    """导出跟进记录为 CSV"""
    from fastapi.responses import StreamingResponse
    import csv, io

    q = db.query(CustomerRemark, Customer, User).join(
        Customer, Customer.id == CustomerRemark.customer_id
    ).join(User, User.id == CustomerRemark.advisor_id)

    if advisor_id:
        q = q.filter(CustomerRemark.advisor_id == advisor_id)
    if start_date:
        q = q.filter(CustomerRemark.created_at >= start_date)
    if end_date:
        q = q.filter(CustomerRemark.created_at <= end_date + " 23:59:59")

    rows = q.order_by(CustomerRemark.created_at.desc()).limit(10000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["时间", "顾问", "客户姓名", "客户手机", "状态", "备注内容"])
    for r, c, u in rows:
        writer.writerow([
            r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            u.real_name, c.name or "", mask_phone(c.phone),
            STATUS_MAP.get(r.status_at_remark, ""),
            r.content
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue().encode("utf-8-sig")]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=remarks_export.csv"}
    )



# ===================== 公告管理 =====================

@app.get("/api/notices")
def get_notices(notice_type: int = Query(0), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Notice).filter(Notice.is_visible == 1)
    if notice_type > 0:
        q = q.filter(Notice.notice_type == notice_type)
    notices = q.order_by(Notice.created_at.desc()).limit(50).all()
    return [n.to_dict() for n in notices]


@app.post("/api/notices")
def create_notice(body: dict, user: User = Depends(require_manager), db: Session = Depends(get_db)):
    n = Notice(
        title=body.get("title", ""),
        content=body.get("content", ""),
        notice_type=body.get("notice_type", 1),
        is_visible=body.get("is_visible", 1),
        created_by=user.id
    )
    db.add(n)
    db.commit()
    return n.to_dict()


@app.put("/api/notices/{nid}")
def update_notice(nid: int, body: dict, user: User = Depends(require_manager), db: Session = Depends(get_db)):
    n = db.query(Notice).filter(Notice.id == nid).first()
    if not n:
        raise HTTPException(404, "公告不存在")
    if "title" in body:
        n.title = body["title"]
    if "content" in body:
        n.content = body["content"]
    if "is_visible" in body:
        n.is_visible = body["is_visible"]
    db.commit()
    return n.to_dict()


@app.delete("/api/notices/{nid}")
def delete_notice(nid: int, user: User = Depends(require_manager), db: Session = Depends(get_db)):
    n = db.query(Notice).filter(Notice.id == nid).first()
    if not n:
        raise HTTPException(404, "公告不存在")
    db.delete(n)
    db.commit()
    return {"ok": True}


# ===================== 业绩排行榜 =====================

@app.get("/api/stats/ranking")
def get_ranking(
    period: str = Query("month"),  # month/week/today
    dept_id: int = Query(0),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """业绩排行榜：按备注数/进件数/放款额排行"""
    now = datetime.now()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # month
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 查询各顾问备注数
    remark_counts = db.query(
        CustomerRemark.advisor_id,
        func.count(CustomerRemark.id).label("remark_count")
    ).filter(
        CustomerRemark.created_at >= start,
        CustomerRemark.remark_type == 0
    ).group_by(CustomerRemark.advisor_id).all()

    # 查询各顾问进件数
    loan_counts = db.query(
        LoanCase.advisor_id,
        func.count(LoanCase.id).label("loan_count"),
        func.sum(LoanCase.approve_amount).label("approve_total")
    ).filter(LoanCase.created_at >= start).group_by(LoanCase.advisor_id).all()

    # 查询各顾问新客户数
    new_customer_counts = db.query(
        CustomerAssignment.advisor_id,
        func.count(CustomerAssignment.id).label("new_count")
    ).filter(CustomerAssignment.assigned_at >= start).group_by(CustomerAssignment.advisor_id).all()

    # 合并数据
    remark_map = {r.advisor_id: r.remark_count for r in remark_counts}
    loan_map = {l.advisor_id: l.loan_count for l in loan_counts}
    approve_map = {l.advisor_id: float(l.approve_total or 0) for l in loan_counts}
    new_map = {n.advisor_id: n.new_count for n in new_customer_counts}

    # 获取所有相关顾问
    advisor_ids = set(list(remark_map.keys()) + list(loan_map.keys()) + list(new_map.keys()))

    # 只返回同部门顾问（管理员看全部）
    if user.role <= 4 and user.dept_id:
        advisors = db.query(User).filter(User.dept_id == user.dept_id, User.status == 1).all()
    else:
        advisors = db.query(User).filter(User.status == 1).all()

    result = []
    for a in advisors:
        result.append({
            "advisor_id": a.id,
            "real_name": a.real_name,
            "role_text": ROLE_TEXT.get(a.role, "顾问"),
            "remark_count": remark_map.get(a.id, 0),
            "loan_count": loan_map.get(a.id, 0),
            "approve_amount": approve_map.get(a.id, 0),
            "new_count": new_map.get(a.id, 0),
        })

    # 按备注数排序
    result.sort(key=lambda x: x["remark_count"], reverse=True)
    # 添加排名
    for i, r in enumerate(result):
        r["rank"] = i + 1

    return {"period": period, "start": start.strftime("%Y-%m-%d"), "list": result}


# ===================== 工作简报增强 =====================

@app.get("/api/dashboard/brief")
def get_dashboard_brief(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """工作简报：今日/昨日统计、进件统计、主管点评情况"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def get_stats_for_period(start, end):
        # 新申请（本人新增客户数）
        new_clients = db.query(func.count(CustomerAssignment.id)).filter(
            CustomerAssignment.advisor_id == user.id,
            CustomerAssignment.assigned_at >= start,
            CustomerAssignment.assigned_at < end
        ).scalar() or 0

        # 未处理（待跟进状态）
        unhandled = db.query(func.count(Customer.id)).join(
            CustomerAssignment,
            and_(CustomerAssignment.customer_id == Customer.id,
                 CustomerAssignment.advisor_id == user.id,
                 CustomerAssignment.pool_type.in_([1, 2, 4]))
        ).filter(Customer.status == 0).scalar() or 0

        # 跟进数（今日备注数）
        remarks = db.query(func.count(CustomerRemark.id)).filter(
            CustomerRemark.advisor_id == user.id,
            CustomerRemark.remark_type == 0,
            CustomerRemark.created_at >= start,
            CustomerRemark.created_at < end
        ).scalar() or 0

        # 进件数
        loan_in = db.query(func.count(LoanCase.id)).filter(
            LoanCase.advisor_id == user.id,
            LoanCase.created_at >= start,
            LoanCase.created_at < end
        ).scalar() or 0

        # 批款数、批款金额
        approved = db.query(
            func.count(LoanCase.id),
            func.sum(LoanCase.approve_amount)
        ).filter(
            LoanCase.advisor_id == user.id,
            LoanCase.stage == 2,
            LoanCase.approve_at >= start,
            LoanCase.approve_at < end
        ).first()

        # 创收（收款金额 * 手续费率）
        collected = db.query(func.sum(LoanCase.collection_amount)).filter(
            LoanCase.advisor_id == user.id,
            LoanCase.stage == 3,
            LoanCase.collection_at >= start,
            LoanCase.collection_at < end
        ).scalar() or 0

        return {
            "new_clients": new_clients,
            "unhandled": unhandled,
            "remarks": remarks,
            "loan_in": loan_in,
            "loan_approved": approved[0] or 0,
            "approve_amount": float(approved[1] or 0),
            "collection": float(collected or 0),
        }

    today_stats = get_stats_for_period(today_start, now)
    yesterday_stats = get_stats_for_period(yesterday_start, today_start)
    month_stats = get_stats_for_period(month_start, now)

    # 主管点评情况
    review_total = db.query(func.count(CustomerRemark.id)).filter(
        CustomerRemark.advisor_id == user.id,
        CustomerRemark.remark_type == 1,
        CustomerRemark.created_at >= month_start
    ).scalar() or 0

    # 未回复的点评（remark_type=1，顾问还没有在该客户后续写新备注的）
    review_unreplied = review_total  # 简化处理

    # 当月绩效目标
    perf = db.query(PerformanceTarget).filter(
        PerformanceTarget.user_id == user.id,
        PerformanceTarget.start_date <= now,
        PerformanceTarget.end_date >= now
    ).first()

    return {
        "today": today_stats,
        "yesterday": yesterday_stats,
        "month": month_stats,
        "review": {"total": review_total, "unreplied": review_unreplied},
        "performance": perf.to_dict() if perf else None,
    }


# ===================== 团队工作简报（主管视角） =====================

@app.get("/api/dashboard/team-brief")
def get_team_brief(user: User = Depends(require_manager), db: Session = Depends(get_db)):
    """团队工作简报：每位顾问的当日统计"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 获取团队成员
    team = db.query(User).filter(User.dept_id == user.dept_id, User.status == 1).all()

    result = []
    for member in team:
        # 今日备注数
        remarks = db.query(func.count(CustomerRemark.id)).filter(
            CustomerRemark.advisor_id == member.id,
            CustomerRemark.remark_type == 0,
            CustomerRemark.created_at >= today_start
        ).scalar() or 0

        # 今日进件数
        loans = db.query(func.count(LoanCase.id)).filter(
            LoanCase.advisor_id == member.id,
            LoanCase.created_at >= today_start
        ).scalar() or 0

        # 客户总数
        customer_count = db.query(func.count(CustomerAssignment.id)).filter(
            CustomerAssignment.advisor_id == member.id,
            CustomerAssignment.pool_type.in_([1, 2, 4])
        ).scalar() or 0

        result.append({
            "id": member.id,
            "real_name": member.real_name,
            "role_text": ROLE_TEXT.get(member.role, "顾问"),
            "today_remarks": remarks,
            "today_loans": loans,
            "customer_count": customer_count,
        })

    result.sort(key=lambda x: x["today_remarks"], reverse=True)
    return result


# ===================== 系统设置增强 =====================

@app.get("/api/settings/system")
def get_system_settings(user: User = Depends(require_manager), db: Session = Depends(get_db)):
    """获取系统级设置"""
    # 从db查询，若没有则返回默认值
    settings = {
        "night_login_allowed": 1,  # 晚上10:30后能否登录
        "accept_new_data_default": 1,  # 默认接受新数据
        "sources": ["BXMJ-excel", "T+1-excel", "有钱花", "分期乐", "豆豆钱",
                    "钱袋子", "桔多多", "宜融推单", "优乐推", "千橙广告", "其他"],
    }
    return settings


@app.put("/api/settings/system")
def update_system_settings(body: dict, user: User = Depends(require_manager), db: Session = Depends(get_db)):
    """更新系统级设置（简化：直接返回OK）"""
    return {"ok": True, "msg": "系统设置已更新"}


# ===================== 数据导入/导出 =====================

@app.get("/api/customers/export")
def export_customers(
    pool_type: int = Query(1),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """导出客户列表为CSV"""
    from fastapi.responses import StreamingResponse
    import csv, io

    q = db.query(Customer).join(
        CustomerAssignment,
        and_(CustomerAssignment.customer_id == Customer.id,
             CustomerAssignment.advisor_id == user.id,
             CustomerAssignment.pool_type == pool_type)
    )

    customers = q.limit(10000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "姓名", "手机", "性别", "状态", "星级", "城市", "来源", "贷款类型", "申请额度", "最后备注时间", "进系统时间"])
    for c in customers:
        writer.writerow([
            c.id, c.name or "", mask_phone(c.phone),
            GENDER_MAP.get(c.gender, ""),
            STATUS_MAP.get(c.status, ""),
            c.star_level, c.city or "", c.source or "",
            LOAN_TYPE_MAP.get(c.loan_type, ""),
            float(c.apply_amount or 0),
            c.last_remark_at.strftime("%Y-%m-%d") if c.last_remark_at else "",
            c.created_at.strftime("%Y-%m-%d") if c.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue().encode("utf-8-sig")]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers_export.csv"}
    )


# ===================== 批量操作 API =====================

class BatchStatusUpd(BaseModel):
    customer_ids: List[int]
    status: int

class BatchToPoolUpd(BaseModel):
    customer_ids: List[int]

class BatchAssignUpd(BaseModel):
    customer_ids: List[int]
    advisor_id: int
    pool_type: int = 1  # 1我的客户 2再分配 3公共池

@app.post("/api/customers/batch-status")
def batch_update_status(
    body: BatchStatusUpd,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """批量修改客户状态"""
    count = 0
    for cid in body.customer_ids:
        c = db.query(Customer).filter(Customer.id == cid).first()
        if not c:
            continue
        # 权限检查：必须是该顾问的客户（或主管）
        if user.role < 2:
            asn = db.query(CustomerAssignment).filter(
                CustomerAssignment.customer_id == cid,
                CustomerAssignment.advisor_id == user.id,
                CustomerAssignment.status == 1
            ).first()
            if not asn:
                continue
        c.status = body.status
        count += 1
    db.commit()
    return {"success": True, "updated": count}


@app.post("/api/customers/batch-to-pool")
def batch_to_pool(
    body: BatchToPoolUpd,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """批量移入公共池"""
    count = 0
    for cid in body.customer_ids:
        # 失效当前分配
        asns = db.query(CustomerAssignment).filter(
            CustomerAssignment.customer_id == cid,
            CustomerAssignment.advisor_id == user.id,
            CustomerAssignment.status == 1
        ).all()
        for a in asns:
            a.status = 0
        # 新建公共池分配（pool_type=3）
        # 先检查是否已在公共池
        exists = db.query(CustomerAssignment).filter(
            CustomerAssignment.customer_id == cid,
            CustomerAssignment.pool_type == 3,
            CustomerAssignment.status == 1
        ).first()
        if not exists:
            new_asn = CustomerAssignment(
                customer_id=cid, advisor_id=user.id,
                pool_type=3, assigned_by=user.id, status=1
            )
            db.add(new_asn)
        count += 1
    db.commit()
    return {"success": True, "moved": count}


@app.post("/api/customers/batch-assign")
def batch_assign(
    body: BatchAssignUpd,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """批量分配客户给某顾问（主管操作）"""
    if user.role < 2:
        raise HTTPException(403, "无权限")
    target = db.query(User).filter(User.id == body.advisor_id).first()
    if not target:
        raise HTTPException(404, "顾问不存在")
    count = 0
    for cid in body.customer_ids:
        # 失效旧分配
        db.query(CustomerAssignment).filter(
            CustomerAssignment.customer_id == cid,
            CustomerAssignment.status == 1
        ).update({"status": 0})
        new_asn = CustomerAssignment(
            customer_id=cid, advisor_id=body.advisor_id,
            pool_type=body.pool_type, assigned_by=user.id, status=1
        )
        db.add(new_asn)
        count += 1
    db.commit()
    return {"success": True, "assigned": count}


# ===================== 通话记录 API =====================

CALL_RESULT_MAP = {0: "未接", 1: "接通", 2: "占线", 3: "关机", 4: "空号", 5: "拒接"}
CALL_TYPE_MAP = {1: "呼出", 2: "呼入"}

class CallRecordCreate(BaseModel):
    customer_id: int
    call_type: int = 1
    call_result: int = 0
    duration: int = 0
    call_at: Optional[str] = None
    note: str = ""

@app.get("/api/call-records")
def get_call_records(
    customer_id: Optional[int] = None,
    advisor_id: Optional[int] = None,
    call_result: Optional[int] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1, page_size: int = 20,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """查询通话记录"""
    q = db.query(CallRecord, Customer, User.real_name.label("advisor_name")).join(
        Customer, Customer.id == CallRecord.customer_id
    ).join(User, User.id == CallRecord.advisor_id)

    # 权限：顾问只能看自己的
    if user.role < 2:
        q = q.filter(CallRecord.advisor_id == user.id)
    elif advisor_id:
        q = q.filter(CallRecord.advisor_id == advisor_id)

    if customer_id:
        q = q.filter(CallRecord.customer_id == customer_id)
    if call_result is not None and call_result >= 0:
        q = q.filter(CallRecord.call_result == call_result)
    if keyword:
        q = q.filter(or_(
            Customer.name.like(f"%{keyword}%"),
            Customer.phone.like(f"%{keyword}%")
        ))
    if start_date:
        q = q.filter(CallRecord.call_at >= start_date)
    if end_date:
        q = q.filter(CallRecord.call_at < end_date + " 23:59:59")

    total = q.count()
    rows = q.order_by(CallRecord.call_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    items = []
    for cr, c, advisor_name in rows:
        d = cr.to_dict()
        d["customer_name"] = c.name or ""
        d["customer_phone"] = mask_phone(c.phone) if c.phone else ""
        d["advisor_name"] = advisor_name or ""
        d["call_result_text"] = CALL_RESULT_MAP.get(cr.call_result, "")
        d["call_type_text"] = CALL_TYPE_MAP.get(cr.call_type, "")
        items.append(d)

    return {"total": total, "items": items}


@app.post("/api/call-records")
def create_call_record(
    body: CallRecordCreate,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """新增通话记录"""
    call_at = datetime.now()
    if body.call_at:
        try:
            call_at = datetime.fromisoformat(body.call_at)
        except:
            pass
    rec = CallRecord(
        customer_id=body.customer_id, advisor_id=user.id,
        call_type=body.call_type, call_result=body.call_result,
        duration=body.duration, call_at=call_at, note=body.note
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec.to_dict()


@app.get("/api/call-records/stats")
def get_call_stats(
    period: str = "today",  # today/week/month
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """通话统计数据"""
    now = datetime.now()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # month
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    q = db.query(CallRecord)
    if user.role < 2:
        q = q.filter(CallRecord.advisor_id == user.id)
    q = q.filter(CallRecord.call_at >= start)

    records = q.all()
    total = len(records)
    connected = sum(1 for r in records if r.call_result == 1)
    total_duration = sum(r.duration or 0 for r in records)

    result_dist = {}
    for k, v in CALL_RESULT_MAP.items():
        result_dist[v] = sum(1 for r in records if r.call_result == k)

    return {
        "total": total,
        "connected": connected,
        "connect_rate": round(connected / total * 100, 1) if total else 0,
        "total_duration": total_duration,
        "avg_duration": round(total_duration / connected, 0) if connected else 0,
        "result_dist": result_dist
    }


@app.delete("/api/call-records/{rid}")
def delete_call_record(
    rid: int,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    rec = db.query(CallRecord).filter(CallRecord.id == rid).first()
    if not rec:
        raise HTTPException(404, "记录不存在")
    if rec.advisor_id != user.id and user.role < 2:
        raise HTTPException(403, "无权限")
    db.delete(rec)
    db.commit()
    return {"success": True}


# ===================== 月度趋势 API（创收分析增强）=====================

@app.get("/api/stats/monthly-trend")
def get_monthly_trend(
    months: int = 6,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """最近N个月进件/批款/收款趋势"""
    now = datetime.now()
    result = []
    for i in range(months - 1, -1, -1):
        d = now - timedelta(days=30 * i)
        month_start = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if d.month == 12:
            month_end = month_start.replace(year=d.year + 1, month=1)
        else:
            month_end = month_start.replace(month=d.month + 1)

        q = db.query(LoanCase)
        if user.role < 2:
            q = q.filter(LoanCase.advisor_id == user.id)

        cases_in_month = q.filter(
            LoanCase.created_at >= month_start,
            LoanCase.created_at < month_end
        ).all()

        case_count = len(cases_in_month)
        approve_count = sum(1 for c in cases_in_month if c.stage >= 2)
        collection_count = sum(1 for c in cases_in_month if c.stage >= 3)
        approve_amount = float(sum((c.approve_amount or 0) for c in cases_in_month if c.stage >= 2))

        result.append({
            "month": f"{d.year}-{str(d.month).zfill(2)}",
            "label": f"{d.month}月",
            "case_count": case_count,
            "approve_count": approve_count,
            "collection_count": collection_count,
            "approve_amount": round(approve_amount, 2)
        })
    return result


@app.get("/api/stats/bank-dist")
def get_bank_dist(
    month: Optional[str] = None,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """进件银行分布（真实数据）"""
    q = db.query(LoanCase.bank_name, func.count(LoanCase.id).label("cnt"))
    if user.role < 2:
        q = q.filter(LoanCase.advisor_id == user.id)
    if month:
        try:
            parts = month.split("-")
            year, mo = int(parts[0]), int(parts[1])
            start = datetime(year, mo, 1)
            end = datetime(year, mo + 1, 1) if mo < 12 else datetime(year + 1, 1, 1)
            q = q.filter(LoanCase.created_at >= start, LoanCase.created_at < end)
        except:
            pass
    rows = q.group_by(LoanCase.bank_name).order_by(func.count(LoanCase.id).desc()).limit(10).all()
    return [{"name": r.bank_name or "未知", "value": r.cnt} for r in rows]




# ===================== 数据统计模块 API =====================

@app.get("/api/stats/daily-stats")
def get_stats_daily(
    mode: str = Query("daily"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """数据日统计 / 按月统计"""
    fmt = "%Y-%m-%d" if mode == "daily" else "%Y-%m"
    now = datetime.now()
    if mode == "daily":
        start = now - timedelta(days=90)
        date_col = func.date(Customer.created_at)
    else:
        start = now - timedelta(days=365)
        date_col = func.strftime("%Y-%m", Customer.created_at)

    rows = db.query(
        date_col.label("date"),
        func.count(Customer.id).label("new_apply_count"),
    ).filter(Customer.created_at >= start).group_by(date_col).all()

    result = []
    for r in rows:
        date_str = r.date
        customers = db.query(Customer).filter(
            func.date(Customer.created_at) == date_str if mode == "daily" else func.strftime("%Y-%m", Customer.created_at) == date_str
        ).all()
        entry = {"date": str(date_str), "new_apply_count": r.new_apply_count,
                 "new_accepted": 0, "new_pending": 0,
                 "new_star0": 0, "new_star1": 0, "new_star2": 0,
                 "new_star3": 0, "new_star4": 0, "new_star5": 0, "new_spam": 0,
                 "reassign_count": 0, "re_accepted": 0, "re_pending": 0,
                 "re_star1": 0, "re_star2": 0, "re_star3": 0, "re_star4": 0, "re_star5": 0, "re_spam": 0}
        for c in customers:
            s = c.star_level or 0
            if 0 <= s <= 5:
                entry["new_star" + str(s)] += 1
            if c.status == 1: entry["new_accepted"] += 1
            if c.status == 3: entry["new_pending"] += 1
            if c.status == 99: entry["new_spam"] += 1
        re_assignments = db.query(CustomerAssignment).filter(
            CustomerAssignment.pool_type == 2,
            func.date(CustomerAssignment.assigned_at) == date_str if mode == "daily" else func.strftime("%Y-%m", CustomerAssignment.assigned_at) == date_str
        ).all()
        entry["reassign_count"] = len(re_assignments)
        for a in re_assignments:
            c = db.query(Customer).filter(Customer.id == a.customer_id).first()
            if c:
                s = c.star_level or 0
                if 1 <= s <= 5: entry["re_star" + str(s)] += 1
                if c.status == 1: entry["re_accepted"] += 1
                if c.status == 3: entry["re_pending"] += 1
                if c.status == 99: entry["re_spam"] += 1
        total_new = entry["new_star3"] + entry["new_star4"] + entry["new_star5"]
        denom = max(entry["new_apply_count"], 1)
        entry["new_lendable_rate"] = round(total_new / denom * 100, 1)
        entry["new_star3plus_rate"] = round(total_new / denom * 100, 1)
        result.append(entry)
    return sorted(result, key=lambda x: x["date"], reverse=True)


@app.get("/api/stats/remark-counts")
def get_stats_remark_counts(
    mode: str = Query("daily"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """备注数量日统计"""
    if mode == "daily":
        start = datetime.now() - timedelta(days=90)
        date_col = func.date(CustomerRemark.created_at)
    else:
        start = datetime.now() - timedelta(days=365)
        date_col = func.strftime("%Y-%m", CustomerRemark.created_at)

    rows = db.query(
        date_col.label("date"),
        func.count(CustomerRemark.id).label("total_remarks"),
        func.count(func.distinct(CustomerRemark.customer_id)).label("customers_with_remark")
    ).filter(CustomerRemark.created_at >= start).group_by(date_col).all()

    result = []
    for r in rows:
        total = r.total_remarks or 0
        cw = r.customers_with_remark or 0
        result.append({
            "date": str(r.date),
            "total_remarks": total,
            "customers_with_remark": cw,
            "avg_remarks": round(total / max(cw, 1), 1),
            "customers_no_remark": 0
        })
    return sorted(result, key=lambda x: x["date"], reverse=True)


@app.get("/api/stats/my-remarks")
def get_stats_my_remarks(
    page: int = Query(1), page_size: int = Query(20),
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """我的备注记录"""
    q = db.query(CustomerRemark).filter(CustomerRemark.advisor_id == user.id)
    total = q.count()
    remarks = q.order_by(CustomerRemark.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for r in remarks:
        c = db.query(Customer).filter(Customer.id == r.customer_id).first()
        items.append({
            "id": r.id,
            "customer_id": r.customer_id,
            "customer_name": c.name if c else "",
            "content": r.content,
            "star_before": r.star_before,
            "star_after": r.star_after,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else ""
        })
    return {"total": total, "items": items}


@app.get("/api/stats/upcoming-pool")
def get_stats_upcoming_pool(
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """即将抓入公共池（超过N天未备注的客户）"""
    cutoff = datetime.now() - timedelta(days=15)
    if user.role >= 2:
        customers = db.query(Customer).filter(
            or_(Customer.last_remark_at == None, Customer.last_remark_at < cutoff)
        ).all()
    else:
        cust_ids = [a.customer_id for a in db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == user.id,
            CustomerAssignment.status == 1
        ).all()]
        customers = db.query(Customer).filter(
            Customer.id.in_(cust_ids),
            or_(Customer.last_remark_at == None, Customer.last_remark_at < cutoff)
        ).all()
    result = []
    for c in customers:
        days = (datetime.now() - (c.last_remark_at or c.created_at)).days
        advisor_name = ""
        asgn = db.query(CustomerAssignment).filter(
            CustomerAssignment.customer_id == c.id, CustomerAssignment.status == 1
        ).first()
        if asgn:
            u = db.query(User).filter(User.id == asgn.advisor_id).first()
            if u: advisor_name = u.real_name
        result.append({
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "advisor_name": advisor_name,
            "last_remark_at": c.last_remark_at.strftime("%Y-%m-%d %H:%M") if c.last_remark_at else "从未备注",
            "no_remark_days": days
        })
    return {"items": result}


@app.get("/api/stats/new-customer-stats")
def get_stats_new_customer(
    user: User = Depends(get_current_user), db: Session = Depends(get_db")
):
    """顾问新数据统计（管理员视角）"""
    if user.role < 2:
        return {"items": []}
    users = db.query(User).filter(User.role == 1, User.dept_id == user.dept_id).all()
    result = []
    for u in users:
        assignments = db.query(CustomerAssignment).filter(
            CustomerAssignment.advisor_id == u.id,
            CustomerAssignment.pool_type == 1,
            CustomerAssignment.assigned_at >= datetime.now() - timedelta(days=30)
        ).all()
        new_count = len(assignments)
        contacted = 0
        star3plus = 0
        for a in assignments:
            c = db.query(Customer).filter(Customer.id == a.customer_id).first()
            if c:
                if c.last_remark_at: contacted += 1
                if (c.star_level or 0) >= 3: star3plus += 1
        result.append({
            "advisor_name": u.real_name,
            "new_count": new_count,
            "contacted_count": contacted,
            "contact_rate": round(contacted / max(new_count, 1) * 100, 1),
            "star3plus_count": star3plus,
            "high_intent_rate": round(star3plus / max(new_count, 1) * 100, 1)
        })
    return {"items": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
