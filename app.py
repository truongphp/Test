import streamlit as st
import json
import os
import io
import csv
import math
import uuid
import time
import random
import hashlib
import statistics
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional, Tuple, Union

import pandas as pd
import numpy as np

# ==============================================================================
# 1. CẤU HÌNH TRANG & HẰNG SỐ HỆ THỐNG (SYSTEM CONSTANTS & CONFIG)
# ==============================================================================

APP_TITLE = "MMO FinTech & Expense Suite Pro"
APP_VERSION = "4.5.0-Enterprise"
PRIMARY_DATA_FILE = "so_hoan_chinh.json"
CAMPAIGNS_FILE = "mmo_campaigns.json"
WALLETS_FILE = "mmo_wallets.json"
SUBSCRIPTIONS_FILE = "mmo_subscriptions.json"
TEAM_FILE = "mmo_team.json"
BUDGETS_FILE = "mmo_budgets.json"
TRASH_FILE = "mmo_trash.json"
AUDIT_LOG_FILE = "mmo_audit_logs.json"
SETTINGS_FILE = "mmo_settings.json"

DEFAULT_EXCHANGE_RATES = {
    "VND": 1.0,
    "USD": 25450.0,
    "USDT": 25680.0,
    "EUR": 27500.0,
    "GBP": 32100.0,
    "SGD": 18900.0,
}

TRANSACTION_TYPES = [
    "Chi tiêu (Expense)",
    "Thu nhập / Payout (Revenue)",
    "Hoàn tiền / Rebate (Cashback)",
    "Rút vốn / Chia lãi (Withdrawal)",
    "Nạp vốn / Đầu tư (Capital Injection)",
]

EXPENSE_CATEGORIES = [
    "Quảng cáo Facebook Ads",
    "Quảng cáo TikTok Ads",
    "Quảng cáo Google / YouTube Ads",
    "Mua VIA / BM / Tài khoản Ads",
    "Proxy / IP Dân cư / 4G",
    "Antidetect Browser (AdsPower/Multilogin/GoLogin)",
    "VPS / Cloud Server / Hosting / Domain",
    "Tool MMO / Phần mềm AI / API (OpenAI/Claude/CapCut)",
    "Fulfillment / Giá vốn hàng bán (COGS / Dropship)",
    "Phí cổng thanh toán / Gas Fee / Chênh lệch tỷ giá",
    "Lương nhân sự / Media Buyer / Editor / VA",
    "Seeding / Booking KOL / KOC",
    "Chi phí văn phòng / Thiết bị / Điện & Internet",
    "Ăn uống / Sinh hoạt cá nhân",
    "Đào tạo / Khóa học / Mastermind",
    "Chi phí vận hành khác",
]

REVENUE_CATEGORIES = [
    "Payout Affiliate (ClickBank / Offervault / CJ / Impact)",
    "Doanh thu TikTok Shop / Shopee / Lazada",
    "Doanh thu Shopify / WooCommerce / POD",
    "Doanh thu YouTube AdSense / Facebook Reels",
    "Cashback thẻ Ads / Hoàn tiền cổng thanh toán",
    "Airdrop / Retroactive / Staking / Crypto Trading",
    "Dịch vụ Agency / Cho thuê tài khoản BM / Bán nguyên liệu",
    "Bán Tool / SaaS / Khóa học",
    "Thu nhập khác",
]

ALL_CATEGORIES = EXPENSE_CATEGORIES + REVENUE_CATEGORIES

DEFAULT_PAYMENT_METHODS = [
    "Vietcombank (VND)",
    "Techcombank / Thẻ Visa Ads (VND)",
    "MB Bank / VPBank (VND)",
    "Ví MoMo / ZaloPay (VND)",
    "Binance Pay / Ví USDT (TRC20/BEP20)",
    "Payoneer (USD)",
    "PingPong Payments (USD)",
    "Wise Business (USD/EUR)",
    "PayPal Business (USD)",
    "MetaMask / Ví Web3 (USDT)",
    "Tiền mặt (Cash VND)",
]

TRANSACTION_STATUSES = [
    "Hoàn thành (Completed)",
    "Đang xử lý / Hold (Pending)",
    "Tạm giữ kiểm duyệt (Under Review)",
    "Đã hoàn tiền (Refunded)",
    "Đã huỷ (Cancelled)",
]

MMO_PLATFORMS = [
    "Facebook Ads",
    "TikTok Ads & TikTok Shop",
    "Google Ads & YouTube",
    "Affiliate Global (ClickBank / MaxBounty / Digistore24)",
    "E-Commerce Global (Shopify / Etsy / Amazon / POD)",
    "Crypto / Web3 / Airdrop / Node",
    "Content Automation / AI Channel",
    "Agency & Dịch vụ MMO",
    "Vận hành chung / Nội bộ",
]

QUICK_EXPENSE_TEMPLATES = [
    {
        "label": "🔥 Nạp ngân sách Facebook Ads ($200)",
        "ten": "Thanh toán ngưỡng thẻ Facebook Ads Campaign Scale",
        "loai": "Chi tiêu (Expense)",
        "nguyen_te": 200.0,
        "loai_tien": "USD",
        "danh_muc": "Quảng cáo Facebook Ads",
        "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
        "phi_phan_tram": 2.5,
        "thue_phan_tram": 5.0,
        "tags": "fb-ads,media-buying,scale",
        "ghi_chu": "Thanh toán hóa đơn ngưỡng $200 + thuế VAT nhà thầu nước ngoài 5%",
    },
    {
        "label": "⚡ Gia hạn गोLogin / AdsPower (1 tháng)",
        "ten": "Gia hạn gói Antidetect Browser AdsPower Team 100 Profiles",
        "loai": "Chi tiêu (Expense)",
        "nguyen_te": 50.0,
        "loai_tien": "USDT",
        "danh_muc": "Antidetect Browser (AdsPower/Multilogin/GoLogin)",
        "vi_thanh_toan": "Binance Pay / Ví USDT (TRC20/BEP20)",
        "phi_phan_tram": 0.5,
        "thue_phan_tram": 0.0,
        "tags": "antidetect,tool,monthly",
        "ghi_chu": "Gói 100 profiles + 3 thành viên vận hành",
    },
    {
        "label": "🌐 Mua gói Proxy Dân Cư Xoay (100GB)",
        "ten": "Nạp lưu lượng Proxy Dân Cư Rotating IP (BrightData / 922Proxy)",
        "loai": "Chi tiêu (Expense)",
        "nguyen_te": 85.0,
        "loai_tien": "USDT",
        "danh_muc": "Proxy / IP Dân cư / 4G",
        "vi_thanh_toan": "Binance Pay / Ví USDT (TRC20/BEP20)",
        "phi_phan_tram": 1.0,
        "thue_phan_tram": 0.0,
        "tags": "proxy,residential-ip,infra",
        "ghi_chu": "Phục vụ nuôi tài khoản và chạy chiến dịch Global US/UK",
    },
    {
        "label": "💻 Mua lô 20 VIA Cổ + 5 BM350 Kháng",
        "ten": "Nhập nguyên liệu 20 VIA XMDT + 5 BM350 Limit $250",
        "loai": "Chi tiêu (Expense)",
        "nguyen_te": 4500000.0,
        "loai_tien": "VND",
        "danh_muc": "Mua VIA / BM / Tài khoản Ads",
        "vi_thanh_toan": "Vietcombank (VND)",
        "phi_phan_tram": 0.0,
        "thue_phan_tram": 0.0,
        "tags": "via,bm,nguyen-lieu",
        "ghi_chu": "Bảo hành login 1 đổi 1 trong 48h",
    },
    {
        "label": "💰 Nhận Payout Affiliate Network ($1,500)",
        "ten": "Nhận thanh toán Payout Tuần 4 từ Affiliate Network (Wire/Payoneer)",
        "loai": "Thu nhập / Payout (Revenue)",
        "nguyen_te": 1500.0,
        "loai_tien": "USD",
        "danh_muc": "Payout Affiliate (ClickBank / Offervault / CJ / Impact)",
        "vi_thanh_toan": "Payoneer (USD)",
        "phi_phan_tram": 1.0,
        "thue_phan_tram": 0.0,
        "tags": "payout,affiliate,revenue",
        "ghi_chu": "Doanh thu tuần chiến dịch Nutra / SaaS US",
    },
    {
        "label": "💎 Nhận Cashback Thẻ Tín Dụng Ads (3%)",
        "ten": "Hoàn tiền Cashback chi tiêu Quảng cáo Thẻ Doanh Nghiệp tháng này",
        "loai": "Hoàn tiền / Rebate (Cashback)",
        "nguyen_te": 3600000.0,
        "loai_tien": "VND",
        "danh_muc": "Cashback thẻ Ads / Hoàn tiền cổng thanh toán",
        "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
        "phi_phan_tram": 0.0,
        "thue_phan_tram": 0.0,
        "tags": "cashback,rebate,credit-card",
        "ghi_chu": "Hoàn tiền tự động vào sao kê thẻ",
    },
]


# ==============================================================================
# 2. HỆ THỐNG GIAO DIỆN CYBER-FINTECH & CUSTOM HTML/CSS ENGINE
# ==============================================================================

def configure_page() -> None:
    """Thiết lập cấu hình trang Streamlit chuẩn Wide-screen Dashboard."""
    try:
        st.set_page_config(
            page_title=f"{APP_TITLE} | Quản Trị Tài Chính MMO",
            page_icon="💎",
            layout="wide",
            initial_sidebar_state="expanded",
        )
    except Exception:
        # Phòng trường hợp set_page_config đã được gọi trước đó
        pass


def inject_enterprise_css(theme_mode: str = "Dark Cyber-FinTech") -> None:
    """
    Nhúng hệ thống CSS chuyên nghiệp theo phong cách nền tảng MMO / SaaS hiện đại
    (Binance / Stripe / Linear / Bybit Dashboard).
    """
    is_dark = "Dark" in theme_mode

    bg_primary = "#0B0F19" if is_dark else "#F4F7FB"
    bg_card = "rgba(17, 24, 39, 0.86)" if is_dark else "#FFFFFF"
    bg_card_hover = "rgba(30, 41, 59, 0.95)" if is_dark else "#F8FAFC"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#475569"
    border_color = "rgba(148, 163, 184, 0.16)" if is_dark else "rgba(203, 213, 225, 0.85)"
    accent_primary = "#10B981"  # Emerald Neon
    accent_secondary = "#3B82F6"  # Cyber Blue
    accent_warning = "#F59E0B"  # Amber Gold
    accent_danger = "#EF4444"  # Crimson Red
    accent_purple = "#8B5CF6"  # Royal Violet

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Nền tổng thể & Container */
        .stApp {{
            background: {bg_primary};
            color: {text_primary};
        }}

        .block-container {{
            padding-top: 1.25rem !important;
            padding-bottom: 3rem !important;
            max-width: 1480px !important;
        }}

        /* Thanh Ticker Tỷ Giá & Trạng Thái MMO */
        .mmo-ticker-bar {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            background: linear-gradient(90deg, rgba(16,185,129,0.12) 0%, rgba(59,130,246,0.12) 50%, rgba(139,92,246,0.12) 100%);
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 10px 18px;
            margin-bottom: 18px;
            backdrop-filter: blur(12px);
        }}

        .mmo-ticker-item {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            color: {text_primary};
            font-family: 'JetBrains Mono', monospace;
        }}

        .mmo-ticker-badge {{
            background: rgba(16, 185, 129, 0.18);
            color: #10B981;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 700;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }}

        /* Hero Banner */
        .mmo-hero-header {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.90) 100%);
            border: 1px solid {border_color};
            border-left: 5px solid {accent_primary};
            border-radius: 16px;
            padding: 20px 26px;
            margin-bottom: 22px;
            box-shadow: 0 12px 32px -10px rgba(0, 0, 0, 0.35);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }}

        .mmo-hero-title {{
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #FFFFFF;
            margin: 0 0 4px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .mmo-hero-subtitle {{
            font-size: 0.88rem;
            color: #94A3B8;
            margin: 0;
        }}

        /* KPI Stat Cards */
        .mmo-kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}

        .mmo-kpi-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 14px;
            padding: 18px 20px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);
            position: relative;
            overflow: hidden;
        }}

        .mmo-kpi-card:hover {{
            background: {bg_card_hover};
            transform: translateY(-2px);
            border-color: rgba(59, 130, 246, 0.45);
        }}

        .mmo-kpi-label {{
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {text_secondary};
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .mmo-kpi-value {{
            font-size: 1.48rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: {text_primary};
            margin-bottom: 6px;
            line-height: 1.2;
        }}

        .mmo-kpi-delta {{
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 8px;
            border-radius: 999px;
        }}

        .delta-up {{
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
        }}

        .delta-down {{
            background: rgba(239, 68, 68, 0.15);
            color: #EF4444;
        }}

        .delta-neutral {{
            background: rgba(59, 130, 246, 0.15);
            color: #3B82F6;
        }}

        /* Section Title Bar */
        .mmo-section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: rgba(59, 130, 246, 0.08);
            border-left: 4px solid {accent_secondary};
            border-radius: 8px;
            margin: 18px 0 14px 0;
        }}

        .mmo-section-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {text_primary};
            margin: 0;
        }}

        .mmo-section-tag {{
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            color: {accent_secondary};
            font-weight: 600;
        }}

        /* Glass Panel & Receipt Box */
        .mmo-glass-panel {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 16px;
        }}

        .mmo-receipt-box {{
            background: linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%);
            border: 1px dashed rgba(16, 185, 129, 0.5);
            border-radius: 14px;
            padding: 20px;
            color: #F8FAFC;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Status Badges */
        .status-pill {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.73rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .pill-green {{ background: rgba(16, 185, 129, 0.18); color: #10B981; border: 1px solid rgba(16,185,129,0.35); }}
        .pill-red {{ background: rgba(239, 68, 68, 0.18); color: #EF4444; border: 1px solid rgba(239,68,68,0.35); }}
        .pill-amber {{ background: rgba(245, 158, 11, 0.18); color: #F59E0B; border: 1px solid rgba(245,158,11,0.35); }}
        .pill-blue {{ background: rgba(59, 130, 246, 0.18); color: #3B82F6; border: 1px solid rgba(59,130,246,0.35); }}
        .pill-purple {{ background: rgba(139, 92, 246, 0.18); color: #A78BFA; border: 1px solid rgba(139,92,246,0.35); }}

        /* Progress Bar Custom */
        .mmo-progress-track {{
            width: 100%;
            height: 10px;
            background: rgba(148, 163, 184, 0.2);
            border-radius: 999px;
            overflow: hidden;
            margin: 6px 0;
        }}
        .mmo-progress-fill {{
            height: 100%;
            border-radius: 999px;
            transition: width 0.35s ease;
        }}

        /* Tùy chỉnh nút bấm Streamlit */
        div.stButton > button {{
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.18s ease;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def format_vnd(amount: Union[int, float], include_symbol: bool = True) -> str:
    """Định dạng số tiền chuẩn VNĐ (ví dụ: 15,250,000đ)."""
    try:
        val = float(amount)
    except (ValueError, TypeError):
        val = 0.0
    suffix = "đ" if include_symbol else ""
    return f"{val:,.0f}{suffix}"


def format_currency(amount: Union[int, float], currency: str = "VND") -> str:
    """Định dạng số tiền theo loại ngoại tệ tương ứng."""
    try:
        val = float(amount)
    except (ValueError, TypeError):
        val = 0.0
    curr = (currency or "VND").upper()
    if curr == "VND":
        return f"{val:,.0f}đ"
    elif curr in ("USD", "SGD"):
        return f"${val:,.2f} {curr}"
    elif curr == "USDT":
        return f"{val:,.2f} USDT"
    elif curr == "EUR":
        return f"€{val:,.2f}"
    elif curr == "GBP":
        return f"£{val:,.2f}"
    return f"{val:,.2f} {curr}"


def render_section_header(title: str, tag: str = "MMO FINTECH SUITE") -> None:
    """Hiển thị thanh tiêu đề phân mục chuyên nghiệp."""
    st.markdown(
        f"""
        <div class="mmo-section-header">
            <div class="mmo-section-title">{title}</div>
            <div class="mmo-section-tag">{tag}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card_html(
    label: str,
    value: str,
    delta_text: str,
    delta_type: str = "neutral",
    icon: str = "📊",
) -> str:
    """Tạo mã HTML cho một thẻ KPI chuẩn FinTech."""
    delta_cls = {
        "up": "delta-up",
        "down": "delta-down",
        "neutral": "delta-neutral",
    }.get(delta_type, "delta-neutral")
    return f"""
    <div class="mmo-kpi-card">
        <div class="mmo-kpi-label">
            <span>{label}</span>
            <span>{icon}</span>
        </div>
        <div class="mmo-kpi-value">{value}</div>
        <div class="mmo-kpi-delta {delta_cls}">{delta_text}</div>
    </div>
    """


# ==============================================================================
# 3. LỚP LƯU TRỮ DỮ LIỆU & TƯƠNG THÍCH NGƯỢC (DATA ENGINE & PERSISTENCE LAYER)
# ==============================================================================

def _safe_read_json(filepath: str, default_factory=list) -> Any:
    """Đọc file JSON an toàn với xử lý ngoại lệ chống hỏng file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            return default_factory()
    return default_factory()


def _safe_write_json(filepath: str, data: Any) -> bool:
    """Ghi file JSON an toàn với định dạng UTF-8 chuẩn tiếng Việt."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def normalize_transaction_record(raw: Dict[str, Any], index_hint: int = 1) -> Dict[str, Any]:
    """
    Chuẩn hoá bản ghi chi tiêu từ định dạng cơ bản `{"ten": ..., "tien": ...}`
    sang cấu trúc MMO Enterprise đầy đủ mà vẫn giữ nguyên 2 trường gốc `ten` và `tien`.
    """
    if not isinstance(raw, dict):
        raw = {"ten": str(raw), "tien": 0}

    ten = str(raw.get("ten", f"Khoản giao dịch #{index_hint}")).strip()
    if not ten:
        ten = f"Khoản giao dịch #{index_hint}"

    try:
        tien_goc = float(raw.get("tien", 0))
    except (ValueError, TypeError):
        tien_goc = 0.0

    loai_tien = str(raw.get("loai_tien", "VND")).upper()
    ty_gia = float(raw.get("ty_gia", DEFAULT_EXCHANGE_RATES.get(loai_tien, 1.0)))
    if ty_gia <= 0:
        ty_gia = 1.0

    # Nếu bản ghi cũ chỉ có `tien` (VNĐ) mà chưa có `nguyen_te`
    if "nguyen_te" in raw:
        try:
            nguyen_te = float(raw.get("nguyen_te", tien_goc))
        except (ValueError, TypeError):
            nguyen_te = tien_goc
    else:
        nguyen_te = tien_goc if loai_tien == "VND" else round(tien_goc / ty_gia, 2)

    phi_phan_tram = float(raw.get("phi_phan_tram", 0.0))
    thue_phan_tram = float(raw.get("thue_phan_tram", 0.0))

    base_vnd = nguyen_te * ty_gia if loai_tien != "VND" else tien_goc
    if base_vnd == 0 and tien_goc > 0:
        base_vnd = tien_goc

    phi_vnd = float(raw.get("phi_vnd", round(base_vnd * (phi_phan_tram / 100.0), 0)))
    thue_vnd = float(raw.get("thue_vnd", round(base_vnd * (thue_phan_tram / 100.0), 0)))

    # Trường `tien` luôn lưu tổng giá trị quy đổi VNĐ để tương thích ngược 100%
    tong_vnd = float(raw.get("tien", round(base_vnd + phi_vnd + thue_vnd, 0)))
    if tong_vnd <= 0 and base_vnd > 0:
        tong_vnd = round(base_vnd + phi_vnd + thue_vnd, 0)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ngay_gio = str(raw.get("ngay_gio", now_str))
    ngay = ngay_gio[:10] if len(ngay_gio) >= 10 else datetime.now().strftime("%Y-%m-%d")

    tx_id = str(raw.get("id", "")).strip()
    if not tx_id:
        seed_str = f"{ten}-{tong_vnd}-{ngay_gio}-{index_hint}"
        tx_id = "TX-" + hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:8].upper()

    loai = str(raw.get("loai", "Chi tiêu (Expense)"))
    if loai not in TRANSACTION_TYPES:
        loai = "Chi tiêu (Expense)"

    danh_muc = str(raw.get("danh_muc", "")).strip()
    if not danh_muc:
        # Tự động suy luận danh mục thông minh từ tên khoản chi
        ten_lower = ten.lower()
        if any(k in ten_lower for k in ["fb", "facebook", "bm", "via"]):
            danh_muc = "Quảng cáo Facebook Ads"
        elif any(k in ten_lower for k in ["tiktok", "tik tok", "shop"]):
            danh_muc = "Quảng cáo TikTok Ads"
        elif any(k in ten_lower for k in ["google", "youtube", "gg"]):
            danh_muc = "Quảng cáo Google / YouTube Ads"
        elif any(k in ten_lower for k in ["proxy", "ip", "922", "brightdata", "luna"]):
            danh_muc = "Proxy / IP Dân cư / 4G"
        elif any(k in ten_lower for k in ["adspower", "gologin", "multilogin", "dolphin"]):
            danh_muc = "Antidetect Browser (AdsPower/Multilogin/GoLogin)"
        elif any(k in ten_lower for k in ["vps", "server", "domain", "hosting", "aws"]):
            danh_muc = "VPS / Cloud Server / Hosting / Domain"
        elif any(k in ten_lower for k in ["payout", "hoa hồng", "affiliate", "clickbank"]):
            danh_muc = "Payout Affiliate (ClickBank / Offervault / CJ / Impact)"
        elif any(k in ten_lower for k in ["lương", "nhân sự", "editor", "media buyer"]):
            danh_muc = "Lương nhân sự / Media Buyer / Editor / VA"
        else:
            danh_muc = "Chi phí vận hành khác" if "Chi" in loai else "Thu nhập khác"

    tags_raw = raw.get("tags", [])
    if isinstance(tags_raw, str):
        tags_list = [t.strip() for t in tags_raw.split(",") if t.strip()]
    elif isinstance(tags_raw, list):
        tags_list = [str(t).strip() for t in tags_raw if str(t).strip()]
    else:
        tags_list = []

    lich_su_sua = raw.get("lich_su_sua", [])
    if not isinstance(lich_su_sua, list):
        lich_su_sua = []

    return {
        "id": tx_id,
        "ten": ten,
        "tien": round(tong_vnd, 0),
        "loai": loai,
        "nguyen_te": round(nguyen_te, 2),
        "loai_tien": loai_tien,
        "ty_gia": round(ty_gia, 2),
        "phi_phan_tram": round(phi_phan_tram, 2),
        "thue_phan_tram": round(thue_phan_tram, 2),
        "phi_vnd": round(phi_vnd, 0),
        "thue_vnd": round(thue_vnd, 0),
        "danh_muc": danh_muc,
        "chien_dich": str(raw.get("chien_dich", "Vận hành chung / Nội bộ")),
        "nen_tang": str(raw.get("nen_tang", "Facebook Ads")),
        "vi_thanh_toan": str(raw.get("vi_thanh_toan", "Vietcombank (VND)")),
        "trang_thai": str(raw.get("trang_thai", "Hoàn thành (Completed)")),
        "ngay": ngay,
        "ngay_gio": ngay_gio,
        "nguoi_tao": str(raw.get("nguoi_tao", "Admin / MMO Owner")),
        "ma_tham_chieu": str(raw.get("ma_tham_chieu", f"REF-{tx_id[-5:]}")),
        "tags": tags_list,
        "ghi_chu": str(raw.get("ghi_chu", "")),
        "lich_su_sua": lich_su_sua,
    }


def doc_file() -> List[Dict[str, Any]]:
    """
    Hàm gốc `doc_file()` đọc dữ liệu từ `so_hoan_chinh.json` và tự động chuẩn hoá
    các trường nâng cao cho hệ thống MMO mà vẫn giữ nguyên cấu trúc list[dict].
    """
    if os.path.exists(PRIMARY_DATA_FILE):
        try:
            with open(PRIMARY_DATA_FILE, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
                if not isinstance(raw_list, list):
                    return []
                return [
                    normalize_transaction_record(item, idx + 1)
                    for idx, item in enumerate(raw_list)
                ]
        except Exception:
            return []
    else:
        return []


def luu_file(du_lieu: List[Dict[str, Any]]) -> bool:
    """
    Hàm gốc `luu_file(du_lieu)` lưu toàn bộ danh sách giao dịch vào `so_hoan_chinh.json`
    với chuẩn UTF-8 và indent=2.
    """
    normalized = [
        normalize_transaction_record(item, idx + 1)
        for idx, item in enumerate(du_lieu)
    ]
    with open(PRIMARY_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)
    return True


# ==============================================================================
# 4. QUẢN LÝ CÁC BẢNG DỮ LIỆU PHỤ TRỢ HỆ SINH THÁI MMO (EXTENDED MMO TABLES)
# ==============================================================================

def doc_cai_dat() -> Dict[str, Any]:
    """Đọc cấu hình hệ thống (Tỷ giá, Thuế mặc định, Giao diện, Thông tin Team)."""
    default_settings = {
        "ten_doanh_nghiep": "Alpha MMO Media & Affiliate Group",
        "chu_so_huu": "Founder / Admin",
        "theme_mode": "Dark Cyber-FinTech",
        "ty_gia": DEFAULT_EXCHANGE_RATES.copy(),
        "muc_tieu_loi_nhuan_thang": 150000000.0,
        "ngan_sach_chi_tieu_thang": 200000000.0,
        "canh_bao_roas_toi_thieu": 1.65,
        "tu_dong_ sao_luu": True,
        "hien_thi_che_do_co_dien": False,
    }
    data = _safe_read_json(SETTINGS_FILE, dict)
    if not isinstance(data, dict) or not data:
        return default_settings
    merged = default_settings.copy()
    merged.update(data)
    if "ty_gia" not in merged or not isinstance(merged["ty_gia"], dict):
        merged["ty_gia"] = DEFAULT_EXCHANGE_RATES.copy()
    return merged


def luu_cai_dat(settings: Dict[str, Any]) -> bool:
    return _safe_write_json(SETTINGS_FILE, settings)


def ghi_nhat_ky(hanh_dong: str, chi_tiet: str, gia_tri_vnd: float = 0.0, muc_do: str = "INFO") -> None:
    """Ghi lại lịch sử thao tác (Audit Trail) phục vụ kiểm toán nội bộ MMO."""
    logs = _safe_read_json(AUDIT_LOG_FILE, list)
    if not isinstance(logs, list):
        logs = []
    entry = {
        "log_id": "LOG-" + uuid.uuid4().hex[:8].upper(),
        "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hanh_dong": hanh_dong,
        "chi_tiet": chi_tiet,
        "gia_tri_vnd": round(float(gia_tri_vnd), 0),
        "muc_do": muc_do,
        "nguoi_thuc_hien": "Admin / Owner",
    }
    logs.insert(0, entry)
    # Giữ tối đa 500 bản ghi log gần nhất
    _safe_write_json(AUDIT_LOG_FILE, logs[:500])


def doc_nhat_ky() -> List[Dict[str, Any]]:
    logs = _safe_read_json(AUDIT_LOG_FILE, list)
    return logs if isinstance(logs, list) else []


def doc_thung_rac() -> List[Dict[str, Any]]:
    """Đọc danh sách các khoản chi đã xoá tạm thời (Recycle Bin)."""
    trash = _safe_read_json(TRASH_FILE, list)
    return trash if isinstance(trash, list) else []


def luu_thung_rac(trash_list: List[Dict[str, Any]]) -> bool:
    return _safe_write_json(TRASH_FILE, trash_list)


def doc_chien_dich() -> List[Dict[str, Any]]:
    """Đọc danh sách Chiến dịch MMO (Campaigns) cùng chỉ số Ads & ROAS."""
    default_campaigns = [
        {
            "ma_cd": "CAMP-FB-01",
            "ten_cd": "FB Ads - Nutra Kerassentials US/CA Scale",
            "nen_tang": "Facebook Ads",
            "trang_thai": "Đang chạy (Active)",
            "ngan_sach_ngay_vnd": 12000000.0,
            "tong_chi_ads_vnd": 84500000.0,
            "tong_doanh_thu_vnd": 168200000.0,
            "impressions": 640000,
            "clicks": 14800,
            "conversions": 215,
            "nguoi_phu_trach": "Minh Quân (Senior Media Buyer)",
            "ngay_bat_dau": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
            "ghi_chu": "Winning creative video hook #3, ROAS ổn định ~1.99x",
        },
        {
            "ma_cd": "CAMP-TT-02",
            "ten_cd": "TikTok Shop Global - Phụ Kiện Công Nghệ UK",
            "nen_tang": "TikTok Ads & TikTok Shop",
            "trang_thai": "Đang chạy (Active)",
            "ngan_sach_ngay_vnd": 8500000.0,
            "tong_chi_ads_vnd": 52000000.0,
            "tong_doanh_thu_vnd": 119600000.0,
            "impressions": 920000,
            "clicks": 23500,
            "conversions": 480,
            "nguoi_phu_trach": "Hoàng Yến (TikTok Leader)",
            "ngay_bat_dau": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "ghi_chu": "GMV Max kết hợp 12 KOC affiliate livestream",
        },
        {
            "ma_cd": "CAMP-GG-03",
            "ten_cd": "Google Search Ads - SaaS AI VPN Brand Bid",
            "nen_tang": "Google Ads & YouTube",
            "trang_thai": "Đang chạy (Active)",
            "ngan_sach_ngay_vnd": 5000000.0,
            "tong_chi_ads_vnd": 31000000.0,
            "tong_doanh_thu_vnd": 74400000.0,
            "impressions": 180000,
            "clicks": 9400,
            "conversions": 190,
            "nguoi_phu_trach": "Tuấn Kiệt (Google Ads Specialist)",
            "ngay_bat_dau": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),
            "ghi_chu": "Tỷ lệ chuyển đổi cao từ bộ từ khóa đối sánh chính xác",
        },
        {
            "ma_cd": "CAMP-AIR-04",
            "ten_cd": "Web3 Retroactive & Node Farming (200 Wallets)",
            "nen_tang": "Crypto / Web3 / Airdrop / Node",
            "trang_thai": "Đang nuôi (Farming)",
            "ngan_sach_ngay_vnd": 1500000.0,
            "tong_chi_ads_vnd": 18500000.0,
            "tong_doanh_thu_vnd": 62000000.0,
            "impressions": 50000,
            "clicks": 2500,
            "conversions": 85,
            "nguoi_phu_trach": "Đức Anh (Web3 Automation)",
            "ngay_bat_dau": (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d"),
            "ghi_chu": "Chi phí VPS, Proxy tĩnh và Gas fee L2",
        },
    ]
    data = _safe_read_json(CAMPAIGNS_FILE, list)
    if not isinstance(data, list) or len(data) == 0:
        _safe_write_json(CAMPAIGNS_FILE, default_campaigns)
        return default_campaigns
    return data


def luu_chien_dich(campaigns: List[Dict[str, Any]]) -> bool:
    return _safe_write_json(CAMPAIGNS_FILE, campaigns)


def doc_danh_sach_vi() -> List[Dict[str, Any]]:
    """Đọc danh sách Đa Ví & Cổng Thanh Toán MMO."""
    default_wallets = [
        {
            "ma_vi": "WAL-VCB",
            "ten_vi": "Vietcombank (VND)",
            "loai_vi": "Ngân hàng nội địa (Bank)",
            "loai_tien": "VND",
            "so_du_ban_dau": 185000000.0,
            "so_tk": "0071001288999",
            "chu_tk": "ALPHA MMO MEDIA",
            "trang_thai": "Hoạt động",
        },
        {
            "ma_vi": "WAL-TCB",
            "ten_vi": "Techcombank / Thẻ Visa Ads (VND)",
            "loai_vi": "Thẻ tín dụng / Debit Ads",
            "loai_tien": "VND",
            "so_du_ban_dau": 120000000.0,
            "so_tk": "4221-XXXX-XXXX-8892",
            "chu_tk": "MEDIA BUYING CARD",
            "trang_thai": "Hoạt động",
        },
        {
            "ma_vi": "WAL-USDT",
            "ten_vi": "Binance Pay / Ví USDT (TRC20/BEP20)",
            "loai_vi": "Crypto / Stablecoin Wallet",
            "loai_tien": "USDT",
            "so_du_ban_dau": 4500.0,
            "so_tk": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
            "chu_tk": "TREASURY USDT TRC20",
            "trang_thai": "Hoạt động",
        },
        {
            "ma_vi": "WAL-PAYO",
            "ten_vi": "Payoneer (USD)",
            "loai_vi": "Cổng thanh toán Quốc tế",
            "loai_tien": "USD",
            "so_du_ban_dau": 3850.0,
            "so_tk": "billing@alphammo.io",
            "chu_tk": "ALPHA GLOBAL LLC",
            "trang_thai": "Hoạt động",
        },
        {
            "ma_vi": "WAL-PING",
            "ten_vi": "PingPong Payments (USD)",
            "loai_vi": "Cổng thanh toán Quốc tế",
            "loai_tien": "USD",
            "so_du_ban_dau": 2100.0,
            "so_tk": "pp_uk_9928172",
            "chu_tk": "ALPHA ECOM STORE",
            "trang_thai": "Hoạt động",
        },
        {
            "ma_vi": "WAL-MOMO",
            "ten_vi": "Ví MoMo / ZaloPay (VND)",
            "loai_vi": "Ví điện tử nội địa",
            "loai_tien": "VND",
            "so_du_ban_dau": 15000000.0,
            "so_tk": "0988776655",
            "chu_tk": "QUỸ VẬN HÀNH NHANH",
            "trang_thai": "Hoạt động",
        },
    ]
    data = _safe_read_json(WALLETS_FILE, list)
    if not isinstance(data, list) or len(data) == 0:
        _safe_write_json(WALLETS_FILE, default_wallets)
        return default_wallets
    return data


def luu_danh_sach_vi(wallets: List[Dict[str, Any]]) -> bool:
    return _safe_write_json(WALLETS_FILE, wallets)


def doc_dinh_phi_mmo() -> List[Dict[str, Any]]:
    """Đọc danh sách Tài nguyên & Định phí MMO (Subscriptions: Antidetect, Proxy, VPS, AI)."""
    today = datetime.now().date()
    default_subs = [
        {
            "ma_sub": "SUB-001",
            "ten_dich_vu": "AdsPower Antidetect Browser (Gói 200 Profiles + 5 Seats)",
            "nhom": "Antidetect Browser (AdsPower/Multilogin/GoLogin)",
            "chu_ky": "Hàng tháng (Monthly)",
            "nguyen_te": 90.0,
            "loai_tien": "USDT",
            "vi_thanh_toan": "Binance Pay / Ví USDT (TRC20/BEP20)",
            "ngay_gia_han": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "tu_dong_gia_han": True,
            "trang_thai": "Đang hoạt động",
            "ghi_chu": "Tài khoản chính quản lý dàn tài khoản FB & TikTok Shop",
        },
        {
            "ma_sub": "SUB-002",
            "ten_dich_vu": "BrightData / 922Proxy Residential IP (Gói Doanh Nghiệp 300GB)",
            "nhom": "Proxy / IP Dân cư / 4G",
            "chu_ky": "Hàng tháng (Monthly)",
            "nguyen_te": 180.0,
            "loai_tien": "USD",
            "vi_thanh_toan": "Payoneer (USD)",
            "ngay_gia_han": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
            "tu_dong_gia_han": True,
            "trang_thai": "Sắp đến hạn",
            "ghi_chu": "IP sạch US/UK/EU phục vụ nuôi VIA và checkout",
        },
        {
            "ma_sub": "SUB-003",
            "ten_dich_vu": "Hetzner / Contabo Cloud Dedicated VPS (12 Nodes Windows/Ubuntu)",
            "nhom": "VPS / Cloud Server / Hosting / Domain",
            "chu_ky": "Hàng tháng (Monthly)",
            "nguyen_te": 145.0,
            "loai_tien": "USD",
            "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
            "ngay_gia_han": (today + timedelta(days=12)).strftime("%Y-%m-%d"),
            "tu_dong_gia_han": True,
            "trang_thai": "Đang hoạt động",
            "ghi_chu": "Chạy bot tự động hóa, nuôi node và tool cronjob 24/7",
        },
        {
            "ma_sub": "SUB-004",
            "ten_dich_vu": "OpenAI API + Claude Pro + ElevenLabs + CapCut Pro Team",
            "nhom": "Tool MMO / Phần mềm AI / API (OpenAI/Claude/CapCut)",
            "chu_ky": "Hàng tháng (Monthly)",
            "nguyen_te": 110.0,
            "loai_tien": "USD",
            "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
            "ngay_gia_han": (today + timedelta(days=18)).strftime("%Y-%m-%d"),
            "tu_dong_gia_han": True,
            "trang_thai": "Đang hoạt động",
            "ghi_chu": "Sản xuất kịch bản, voiceover và video spy/render hàng loạt",
        },
        {
            "ma_sub": "SUB-005",
            "ten_dich_vu": "AdSpy / PipiAds / Kalodata TikTok Analytics VIP",
            "nhom": "Tool MMO / Phần mềm AI / API (OpenAI/Claude/CapCut)",
            "chu_ky": "Hàng tháng (Monthly)",
            "nguyen_te": 155.0,
            "loai_tien": "USD",
            "vi_thanh_toan": "Payoneer (USD)",
            "ngay_gia_han": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "tu_dong_gia_han": False,
            "trang_thai": "Sắp đến hạn",
            "ghi_chu": "Spy win product và mẫu quảng cáo đối thủ",
        },
    ]
    data = _safe_read_json(SUBSCRIPTIONS_FILE, list)
    if not isinstance(data, list) or len(data) == 0:
        _safe_write_json(SUBSCRIPTIONS_FILE, default_subs)
        return default_subs
    return data


def luu_dinh_phi_mmo(subs: List[Dict[str, Any]]) -> bool:
    return _safe_write_json(SUBSCRIPTIONS_FILE, subs)


def doc_nhan_su_mmo() -> List[Dict[str, Any]]:
    """Đọc danh sách Đội nhóm MMO (Media Buyers, Editors, VAs, Developers) & Cấu trúc chia lãi."""
    default_team = [
        {
            "ma_nv": "MEM-01",
            "ho_ten": "Nguyễn Minh Quân",
            "vai_tro": "Senior Facebook Media Buyer",
            "luong_cung_vnd": 15000000.0,
            "phan_tram_loi_nhuan": 12.0,
            "loi_nhuan_mang_ve_vnd": 83700000.0,
            "thuong_kpi_vnd": 3000000.0,
            "vi_nhan_luong": "Vietcombank - 007100998877",
            "trang_thai": "Full-time",
        },
        {
            "ma_nv": "MEM-02",
            "ho_ten": "Trần Hoàng Yến",
            "vai_tro": "TikTok Shop & Affiliate Team Lead",
            "luong_cung_vnd": 14000000.0,
            "phan_tram_loi_nhuan": 10.0,
            "loi_nhuan_mang_ve_vnd": 67600000.0,
            "thuong_kpi_vnd": 2500000.0,
            "vi_nhan_luong": "Techcombank - 190344556677",
            "trang_thai": "Full-time",
        },
        {
            "ma_nv": "MEM-03",
            "ho_ten": "Lê Tuấn Kiệt",
            "vai_tro": "Google Ads & Funnel Optimizer",
            "luong_cung_vnd": 12000000.0,
            "phan_tram_loi_nhuan": 8.0,
            "loi_nhuan_mang_ve_vnd": 43400000.0,
            "thuong_kpi_vnd": 1500000.0,
            "vi_nhan_luong": "MB Bank - 889900112233",
            "trang_thai": "Full-time",
        },
        {
            "ma_nv": "MEM-04",
            "ho_ten": "Phạm Đức Anh",
            "vai_tro": "Web3 Automation & Tool Developer",
            "luong_cung_vnd": 13000000.0,
            "phan_tram_loi_nhuan": 10.0,
            "loi_nhuan_mang_ve_vnd": 43500000.0,
            "thuong_kpi_vnd": 2000000.0,
            "vi_nhan_luong": "Binance USDT - TRC20",
            "trang_thai": "Full-time",
        },
        {
            "ma_nv": "MEM-05",
            "ho_ten": "Vũ Thảo My",
            "vai_tro": "Creative Video Editor & Resource VA",
            "luong_cung_vnd": 9500000.0,
            "phan_tram_loi_nhuan": 3.0,
            "loi_nhuan_mang_ve_vnd": 25000000.0,
            "thuong_kpi_vnd": 1500000.0,
            "vi_nhan_luong": "Vietcombank - 045100223344",
            "trang_thai": "Full-time",
        },
    ]
    data = _safe_read_json(TEAM_FILE, list)
    if not isinstance(data, list) or len(data) == 0:
        _safe_write_json(TEAM_FILE, default_team)
        return default_team
    return data


def luu_nhan_su_mmo(team: List[Dict[str, Any]]) -> bool:
    return _safe_write_json(TEAM_FILE, team)


def doc_ngan_sach_danh_muc() -> Dict[str, float]:
    """Đọc hạn mức ngân sách chi tiêu hàng tháng theo từng danh mục."""
    default_budgets = {
        "Quảng cáo Facebook Ads": 90000000.0,
        "Quảng cáo TikTok Ads": 60000000.0,
        "Quảng cáo Google / YouTube Ads": 40000000.0,
        "Mua VIA / BM / Tài khoản Ads": 15000000.0,
        "Proxy / IP Dân cư / 4G": 8000000.0,
        "Antidetect Browser (AdsPower/Multilogin/GoLogin)": 4000000.0,
        "VPS / Cloud Server / Hosting / Domain": 6000000.0,
        "Tool MMO / Phần mềm AI / API (OpenAI/Claude/CapCut)": 8000000.0,
        "Fulfillment / Giá vốn hàng bán (COGS / Dropship)": 45000000.0,
        "Lương nhân sự / Media Buyer / Editor / VA": 75000000.0,
        "Chi phí văn phòng / Thiết bị / Điện & Internet": 12000000.0,
        "Ăn uống / Sinh hoạt cá nhân": 10000000.0,
    }
    data = _safe_read_json(BUDGETS_FILE, dict)
    if not isinstance(data, dict) or len(data) == 0:
        _safe_write_json(BUDGETS_FILE, default_budgets)
        return default_budgets
    return data


def luu_ngan_sach_danh_muc(budgets: Dict[str, float]) -> bool:
    return _safe_write_json(BUDGETS_FILE, budgets)


def seed_mmo_enterprise_data(append_mode: bool = True) -> int:
    """
    Khởi tạo bộ dữ liệu mẫu MMO thực tế (Facebook Ads, TikTok Shop, Affiliate Payout,
    Mua VIA/BM, Proxy, Antidetect, Cashback, Lương Team) vào `so_hoan_chinh.json`
    để người dùng trải nghiệm ngay đầy đủ biểu đồ và báo cáo.
    """
    now = datetime.now()
    sample_records = [
        {
            "ten": "Thanh toán ngưỡng thẻ Facebook Ads - Chiến dịch Nutra US #01",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 900.0,
            "loai_tien": "USD",
            "ty_gia": 25450.0,
            "phi_phan_tram": 2.0,
            "thue_phan_tram": 5.0,
            "danh_muc": "Quảng cáo Facebook Ads",
            "chien_dich": "FB Ads - Nutra Kerassentials US/CA Scale",
            "nen_tang": "Facebook Ads",
            "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=12, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["fb-ads", "nutra", "threshold-900"],
            "ghi_chu": "Bill ngưỡng $900 thẻ Visa Signature đuôi 8892",
        },
        {
            "ten": "Mua lô 30 VIA Cổ Mỹ XMDT + 5 BM350 kháng sẵn",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 6800000.0,
            "loai_tien": "VND",
            "ty_gia": 1.0,
            "phi_phan_tram": 0.0,
            "thue_phan_tram": 0.0,
            "danh_muc": "Mua VIA / BM / Tài khoản Ads",
            "chien_dich": "FB Ads - Nutra Kerassentials US/CA Scale",
            "nen_tang": "Facebook Ads",
            "vi_thanh_toan": "Vietcombank (VND)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=11, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["via-xmdt", "bm350", "nguyen-lieu"],
            "ghi_chu": "Nhập từ đối tác Agency bảo hành 1 đổi 1",
        },
        {
            "ten": "Gia hạn gói Proxy Dân Cư Xoay BrightData 300GB",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 180.0,
            "loai_tien": "USD",
            "ty_gia": 25450.0,
            "phi_phan_tram": 1.0,
            "thue_phan_tram": 0.0,
            "danh_muc": "Proxy / IP Dân cư / 4G",
            "chien_dich": "Vận hành chung / Nội bộ",
            "nen_tang": "Vận hành chung / Nội bộ",
            "vi_thanh_toan": "Payoneer (USD)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=10, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["proxy", "brightdata", "ip-us"],
            "ghi_chu": "Phục vụ 200 profiles AdsPower không trùng IP",
        },
        {
            "ten": "Gia hạn AdsPower Antidetect Browser (200 Profiles Team)",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 90.0,
            "loai_tien": "USDT",
            "ty_gia": 25680.0,
            "phi_phan_tram": 0.5,
            "thue_phan_tram": 0.0,
            "danh_muc": "Antidetect Browser (AdsPower/Multilogin/GoLogin)",
            "chien_dich": "Vận hành chung / Nội bộ",
            "nen_tang": "Vận hành chung / Nội bộ",
            "vi_thanh_toan": "Binance Pay / Ví USDT (TRC20/BEP20)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=9, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["adspower", "antidetect", "subscription"],
            "ghi_chu": "Thanh toán qua cổng Binance Pay hoàn tất",
        },
        {
            "ten": "Nhận Payout ClickBank & Digistore24 Tuần 1 (US Offers)",
            "loai": "Thu nhập / Payout (Revenue)",
            "nguyen_te": 3450.0,
            "loai_tien": "USD",
            "ty_gia": 25450.0,
            "phi_phan_tram": 1.0,
            "thue_phan_tram": 0.0,
            "danh_muc": "Payout Affiliate (ClickBank / Offervault / CJ / Impact)",
            "chien_dich": "FB Ads - Nutra Kerassentials US/CA Scale",
            "nen_tang": "Affiliate Global (ClickBank / MaxBounty / Digistore24)",
            "vi_thanh_toan": "Payoneer (USD)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=8, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["payout", "clickbank", "revenue"],
            "ghi_chu": "Direct Deposit về tài khoản Payoneer USD",
        },
        {
            "ten": "Nạp ngân sách TikTok Ads GMV Max UK Store",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 1200.0,
            "loai_tien": "USD",
            "ty_gia": 25450.0,
            "phi_phan_tram": 2.0,
            "thue_phan_tram": 0.0,
            "danh_muc": "Quảng cáo TikTok Ads",
            "chien_dich": "TikTok Shop Global - Phụ Kiện Công Nghệ UK",
            "nen_tang": "TikTok Ads & TikTok Shop",
            "vi_thanh_toan": "PingPong Payments (USD)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=7, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["tiktok-ads", "gmv-max", "uk-store"],
            "ghi_chu": "Chạy chiến dịch livestream + video shopping",
        },
        {
            "ten": "Thanh toán tiền hàng Fulfillment & Ship YunExpress (180 đơn UK)",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 920.0,
            "loai_tien": "USDT",
            "ty_gia": 25680.0,
            "phi_phan_tram": 0.5,
            "thue_phan_tram": 0.0,
            "danh_muc": "Fulfillment / Giá vốn hàng bán (COGS / Dropship)",
            "chien_dich": "TikTok Shop Global - Phụ Kiện Công Nghệ UK",
            "nen_tang": "TikTok Ads & TikTok Shop",
            "vi_thanh_toan": "Binance Pay / Ví USDT (TRC20/BEP20)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=6, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["fulfillment", "cogs", "yunexpress"],
            "ghi_chu": "Thanh toán cho Private Agent Thâm Quyến qua USDT",
        },
        {
            "ten": "Rút doanh thu Settlement TikTok Shop UK về PingPong",
            "loai": "Thu nhập / Payout (Revenue)",
            "nguyen_te": 4280.0,
            "loai_tien": "USD",
            "ty_gia": 25450.0,
            "phi_phan_tram": 1.0,
            "thue_phan_tram": 0.0,
            "danh_muc": "Doanh thu TikTok Shop / Shopee / Lazada",
            "chien_dich": "TikTok Shop Global - Phụ Kiện Công Nghệ UK",
            "nen_tang": "TikTok Ads & TikTok Shop",
            "vi_thanh_toan": "PingPong Payments (USD)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=5, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["tiktok-payout", "settlement", "uk"],
            "ghi_chu": "Đối soát 180 đơn giao thành công tuần trước",
        },
        {
            "ten": "Thanh toán Google Search Ads - Chiến dịch SaaS AI VPN",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 650.0,
            "loai_tien": "USD",
            "ty_gia": 25450.0,
            "phi_phan_tram": 2.2,
            "thue_phan_tram": 5.0,
            "danh_muc": "Quảng cáo Google / YouTube Ads",
            "chien_dich": "Google Search Ads - SaaS AI VPN Brand Bid",
            "nen_tang": "Google Ads & YouTube",
            "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=4, hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["google-ads", "search", "saas"],
            "ghi_chu": "Ngưỡng thanh toán tự động MCC Google Ads",
        },
        {
            "ten": "Gia hạn cụm 12 VPS Hetzner + OpenAI API / Claude / CapCut Team",
            "loai": "Chi tiêu (Expense)",
            "nguyen_te": 255.0,
            "loai_tien": "USD",
            "ty_gia": 25450.0,
            "phi_phan_tram": 1.5,
            "thue_phan_tram": 0.0,
            "danh_muc": "VPS / Cloud Server / Hosting / Domain",
            "chien_dich": "Web3 Retroactive & Node Farming (200 Wallets)",
            "nen_tang": "Crypto / Web3 / Airdrop / Node",
            "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=3, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["vps", "hetzner", "ai-api"],
            "ghi_chu": "Duy trì hạ tầng server tự động hóa 24/7",
        },
        {
            "ten": "Thu hoạch Airdrop & Staking Rewards L2 (85 Ví đạt chuẩn)",
            "loai": "Thu nhập / Payout (Revenue)",
            "nguyen_te": 2400.0,
            "loai_tien": "USDT",
            "ty_gia": 25680.0,
            "phi_phan_tram": 0.2,
            "thue_phan_tram": 0.0,
            "danh_muc": "Airdrop / Retroactive / Staking / Crypto Trading",
            "chien_dich": "Web3 Retroactive & Node Farming (200 Wallets)",
            "nen_tang": "Crypto / Web3 / Airdrop / Node",
            "vi_thanh_toan": "Binance Pay / Ví USDT (TRC20/BEP20)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["airdrop", "web3", "usdt"],
            "ghi_chu": "Đã quy đổi token sang USDT trên sàn Binance",
        },
        {
            "ten": "Hoàn tiền Cashback 3% Thẻ Tín Dụng Doanh Nghiệp Techcombank",
            "loai": "Hoàn tiền / Rebate (Cashback)",
            "nguyen_te": 4850000.0,
            "loai_tien": "VND",
            "ty_gia": 1.0,
            "phi_phan_tram": 0.0,
            "thue_phan_tram": 0.0,
            "danh_muc": "Cashback thẻ Ads / Hoàn tiền cổng thanh toán",
            "chien_dich": "Vận hành chung / Nội bộ",
            "nen_tang": "Vận hành chung / Nội bộ",
            "vi_thanh_toan": "Techcombank / Thẻ Visa Ads (VND)",
            "trang_thai": "Hoàn thành (Completed)",
            "ngay_gio": (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "tags": ["cashback", "rebate", "card"],
            "ghi_chu": "Hoàn tiền chi tiêu quảng cáo quốc tế kỳ sao kê",
        },
    ]

    current_data = doc_file() if append_mode else []
    start_idx = len(current_data) + 1
    for offset, rec in enumerate(sample_records):
        # Tính sẵn trường `tien` để normalize chuẩn xác
        base_vnd = rec["nguyen_te"] * rec["ty_gia"]
        fee_vnd = base_vnd * (rec["phi_phan_tram"] / 100.0)
        tax_vnd = base_vnd * (rec["thue_phan_tram"] / 100.0)
        rec["phi_vnd"] = round(fee_vnd, 0)
        rec["thue_vnd"] = round(tax_vnd, 0)
        rec["tien"] = round(base_vnd + fee_vnd + tax_vnd, 0)
        current_data.append(normalize_transaction_record(rec, start_idx + offset))

    luu_file(current_data)
    ghi_nhat_ky(
        "SEED_DEMO_DATA",
        f"Đã nạp {len(sample_records)} giao dịch mẫu MMO chuyên nghiệp vào sổ cái",
        sum(r["tien"] for r in sample_records),
        "SUCCESS",
    )
    return len(sample_records)


# ==============================================================================
# 5. ĐỘNG CƠ PHÂN TÍCH TÀI CHÍNH & CHỈ SỐ MMO (QUANTITATIVE ANALYTICS ENGINE)
# ==============================================================================

def phan_tich_tong_quan_tai_chinh(ds_ct: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tính toán toàn diện các chỉ số tài chính MMO:
    - Tổng chi tiêu (Total Expense)
    - Tổng doanh thu / Payout (Total Revenue)
    - Hoàn tiền / Cashback (Total Rebate)
    - Lợi nhuận ròng (Net Profit)
    - Tỷ suất lợi nhuận (Net Margin %)
    - ROAS / ROI trung bình toàn hệ thống
    - Tổng phí cổng thanh toán & thuế nhà thầu
    - Burn Rate trung bình/ngày & Runway dự kiến
    - Điểm sức khỏe tài chính MMO (Financial Health Score 0-100)
    """
    tong_chi = 0.0
    tong_thu = 0.0
    tong_hoan_tien = 0.0
    tong_rut_von = 0.0
    tong_nap_von = 0.0
    tong_phi_gd = 0.0
    tong_thue = 0.0
    tong_tat_ca = 0.0

    chi_theo_danh_muc: Dict[str, float] = defaultdict(float)
    thu_theo_danh_muc: Dict[str, float] = defaultdict(float)
    chi_theo_vi: Dict[str, float] = defaultdict(float)
    thu_theo_vi: Dict[str, float] = defaultdict(float)
    chi_theo_chien_dich: Dict[str, float] = defaultdict(float)
    thu_theo_chien_dich: Dict[str, float] = defaultdict(float)
    dong_tien_theo_ngay: Dict[str, Dict[str, float]] = defaultdict(
        lambda: {"Chi": 0.0, "Thu": 0.0, "Rong": 0.0}
    )

    so_giao_dich_chi = 0
    so_giao_dich_thu = 0
    danh_sach_khoan_chi: List[float] = []

    for item in ds_ct:
        tien = float(item.get("tien", 0.0))
        loai = str(item.get("loai", "Chi tiêu (Expense)"))
        danh_muc = str(item.get("danh_muc", "Khác"))
        vi = str(item.get("vi_thanh_toan", "Vietcombank (VND)"))
        cd = str(item.get("chien_dich", "Vận hành chung / Nội bộ"))
        ngay = str(item.get("ngay", datetime.now().strftime("%Y-%m-%d")))
        phi_vnd = float(item.get("phi_vnd", 0.0))
        thue_vnd = float(item.get("thue_vnd", 0.0))

        tong_tat_ca += tien
        tong_phi_gd += phi_vnd
        tong_thue += thue_vnd

        if "Thu nhập" in loai or "Revenue" in loai:
            tong_thu += tien
            so_giao_dich_thu += 1
            thu_theo_danh_muc[danh_muc] += tien
            thu_theo_vi[vi] += tien
            thu_theo_chien_dich[cd] += tien
            dong_tien_theo_ngay[ngay]["Thu"] += tien
            dong_tien_theo_ngay[ngay]["Rong"] += tien
        elif "Hoàn tiền" in loai or "Cashback" in loai:
            tong_hoan_tien += tien
            so_giao_dich_thu += 1
            thu_theo_danh_muc[danh_muc] += tien
            thu_theo_vi[vi] += tien
            dong_tien_theo_ngay[ngay]["Thu"] += tien
            dong_tien_theo_ngay[ngay]["Rong"] += tien
        elif "Nạp vốn" in loai:
            tong_nap_von += tien
            thu_theo_vi[vi] += tien
        elif "Rút vốn" in loai:
            tong_rut_von += tien
            chi_theo_vi[vi] += tien
        else:
            tong_chi += tien
            so_giao_dich_chi += 1
            danh_sach_khoan_chi.append(tien)
            chi_theo_danh_muc[danh_muc] += tien
            chi_theo_vi[vi] += tien
            chi_theo_chien_dich[cd] += tien
            dong_tien_theo_ngay[ngay]["Chi"] += tien
            dong_tien_theo_ngay[ngay]["Rong"] -= tien

    tong_thu_thuc_te = tong_thu + tong_hoan_tien
    loi_nhuan_rong = tong_thu_thuc_te - tong_chi
    ty_suat_loi_nhuan = (
        (loi_nhuan_rong / tong_thu_thuc_te * 100.0) if tong_thu_thuc_te > 0 else 0.0
    )
    roas_chung = (tong_thu_thuc_te / tong_chi) if tong_chi > 0 else 0.0
    roi_phan_tram = ((loi_nhuan_rong / tong_chi) * 100.0) if tong_chi > 0 else 0.0

    so_ngay_hoat_dong = max(len(dong_tien_theo_ngay), 1)
    burn_rate_ngay = tong_chi / so_ngay_hoat_dong
    trung_binh_khoan_chi = (
        statistics.mean(danh_sach_khoan_chi) if danh_sach_khoan_chi else 0.0
    )
    trung_vi_khoan_chi = (
        statistics.median(danh_sach_khoan_chi) if danh_sach_khoan_chi else 0.0
    )
    max_khoan_chi = max(danh_sach_khoan_chi) if danh_sach_khoan_chi else 0.0

    # Tính điểm sức khỏe tài chính MMO (0 - 100)
    diem_suc_khoe = 65
    if loi_nhuan_rong > 0:
        diem_suc_khoe += 15
    if roas_chung >= 1.8:
        diem_suc_khoe += 12
    elif roas_chung >= 1.3:
        diem_suc_khoe += 6
    elif 0 < roas_chung < 1.0:
        diem_suc_khoe -= 15
    if tong_phi_gd + tong_thue < tong_chi * 0.06:
        diem_suc_khoe += 8
    diem_suc_khoe = max(10, min(100, int(diem_suc_khoe)))

    return {
        "tong_tat_ca": tong_tat_ca,
        "tong_chi": tong_chi,
        "tong_thu": tong_thu,
        "tong_hoan_tien": tong_hoan_tien,
        "tong_thu_thuc_te": tong_thu_thuc_te,
        "tong_nap_von": tong_nap_von,
        "tong_rut_von": tong_rut_von,
        "loi_nhuan_rong": loi_nhuan_rong,
        "ty_suat_loi_nhuan": ty_suat_loi_nhuan,
        "roas_chung": roas_chung,
        "roi_phan_tram": roi_phan_tram,
        "tong_phi_gd": tong_phi_gd,
        "tong_thue": tong_thue,
        "so_giao_dich": len(ds_ct),
        "so_giao_dich_chi": so_giao_dich_chi,
        "so_giao_dich_thu": so_giao_dich_thu,
        "burn_rate_ngay": burn_rate_ngay,
        "trung_binh_khoan_chi": trung_binh_khoan_chi,
        "trung_vi_khoan_chi": trung_vi_khoan_chi,
        "max_khoan_chi": max_khoan_chi,
        "diem_suc_khoe": diem_suc_khoe,
        "chi_theo_danh_muc": dict(chi_theo_danh_muc),
        "thu_theo_danh_muc": dict(thu_theo_danh_muc),
        "chi_theo_vi": dict(chi_theo_vi),
        "thu_theo_vi": dict(thu_theo_vi),
        "chi_theo_chien_dich": dict(chi_theo_chien_dich),
        "thu_theo_chien_dich": dict(thu_theo_chien_dich),
        "dong_tien_theo_ngay": dict(dong_tien_theo_ngay),
    }


def phat_hien_giao_dich_bat_thuong(ds_ct: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Thuật toán phát hiện các khoản chi tiêu đột biến (Anomaly Detection) dựa trên
    ngưỡng trung bình + độ lệch chuẩn (Z-Score) để cảnh báo vượt ngưỡng thẻ Ads.
    """
    chi_items = [
        x for x in ds_ct
        if "Chi" in str(x.get("loai", "Chi tiêu")) and float(x.get("tien", 0)) > 0
    ]
    if len(chi_items) < 3:
        return []
    values = [float(x["tien"]) for x in chi_items]
    mean_val = statistics.mean(values)
    stdev_val = statistics.stdev(values) if len(values) > 1 else 0.0
    threshold = mean_val + max(1.25 * stdev_val, mean_val * 0.65)
    anomalies = []
    for x in chi_items:
        val = float(x["tien"])
        if val >= threshold:
            pct_over = ((val - mean_val) / mean_val * 100.0) if mean_val > 0 else 0.0
            anomalies.append({
                "id": x.get("id", ""),
                "ten": x.get("ten", ""),
                "tien": val,
                "danh_muc": x.get("danh_muc", ""),
                "ngay": x.get("ngay", ""),
                "vuot_trung_binh_pct": round(pct_over, 1),
            })
    return sorted(anomalies, key=lambda item: item["tien"], reverse=True)


def xuat_bao_cao_html_chuyen_nghiep(ds_ct: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """Tạo file Báo cáo Tài chính MMO định dạng HTML độc lập có thể in ra PDF."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    rows_html = ""
    for idx, item in enumerate(ds_ct, start=1):
        loai = item.get("loai", "Chi tiêu")
        color = "#10B981" if ("Thu" in loai or "Hoàn" in loai) else "#EF4444"
        rows_html += f"""
        <tr>
            <td>{idx}</td>
            <td><code>{item.get('id', '')}</code></td>
            <td>{item.get('ngay', '')}</td>
            <td><strong>{item.get('ten', '')}</strong></td>
            <td>{item.get('danh_muc', '')}</td>
            <td>{item.get('chien_dich', '')}</td>
            <td>{item.get('vi_thanh_toan', '')}</td>
            <td style="color:{color}; font-weight:700; text-align:right;">{format_vnd(item.get('tien', 0))}</td>
        </tr>
        """

    html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo Cáo Tài Chính MMO - {now_str}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 32px; }}
        .container {{ max-width: 1180px; margin: 0 auto; background: #1e293b; padding: 28px; border-radius: 16px; border: 1px solid #334155; }}
        h1 {{ color: #10b981; margin-top: 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 20px 0; }}
        .card {{ background: #0f172a; padding: 16px; border-radius: 10px; border: 1px solid #334155; }}
        .card-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
        .card-val {{ font-size: 20px; font-weight: 800; margin-top: 6px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
        th {{ background: #0f172a; color: #38bdf8; text-align: left; padding: 10px; border-bottom: 2px solid #334155; }}
        td {{ padding: 9px 10px; border-bottom: 1px solid #334155; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>💎 BÁO CÁO QUẢN TRỊ DÒNG TIỀN & CHI TIÊU MMO</h1>
        <p>Thời điểm xuất báo cáo: <strong>{now_str}</strong> | Tổng số bản ghi: <strong>{len(ds_ct)}</strong></p>
        <div class="summary-grid">
            <div class="card"><div class="card-label">Tổng Doanh Thu & Payout</div><div class="card-val" style="color:#10b981;">{format_vnd(stats['tong_thu_thuc_te'])}</div></div>
            <div class="card"><div class="card-label">Tổng Chi Tiêu Vận Hành</div><div class="card-val" style="color:#ef4444;">{format_vnd(stats['tong_chi'])}</div></div>
            <div class="card"><div class="card-label">Lợi Nhuận Ròng (Net P&L)</div><div class="card-val" style="color:#38bdf8;">{format_vnd(stats['loi_nhuan_rong'])}</div></div>
            <div class="card"><div class="card-label">Chỉ Số ROAS Chung</div><div class="card-val" style="color:#f59e0b;">{stats['roas_chung']:.2f}x</div></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>STT</th>
                    <th>Mã GD</th>
                    <th>Ngày</th>
                    <th>Nội Dung Khoản Giao Dịch</th>
                    <th>Danh Mục</th>
                    <th>Chiến Dịch</th>
                    <th>Ví Thanh Toán</th>
                    <th style="text-align:right;">Số Tiền (VNĐ)</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>"""
    return html_doc


# ==============================================================================
# 6. THANH ĐIỀU HƯỚNG SIDEBAR & HEADER TRUNG TÂM (NAVIGATION & TICKER)
# ==============================================================================

MENU_OPTIONS = [
    " 1. Thêm khoản chi mới",
    " 2. Xem toàn bộ danh sách & tổng tiền",
    " 3. Xoá khoản chi tiêu",
    " 4. Sửa khoản chi tiêu",
    "📊 5. MMO Command Center (Dashboard Tổng Quan)",
    "🚀 6. Quản lý Chiến dịch Ads & ROAS (Campaigns)",
    "💳 7. Quản lý Đa Ví & Cổng Thanh Toán (Treasury)",
    "🔄 8. Tài nguyên & Định phí MMO (Proxy/VPS/Antidetect)",
    "👥 9. Đội nhóm MMO, Lương KPI & Chia Lợi Nhuận",
    "🎯 10. Ngân sách, Dự báo AI & Giả lập Scale ROAS",
    "🛡️ 11. Nhật ký Bảo mật, Sao lưu & Hệ thống",
]


def render_top_ticker_and_hero(settings: Dict[str, Any], stats: Dict[str, Any]) -> None:
    """Hiển thị thanh tỷ giá trực tuyến MMO và Banner thương hiệu ở đầu trang."""
    rates = settings.get("ty_gia", DEFAULT_EXCHANGE_RATES)
    usd_rate = rates.get("USD", 25450.0)
    usdt_rate = rates.get("USDT", 25680.0)
    eur_rate = rates.get("EUR", 27500.0)

    st.markdown(
        f"""
        <div class="mmo-ticker-bar">
            <div class="mmo-ticker-item">
                <span class="mmo-ticker-badge">LIVE TREASURY</span>
                <span>🇺🇸 USD/VND: <strong>{usd_rate:,.0f}đ</strong></span>
            </div>
            <div class="mmo-ticker-item">
                <span>💎 USDT (TRC20 P2P): <strong>{usdt_rate:,.0f}đ</strong></span>
            </div>
            <div class="mmo-ticker-item">
                <span>🇪🇺 EUR/VND: <strong>{eur_rate:,.0f}đ</strong></span>
            </div>
            <div class="mmo-ticker-item">
                <span>⚡ ROAS Hệ Thống: <strong>{stats['roas_chung']:.2f}x</strong></span>
            </div>
            <div class="mmo-ticker-item">
                <span>🛡️ Health Score: <strong>{stats['diem_suc_khoe']}/100</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="mmo-hero-header">
            <div>
                <div class="mmo-hero-title">
                    💎 {settings.get('ten_doanh_nghiep', 'MMO FinTech & Expense Suite Pro')}
                </div>
                <p class="mmo-hero-subtitle">
                    Hệ thống Quản trị Chi tiêu, Dòng tiền Đa ví, Chiến dịch Quảng cáo (FB/TikTok/Google Ads) &的对 soát Lợi nhuận MMO chuyên sâu
                </p>
            </div>
            <div style="text-align:right; font-family:'JetBrains Mono', monospace; font-size:0.82rem; color:#10B981;">
                <div>● SYSTEM ONLINE | v{APP_VERSION}</div>
                <div style="color:#94A3B8;">Data File: {PRIMARY_DATA_FILE} ({stats['so_giao_dich']} records)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 7. MODULE 1: THÊM KHOẢN CHI MỚI & TRẠM NHẬP GIAO DỊCH MMO (NÂNG CẤP MỤC 1)
# ==============================================================================

def render_module_add_transaction(
    ds_ct: List[Dict[str, Any]],
    settings: Dict[str, Any],
    campaigns: List[Dict[str, Any]],
    wallets: List[Dict[str, Any]],
) -> None:
    """
    Nâng cấp toàn diện Mục 1: ' 1. Thêm khoản chi mới'
    - Vẫn giữ nguyên chế độ Nhập Nhanh Cổ Điển (2 cột: Nhập khoản chi mới + Nhập số tiền + Nút Lưu khoản chi)
      tương thích 100% với code gốc của người dùng.
    - Bổ sung Chế độ Chuyên Nghiệp MMO (Đa tiền tệ VND/USD/USDT, tự động tính Phí cổng/Thuế thẻ Ads,
      gắn Chiến dịch, chọn Ví thanh toán, Nhập hàng loạt Batch Entry & Mẫu giao dịch nhanh 1-Click).
    """
    render_section_header(
        "➕ THÊM KHOẢN CHI TIÊU & GIAO DỊCH MMO MỚI",
        "MODULE 01 • TRANSACTION ENTRY",
    )

    tab_classic, tab_pro, tab_templates, tab_batch = st.tabs([
        "⚡ Nhập Nhanh (Chuẩn Gốc + Mở Rộng)",
        "💎 Nhập Chuyên Sâu MMO (Đa Tiền Tệ & Thuế/Phí Ads)",
        "🔥 Mẫu Giao Dịch MMO 1-Click (Quick Templates)",
        "📥 Nhập Hàng Loạt (Batch Import / Paste)",
    ])

    campaign_names = ["Vận hành chung / Nội bộ"] + [
        c.get("ten_cd", "") for c in campaigns if c.get("ten_cd")
    ]
    wallet_names = [w.get("ten_vi", "") for w in wallets if w.get("ten_vi")]
    if not wallet_names:
        wallet_names = DEFAULT_PAYMENT_METHODS

    # --------------------------------------------------------------------------
    # TAB 1: CHẾ ĐỘ NHẬP NHANH (GIỮ NGUYÊN LOGIC CỘT 1 & CỘT 2 GỐC CỦA USER)
    # --------------------------------------------------------------------------
    with tab_classic:
        st.markdown(
            """
            <div class="mmo-glass-panel">
                <strong>💡 Chế độ Nhập Nhanh Tương Thích Gốc:</strong> Giữ nguyên bố cục 2 cột
                (<code>Nhập khoản chi mới</code> & <code>Nhập số tiền</code>) như phiên bản ban đầu,
                đồng thời tự động phân loại danh mục thông minh và ghi nhật ký bảo mật.
            </div>
            """,
            unsafe_allow_html=True,
        )

        cot1, cot2 = st.columns(2)
        with cot1:
            ten_moi = st.text_input(
                "Nhập khoản chi mới: ",
                placeholder="VD: Chạy quảng cáo Facebook Ads chiến dịch mới...",
                key="classic_ten_moi",
            )
            danh_muc_nhanh = st.selectbox(
                "Danh mục (Tự động gợi ý hoặc chọn):",
                options=["Tự động nhận diện thông minh"] + ALL_CATEGORIES,
                key="classic_danh_muc",
            )
        with cot2:
            tien_moi = st.number_input(
                "Nhập số tiền: ",
                min_value=0,
                step=1000,
                value=0,
                key="classic_tien_moi",
            )
            vi_nhanh = st.selectbox(
                "Nguồn tiền / Ví thanh toán:",
                options=wallet_names,
                key="classic_vi",
            )

        if st.button("Lưu khoản chi", type="primary", use_container_width=True, key="btn_classic_save"):
            if not ten_moi.strip():
                st.warning("⚠️ Vui lòng nhập tên khoản chi mới trước khi lưu!")
            elif tien_moi <= 0:
                st.warning("⚠️ Số tiền phải lớn hơn 0đ!")
            else:
                record_raw = {
                    "ten": ten_moi.strip(),
                    "tien": float(tien_moi),
                    "loai": "Chi tiêu (Expense)",
                    "nguyen_te": float(tien_moi),
                    "loai_tien": "VND",
                    "ty_gia": 1.0,
                    "vi_thanh_toan": vi_nhanh,
                    "ngay_gio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                if danh_muc_nhanh != "Tự động nhận diện thông minh":
                    record_raw["danh_muc"] = danh_muc_nhanh

                normalized_rec = normalize_transaction_record(record_raw, len(ds_ct) + 1)
                ds_ct.append(normalized_rec)
                luu_file(ds_ct)
                ghi_nhat_ky(
                    "ADD_EXPENSE_QUICK",
                    f"Thêm khoản chi: {normalized_rec['ten']} ({format_vnd(normalized_rec['tien'])})",
                    normalized_rec["tien"],
                    "SUCCESS",
                )
                st.success(
                    f"✅ Đã thêm thành công: **{normalized_rec['ten']}** | Số tiền: **{format_vnd(normalized_rec['tien'])}** (Mã GD: `{normalized_rec['id']}`)"
                )

    # --------------------------------------------------------------------------
    # TAB 2: CHẾ ĐỘ NHẬP CHUYÊN SÂU MMO (MULTI-CURRENCY, TAX/FEE, CAMPAIGN)
    # --------------------------------------------------------------------------
    with tab_pro:
        st.markdown(
            """
            <div class="mmo-glass-panel">
                <strong>💎 Trạm Nhập Giao Dịch MMO Chuyên Nghiệp:</strong> Hỗ trợ quy đổi tự động ngoại tệ
                (<code>USD</code>, <code>USDT</code>, <code>EUR</code> sang <code>VND</code>), bóc tách
                <strong>Phí cổng thanh toán / Phí chuyển đổi ngoại tệ thẻ Ads</strong> và
                <strong>Thuế nhà thầu (VAT 5% Facebook/Google/TikTok)</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a1, col_a2, col_a3 = st.columns([2, 1, 1])
        with col_a1:
            pro_ten = st.text_input(
                "Tên giao dịch / Nội dung hóa đơn MMO:",
                placeholder="VD: Thanh toán hóa đơn ngưỡng $900 Facebook Ads BM#04",
                key="pro_ten",
            )
        with col_a2:
            pro_loai = st.selectbox(
                "Loại giao dịch:",
                options=TRANSACTION_TYPES,
                key="pro_loai",
            )
        with col_a3:
            pro_trang_thai = st.selectbox(
                "Trạng thái đối soát:",
                options=TRANSACTION_STATUSES,
                key="pro_trang_thai",
            )

        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        rates_cfg = settings.get("ty_gia", DEFAULT_EXCHANGE_RATES)
        with col_b1:
            pro_loai_tien = st.selectbox(
                "Loại tiền tệ (Currency):",
                options=list(DEFAULT_EXCHANGE_RATES.keys()),
                index=0,
                key="pro_loai_tien",
            )
        with col_b2:
            default_rate = float(rates_cfg.get(pro_loai_tien, 1.0))
            pro_ty_gia = st.number_input(
                f"Tỷ giá quy đổi ({pro_loai_tien} → VND):",
                min_value=1.0,
                value=default_rate,
                step=50.0 if pro_loai_tien != "VND" else 1.0,
                key="pro_ty_gia",
            )
        with col_b3:
            step_val = 10000.0 if pro_loai_tien == "VND" else 10.0
            pro_nguyen_te = st.number_input(
                f"Số tiền nguyên tệ ({pro_loai_tien}):",
                min_value=0.0,
                value=0.0,
                step=step_val,
                key="pro_nguyen_te",
            )
        with col_b4:
            pro_ngay = st.date_input(
                "Ngày hạch toán:",
                value=datetime.now().date(),
                key="pro_ngay",
            )

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            pro_phi_pct = st.number_input(
                "Phí cổng / Chuyển đổi ngoại tệ (%):",
                min_value=0.0,
                max_value=50.0,
                value=0.0,
                step=0.5,
                key="pro_phi_pct",
            )
        with col_c2:
            pro_thue_pct = st.number_input(
                "Thuế nhà thầu / VAT Ads (%):",
                min_value=0.0,
                max_value=50.0,
                value=0.0,
                step=1.0,
                key="pro_thue_pct",
            )
        with col_c3:
            filtered_cats = (
                REVENUE_CATEGORIES
                if ("Thu nhập" in pro_loai or "Hoàn tiền" in pro_loai)
                else EXPENSE_CATEGORIES
            )
            pro_danh_muc = st.selectbox(
                "Danh mục hạch toán:",
                options=filtered_cats,
                key="pro_danh_muc",
            )
        with col_c4:
            pro_vi = st.selectbox(
                "Ví / Cổng thanh toán:",
                options=wallet_names,
                key="pro_vi",
            )

        col_d1, col_d2, col_d3 = st.columns([2, 1, 1])
        with col_d1:
            pro_chien_dich = st.selectbox(
                "Gắn kết Chiến dịch MMO (Campaign Attribution):",
                options=campaign_names,
                key="pro_chien_dich",
            )
        with col_d2:
            pro_nen_tang = st.selectbox(
                "Nền tảng (Platform):",
                options=MMO_PLATFORMS,
                key="pro_nen_tang",
            )
        with col_d3:
            pro_ma_ref = st.text_input(
                "Mã hóa đơn / TxHash / Invoice ID:",
                placeholder="VD: INV-FB-99281 / 0x89a...",
                key="pro_ma_ref",
            )

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            pro_tags = st.text_input(
                "Tags phân loại (cách nhau bởi dấu phẩy):",
                placeholder="VD: fb-ads, scale, the-8892, nutra-us",
                key="pro_tags",
            )
        with col_e2:
            pro_ghi_chu = st.text_input(
                "Ghi chú vận hành chi tiết:",
                placeholder="Ghi chú thêm về tài khoản, nhân sự phụ trách hoặc đối tác...",
                key="pro_ghi_chu",
            )

        # Tính toán Preview Hóa đơn theo thời gian thực
        base_vnd_calc = pro_nguyen_te * pro_ty_gia
        fee_vnd_calc = round(base_vnd_calc * (pro_phi_pct / 100.0), 0)
        tax_vnd_calc = round(base_vnd_calc * (pro_thue_pct / 100.0), 0)
        total_vnd_calc = round(base_vnd_calc + fee_vnd_calc + tax_vnd_calc, 0)

        st.markdown(
            f"""
            <div class="mmo-receipt-box">
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(148,163,184,0.25); padding-bottom:8px; margin-bottom:10px;">
                    <span>🧾 <strong>BẢN XEM TRƯỚC PHIẾU HẠCH TOÁN (LIVE RECEIPT PREVIEW)</strong></span>
                    <span style="color:#10B981;">{pro_loai}</span>
                </div>
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; font-size:0.86rem;">
                    <div>Giá trị gốc: <strong>{format_currency(pro_nguyen_te, pro_loai_tien)}</strong></div>
                    <div>Quy đổi cơ sở: <strong>{format_vnd(base_vnd_calc)}</strong></div>
                    <div>Phí ({pro_phi_pct}%): <strong>{format_vnd(fee_vnd_calc)}</strong> | Thuế ({pro_thue_pct}%): <strong>{format_vnd(tax_vnd_calc)}</strong></div>
                    <div style="font-size:1.05rem; color:#10B981;">TỔNG CỘNG: <strong>{format_vnd(total_vnd_calc)}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("💾 Lưu Giao Dịch MMO Chuyên Sâu", type="primary", use_container_width=True, key="btn_pro_save"):
            if not pro_ten.strip():
                st.error("❌ Vui lòng nhập Tên giao dịch / Nội dung hóa đơn!")
            elif total_vnd_calc <= 0:
                st.error("❌ Tổng giá trị giao dịch phải lớn hơn 0!")
            else:
                now_time_part = datetime.now().strftime("%H:%M:%S")
                ngay_gio_str = f"{pro_ngay.strftime('%Y-%m-%d')} {now_time_part}"
                new_rec = normalize_transaction_record(
                    {
                        "ten": pro_ten.strip(),
                        "tien": total_vnd_calc,
                        "loai": pro_loai,
                        "nguyen_te": pro_nguyen_te,
                        "loai_tien": pro_loai_tien,
                        "ty_gia": pro_ty_gia,
                        "phi_phan_tram": pro_phi_pct,
                        "thue_phan_tram": pro_thue_pct,
                        "phi_vnd": fee_vnd_calc,
                        "thue_vnd": tax_vnd_calc,
                        "danh_muc": pro_danh_muc,
                        "chien_dich": pro_chien_dich,
                        "nen_tang": pro_nen_tang,
                        "vi_thanh_toan": pro_vi,
                        "trang_thai": pro_trang_thai,
                        "ngay_gio": ngay_gio_str,
                        "ma_tham_chieu": pro_ma_ref.strip() or f"REF-{uuid.uuid4().hex[:6].upper()}",
                        "tags": pro_tags,
                        "ghi_chu": pro_ghi_chu.strip(),
                    },
                    len(ds_ct) + 1,
                )
                ds_ct.append(new_rec)
                luu_file(ds_ct)
                ghi_nhat_ky(
                    "ADD_TRANSACTION_PRO",
                    f"[{new_rec['loai']}] {new_rec['ten']} | Tổng: {format_vnd(new_rec['tien'])} ({format_currency(pro_nguyen_te, pro_loai_tien)})",
                    new_rec["tien"],
                    "SUCCESS",
                )
                st.success(
                    f"✅ Đã hạch toán giao dịch **{new_rec['id']}**: **{new_rec['ten']}** — Tổng quy đổi: **{format_vnd(new_rec['tien'])}**"
                )

    # --------------------------------------------------------------------------
    # TAB 3: MẪU GIAO DỊCH MMO NHANH 1-CLICK (QUICK TEMPLATES)
    # --------------------------------------------------------------------------
    with tab_templates:
        st.markdown(
            "Chọn một mẫu giao dịch MMO phổ biến bên dưới để ghi sổ tức thì chỉ với 1 cú nhấp chuột:"
        )
        rates_cfg = settings.get("ty_gia", DEFAULT_EXCHANGE_RATES)
        cols_tpl = st.columns(2)
        for idx, tpl in enumerate(QUICK_EXPENSE_TEMPLATES):
            with cols_tpl[idx % 2]:
                curr = tpl["loai_tien"]
                rate = float(rates_cfg.get(curr, DEFAULT_EXCHANGE_RATES.get(curr, 1.0)))
                base_v = tpl["nguyen_te"] * rate
                fee_v = base_v * (tpl["phi_phan_tram"] / 100.0)
                tax_v = base_v * (tpl["thue_phan_tram"] / 100.0)
                tot_v = round(base_v + fee_v + tax_v, 0)

                st.markdown(
                    f"""
                    <div class="mmo-glass-panel" style="margin-bottom:10px;">
                        <div style="font-weight:700; font-size:0.96rem; margin-bottom:4px;">{tpl['label']}</div>
                        <div style="font-size:0.82rem; color:#94A3B8; margin-bottom:6px;">{tpl['ten']}</div>
                        <div style="font-family:'JetBrains Mono', monospace; font-size:0.84rem; color:#10B981;">
                            Nguyên tệ: {format_currency(tpl['nguyen_te'], curr)} → <strong>{format_vnd(tot_v)}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"⚡ Áp dụng: {tpl['label']}", key=f"btn_tpl_{idx}", use_container_width=True):
                    rec = normalize_transaction_record(
                        {
                            "ten": tpl["ten"],
                            "tien": tot_v,
                            "loai": tpl["loai"],
                            "nguyen_te": tpl["nguyen_te"],
                            "loai_tien": curr,
                            "ty_gia": rate,
                            "phi_phan_tram": tpl["phi_phan_tram"],
                            "thue_phan_tram": tpl["thue_phan_tram"],
                            "phi_vnd": round(fee_v, 0),
                            "thue_vnd": round(tax_v, 0),
                            "danh_muc": tpl["danh_muc"],
                            "vi_thanh_toan": tpl["vi_thanh_toan"],
                            "tags": tpl["tags"],
                            "ghi_chu": tpl["ghi_chu"],
                        },
                        len(ds_ct) + 1,
                    )
                    ds_ct.append(rec)
                    luu_file(ds_ct)
                    ghi_nhat_ky(
                        "ADD_TEMPLATE_TX",
                        f"Áp dụng mẫu nhanh: {rec['ten']} ({format_vnd(rec['tien'])})",
                        rec["tien"],
                        "INFO",
                    )
                    st.success(f"✅ Đã thêm nhanh khoản giao dịch mẫu: **{rec['ten']}** ({format_vnd(rec['tien'])})")

    # --------------------------------------------------------------------------
    # TAB 4: NHẬP HÀNG LOẠT (BATCH ENTRY)
    # --------------------------------------------------------------------------
    with tab_batch:
        st.markdown(
            """
            <div class="mmo-glass-panel">
                <strong>📥 Nhập Hàng Loạt Từ Sao Kê / Excel (Mỗi dòng 1 khoản giao dịch):</strong><br/>
                Cú pháp mỗi dòng: <code>Tên khoản chi | Số tiền VNĐ | Danh mục (tuỳ chọn) | Ví (tuỳ chọn)</code>
            </div>
            """,
            unsafe_allow_html=True,
        )
        sample_batch_text = (
            "Mua 10 VIA Cổ US XMDT | 2500000 | Mua VIA / BM / Tài khoản Ads | Vietcombank (VND)\n"
            "Nạp Proxy 922 S5 200 IPs | 1250000 | Proxy / IP Dân cư / 4G | Binance Pay / Ví USDT (TRC20/BEP20)\n"
            "Thanh toán bill Facebook Ads TK#09 | 5400000 | Quảng cáo Facebook Ads | Techcombank / Thẻ Visa Ads (VND)"
        )
        batch_input = st.text_area(
            "Dán danh sách các khoản chi tiêu vào đây:",
            value=sample_batch_text,
            height=150,
            key="batch_textarea",
        )
        if st.button("🚀 Xử Lý & Lưu Toàn Bộ Danh Sách Hàng Loạt", type="primary", key="btn_batch_save"):
            lines = [line.strip() for line in batch_input.splitlines() if line.strip()]
            added_count = 0
            total_batch_vnd = 0.0
            for line in lines:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2:
                    b_ten = parts[0]
                    try:
                        b_tien = float(parts[1].replace(",", "").replace("đ", "").strip())
                    except ValueError:
                        continue
                    if b_ten and b_tien > 0:
                        b_cat = parts[2] if len(parts) >= 3 and parts[2] else ""
                        b_wallet = parts[3] if len(parts) >= 4 and parts[3] else "Vietcombank (VND)"
                        rec = normalize_transaction_record(
                            {
                                "ten": b_ten,
                                "tien": b_tien,
                                "danh_muc": b_cat,
                                "vi_thanh_toan": b_wallet,
                            },
                            len(ds_ct) + 1,
                        )
                        ds_ct.append(rec)
                        added_count += 1
                        total_batch_vnd += b_tien
            if added_count > 0:
                luu_file(ds_ct)
                ghi_nhat_ky(
                    "BATCH_IMPORT",
                    f"Nhập hàng loạt {added_count} khoản chi, tổng {format_vnd(total_batch_vnd)}",
                    total_batch_vnd,
                    "SUCCESS",
                )
                st.success(
                    f"✅ Đã nhập hàng loạt thành công **{added_count}** khoản giao dịch | Tổng cộng: **{format_vnd(total_batch_vnd)}**"
                )
            else:
                st.warning("⚠️ Không tìm thấy dòng dữ liệu hợp lệ nào. Hãy kiểm tra lại cú pháp `Tên | Số tiền`!")


# ==============================================================================
# 8. MODULE 2: XEM TOÀN BỘ DANH SÁCH, SỔ CÁI ĐA CHIỀU & TỔNG TIỀN (NÂNG CẤP MỤC 2)
# ==============================================================================

def render_module_view_ledger(ds_ct: List[Dict[str, Any]], stats: Dict[str, Any]) -> None:
    """
    Nâng cấp toàn diện Mục 2: ' 2. Xem toàn bộ danh sách & tổng tiền'
    - Bao gồm cả chế độ hiển thị chuẩn gốc (`st.table`, danh sách đánh số `1. Mục: ... | Số tiền: ...` và `st.metric(label="Tổng số tiền")`).
    - Mở rộng thành Sổ Cái Tài Chính Đa Chiều (DataGrid Pro) với bộ lọc thông minh theo
      Từ khóa, Loại giao dịch, Danh mục, Chiến dịch, Ví thanh toán, Khoảng tiền, Sắp xếp & Xuất CSV/JSON/HTML.
    """
    render_section_header(
        "📋 SỔ CÁI TOÀN BỘ DANH SÁCH GIAO DỊCH & ĐỐI SOÁT TỔNG TIỀN",
        "MODULE 02 • GENERAL LEDGER & EXPLORER",
    )

    if len(ds_ct) == 0:
        st.warning("Danh sách trống! Bạn có thể thêm khoản chi mới hoặc nạp dữ liệu mẫu MMO bên dưới.")
        if st.button("🚀 Nạp Ngay Bộ Dữ Liệu Mẫu MMO Thực Tế (12 Giao Dịch)", type="primary"):
            count = seed_mmo_enterprise_data(append_mode=True)
            st.success(f"Đã nạp {count} giao dịch mẫu MMO! Hãy tải lại hoặc chuyển tab để xem.")
            st.rerun()
        return

    # Hàng thẻ KPI Tổng hợp nhanh
    kpi_html = f"""
    <div class="mmo-kpi-grid">
        {render_kpi_card_html("Tổng Giá Trị Sổ Cái (All Records)", format_vnd(stats['tong_tat_ca']), f"{stats['so_giao_dich']} bản ghi hạch toán", "neutral", "📚")}
        {render_kpi_card_html("Tổng Chi Tiêu Vận Hành", format_vnd(stats['tong_chi']), f"{stats['so_giao_dich_chi']} khoản chi • TB: {format_vnd(stats['trung_binh_khoan_chi'])}", "down", "🔥")}
        {render_kpi_card_html("Tổng Doanh Thu & Payout", format_vnd(stats['tong_thu_thuc_te']), f"{stats['so_giao_dich_thu']} khoản thu & cashback", "up", "💰")}
        {render_kpi_card_html("Lợi Nhuận Ròng (Net P&L)", format_vnd(stats['loi_nhuan_rong']), f"ROAS: {stats['roas_chung']:.2f}x | Margin: {stats['ty_suat_loi_nhuan']:.1f}%", "up" if stats['loi_nhuan_rong'] >= 0 else "down", "💎")}
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    # Bộ lọc đa chiều chuyên sâu
    with st.expander("🔍 BỘ LỌC ĐA CHIỀU, TÌM KIẾM & SẮP XẾP SỔ CÁI (ADVANCED FILTER)", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.2, 1.4, 1.4])
        with f_col1:
            tu_khoa = st.text_input(
                "Tìm kiếm theo Tên, Mã GD, Tags, Ghi chú:",
                placeholder="Gõ từ khóa (VD: Facebook, VIA, Proxy, ClickBank...)",
                key="ledger_search_kw",
            )
        with f_col2:
            loc_loai = st.multiselect(
                "Loại giao dịch:",
                options=TRANSACTION_TYPES,
                default=[],
                key="ledger_filter_type",
            )
        with f_col3:
            all_cats_in_data = sorted(list({str(x.get("danh_muc", "Khác")) for x in ds_ct}))
            loc_danh_muc = st.multiselect(
                "Danh mục:",
                options=all_cats_in_data,
                default=[],
                key="ledger_filter_cat",
            )
        with f_col4:
            all_wallets_in_data = sorted(list({str(x.get("vi_thanh_toan", "Khác")) for x in ds_ct}))
            loc_vi = st.multiselect(
                "Ví thanh toán:",
                options=all_wallets_in_data,
                default=[],
                key="ledger_filter_wallet",
            )

        f_col5, f_col6, f_col7, f_col8 = st.columns(4)
        max_tien_val = max([float(x.get("tien", 0)) for x in ds_ct] + [1000000.0])
        with f_col5:
            min_tien = st.number_input("Số tiền tối thiểu (VNĐ):", min_value=0.0, value=0.0, step=100000.0)
        with f_col6:
            max_tien = st.number_input("Số tiền tối đa (VNĐ):", min_value=0.0, value=float(max_tien_val), step=500000.0)
        with f_col7:
            sap_xep_theo = st.selectbox(
                "Sắp xếp theo:",
                options=[
                    "STT gốc (Mặc định)",
                    "Số tiền: Cao → Thấp",
                    "Số tiền: Thấp → Cao",
                    "Thời gian: Mới nhất → Cũ nhất",
                    "Thời gian: Cũ nhất → Mới nhất",
                ],
                key="ledger_sort_by",
            )
        with f_col8:
            che_do_xem = st.selectbox(
                "Chế độ hiển thị:",
                options=[
                    "Bảng Chuyên Nghiệp + Danh sách gốc",
                    "Chỉ Bảng Sổ Cái MMO (DataGrid)",
                    "Chỉ Giao Diện Cổ Điển Gốc (st.table)",
                ],
                key="ledger_view_mode",
            )

    # Thực thi lọc dữ liệu
    filtered_list: List[Tuple[int, Dict[str, Any]]] = []
    for stt, item in enumerate(ds_ct, start=1):
        tien_val = float(item.get("tien", 0.0))
        if tien_val < min_tien or tien_val > max_tien:
            continue
        if loc_loai and item.get("loai") not in loc_loai:
            continue
        if loc_danh_muc and item.get("danh_muc") not in loc_danh_muc:
            continue
        if loc_vi and item.get("vi_thanh_toan") not in loc_vi:
            continue
        if tu_khoa.strip():
            kw = tu_khoa.strip().lower()
            searchable = " ".join([
                str(item.get("id", "")),
                str(item.get("ten", "")),
                str(item.get("danh_muc", "")),
                str(item.get("chien_dich", "")),
                str(item.get("vi_thanh_toan", "")),
                str(item.get("ghi_chu", "")),
                " ".join(item.get("tags", [])),
            ]).lower()
            if kw not in searchable:
                continue
        filtered_list.append((stt, item))

    # Thực thi sắp xếp
    if sap_xep_theo == "Số tiền: Cao → Thấp":
        filtered_list.sort(key=lambda x: float(x[1].get("tien", 0)), reverse=True)
    elif sap_xep_theo == "Số tiền: Thấp → Cao":
        filtered_list.sort(key=lambda x: float(x[1].get("tien", 0)))
    elif sap_xep_theo == "Thời gian: Mới nhất → Cũ nhất":
        filtered_list.sort(key=lambda x: str(x[1].get("ngay_gio", "")), reverse=True)
    elif sap_xep_theo == "Thời gian: Cũ nhất → Mới nhất":
        filtered_list.sort(key=lambda x: str(x[1].get("ngay_gio", "")))

    # Hiển thị bảng DataGrid Chuyên nghiệp
    if "Bảng Chuyên Nghiệp" in che_do_xem or "Chỉ Bảng Sổ Cái" in che_do_xem:
        st.subheader(f"📊 Bảng Sổ Cái Chi Tiết ({len(filtered_list)}/{len(ds_ct)} khoản phù hợp)")
        if filtered_list:
            df_rows = []
            for stt_goc, item in filtered_list:
                df_rows.append({
                    "Vị trí (STT)": stt_goc,
                    "Mã GD": item.get("id", ""),
                    "Ngày": item.get("ngay", ""),
                    "Loại": item.get("loai", ""),
                    "Tên khoản chi / Nội dung": item.get("ten", ""),
                    "Danh mục": item.get("danh_muc", ""),
                    "Chiến dịch MMO": item.get("chien_dich", ""),
                    "Ví thanh toán": item.get("vi_thanh_toan", ""),
                    "Nguyên tệ": format_currency(item.get("nguyen_te", 0), item.get("loai_tien", "VND")),
                    "Tổng VNĐ (tien)": float(item.get("tien", 0)),
                    "Trạng thái": item.get("trang_thai", ""),
                })
            df_display = pd.DataFrame(df_rows)
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Tổng VNĐ (tien)": st.column_config.NumberColumn(
                        "Số tiền (VNĐ)",
                        format="%d đ",
                    )
                },
            )
        else:
            st.info("Không có bản ghi nào khớp với bộ lọc hiện tại.")

    # Hiển thị theo chuẩn gốc của người dùng (st.table + danh sách stt + st.metric("Tổng số tiền"))
    if "Bảng Chuyên Nghiệp" in che_do_xem or "Cổ Điển Gốc" in che_do_xem:
        with st.expander("📜 Chế Độ Hiển Thị Danh Sách & Tổng Tiền Chuẩn Gốc", expanded=("Cổ Điển" in che_do_xem)):
            bang_rut_gon = [
                {"STT": stt, "ten": item["ten"], "tien": f"{int(item['tien']):,}đ", "danh_muc": item.get("danh_muc", "")}
                for stt, item in filtered_list
            ]
            st.table(bang_rut_gon)
            tong = 0
            for stt, i in filtered_list:
                tong += int(i["tien"])
                st.write(
                    f"**{stt}.** Mục: **{i['ten']}** | Số tiền: **{int(i['tien']):,}đ** "
                    f"| _({i.get('danh_muc', 'Khác')} - {i.get('vi_thanh_toan', '')})_"
                )
            st.metric(label="Tổng số tiền", value=f"{tong:,}đ")

    # Thanh công cụ Xuất dữ liệu (CSV, JSON, Báo cáo HTML)
    st.markdown("### 📤 Xuất Báo Cáo & Tải Xuống Sổ Cái (Export Center)")
    ex_col1, ex_col2, ex_col3 = st.columns(3)

    with ex_col1:
        json_bytes = json.dumps(ds_ct, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            label="📥 Tải xuống File gốc `so_hoan_chinh.json`",
            data=json_bytes,
            file_name="so_hoan_chinh.json",
            mime="application/json",
            use_container_width=True,
        )

    with ex_col2:
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["STT", "ID", "Ngay", "Loai", "Ten", "Danh_Muc", "Chien_Dich", "Vi", "Nguyen_Te", "Loai_Tien", "Tong_VND"])
        for stt_goc, item in filtered_list:
            writer.writerow([
                stt_goc,
                item.get("id", ""),
                item.get("ngay", ""),
                item.get("loai", ""),
                item.get("ten", ""),
                item.get("danh_muc", ""),
                item.get("chien_dich", ""),
                item.get("vi_thanh_toan", ""),
                item.get("nguyen_te", 0),
                item.get("loai_tien", "VND"),
                int(item.get("tien", 0)),
            ])
        st.download_button(
            label="📊 Xuất Bảng Sổ Cái ra Excel / CSV",
            data=csv_buffer.getvalue().encode("utf-8-sig"),
            file_name=f"so_cai_mmo_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with ex_col3:
        html_report = xuat_bao_cao_html_chuyen_nghiep([x[1] for x in filtered_list], stats)
        st.download_button(
            label="🖨️ Xuất Báo Cáo Tài Chính HTML (Chuẩn In PDF)",
            data=html_report.encode("utf-8"),
            file_name=f"bao_cao_mmo_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True,
        )


# ==============================================================================
# 9. MODULE 3: XOÁ KHOẢN CHI TIÊU, THÙNG RÁC & DỌN DẸP (NÂNG CẤP MỤC 3)
# ==============================================================================

def render_module_delete_transaction(ds_ct: List[Dict[str, Any]]) -> None:
    """
    Nâng cấp toàn diện Mục 3: ' 3. Xoá khoản chi tiêu'
    - Giữ nguyên thao tác xoá theo Số vị trí (STT từ 1..N) như code gốc của người dùng,
      nhưng có hiển thị Thẻ Xem Trước (Preview Card) để tránh xoá nhầm!
    - Tự động chuyển khoản bị xoá vào Thùng Rác (`mmo_trash.json`) để có thể Khôi Phục (Undo/Restore) 1-Click.
    - Bổ sung tính năng Xoá Hàng Loạt (Batch Delete) và Quét Giao Dịch Trùng Lặp (Duplicate Cleaner).
    """
    render_section_header(
        "🗑️ XOÁ KHOẢN CHI TIÊU, THÙNG RÁC KHÔI PHỤC & DỌN DẸP DỮ LIỆU",
        "MODULE 03 • SAFE DELETE & RECYCLE BIN",
    )

    trash_list = doc_thung_rac()

    tab_del_single, tab_del_batch, tab_recycle_bin, tab_dedup = st.tabs([
        "🎯 Xoá Theo Vị Trí STT (Chuẩn Gốc + An Toàn)",
        "🧹 Xoá Hàng Loạt (Batch Delete)",
        f"♻️ Thùng Rác Khôi Phục ({len(trash_list)})",
        "🔍 Quét & Dọn Giao Dịch Trùng Lặp",
    ])

    # --------------------------------------------------------------------------
    # TAB 1: XOÁ THEO VỊ TRÍ STT (CHUẨN GỐC CỦA NGƯỜI DÙNG + XEM TRƯỚC)
    # --------------------------------------------------------------------------
    with tab_del_single:
        if len(ds_ct) == 0:
            st.warning("Danh sách trống không có gì để xóa!")
        else:
            st.markdown(
                f"Hiện đang có **{len(ds_ct)}** khoản chi tiêu trong sổ cái (Vị trí hợp lệ từ **1** đến **{len(ds_ct)}**)."
            )
            col_d1, col_d2 = st.columns([1, 2])
            with col_d1:
                vi_tri_nhap = int(
                    st.number_input(
                        "Hãy nhập số vị trí muốn xoá: ",
                        min_value=1,
                        max_value=max(len(ds_ct), 1),
                        value=1,
                        step=1,
                        key="del_stt_input",
                    )
                )
                xoa = vi_tri_nhap - 1
                luu_vao_thung_rac = st.checkbox(
                    "Chuyển vào Thùng rác để có thể khôi phục lại khi cần",
                    value=True,
                    key="chk_soft_delete",
                )

            with col_d2:
                if 0 <= xoa < len(ds_ct):
                    target_item = ds_ct[xoa]
                    st.markdown(
                        f"""
                        <div class="mmo-receipt-box" style="border-color:#EF4444;">
                            <div style="color:#EF4444; font-weight:700; margin-bottom:6px;">
                                ⚠️ XEM TRƯỚC KHOẢN SẼ XOÁ (VỊ TRÍ #{vi_tri_nhap} • MÃ: {target_item.get('id', '')})
                            </div>
                            <div><strong>Tên khoản chi:</strong> {target_item.get('ten', '')}</div>
                            <div><strong>Số tiền:</strong> <span style="color:#10B981; font-weight:700;">{format_vnd(target_item.get('tien', 0))}</span></div>
                            <div><strong>Danh mục:</strong> {target_item.get('danh_muc', '')} | <strong>Ví:</strong> {target_item.get('vi_thanh_toan', '')}</div>
                            <div><strong>Thời gian:</strong> {target_item.get('ngay_gio', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning("Vị trí không tồn tại!")

            if st.button("Xác nhận xoá", type="primary", use_container_width=True, key="btn_confirm_delete"):
                if 0 <= xoa < len(ds_ct):
                    removed_item = ds_ct.pop(xoa)
                    luu_file(ds_ct)
                    if luu_vao_thung_rac:
                        removed_item["thoi_gian_xoa"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        trash_list.insert(0, removed_item)
                        luu_thung_rac(trash_list)
                    ghi_nhat_ky(
                        "DELETE_TRANSACTION",
                        f"Đã xoá vị trí #{vi_tri_nhap}: {removed_item.get('ten')} ({format_vnd(removed_item.get('tien', 0))})",
                        float(removed_item.get("tien", 0)),
                        "WARNING",
                    )
                    st.success(
                        f"✅ Đã xoá xong khoản chi vị trí #{vi_tri_nhap}: **{removed_item.get('ten')}** ({format_vnd(removed_item.get('tien', 0))})!"
                    )
                else:
                    st.warning("Vị trí không tồn tại!")

    # --------------------------------------------------------------------------
    # TAB 2: XOÁ HÀNG LOẠT (BATCH DELETE)
    # --------------------------------------------------------------------------
    with tab_del_batch:
        if len(ds_ct) == 0:
            st.info("Danh sách đang trống.")
        else:
            options_map = {
                f"#{idx + 1} [{item.get('id')}] {item.get('ten')} — {format_vnd(item.get('tien', 0))}": idx
                for idx, item in enumerate(ds_ct)
            }
            selected_labels = st.multiselect(
                "Chọn các khoản giao dịch muốn xoá cùng lúc:",
                options=list(options_map.keys()),
                key="batch_del_multiselect",
            )
            if st.button("🗑️ Xoá Tất Cả Các Khoản Đã Chọn", type="primary", key="btn_batch_del_exec"):
                if not selected_labels:
                    st.warning("Vui lòng chọn ít nhất 1 khoản giao dịch để xoá!")
                else:
                    indices_to_remove = sorted([options_map[lbl] for lbl in selected_labels], reverse=True)
                    total_removed_val = 0.0
                    for i_rem in indices_to_remove:
                        rem = ds_ct.pop(i_rem)
                        total_removed_val += float(rem.get("tien", 0))
                        rem["thoi_gian_xoa"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        trash_list.insert(0, rem)
                    luu_file(ds_ct)
                    luu_thung_rac(trash_list)
                    ghi_nhat_ky(
                        "BATCH_DELETE",
                        f"Xoá hàng loạt {len(indices_to_remove)} khoản, tổng {format_vnd(total_removed_val)}",
                        total_removed_val,
                        "WARNING",
                    )
                    st.success(f"✅ Đã xoá {len(indices_to_remove)} khoản giao dịch và lưu bản sao vào Thùng rác!")
                    st.rerun()

    # --------------------------------------------------------------------------
    # TAB 3: THÙNG RÁC & KHÔI PHỤC (RECYCLE BIN)
    # --------------------------------------------------------------------------
    with tab_recycle_bin:
        if len(trash_list) == 0:
            st.info("🎉 Thùng rác hiện đang trống.")
        else:
            st.markdown(f"Đang lưu giữ **{len(trash_list)}** khoản giao dịch đã xoá gần đây:")
            for t_idx, t_item in enumerate(trash_list):
                c_t1, c_t2, c_t3 = st.columns([4, 1.2, 1.2])
                with c_t1:
                    st.write(
                        f"**{t_idx + 1}. [{t_item.get('id', '')}] {t_item.get('ten', '')}** — "
                        f"**{format_vnd(t_item.get('tien', 0))}** | _Xoá lúc: {t_item.get('thoi_gian_xoa', 'N/A')}_"
                    )
                with c_t2:
                    if st.button("♻️ Khôi phục", key=f"restore_btn_{t_idx}", use_container_width=True):
                        restored = trash_list.pop(t_idx)
                        restored.pop("thoi_gian_xoa", None)
                        ds_ct.append(normalize_transaction_record(restored, len(ds_ct) + 1))
                        luu_file(ds_ct)
                        luu_thung_rac(trash_list)
                        ghi_nhat_ky(
                            "RESTORE_TRANSACTION",
                            f"Khôi phục từ thùng rác: {restored.get('ten')}",
                            float(restored.get("tien", 0)),
                            "INFO",
                        )
                        st.success(f"Đã khôi phục khoản: **{restored.get('ten')}**!")
                        st.rerun()
                with c_t3:
                    if st.button("❌ Xoá vĩnh viễn", key=f"perm_del_btn_{t_idx}", use_container_width=True):
                        trash_list.pop(t_idx)
                        luu_thung_rac(trash_list)
                        st.rerun()

            if st.button("🔥 Dọn Sạch Toàn Bộ Thùng Rác", key="btn_empty_trash"):
                luu_thung_rac([])
                st.success("Đã dọn sạch thùng rác!")
                st.rerun()

    # --------------------------------------------------------------------------
    # TAB 4: QUÉT GIAO DỊCH TRÙNG LẶP (DUPLICATE DETECTOR)
    # --------------------------------------------------------------------------
    with tab_dedup:
        seen_keys: Dict[Tuple[str, float, str], List[int]] = defaultdict(list)
        for idx, item in enumerate(ds_ct):
            key = (
                str(item.get("ten", "")).strip().lower(),
                float(item.get("tien", 0)),
                str(item.get("ngay", "")),
            )
            seen_keys[key].append(idx)

        duplicates = {k: v for k, v in seen_keys.items() if len(v) > 1}
        if not duplicates:
            st.success("✅ Sổ cái hoàn toàn sạch sẽ! Không phát hiện giao dịch nào bị trùng lặp (cùng Tên, Số tiền và Ngày).")
        else:
            st.warning(f"⚠️ Phát hiện **{len(duplicates)}** nhóm giao dịch có dấu hiệu trùng lặp:")
            for (d_ten, d_tien, d_ngay), idx_list in duplicates.items():
                st.write(
                    f"- **{d_ten}** ({format_vnd(d_tien)} ngày `{d_ngay}`) xuất hiện tại các vị trí STT: "
                    f"**{', '.join(str(i + 1) for i in idx_list)}**"
                )
            if st.button("✨ Tự Động Loại Bỏ Các Bản Ghi Trùng (Chỉ Giữ Lại 1 Bản Gốc)", type="primary"):
                to_remove = []
                for idx_list in duplicates.values():
                    to_remove.extend(idx_list[1:])
                for i_rem in sorted(to_remove, reverse=True):
                    rem = ds_ct.pop(i_rem)
                    trash_list.insert(0, rem)
                luu_file(ds_ct)
                luu_thung_rac(trash_list)
                st.success(f"Đã dọn dẹp {len(to_remove)} bản ghi trùng lặp và chuyển vào Thùng rác!")
                st.rerun()


# ==============================================================================
# 10. MODULE 4: SỬA KHOẢN CHI TIÊU & LỊCH SỬ PHIÊN BẢN (NÂNG CẤP MỤC 4)
# ==============================================================================

def render_module_edit_transaction(
    ds_ct: List[Dict[str, Any]],
    campaigns: List[Dict[str, Any]],
    wallets: List[Dict[str, Any]],
) -> None:
    """
    Nâng cấp toàn diện Mục 4: ' 4. Sửa khoản chi tiêu'
    - Giữ nguyên thao tác sửa theo vị trí STT (`Nhập vị trí sửa`, `Hãy nhập tên mới`, `Hãy nhập số tiền`, `Xác nhận sửa`).
    - Tự động điền sẵn (Pre-fill) dữ liệu hiện tại của vị trí đó để người dùng không phải gõ lại từ đầu.
    - Lưu lại Lịch sử chỉnh sửa (Revision History) ngay trong bản ghi và hiển thị bảng So sánh Trước / Sau (Diff Preview).
    """
    render_section_header(
        "✏️ SỬA KHOẢN CHI TIÊU, CẬP NHẬT THÔNG TIN & LỊCH SỬ PHIÊN BẢN",
        "MODULE 04 • SMART EDITOR & VERSION DIFF",
    )

    if len(ds_ct) == 0:
        st.warning("Danh sách trống không có gì để sửa!")
        return

    tab_edit_single, tab_edit_bulk = st.tabs([
        "✏️ Sửa Chi Tiết Theo Vị Trí STT (Chuẩn Gốc + Nâng Cao)",
        "⚡ Cập Nhật Hàng Loạt Danh Mục / Chiến Dịch (Bulk Update)",
    ])

    campaign_names = ["Vận hành chung / Nội bộ"] + [
        c.get("ten_cd", "") for c in campaigns if c.get("ten_cd")
    ]
    wallet_names = [w.get("ten_vi", "") for w in wallets if w.get("ten_vi")] or DEFAULT_PAYMENT_METHODS

    with tab_edit_single:
        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            vi_tri_sua = int(
                st.number_input(
                    "Nhập vị trí sửa: ",
                    min_value=1,
                    max_value=max(len(ds_ct), 1),
                    value=1,
                    step=1,
                    key="edit_stt_input",
                )
            )
            sua = vi_tri_sua - 1

        if 0 <= sua < len(ds_ct):
            current_item = ds_ct[sua]
            with col_sel2:
                st.markdown(
                    f"""
                    <div class="mmo-glass-panel">
                        <strong>📌 Đang chọn Vị trí #{vi_tri_sua} (Mã GD: <code>{current_item.get('id')}</code>)</strong><br/>
                        Nội dung hiện tại: <strong>{current_item.get('ten')}</strong> |
                        Số tiền hiện tại: <strong style="color:#10B981;">{format_vnd(current_item.get('tien', 0))}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            e_col1, e_col2 = st.columns(2)
            with e_col1:
                ten_moi = st.text_input(
                    "Hãy nhập tên mới: ",
                    value=str(current_item.get("ten", "")),
                    key=f"edit_ten_{sua}",
                )
                cur_cat = str(current_item.get("danh_muc", EXPENSE_CATEGORIES[0]))
                cat_options = ALL_CATEGORIES if cur_cat in ALL_CATEGORIES else [cur_cat] + ALL_CATEGORIES
                danh_muc_moi = st.selectbox(
                    "Danh mục hạch toán:",
                    options=cat_options,
                    index=cat_options.index(cur_cat),
                    key=f"edit_cat_{sua}",
                )
                cur_camp = str(current_item.get("chien_dich", "Vận hành chung / Nội bộ"))
                camp_opts = campaign_names if cur_camp in campaign_names else [cur_camp] + campaign_names
                chien_dich_moi = st.selectbox(
                    "Chiến dịch MMO:",
                    options=camp_opts,
                    index=camp_opts.index(cur_camp),
                    key=f"edit_camp_{sua}",
                )

            with e_col2:
                tien_moi = st.number_input(
                    "Hãy nhập số tiền: ",
                    min_value=0,
                    value=int(float(current_item.get("tien", 0))),
                    step=1000,
                    key=f"edit_tien_{sua}",
                )
                cur_wal = str(current_item.get("vi_thanh_toan", wallet_names[0]))
                wal_opts = wallet_names if cur_wal in wallet_names else [cur_wal] + wallet_names
                vi_moi = st.selectbox(
                    "Ví thanh toán:",
                    options=wal_opts,
                    index=wal_opts.index(cur_wal),
                    key=f"edit_wal_{sua}",
                )
                ghi_chu_moi = st.text_input(
                    "Ghi chú bổ sung:",
                    value=str(current_item.get("ghi_chu", "")),
                    key=f"edit_note_{sua}",
                )

            # Bảng đối chiếu Trước & Sau khi sửa (Diff Preview)
            chenh_lech = float(tien_moi) - float(current_item.get("tien", 0))
            st.markdown(
                f"""
                <div class="mmo-receipt-box">
                    <div style="font-weight:700; color:#38BDF8; margin-bottom:6px;">
                        🔍 SO SÁNH THAY ĐỔI TRƯỚC & SAU KHI SỬA (DIFF PREVIEW)
                    </div>
                    <div>• Tên khoản chi: <code>{current_item.get('ten')}</code> ➔ <strong>{ten_moi}</strong></div>
                    <div>• Số tiền: <code>{format_vnd(current_item.get('tien', 0))}</code> ➔ <strong style="color:#10B981;">{format_vnd(tien_moi)}</strong> (Chênh lệch: {chenh_lech:+,.0f}đ)</div>
                    <div>• Danh mục: <code>{current_item.get('danh_muc')}</code> ➔ <strong>{danh_muc_moi}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Xác nhận sửa", type="primary", use_container_width=True, key="btn_confirm_edit"):
                if not ten_moi.strip():
                    st.warning("⚠️ Tên khoản chi không được để trống!")
                else:
                    old_snapshot = {
                        "thoi_gian_sua": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ten_cu": current_item.get("ten"),
                        "tien_cu": current_item.get("tien"),
                        "danh_muc_cu": current_item.get("danh_muc"),
                    }
                    lich_su = current_item.get("lich_su_sua", [])
                    if not isinstance(lich_su, list):
                        lich_su = []
                    lich_su.append(old_snapshot)

                    ds_ct[sua]["ten"] = ten_moi.strip()
                    ds_ct[sua]["tien"] = float(tien_moi)
                    ds_ct[sua]["nguyen_te"] = float(tien_moi) if ds_ct[sua].get("loai_tien", "VND") == "VND" else ds_ct[sua].get("nguyen_te", float(tien_moi))
                    ds_ct[sua]["danh_muc"] = danh_muc_moi
                    ds_ct[sua]["chien_dich"] = chien_dich_moi
                    ds_ct[sua]["vi_thanh_toan"] = vi_moi
                    ds_ct[sua]["ghi_chu"] = ghi_chu_moi
                    ds_ct[sua]["lich_su_sua"] = lich_su

                    luu_file(ds_ct)
                    ghi_nhat_ky(
                        "EDIT_TRANSACTION",
                        f"Sửa vị trí #{vi_tri_sua}: '{old_snapshot['ten_cu']}' ({format_vnd(old_snapshot['tien_cu'])}) -> '{ten_moi}' ({format_vnd(tien_moi)})",
                        float(tien_moi),
                        "INFO",
                    )
                    st.success(f"✅ Đã sửa thành công vị trí #{vi_tri_sua}!")

            # Hiển thị lịch sử các lần chỉnh sửa trước của khoản này (nếu có)
            if current_item.get("lich_su_sua"):
                with st.expander(f"🕒 Xem lịch sử {len(current_item['lich_su_sua'])} lần chỉnh sửa của khoản này"):
                    st.table(current_item["lich_su_sua"])
        else:
            st.warning("Vị trí không tồn tại!")

    with tab_edit_bulk:
        st.markdown("Chọn nhiều khoản giao dịch để chuyển đổi Danh mục hoặc Chiến dịch MMO cùng lúc:")
        bulk_opts = {
            f"#{i + 1} - {x.get('ten')} ({format_vnd(x.get('tien', 0))})": i
            for i, x in enumerate(ds_ct)
        }
        chosen_bulk = st.multiselect("Chọn các khoản cần cập nhật:", options=list(bulk_opts.keys()))
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            new_bulk_cat = st.selectbox("Đổi sang Danh mục:", options=["(Giữ nguyên)"] + ALL_CATEGORIES)
        with b_col2:
            new_bulk_camp = st.selectbox("Đổi sang Chiến dịch:", options=["(Giữ nguyên)"] + campaign_names)

        if st.button("⚡ Áp Dụng Cập Nhật Hàng Loạt", type="primary"):
            if not chosen_bulk:
                st.warning("Vui lòng chọn ít nhất 1 bản ghi!")
            else:
                for lbl in chosen_bulk:
                    idx_b = bulk_opts[lbl]
                    if new_bulk_cat != "(Giữ nguyên)":
                        ds_ct[idx_b]["danh_muc"] = new_bulk_cat
                    if new_bulk_camp != "(Giữ nguyên)":
                        ds_ct[idx_b]["chien_dich"] = new_bulk_camp
                luu_file(ds_ct)
                ghi_nhat_ky("BULK_EDIT", f"Cập nhật hàng loạt {len(chosen_bulk)} bản ghi", 0, "INFO")
                st.success(f"✅ Đã cập nhật hàng loạt {len(chosen_bulk)} khoản giao dịch!")
                st.rerun()


# ==============================================================================
# 11. MODULE 5: MMO COMMAND CENTER — DASHBOARD TỔNG QUAN & PHÂN TÍCH DÒNG TIỀN
# ==============================================================================

def render_module_dashboard(
    ds_ct: List[Dict[str, Any]],
    stats: Dict[str, Any],
    campaigns: List[Dict[str, Any]],
    wallets: List[Dict[str, Any]],
    subs: List[Dict[str, Any]],
) -> None:
    """
    Trung tâm Chỉ huy Tài chính MMO (Executive Command Center):
    - 8 KPI Cards thời gian thực (Tổng thu, Tổng chi, Lợi nhuận ròng, ROAS, Burn Rate, Thuế/Phí, Sức khỏe tài chính).
    - Biểu đồ Xu hướng Dòng tiền theo ngày (Thu vs Chi vs Lợi nhuận lũy kế).
    - Phân bổ Chi tiêu theo Danh mục MMO & Ví thanh toán.
    - Bảng Xếp hạng Chiến dịch ROAS cao nhất & Cảnh báo Giao dịch Bất thường (Anomaly Detection).
    """
    render_section_header(
        "📊 MMO COMMAND CENTER — BẢNG ĐIỀU KHIỂN TÀI CHÍNH & HIỆU SUẤT ADS",
        "MODULE 05 • EXECUTIVE ANALYTICS",
    )

    if len(ds_ct) == 0:
        st.info("💡 Chưa có dữ liệu giao dịch trong `so_hoan_chinh.json`. Hãy nhấn nút bên dưới để khởi tạo dữ liệu mẫu MMO chuyên nghiệp!")
        if st.button("🚀 Khởi Tạo Ngay Bộ Dữ Liệu Mẫu MMO Enterprise (12 Giao Dịch)", type="primary", key="dash_seed_btn"):
            seed_mmo_enterprise_data(append_mode=True)
            st.rerun()
        return

    # 8 Thẻ KPI Chuyên sâu chia làm 2 hàng
    grid_row1 = f"""
    <div class="mmo-kpi-grid">
        {render_kpi_card_html("Tổng Doanh Thu & Payout", format_vnd(stats['tong_thu_thuc_te']), f"Gồm {format_vnd(stats['tong_hoan_tien'])} Cashback", "up", "💰")}
        {render_kpi_card_html("Tổng Chi Tiêu Vận Hành", format_vnd(stats['tong_chi']), f"{stats['so_giao_dich_chi']} lệnh chi • Max: {format_vnd(stats['max_khoan_chi'])}", "down", "🔥")}
        {render_kpi_card_html("Lợi Nhuận Ròng (Net Profit)", format_vnd(stats['loi_nhuan_rong']), f"Biên lợi nhuận: {stats['ty_suat_loi_nhuan']:.1f}%", "up" if stats['loi_nhuan_rong'] >= 0 else "down", "💎")}
        {render_kpi_card_html("ROAS & ROI Toàn Hệ Thống", f"{stats['roas_chung']:.2f}x", f"ROI: {stats['roi_phan_tram']:+.1f}% trên vốn chi", "up" if stats['roas_chung'] >= 1.5 else "neutral", "🚀")}
    </div>
    """
    grid_row2 = f"""
    <div class="mmo-kpi-grid">
        {render_kpi_card_html("Burn Rate Trung Bình / Ngày", format_vnd(stats['burn_rate_ngay']), f"Trung vị lệnh chi: {format_vnd(stats['trung_vi_khoan_chi'])}", "neutral", "⏱️")}
        {render_kpi_card_html("Tổng Phí Cổng & Thuế Ads", format_vnd(stats['tong_phi_gd'] + stats['tong_thue']), f"Phí: {format_vnd(stats['tong_phi_gd'])} | Thuế: {format_vnd(stats['tong_thue'])}", "down", "🧾")}
        {render_kpi_card_html("Chiến Dịch MMO Đang Chạy", f"{len(campaigns)} Chiến dịch", f"Đang quản lý {len(wallets)} Ví thanh toán", "neutral", "🎯")}
        {render_kpi_card_html("Điểm Sức Khỏe Tài Chính", f"{stats['diem_suc_khoe']} / 100", "Chuẩn an toàn quỹ MMO Enterprise", "up" if stats['diem_suc_khoe'] >= 75 else "neutral", "🛡️")}
    </div>
    """
    st.markdown(grid_row1 + grid_row2, unsafe_allow_html=True)

    # Khu vực Biểu đồ Dòng tiền & Phân bổ Danh mục
    chart_col1, chart_col2 = st.columns([1.45, 1.0])

    with chart_col1:
        st.markdown("#### 📈 Diễn Biến Dòng Tiền Theo Ngày (Thu Nhập vs Chi Tiêu)")
        daily_map = stats.get("dong_tien_theo_ngay", {})
        if daily_map:
            sorted_days = sorted(daily_map.keys())
            df_daily = pd.DataFrame([
                {
                    "Ngày": d,
                    "Doanh Thu & Payout (VNĐ)": daily_map[d]["Thu"],
                    "Chi Tiêu Vận Hành (VNĐ)": daily_map[d]["Chi"],
                    "Dòng Tiền Ròng (VNĐ)": daily_map[d]["Rong"],
                }
                for d in sorted_days
            ]).set_index("Ngày")
            st.bar_chart(df_daily[["Doanh Thu & Payout (VNĐ)", "Chi Tiêu Vận Hành (VNĐ)"]])
        else:
            st.info("Chưa đủ dữ liệu ngày để vẽ biểu đồ xu hướng.")

    with chart_col2:
        st.markdown("#### 🧩 Cơ Cấu Chi Tiêu Theo Danh Mục MMO")
        cat_map = stats.get("chi_theo_danh_muc", {})
        if cat_map:
            sorted_cats = sorted(cat_map.items(), key=lambda x: x[1], reverse=True)
            total_c = max(stats["tong_chi"], 1.0)
            for c_name, c_val in sorted_cats[:6]:
                pct = (c_val / total_c) * 100.0
                st.markdown(
                    f"""
                    <div style="margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.83rem; font-weight:600;">
                            <span>{c_name}</span>
                            <span style="color:#10B981;">{format_vnd(c_val)} ({pct:.1f}%)</span>
                        </div>
                        <div class="mmo-progress-track">
                            <div class="mmo-progress-fill" style="width:{min(pct, 100):.1f}%; background:linear-gradient(90deg, #3B82F6, #10B981);"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Chưa có dữ liệu chi tiêu theo danh mục.")

    # Khu vực Cảnh báo Bất thường & Hiệu suất Chiến dịch
    bot_col1, bot_col2 = st.columns(2)
    with bot_col1:
        st.markdown("#### 🏆 Top Chiến Dịch MMO & Hiệu Suất ROAS")
        if campaigns:
            camp_rows = []
            for c in campaigns:
                spend = float(c.get("tong_chi_ads_vnd", 0))
                rev = float(c.get("tong_doanh_thu_vnd", 0))
                roas = (rev / spend) if spend > 0 else 0.0
                profit = rev - spend
                camp_rows.append({
                    "Chiến dịch": c.get("ten_cd", ""),
                    "Nền tảng": c.get("nen_tang", ""),
                    "Chi Ads": format_vnd(spend),
                    "Doanh thu": format_vnd(rev),
                    "ROAS": f"{roas:.2f}x",
                    "Lợi nhuận": format_vnd(profit),
                })
            st.dataframe(pd.DataFrame(camp_rows), use_container_width=True, hide_index=True)

    with bot_col2:
        st.markdown("#### 🚨 Hệ Thống Phát Hiện Khoản Chi Đột Biến (Anomaly Radar)")
        anomalies = phat_hien_giao_dich_bat_thuong(ds_ct)
        if not anomalies:
            st.success("✅ Mọi khoản chi tiêu đều nằm trong biên độ an toàn, không có khoản chi đột biến bất thường.")
        else:
            for anom in anomalies[:4]:
                st.markdown(
                    f"""
                    <div class="mmo-glass-panel" style="border-left:4px solid #F59E0B; padding:10px 14px; margin-bottom:8px;">
                        <div style="font-weight:700; font-size:0.88rem; color:#F59E0B;">
                            ⚠️ [{anom['id']}] {anom['ten']} (+{anom['vuot_trung_binh_pct']}% so với TB)
                        </div>
                        <div style="font-size:0.82rem; color:#94A3B8;">
                            Số tiền: <strong style="color:#F8FAFC;">{format_vnd(anom['tien'])}</strong> | Danh mục: {anom['danh_muc']} | Ngày: {anom['ngay']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ==============================================================================
# 12. MODULE 6: QUẢN LÝ CHIẾN DỊCH ADS & PHÂN TÍCH ROAS/CPA (CAMPAIGN MANAGER)
# ==============================================================================

def render_module_campaigns(
    campaigns: List[Dict[str, Any]],
    ds_ct: List[Dict[str, Any]],
) -> None:
    """
    Phân hệ Quản trị Chiến dịch Quảng cáo & Dự án MMO (Facebook Ads, TikTok Shop,
    Google Ads, Affiliate, Crypto/Airdrop):
    - Tính toán tự động CTR (%), CPC, CPA (Chi phí/Chuyển đổi), CR (%), ROAS, ROI và Lợi nhuận ròng.
    - Cho phép tạo chiến dịch mới, cập nhật số liệu Ads hoặc tự động đồng bộ khoản chi/thu vào `so_hoan_chinh.json`.
    """
    render_section_header(
        "🚀 QUẢN LÝ CHIẾN DỊCH ADS, ĐỐI SOÁT ROAS & CHỈ SỐ MEDIA BUYING",
        "MODULE 06 • CAMPAIGN & ROAS CENTER",
    )

    total_spend_c = sum(float(c.get("tong_chi_ads_vnd", 0)) for c in campaigns)
    total_rev_c = sum(float(c.get("tong_doanh_thu_vnd", 0)) for c in campaigns)
    total_profit_c = total_rev_c - total_spend_c
    avg_roas_c = (total_rev_c / total_spend_c) if total_spend_c > 0 else 0.0

    st.markdown(
        f"""
        <div class="mmo-kpi-grid">
            {render_kpi_card_html("Tổng Ngân Sách Ads Đã Chi", format_vnd(total_spend_c), f"{len(campaigns)} chiến dịch đang theo dõi", "down", "📢")}
            {render_kpi_card_html("Tổng Doanh Thu Chiến Dịch", format_vnd(total_rev_c), "Tổng GMV / Payout ghi nhận", "up", "💰")}
            {render_kpi_card_html("Lợi Nhuận Gộp Chiến Dịch", format_vnd(total_profit_c), f"ROAS Trung bình: {avg_roas_c:.2f}x", "up" if total_profit_c >= 0 else "down", "📈")}
            {render_kpi_card_html("Trạng Thái Tối Ưu Hóa", "Đang Scale Tốt" if avg_roas_c >= 1.7 else "Cần Tối Ưu Creative", "Ngưỡng hòa vốn: 1.35x", "neutral", "🎯")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_camp_list, tab_camp_add, tab_camp_log = st.tabs([
        "📊 Bảng Chỉ Số Chiến Dịch (ROAS / CPA / CTR / CPC)",
        "➕ Khởi Tạo Chiến Dịch MMO Mới",
        "⚡ Ghi Nhận Chi Tiêu Ads / Doanh Thu & Đồng Bộ Sổ Cái",
    ])

    with tab_camp_list:
        if not campaigns:
            st.info("Chưa có chiến dịch nào.")
        else:
            detailed_rows = []
            for c in campaigns:
                spend = float(c.get("tong_chi_ads_vnd", 0))
                rev = float(c.get("tong_doanh_thu_vnd", 0))
                imps = max(int(c.get("impressions", 0)), 1)
                clicks = max(int(c.get("clicks", 0)), 1)
                convs = max(int(c.get("conversions", 0)), 1)

                ctr = (clicks / imps) * 100.0
                cpc = spend / clicks
                cpa = spend / convs
                cr = (convs / clicks) * 100.0
                roas = (rev / spend) if spend > 0 else 0.0
                net_p = rev - spend

                detailed_rows.append({
                    "Mã CD": c.get("ma_cd", ""),
                    "Tên Chiến Dịch": c.get("ten_cd", ""),
                    "Nền Tảng": c.get("nen_tang", ""),
                    "Trạng Thái": c.get("trang_thai", ""),
                    "Ngân Sách/Ngày": format_vnd(c.get("ngan_sach_ngay_vnd", 0)),
                    "Tổng Chi Ads": format_vnd(spend),
                    "Doanh Thu": format_vnd(rev),
                    "Lợi Nhuận": format_vnd(net_p),
                    "ROAS": f"{roas:.2f}x",
                    "CTR (%)": f"{ctr:.2f}%",
                    "CPC (VNĐ)": format_vnd(cpc),
                    "CPA / Đơn": format_vnd(cpa),
                    "CR (%)": f"{cr:.2f}%",
                    "Media Buyer": c.get("nguoi_phu_trach", ""),
                })
            st.dataframe(pd.DataFrame(detailed_rows), use_container_width=True, hide_index=True)

    with tab_camp_add:
        c1, c2 = st.columns(2)
        with c1:
            new_c_name = st.text_input("Tên chiến dịch MMO mới:", placeholder="VD: FB Ads - Drop Servicing US Q4")
            new_c_plat = st.selectbox("Nền tảng:", options=MMO_PLATFORMS)
            new_c_owner = st.text_input("Media Buyer / Người phụ trách:", value="Admin / Leader")
        with c2:
            new_c_budget = st.number_input("Ngân sách ngày dự kiến (VNĐ):", min_value=0.0, value=5000000.0, step=500000.0)
            new_c_status = st.selectbox("Trạng thái:", options=["Đang chạy (Active)", "Đang test (Testing)", "Tạm dừng (Paused)"])
            new_c_note = st.text_input("Ghi chú mục tiêu ROAS / Creative:", placeholder="Target ROAS >= 2.0x")

        if st.button("🚀 Tạo Chiến Dịch Mới", type="primary"):
            if not new_c_name.strip():
                st.warning("Vui lòng nhập tên chiến dịch!")
            else:
                new_camp_obj = {
                    "ma_cd": f"CAMP-{uuid.uuid4().hex[:5].upper()}",
                    "ten_cd": new_c_name.strip(),
                    "nen_tang": new_c_plat,
                    "trang_thai": new_c_status,
                    "ngan_sach_ngay_vnd": new_c_budget,
                    "tong_chi_ads_vnd": 0.0,
                    "tong_doanh_thu_vnd": 0.0,
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "nguoi_phu_trach": new_c_owner,
                    "ngay_bat_dau": datetime.now().strftime("%Y-%m-%d"),
                    "ghi_chu": new_c_note,
                }
                campaigns.append(new_camp_obj)
                luu_chien_dich(campaigns)
                ghi_nhat_ky("CREATE_CAMPAIGN", f"Tạo chiến dịch mới: {new_c_name}", new_c_budget, "SUCCESS")
                st.success(f"✅ Đã khởi tạo chiến dịch **{new_c_name}**!")
                st.rerun()

    with tab_camp_log:
        if not campaigns:
            st.info("Hãy tạo chiến dịch trước.")
        else:
            camp_map = {f"{c['ma_cd']} — {c['ten_cd']}": idx for idx, c in enumerate(campaigns)}
            sel_camp_lbl = st.selectbox("Chọn chiến dịch cần cập nhật số liệu:", options=list(camp_map.keys()))
            c_idx = camp_map[sel_camp_lbl]
            target_c = campaigns[c_idx]

            l_col1, l_col2, l_col3 = st.columns(3)
            with l_col1:
                add_spend = st.number_input("Chi phí Ads phát sinh thêm (VNĐ):", min_value=0.0, value=0.0, step=500000.0)
                add_rev = st.number_input("Doanh thu / Payout phát sinh thêm (VNĐ):", min_value=0.0, value=0.0, step=500000.0)
            with l_col2:
                add_imps = st.number_input("Lượt hiển thị (Impressions) thêm:", min_value=0, value=10000, step=1000)
                add_clicks = st.number_input("Lượt nhấp (Clicks) thêm:", min_value=0, value=250, step=50)
            with l_col3:
                add_convs = st.number_input("Số đơn / Chuyển đổi (Conversions) thêm:", min_value=0, value=5, step=1)
                sync_to_ledger = st.checkbox("Tự động ghi khoản Chi/Thu này vào Sổ cái `so_hoan_chinh.json`", value=True)

            if st.button("💾 Cập Nhật Chỉ Số Chiến Dịch", type="primary"):
                target_c["tong_chi_ads_vnd"] = float(target_c.get("tong_chi_ads_vnd", 0)) + add_spend
                target_c["tong_doanh_thu_vnd"] = float(target_c.get("tong_doanh_thu_vnd", 0)) + add_rev
                target_c["impressions"] = int(target_c.get("impressions", 0)) + add_imps
                target_c["clicks"] = int(target_c.get("clicks", 0)) + add_clicks
                target_c["conversions"] = int(target_c.get("conversions", 0)) + add_convs
                luu_chien_dich(campaigns)

                if sync_to_ledger:
                    if add_spend > 0:
                        ds_ct.append(
                            normalize_transaction_record(
                                {
                                    "ten": f"Chi phí Ads chiến dịch: {target_c['ten_cd']}",
                                    "tien": add_spend,
                                    "loai": "Chi tiêu (Expense)",
                                    "danh_muc": "Quảng cáo Facebook Ads" if "Facebook" in target_c.get("nen_tang", "") else "Quảng cáo TikTok Ads",
                                    "chien_dich": target_c["ten_cd"],
                                },
                                len(ds_ct) + 1,
                            )
                        )
                    if add_rev > 0:
                        ds_ct.append(
                            normalize_transaction_record(
                                {
                                    "ten": f"Doanh thu / Payout chiến dịch: {target_c['ten_cd']}",
                                    "tien": add_rev,
                                    "loai": "Thu nhập / Payout (Revenue)",
                                    "danh_muc": "Payout Affiliate (ClickBank / Offervault / CJ / Impact)",
                                    "chien_dich": target_c["ten_cd"],
                                },
                                len(ds_ct) + 1,
                            )
                        )
                    luu_file(ds_ct)

                st.success("✅ Đã cập nhật chỉ số chiến dịch và đồng bộ vào sổ cái thành công!")
                st.rerun()


# ==============================================================================
# 13. MODULE 7: QUẢN LÝ ĐA VÍ, CỔNG THANH TOÁN & CHUYỂN KHOẢN (MULTI-WALLET)
# ==============================================================================

def render_module_wallets(
    wallets: List[Dict[str, Any]],
    ds_ct: List[Dict[str, Any]],
    settings: Dict[str, Any],
) -> None:
    """
    Phân hệ Quản lý Đa Ví & Nguồn Tiền MMO (Vietcombank, Techcombank Visa Ads,
    Binance USDT TRC20, Payoneer, PingPong, MoMo):
    - Tự động đối soát Số dư đầu kỳ + Tổng Thu vào ví - Tổng Chi từ ví = Số dư khả dụng thực tế.
    - Hỗ trợ Chuyển tiền nội bộ / Xả USDT / Rút Payoneer về Bank Việt Nam với tính toán tỷ giá.
    """
    render_section_header(
        "💳 QUẢN LÝ ĐA VÍ, CỔNG THANH TOÁN QUỐC TẾ & ĐỐI SOÁT SỐ DƯ",
        "MODULE 07 • MULTI-WALLET TREASURY",
    )

    rates = settings.get("ty_gia", DEFAULT_EXCHANGE_RATES)

    # Tính toán biến động từng ví từ sổ cái `so_hoan_chinh.json`
    thu_vi_map: Dict[str, float] = defaultdict(float)
    chi_vi_map: Dict[str, float] = defaultdict(float)
    for item in ds_ct:
        w_name = str(item.get("vi_thanh_toan", ""))
        tien_v = float(item.get("tien", 0))
        loai_v = str(item.get("loai", "Chi tiêu"))
        if "Thu" in loai_v or "Hoàn" in loai_v or "Nạp" in loai_v:
            thu_vi_map[w_name] += tien_v
        else:
            chi_vi_map[w_name] += tien_v

    wallet_cards_Rows = []
    tong_tai_san_vnd = 0.0

    cols_w = st.columns(3)
    for idx, w in enumerate(wallets):
        w_name = w.get("ten_vi", "")
        curr = w.get("loai_tien", "VND")
        rate = float(rates.get(curr, DEFAULT_EXCHANGE_RATES.get(curr, 1.0)))
        init_bal_native = float(w.get("so_du_ban_dau", 0.0))
        init_bal_vnd = init_bal_native * rate

        in_vnd = thu_vi_map.get(w_name, 0.0)
        out_vnd = chi_vi_map.get(w_name, 0.0)
        cur_bal_vnd = init_bal_vnd + in_vnd - out_vnd
        cur_bal_native = cur_bal_vnd / rate if rate > 0 else cur_bal_vnd
        tong_tai_san_vnd += cur_bal_vnd

        wallet_cards_Rows.append({
            "Mã Ví": w.get("ma_vi", ""),
            "Tên Ví / Cổng": w_name,
            "Loại Ví": w.get("loai_vi", ""),
            "Tiền Tệ": curr,
            "Số Dư Đầu Kỳ": format_currency(init_bal_native, curr),
            "Tổng Thu Vào (VNĐ)": format_vnd(in_vnd),
            "Tổng Chi Ra (VNĐ)": format_vnd(out_vnd),
            "Số Dư Khả Dụng": format_currency(cur_bal_native, curr),
            "Quy Đổi VNĐ": format_vnd(cur_bal_vnd),
        })

        with cols_w[idx % 3]:
            st.markdown(
                f"""
                <div class="mmo-kpi-card" style="margin-bottom:14px;">
                    <div class="mmo-kpi-label">
                        <span>{w.get('loai_vi', 'Wallet')}</span>
                        <span class="status-pill pill-green">{curr}</span>
                    </div>
                    <div style="font-weight:700; font-size:0.95rem; margin-bottom:6px;">{w_name}</div>
                    <div class="mmo-kpi-value" style="color:#10B981;">{format_currency(cur_bal_native, curr)}</div>
                    <div style="font-size:0.8rem; color:#94A3B8; font-family:'JetBrains Mono', monospace;">
                        ≈ {format_vnd(cur_bal_vnd)} | TK: {w.get('so_tk', '')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.info(f"💎 **TỔNG TÀI SẢN RÒNG TRÊN TẤT CẢ CÁC VÍ (TOTAL TREASURY LIQUIDITY):** **{format_vnd(tong_tai_san_vnd)}**")

    tab_w_table, tab_w_swap, tab_w_add = st.tabs([
        "📋 Bảng Đối Soát Số Dư Đa Ví",
        "🔄 Chuyển Khoản Nội Bộ / Rút Ngoại Tệ Về Bank (USDT/Payoneer ➔ VND)",
        "➕ Thêm Ví Hoặc Cổng Thanh Toán Mới",
    ])

    with tab_w_table:
        st.dataframe(pd.DataFrame(wallet_cards_Rows), use_container_width=True, hide_index=True)

    with tab_w_swap:
        st.markdown("Ghi nhận lệnh rút ngoại tệ (Payoneer / PingPong / Binance USDT) về Ngân hàng nội địa:")
        w_names_list = [w.get("ten_vi", "") for w in wallets]
        sw_c1, sw_c2, sw_c3 = st.columns(3)
        with sw_c1:
            vi_nguon = st.selectbox("Từ Ví nguồn (Rút ra):", options=w_names_list, index=min(3, len(w_names_list) - 1))
        with sw_c2:
            vi_dich = st.selectbox("Về Ví đích (Nhận tiền):", options=w_names_list, index=0)
        with sw_c3:
            so_tien_chuyen_vnd = st.number_input("Giá trị quy đổi chuyển (VNĐ):", min_value=0.0, value=25450000.0, step=1000000.0)

        phi_rut_vnd = st.number_input("Phí rút / Chênh lệch quy đổi (VNĐ):", min_value=0.0, value=250000.0, step=50000.0)
        if st.button("⚡ Thực Hiện Chuyển Khoản & Ghi Sổ Cái", type="primary"):
            if vi_nguon == vi_dich:
                st.warning("Ví nguồn và Ví đích phải khác nhau!")
            elif so_tien_chuyen_vnd <= 0:
                st.warning("Số tiền chuyển phải lớn hơn 0!")
            else:
                if phi_rut_vnd > 0:
                    ds_ct.append(
                        normalize_transaction_record(
                            {
                                "ten": f"Phí rút tiền / Chuyển khoản từ {vi_nguon} về {vi_dich}",
                                "tien": phi_rut_vnd,
                                "loai": "Chi tiêu (Expense)",
                                "danh_muc": "Phí cổng thanh toán / Gas Fee / Chênh lệch tỷ giá",
                                "vi_thanh_toan": vi_nguon,
                            },
                            len(ds_ct) + 1,
                        )
                    )
                    luu_file(ds_ct)
                ghi_nhat_ky(
                    "INTERNAL_TRANSFER",
                    f"Chuyển {format_vnd(so_tien_chuyen_vnd)} từ {vi_nguon} sang {vi_dich} (Phí: {format_vnd(phi_rut_vnd)})",
                    so_tien_chuyen_vnd,
                    "INFO",
                )
                st.success(
                    f"✅ Đã hạch toán lệnh chuyển {format_vnd(so_tien_chuyen_vnd)} từ **{vi_nguon}** về **{vi_dich}**!"
                )
                st.rerun()

    with tab_w_add:
        nw_1, nw_2 = st.columns(2)
        with nw_1:
            new_w_name = st.text_input("Tên Ví / Ngân hàng / Cổng mới:", placeholder="VD: Wise Business UK (GBP)")
            new_w_type = st.selectbox(
                "Loại ví:",
                options=["Ngân hàng nội địa (Bank)", "Thẻ tín dụng / Debit Ads", "Cổng thanh toán Quốc tế", "Crypto / Stablecoin Wallet"],
            )
        with nw_2:
            new_w_curr = st.selectbox("Đơn vị tiền tệ:", options=list(DEFAULT_EXCHANGE_RATES.keys()))
            new_w_bal = st.number_input("Số dư ban đầu (theo nguyên tệ):", min_value=0.0, value=0.0, step=100.0)
        new_w_acc = st.text_input("Số tài khoản / Địa chỉ ví / Email:", placeholder="VD: 0x9988... hoặc billing@domain.com")

        if st.button("💾 Thêm Ví Mới Vào Hệ Thống", type="primary"):
            if not new_w_name.strip():
                st.warning("Vui lòng nhập tên ví!")
            else:
                wallets.append({
                    "ma_vi": f"WAL-{uuid.uuid4().hex[:4].upper()}",
                    "ten_vi": new_w_name.strip(),
                    "loai_vi": new_w_type,
                    "loai_tien": new_w_curr,
                    "so_du_ban_dau": new_w_bal,
                    "so_tk": new_w_acc.strip() or "N/A",
                    "chu_tk": "ALPHA MMO TREASURY",
                    "trang_thai": "Hoạt động",
                })
                luu_danh_sach_vi(wallets)
                st.success(f"✅ Đã thêm ví mới: **{new_w_name}**!")
                st.rerun()


# ==============================================================================
# 14. MODULE 8: QUẢN LÝ TÀI NGUYÊN & ĐỊNH PHÍ MMO (SUBSCRIPTIONS & INFRA)
# ==============================================================================

def render_module_subscriptions(
    subs: List[Dict[str, Any]],
    ds_ct: List[Dict[str, Any]],
    settings: Dict[str, Any],
) -> None:
    """
    Phân hệ Quản lý Định phí & Tài nguyên Hạ tầng MMO:
    - Quản lý các gói thuê bao định kỳ: Antidetect Browser (AdsPower, Multilogin, GoLogin),
      Proxy Dân cư (BrightData, 922Proxy), Cloud VPS (Hetzner, AWS, Contabo), AI & Spy Tools (OpenAI, PipiAds, AdSpy).
    - Tự động tính Tổng chi phí duy trì hạ tầng cố định hàng tháng (Monthly Fixed Burn Rate).
    - Hỗ trợ nút 1-Click "Gia hạn & Hạch toán vào Sổ cái `so_hoan_chinh.json`".
    """
    render_section_header(
        "🔄 QUẢN LÝ TÀI NGUYÊN HẠ TẦNG & ĐỊNH PHÍ MMO (PROXY / VPS / ANTIDETECT / AI)",
        "MODULE 08 • RECURRING INFRASTRUCTURE",
    )

    rates = settings.get("ty_gia", DEFAULT_EXCHANGE_RATES)
    today = datetime.now().date()

    tong_dinh_phi_thang_vnd = 0.0
    sap_het_han_count = 0

    sub_rows = []
    for s in subs:
        curr = s.get("loai_tien", "USD")
        rate = float(rates.get(curr, DEFAULT_EXCHANGE_RATES.get(curr, 1.0)))
        val_native = float(s.get("nguyen_te", 0.0))
        val_vnd = round(val_native * rate, 0)
        tong_dinh_phi_thang_vnd += val_vnd

        due_str = str(s.get("ngay_gia_han", today.strftime("%Y-%m-%d")))
        try:
            due_date = datetime.strptime(due_str[:10], "%Y-%m-%d").date()
            days_left = (due_date - today).days
        except ValueError:
            days_left = 15

        if days_left <= 5:
            sap_het_han_count += 1

        sub_rows.append({
            "Mã Sub": s.get("ma_sub", ""),
            "Tên Công Cụ / Hạ Tầng MMO": s.get("ten_dich_vu", ""),
            "Nhóm Tài Nguyên": s.get("nhom", ""),
            "Chu Kỳ": s.get("chu_ky", ""),
            "Chi Phí Gốc": format_currency(val_native, curr),
            "Quy Đổi VNĐ": format_vnd(val_vnd),
            "Ví Thanh Toán": s.get("vi_thanh_toan", ""),
            "Ngày Gia Hạn": due_str,
            "Còn Lại": f"{days_left} ngày",
            "Trạng Thái": "⚠️ Sắp đến hạn" if days_left <= 5 else "✅ Đang hoạt động",
        })

    st.markdown(
        f"""
        <div class="mmo-kpi-grid">
            {render_kpi_card_html("Tổng Định Phí Hạ Tầng / Tháng", format_vnd(tong_dinh_phi_thang_vnd), f"{len(subs)} gói thuê bao công cụ MMO", "down", "🖥️")}
            {render_kpi_card_html("Chi Phí Hạ Tầng Quy Đổi USD", format_currency(tong_dinh_phi_thang_vnd / float(rates.get('USD', 25450)), 'USD'), "Chi phí cố định (Fixed Burn)", "neutral", "🌐")}
            {render_kpi_card_html("Gói Sắp Đến Hạn (≤ 5 Ngày)", f"{sap_het_han_count} Gói", "Cần chuẩn bị số dư thẻ/ví USDT", "down" if sap_het_han_count > 0 else "up", "⏰")}
            {render_kpi_card_html("Ước Tính Định Phí Cả Năm", format_vnd(tong_dinh_phi_thang_vnd * 12), "Chưa tính chiết khấu gói năm", "neutral", "📅")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_sub_list, tab_sub_renew, tab_sub_add = st.tabs([
        "📋 Danh Sách Thuê Bao Hạ Tầng MMO",
        "⚡ Gia Hạn Nhanh 1-Click & Ghi Sổ Cái",
        "➕ Thêm Gói Thuê Bao Công Cụ Mới",
    ])

    with tab_sub_list:
        st.dataframe(pd.DataFrame(sub_rows), use_container_width=True, hide_index=True)

    with tab_sub_renew:
        st.markdown("Nhấn nút **Gia hạn & Ghi sổ chi tiêu** để tự động cộng thêm 30 ngày sử dụng và lưu khoản chi vào `so_hoan_chinh.json`:")
        for idx, s in enumerate(subs):
            curr = s.get("loai_tien", "USD")
            rate = float(rates.get(curr, DEFAULT_EXCHANGE_RATES.get(curr, 1.0)))
            val_vnd = round(float(s.get("nguyen_te", 0)) * rate, 0)
            c_s1, c_s2 = st.columns([3.5, 1.2])
            with c_s1:
                st.write(
                    f"**{idx + 1}. {s.get('ten_dich_vu')}** — "
                    f"Chi phí: **{format_currency(s.get('nguyen_te', 0), curr)}** ({format_vnd(val_vnd)}) | "
                    f"Hạn tiếp theo: `{s.get('ngay_gia_han')}`"
                )
            with c_s2:
                if st.button("💳 Gia hạn & Ghi sổ", key=f"btn_renew_sub_{idx}", use_container_width=True):
                    try:
                        cur_due = datetime.strptime(str(s.get("ngay_gia_han"))[:10], "%Y-%m-%d").date()
                    except ValueError:
                        cur_due = today
                    next_due = max(cur_due, today) + timedelta(days=30)
                    subs[idx]["ngay_gia_han"] = next_due.strftime("%Y-%m-%d")
                    subs[idx]["trang_thai"] = "Đang hoạt động"
                    luu_dinh_phi_mmo(subs)

                    rec = normalize_transaction_record(
                        {
                            "ten": f"Gia hạn định kỳ: {s.get('ten_dich_vu')}",
                            "tien": val_vnd,
                            "loai": "Chi tiêu (Expense)",
                            "nguyen_te": float(s.get("nguyen_te", 0)),
                            "loai_tien": curr,
                            "ty_gia": rate,
                            "danh_muc": s.get("nhom", "Tool MMO / Phần mềm AI / API (OpenAI/Claude/CapCut)"),
                            "vi_thanh_toan": s.get("vi_thanh_toan", "Payoneer (USD)"),
                            "tags": ["subscription", "renewal", "infra"],
                            "ghi_chu": f"Gia hạn chu kỳ mới đến ngày {next_due.strftime('%Y-%m-%d')}",
                        },
                        len(ds_ct) + 1,
                    )
                    ds_ct.append(rec)
                    luu_file(ds_ct)
                    ghi_nhat_ky(
                        "RENEW_SUBSCRIPTION",
                        f"Gia hạn {s.get('ten_dich_vu')} ({format_vnd(val_vnd)})",
                        val_vnd,
                        "SUCCESS",
                    )
                    st.success(f"✅ Đã gia hạn **{s.get('ten_dich_vu')}** đến `{next_due}` và lưu vào sổ cái!")
                    st.rerun()

    with tab_sub_add:
        sc1, sc2 = st.columns(2)
        with sc1:
            new_s_name = st.text_input("Tên công cụ / dịch vụ MMO:", placeholder="VD: Multilogin Pro 100 Profiles")
            new_s_group = st.selectbox("Nhóm danh mục:", options=EXPENSE_CATEGORIES)
            new_s_wallet = st.selectbox("Ví thanh toán mặc định:", options=DEFAULT_PAYMENT_METHODS)
        with sc2:
            new_s_curr = st.selectbox("Đơn vị tiền tệ:", options=["USD", "USDT", "VND", "EUR"])
            new_s_amt = st.number_input("Chi phí mỗi kỳ (Nguyên tệ):", min_value=0.0, value=49.0, step=5.0)
            new_s_due = st.date_input("Ngày gia hạn tiếp theo:", value=today + timedelta(days=30))

        if st.button("➕ Lưu Gói Định Phí Mới", type="primary"):
            if not new_s_name.strip():
                st.warning("Vui lòng nhập tên dịch vụ!")
            else:
                subs.append({
                    "ma_sub": f"SUB-{uuid.uuid4().hex[:4].upper()}",
                    "ten_dich_vu": new_s_name.strip(),
                    "nhom": new_s_group,
                    "chu_ky": "Hàng tháng (Monthly)",
                    "nguyen_te": new_s_amt,
                    "loai_tien": new_s_curr,
                    "vi_thanh_toan": new_s_wallet,
                    "ngay_gia_han": new_s_due.strftime("%Y-%m-%d"),
                    "tu_dong_gia_han": True,
                    "trang_thai": "Đang hoạt động",
                    "ghi_chu": "Gói thuê bao hạ tầng vận hành MMO",
                })
                luu_dinh_phi_mmo(subs)
                st.success(f"✅ Đã thêm gói định phí **{new_s_name}**!")
                st.rerun()


# ==============================================================================
# 15. MODULE 9: QUẢN LÝ ĐỘI NHÓM MMO, LƯƠNG KPI & CHIA LỢI NHUẬN (TEAM PAYROLL)
# ==============================================================================

def render_module_team_payroll(
    team: List[Dict[str, Any]],
    ds_ct: List[Dict[str, Any]],
) -> None:
    """
    Phân hệ Quản trị Nhân sự MMO, Media Buyer Commission & Chia Lợi Nhuận (Split Profit):
    - Tính toán thu nhập thực lĩnh = Lương cứng + (% Hoa hồng × Lợi nhuận ròng mang về) + Thưởng KPI.
    - Cho phép tất toán bảng lương từng nhân sự hoặc toàn bộ đội ngũ trực tiếp vào `so_hoan_chinh.json`.
    """
    render_section_header(
        "👥 QUẢN LÝ ĐỘI NHÓM MMO, HOA HỒNG MEDIA BUYER & BẢNG LƯƠNG KPI",
        "MODULE 09 • TEAM PAYROLL & PROFIT SHARE",
    )

    tong_luong_cung = 0.0
    tong_hoa_hong = 0.0
    tong_thuong_kpi = 0.0
    tong_thuc_linh = 0.0
    tong_loi_nhuan_team = 0.0

    payroll_rows = []
    for m in team:
        base_sal = float(m.get("luong_cung_vnd", 0))
        pct_share = float(m.get("phan_tram_loi_nhuan", 0))
        net_brought = float(m.get("loi_nhuan_mang_ve_vnd", 0))
        bonus_kpi = float(m.get("thuong_kpi_vnd", 0))

        commission_vnd = round(max(net_brought, 0.0) * (pct_share / 100.0), 0)
        total_payout = base_sal + commission_vnd + bonus_kpi

        tong_luong_cung += base_sal
        tong_hoa_hong += commission_vnd
        tong_thuong_kpi += bonus_kpi
        tong_thuc_linh += total_payout
        tong_loi_nhuan_team += net_brought

        payroll_rows.append({
            "Mã NV": m.get("ma_nv", ""),
            "Họ và Tên": m.get("ho_ten", ""),
            "Vai Trò Chuyên Môn": m.get("vai_tro", ""),
            "Lương Cứng": format_vnd(base_sal),
            "Lợi Nhuận Mang Về": format_vnd(net_brought),
            "% Chia Lãi": f"{pct_share:.1f}%",
            "Hoa Hồng Profit Share": format_vnd(commission_vnd),
            "Thưởng KPI": format_vnd(bonus_kpi),
            "TỔNG THỰC LĨNH": format_vnd(total_payout),
            "Tài Khoản Nhận": m.get("vi_nhan_luong", ""),
        })

    st.markdown(
        f"""
        <div class="mmo-kpi-grid">
            {render_kpi_card_html("Tổng Quỹ Lương & Hoa Hồng", format_vnd(tong_thuc_linh), f"{len(team)} thành viên nòng cốt", "down", "💸")}
            {render_kpi_card_html("Tổng Lương Cứng Cố Định", format_vnd(tong_luong_cung), "Chi phí nhân sự cơ bản", "neutral", "🏢")}
            {render_kpi_card_html("Tổng Hoa Hồng & Thưởng KPI", format_vnd(tong_hoa_hong + tong_thuong_kpi), "Thưởng theo hiệu suất ROAS", "up", "🔥")}
            {render_kpi_card_html("Tổng Lợi Nhuận Team Tạo Ra", format_vnd(tong_loi_nhuan_team), f"Tỷ lệ quỹ lương/lợi nhuận: {(tong_thuc_linh / max(tong_loi_nhuan_team, 1) * 100):.1f}%", "up", "🏆")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_team_board, tab_team_pay, tab_team_add = st.tabs([
        "📊 Bảng Tính Lương & Chia Lợi Nhuận (Profit Share)",
        "💳 Tất Toán Lương & Ghi Sổ Chi Tiêu",
        "➕ Thêm Thành Viên / Cập Nhật KPI",
    ])

    with tab_team_board:
        st.dataframe(pd.DataFrame(payroll_rows), use_container_width=True, hide_index=True)

    with tab_team_pay:
        st.markdown("Chọn nhân sự để xuất phiếu lương và tự động ghi khoản chi vào `so_hoan_chinh.json`:")
        for idx, m in enumerate(team):
            base_sal = float(m.get("luong_cung_vnd", 0))
            pct_share = float(m.get("phan_tram_loi_nhuan", 0))
            net_brought = float(m.get("loi_nhuan_mang_ve_vnd", 0))
            bonus_kpi = float(m.get("thuong_kpi_vnd", 0))
            comm = round(max(net_brought, 0.0) * (pct_share / 100.0), 0)
            tot_pay = base_sal + comm + bonus_kpi

            c_p1, c_p2 = st.columns([3.6, 1.2])
            with c_p1:
                st.write(
                    f"**{idx + 1}. {m.get('ho_ten')}** ({m.get('vai_tro')}) — "
                    f"Thực lĩnh: **{format_vnd(tot_pay)}** _(Cứng: {format_vnd(base_sal)} + Share {pct_share}%: {format_vnd(comm)} + KPI: {format_vnd(bonus_kpi)})_"
                )
            with c_p2:
                if st.button("💸 Chi lương & Ghi sổ", key=f"pay_mem_{idx}", use_container_width=True):
                    rec = normalize_transaction_record(
                        {
                            "ten": f"Thanh toán lương & hoa hồng MMO: {m.get('ho_ten')} ({m.get('vai_tro')})",
                            "tien": tot_pay,
                            "loai": "Chi tiêu (Expense)",
                            "danh_muc": "Lương nhân sự / Media Buyer / Editor / VA",
                            "vi_thanh_toan": "Vietcombank (VND)",
                            "tags": ["payroll", "commission", "team"],
                            "ghi_chu": f"TK nhận: {m.get('vi_nhan_luong')} | Hoa hồng {pct_share}% trên {format_vnd(net_brought)}",
                        },
                        len(ds_ct) + 1,
                    )
                    ds_ct.append(rec)
                    luu_file(ds_ct)
                    ghi_nhat_ky(
                        "PAYROLL_DISBURSEMENT",
                        f"Chi lương {m.get('ho_ten')}: {format_vnd(tot_pay)}",
                        tot_pay,
                        "SUCCESS",
                    )
                    st.success(f"✅ Đã hạch toán chi lương cho **{m.get('ho_ten')}** ({format_vnd(tot_pay)}) vào sổ cái!")

        st.divider()
        if st.button("🚀 Tất Toán Toàn Bộ Quỹ Lương Team Tháng Này (1-Click Batch Payroll)", type="primary"):
            rec_all = normalize_transaction_record(
                {
                    "ten": f"Tất toán tổng quỹ lương & hoa hồng KPI Team MMO ({len(team)} nhân sự)",
                    "tien": tong_thuc_linh,
                    "loai": "Chi tiêu (Expense)",
                    "danh_muc": "Lương nhân sự / Media Buyer / Editor / VA",
                    "vi_thanh_toan": "Vietcombank (VND)",
                    "tags": ["batch-payroll", "team-mmo"],
                    "ghi_chu": f"Lương cứng: {format_vnd(tong_luong_cung)} + Hoa hồng & KPI: {format_vnd(tong_hoa_hong + tong_thuong_kpi)}",
                },
                len(ds_ct) + 1,
            )
            ds_ct.append(rec_all)
            luu_file(ds_ct)
            ghi_nhat_ky("BATCH_PAYROLL", f"Tất toán tổng quỹ lương {format_vnd(tong_thuc_linh)}", tong_thuc_linh, "SUCCESS")
            st.success(f"✅ Đã ghi nhận khoản chi tổng quỹ lương **{format_vnd(tong_thuc_linh)}** vào `so_hoan_chinh.json`!")

    with tab_team_add:
        tc1, tc2 = st.columns(2)
        with tc1:
            t_name = st.text_input("Họ và tên thành viên:", placeholder="VD: Đỗ Hoàng Nam")
            t_role = st.text_input("Vai trò chuyên môn:", placeholder="VD: TikTok Media Buyer / Video Editor")
            t_bank = st.text_input("Thông tin tài khoản nhận lương:", placeholder="VD: Techcombank - 1903889900")
        with tc2:
            t_base = st.number_input("Lương cứng (VNĐ):", min_value=0.0, value=10000000.0, step=500000.0)
            t_pct = st.number_input("% Hoa hồng chia lợi nhuận (Profit Share):", min_value=0.0, max_value=80.0, value=10.0, step=1.0)
            t_net = st.number_input("Lợi nhuận ròng nhân sự mang về kỳ này (VNĐ):", min_value=0.0, value=30000000.0, step=1000000.0)
        t_bonus = st.number_input("Thưởng nóng KPI (VNĐ):", min_value=0.0, value=1000000.0, step=500000.0)

        if st.button("💾 Thêm Nhân Sự Vào Bảng Lương", type="primary"):
            if not t_name.strip():
                st.warning("Vui lòng nhập họ tên nhân sự!")
            else:
                team.append({
                    "ma_nv": f"MEM-{len(team) + 1:02d}",
                    "ho_ten": t_name.strip(),
                    "vai_tro": t_role.strip() or "MMO Specialist",
                    "luong_cung_vnd": t_base,
                    "phan_tram_loi_nhuan": t_pct,
                    "loi_nhuan_mang_ve_vnd": t_net,
                    "thuong_kpi_vnd": t_bonus,
                    "vi_nhan_luong": t_bank.strip() or "Vietcombank",
                    "trang_thai": "Full-time",
                })
                luu_nhan_su_mmo(team)
                st.success(f"✅ Đã thêm nhân sự **{t_name}** vào hệ thống!")
                st.rerun()


# ==============================================================================
# 16. MODULE 10: NGÂN SÁCH, DỰ BÁO DÒNG TIỀN & GIẢ LẬP SCALE ROAS (SIMULATOR)
# ==============================================================================

def render_module_budget_and_simulator(
    ds_ct: List[Dict[str, Any]],
    stats: Dict[str, Any],
) -> None:
    """
    Phân hệ Kiểm soát Hạn mức Ngân sách (Budget Caps) & Phòng Thí Nghiệm Giả Lập
    Chiến Dịch MMO (What-If ROAS & Scaling Simulator + Dự báo Monte Carlo 30-90 ngày).
    """
    render_section_header(
        "🎯 HẠN MỨC NGÂN SÁCH, DỰ BÁO DÒNG TIỀN & PHÒNG LAB GIẢ LẬP SCALE ADS",
        "MODULE 10 • BUDGETING & ROAS SIMULATOR",
    )

    budgets = doc_ngan_sach_danh_muc()
    chi_map = stats.get("chi_theo_danh_muc", {})

    tab_budget_cap, tab_roas_sim, tab_forecast = st.tabs([
        "🛡️ Kiểm Soát Hạn Mức Ngân Sách Theo Danh Mục",
        "🧪 Phòng Lab Giả Lập Scale Ngân Sách Ads & Điểm Hòa Vốn (ROAS Simulator)",
        "🔮 Dự Báo Dòng Tiền 30 / 60 / 90 Ngày Tới (Cashflow Projection)",
    ])

    with tab_budget_cap:
        st.markdown("Theo dõi tỷ lệ giải ngân thực tế so với hạn mức trần ngân sách tháng của từng hạng mục MMO:")
        for cat_name, cap_val in budgets.items():
            actual_val = float(chi_map.get(cat_name, 0.0))
            ratio_pct = (actual_val / cap_val * 100.0) if cap_val > 0 else 0.0
            if ratio_pct >= 100:
                bar_color = "#EF4444"
                status_txt = "🚨 VƯỢT HẠN MỨC"
            elif ratio_pct >= 80:
                bar_color = "#F59E0B"
                status_txt = "⚠️ SẮP CHẠM TRẦN"
            else:
                bar_color = "#10B981"
                status_txt = "✅ AN TOÀN"

            st.markdown(
                f"""
                <div class="mmo-glass-panel" style="padding:12px 16px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.88rem; font-weight:700;">
                        <span>{cat_name}</span>
                        <span>{status_txt} • {format_vnd(actual_val)} / {format_vnd(cap_val)} ({ratio_pct:.1f}%)</span>
                    </div>
                    <div class="mmo-progress-track">
                        <div class="mmo-progress-fill" style="width:{min(ratio_pct, 100.0):.1f}%; background:{bar_color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("⚙️ Điều chỉnh hạn mức ngân sách danh mục"):
            sel_b_cat = st.selectbox("Chọn danh mục cần chỉnh hạn mức:", options=list(budgets.keys()))
            new_b_cap = st.number_input(
                "Hạn mức trần hàng tháng mới (VNĐ):",
                min_value=1000000.0,
                value=float(budgets.get(sel_b_cat, 20000000.0)),
                step=2000000.0,
            )
            if st.button("Lưu hạn mức mới"):
                budgets[sel_b_cat] = new_b_cap
                luu_ngan_sach_danh_muc(budgets)
                st.success(f"Đã cập nhật hạn mức **{sel_b_cat}** thành **{format_vnd(new_b_cap)}**!")
                st.rerun()

    with tab_roas_sim:
        st.markdown(
            """
            <div class="mmo-glass-panel">
                <strong>🧪 Trình Giả Lập Kinh Tế Đơn Vị & Scale Ngân Sách Quảng Cáo (MMO Unit Economics Lab):</strong><br/>
                Giúp Media Buyer tính chính xác <strong>ROAS Hòa Vốn (Break-Even ROAS)</strong>,
                <strong>CPA Tối Đa Cho Phép</strong> và lợi nhuận ròng khi x2, x5, x10 ngân sách Ads.
            </div>
            """,
            unsafe_allow_html=True,
        )
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            sim_aov_vnd = st.number_input("Giá bán trung bình / Payout 1 đơn (AOV - VNĐ):", min_value=50000.0, value=1250000.0, step=50000.0)
            sim_cogs_pct = st.slider("Giá vốn hàng bán + Ship + Fulfillment (% AOV):", 0.0, 80.0, 28.0, 1.0)
        with s_col2:
            sim_fee_pct = st.slider("Phí sàn / Phí cổng thanh toán + Hoàn huỷ (% AOV):", 0.0, 40.0, 8.0, 0.5)
            sim_tax_ads_pct = st.slider("Thuế thẻ Ads + Phí thuê BM/TK (% Ngân sách Ads):", 0.0, 25.0, 6.0, 0.5)
        with s_col3:
            sim_daily_ads = st.number_input("Ngân sách Ads dự kiến / Ngày (VNĐ):", min_value=500000.0, value=15000000.0, step=1000000.0)
            sim_expected_cpa = st.number_input("Chi phí Ads trung bình ra 1 đơn (CPA - VNĐ):", min_value=10000.0, value=420000.0, step=20000.0)

        # Tính toán Unit Economics
        gross_margin_pct = max(100.0 - sim_cogs_pct - sim_fee_pct, 1.0)
        gross_profit_per_order = sim_aov_vnd * (gross_margin_pct / 100.0)
        effective_cpa = sim_expected_cpa * (1.0 + sim_tax_ads_pct / 100.0)
        net_profit_per_order = gross_profit_per_order - effective_cpa
        breakeven_roas = (1.0 + sim_tax_ads_pct / 100.0) / (gross_margin_pct / 100.0)
        expected_roas = sim_aov_vnd / max(sim_expected_cpa, 1.0)

        orders_per_day = sim_daily_ads / max(sim_expected_cpa, 1.0)
        daily_rev = orders_per_day * sim_aov_vnd
        daily_total_ads_cost = sim_daily_ads * (1.0 + sim_tax_ads_pct / 100.0)
        daily_cogs_and_fees = daily_rev * ((sim_cogs_pct + sim_fee_pct) / 100.0)
        daily_net_profit = daily_rev - daily_total_ads_cost - daily_cogs_and_fees
        monthly_net_profit = daily_net_profit * 30.0

        st.markdown(
            f"""
            <div class="mmo-kpi-grid">
                {render_kpi_card_html("ROAS Hòa Vốn (Break-Even)", f"{breakeven_roas:.2f}x", f"CPA tối đa: {format_vnd(gross_profit_per_order)}", "neutral", "⚖️")}
                {render_kpi_card_html("ROAS Kỳ Vọng Hiện Tại", f"{expected_roas:.2f}x", "Có lãi tốt" if expected_roas > breakeven_roas else "Đang lỗ vốn!", "up" if expected_roas > breakeven_roas else "down", "🎯")}
                {render_kpi_card_html("Lãi Ròng / 1 Đơn Hàng", format_vnd(net_profit_per_order), f"Sản lượng: {orders_per_day:.1f} đơn/ngày", "up" if net_profit_per_order > 0 else "down", "📦")}
                {render_kpi_card_html("Lợi Nhuận Ròng / Tháng (30d)", format_vnd(monthly_net_profit), f"Lãi ngày: {format_vnd(daily_net_profit)}", "up" if monthly_net_profit > 0 else "down", "💎")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_forecast:
        st.markdown("Dự báo dòng tiền 30 - 60 - 90 ngày tới dựa trên tốc độ Thu/Chi thực tế trong sổ cái:")
        so_ngay_hd = max(len(stats.get("dong_tien_theo_ngay", {})), 1)
        thu_tb_ngay = stats["tong_thu_thuc_te"] / so_ngay_hd
        chi_tb_ngay = stats["tong_chi"] / so_ngay_hd
        rong_tb_ngay = thu_tb_ngay - chi_tb_ngay

        proj_rows = []
        for horizon in [7, 15, 30, 60, 90]:
            proj_rev = thu_tb_ngay * horizon
            proj_exp = chi_tb_ngay * horizon
            proj_net = rong_tb_ngay * horizon
            proj_rows.append({
                "Chu Kỳ Dự Báo": f"{horizon} Ngày Tới",
                "Doanh Thu Dự Kiến": format_vnd(proj_rev),
                "Chi Tiêu Dự Kiến": format_vnd(proj_exp),
                "Lợi Nhuận Tích Lũy Dự Kiến": format_vnd(proj_net),
                "Kịch Bản Thận Trọng (-15%)": format_vnd(proj_net * 0.85),
                "Kịch Bản Bùng Nổ Scale (+35%)": format_vnd(proj_net * 1.35),
            })
        st.dataframe(pd.DataFrame(proj_rows), use_container_width=True, hide_index=True)


# ==============================================================================
# 17. MODULE 11: NHẬT KÝ BẢO MẬT, SAO LƯU KHÔI PHỤC & CÀI ĐẶT HỆ THỐNG
# ==============================================================================

def render_module_system_and_audit(
    ds_ct: List[Dict[str, Any]],
    settings: Dict[str, Any],
) -> None:
    """
    Phân hệ Quản trị Hệ thống, Nhật ký Kiểm toán (Audit Trail), Cấu hình Tỷ giá Ngoại tệ,
    Sao lưu / Khôi phục JSON và Trình tạo Dữ liệu Mẫu MMO.
    """
    render_section_header(
        "🛡️ NHẬT KÝ BẢO MẬT (AUDIT LOGS), CẤU HÌNH TỶ GIÁ & SAO LƯU HỆ THỐNG",
        "MODULE 11 • SECURITY, AUDIT & SETTINGS",
    )

    tab_audit, tab_rates, tab_backup = st.tabs([
        "📜 Nhật Ký Thao Tác & Kiểm Toán (Audit Trail)",
        "💱 Cấu Hình Tỷ Giá Ngoại Tệ & Thông Tin Đơn Vị",
        "💾 Sao Lưu, Phục Hồi & Nạp Dữ Liệu Mẫu MMO",
    ])

    with tab_audit:
        logs = doc_nhat_ky()
        if not logs:
            st.info("Chưa có bản ghi nhật ký nào.")
        else:
            st.markdown(f"Hiển thị **{len(logs)}** sự kiện thao tác gần nhất trên hệ thống:")
            st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
            if st.button("🧹 Xoá lịch sử nhật ký"):
                _safe_write_json(AUDIT_LOG_FILE, [])
                st.success("Đã làm mới nhật ký hệ thống!")
                st.rerun()

    with tab_rates:
        st.markdown("Cập nhật tỷ giá quy đổi ngoại tệ chuẩn (áp dụng tự động cho toàn bộ Ví và Giao dịch MMO):")
        cur_rates = settings.get("ty_gia", DEFAULT_EXCHANGE_RATES.copy())
        r_c1, r_c2, r_c3 = st.columns(3)
        with r_c1:
            ten_dn = st.text_input("Tên Tổ chức / Team MMO:", value=settings.get("ten_doanh_nghiep", "Alpha MMO Media Group"))
            r_usd = st.number_input("Tỷ giá USD ➔ VND:", min_value=1000.0, value=float(cur_rates.get("USD", 25450.0)), step=50.0)
        with r_c2:
            chu_sh = st.text_input("Người quản trị (Owner):", value=settings.get("chu_so_huu", "Admin"))
            r_usdt = st.number_input("Tỷ giá USDT (P2P) ➔ VND:", min_value=1000.0, value=float(cur_rates.get("USDT", 25680.0)), step=50.0)
        with r_c3:
            theme_sel = st.selectbox("Giao diện hiển thị:", options=["Dark Cyber-FinTech", "Light Clean SaaS"], index=0 if "Dark" in settings.get("theme_mode", "Dark") else 1)
            r_eur = st.number_input("Tỷ giá EUR ➔ VND:", min_value=1000.0, value=float(cur_rates.get("EUR", 27500.0)), step=50.0)

        if st.button("💾 Lưu Cấu Hình & Tỷ Giá", type="primary"):
            settings["ten_doanh_nghiep"] = ten_dn
            settings["chu_so_huu"] = chu_sh
            settings["theme_mode"] = theme_sel
            settings["ty_gia"]["USD"] = r_usd
            settings["ty_gia"]["USDT"] = r_usdt
            settings["ty_gia"]["EUR"] = r_eur
            luu_cai_dat(settings)
            ghi_nhat_ky("UPDATE_SETTINGS", f"Cập nhật tỷ giá USD={r_usd:,.0f}, USDT={r_usdt:,.0f}", 0, "INFO")
            st.success("✅ Đã lưu cấu hình hệ thống & tỷ giá mới!")
            st.rerun()

    with tab_backup:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.markdown("#### 🚀 Trình Tạo Dữ Liệu Mẫu MMO Chuyên Nghiệp")
            st.write("Bơm tự động 12 giao dịch thực tế (Facebook Ads, TikTok Shop, ClickBank Payout, VIA/BM, Proxy, Antidetect, Cashback) vào `so_hoan_chinh.json`:")
            if st.button("✨ Nạp Thêm 12 Giao Dịch Mẫu MMO Vào Sổ Cái", type="primary", use_container_width=True):
                cnt = seed_mmo_enterprise_data(append_mode=True)
                st.success(f"✅ Đã nạp thêm {cnt} giao dịch mẫu MMO thành công!")
                st.rerun()

            if st.button("🔄 Làm Mới Toàn Bộ Về Bộ Mẫu Chuẩn (Reset & Seed)", use_container_width=True):
                cnt = seed_mmo_enterprise_data(append_mode=False)
                st.success(f"✅ Đã làm mới sổ cái với {cnt} giao dịch mẫu chuẩn!")
                st.rerun()

        with b_col2:
            st.markdown("#### 📥 Khôi Phục Sổ Cái Từ File JSON (Import `so_hoan_chinh.json`)")
            uploaded_json = st.file_uploader("Chọn file JSON sao lưu để khôi phục:", type=["json"])
            if uploaded_json is not None:
                if st.button("⚡ Xác Nhận Khôi Phục Dữ Liệu Từ File Upload", type="primary"):
                    try:
                        raw_imported = json.loads(uploaded_json.read().decode("utf-8"))
                        if isinstance(raw_imported, list):
                            luu_file(raw_imported)
                            ghi_nhat_ky("IMPORT_JSON", f"Khôi phục {len(raw_imported)} bản ghi từ file JSON", 0, "SUCCESS")
                            st.success(f"✅ Đã khôi phục thành công {len(raw_imported)} khoản giao dịch!")
                            st.rerun()
                        else:
                            st.error("File JSON phải chứa danh sách (Array/List) các khoản chi tiêu!")
                    except Exception as ex:
                        st.error(f"Lỗi đọc file JSON: {ex}")


# ==============================================================================
# 18. HÀM CHÍNH ĐIỀU PHỐI TOÀN BỘ ỨNG DỤNG (MAIN APPLICATION CONTROLLER)
# ==============================================================================

def main() -> None:
    """
    Điểm khởi chạy trung tâm của ứng dụng Quản Lý Chi Tiêu & Tài Chính MMO Pro.
    Đảm bảo giữ nguyên biến `ds_ct = doc_file()` và `menu = st.sidebar.radio(...)`
    với 4 tùy chọn đầu tiên khớp chính xác 100% với code gốc của người dùng,
    đồng thời mở rộng thêm 7 phân hệ MMO chuyên nghiệp.
    """
    configure_page()
    settings = doc_cai_dat()
    inject_enterprise_css(settings.get("theme_mode", "Dark Cyber-FinTech"))

    # Đọc dữ liệu cốt lõi từ file `so_hoan_chinh.json`
    ds_ct = doc_file()
    campaigns = doc_chien_dich()
    wallets = doc_danh_sach_vi()
    subs = doc_dinh_phi_mmo()
    team = doc_nhan_su_mmo()
    stats = phan_tich_tong_quan_tai_chinh(ds_ct)

    # --------------------------------------------------------------------------
    # SIDEBAR: ĐIỀU HƯỚNG & TÓM TẮT NHANH TRẠNG THÁI QUỸ MMO
    # --------------------------------------------------------------------------
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding:12px 14px; background:linear-gradient(135deg, rgba(16,185,129,0.18), rgba(59,130,246,0.18)); border-radius:12px; border:1px solid rgba(16,185,129,0.35); margin-bottom:14px;">
                <div style="font-weight:800; font-size:1.05rem; color:#10B981;">💎 QUẢN LÝ CHI TIÊU MMO</div>
                <div style="font-size:0.76rem; color:#94A3B8;">Enterprise FinTech Suite v{APP_VERSION}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        menu = st.radio(
            "Chọn thao tác: ",
            MENU_OPTIONS,
            index=0,
        )

        st.divider()
        st.markdown("#### ⚡ Tóm Tắt Nhanh Sổ Cái")
        st.metric("Tổng số khoản giao dịch", f"{len(ds_ct)} mục")
        st.metric("Tổng Chi Tiêu Vận Hành", format_vnd(stats["tong_chi"]))
        st.metric("Tổng Doanh Thu & Payout", format_vnd(stats["tong_thu_thuc_te"]))
        st.metric(
            "Lợi Nhuận Ròng (Net P&L)",
            format_vnd(stats["loi_nhuan_rong"]),
            delta=f"ROAS {stats['roas_chung']:.2f}x",
        )

        st.divider()
        if len(ds_ct) == 0:
            if st.button("🚀 Nạp Dữ Liệu Mẫu MMO", use_container_width=True, type="primary"):
                seed_mmo_enterprise_data(append_mode=True)
                st.rerun()

    # Hiển thị Thanh Ticker Tỷ Giá & Hero Header
    render_top_ticker_and_hero(settings, stats)

    # Tiêu đề chính tương thích gốc
    st.title("Quản lý chi tiêu")

    # --------------------------------------------------------------------------
    # ĐIỀU PHỐI HIỂN THỊ THEO MENU ĐƯỢC CHỌN
    # --------------------------------------------------------------------------
    if menu == " 1. Thêm khoản chi mới":
        render_module_add_transaction(ds_ct, settings, campaigns, wallets)

    elif menu == " 2. Xem toàn bộ danh sách & tổng tiền":
        render_module_view_ledger(ds_ct, stats)

    elif menu == " 3. Xoá khoản chi tiêu":
        render_module_delete_transaction(ds_ct)

    elif menu == " 4. Sửa khoản chi tiêu":
        render_module_edit_transaction(ds_ct, campaigns, wallets)

    elif menu == "📊 5. MMO Command Center (Dashboard Tổng Quan)":
        render_module_dashboard(ds_ct, stats, campaigns, wallets, subs)

    elif menu == "🚀 6. Quản lý Chiến dịch Ads & ROAS (Campaigns)":
        render_module_campaigns(campaigns, ds_ct)

    elif menu == "💳 7. Quản lý Đa Ví & Cổng Thanh Toán (Treasury)":
        render_module_wallets(wallets, ds_ct, settings)

    elif menu == "🔄 8. Tài nguyên & Định phí MMO (Proxy/VPS/Antidetect)":
        render_module_subscriptions(subs, ds_ct, settings)

    elif menu == "👥 9. Đội nhóm MMO, Lương KPI & Chia Lợi Nhuận":
        render_module_team_payroll(team, ds_ct)

    elif menu == "🎯 10. Ngân sách, Dự báo AI & Giả lập Scale ROAS":
        render_module_budget_and_simulator(ds_ct, stats)

    elif menu == "🛡️ 11. Nhật ký Bảo mật, Sao lưu & Hệ thống":
        render_module_system_and_audit(ds_ct, settings)


if __name__ == "__main__":
    main()
