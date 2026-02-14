from flask import Flask, render_template_string, request, jsonify, send_file, session, redirect, url_for
import sqlite3
from datetime import datetime
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zen-protez-lab-2025-secret-key-super-secure')

# Veritabanı yolu
DATABASE = os.environ.get('DATABASE_URL', 'zen_protez_lab.db')
if DATABASE.startswith('postgres://'):
    DATABASE = DATABASE.replace('postgres://', 'postgresql://', 1)

# Varsayılan kullanıcı bilgileri
DEFAULT_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
DEFAULT_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'zen2025')

def get_db():
    if DATABASE.endswith('.db'):
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        return sqlite3.connect('zen_protez_lab.db')

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )''')
    
    # Varsayılan admin kullanıcısı
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                  (DEFAULT_USERNAME, DEFAULT_PASSWORD, 'admin'))
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS dentists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        clinic TEXT,
        phone TEXT,
        email TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_no TEXT NOT NULL,
        dentist_name TEXT,
        job_date TEXT,
        patient_name TEXT,
        selected_services TEXT,
        total_amount REAL,
        status TEXT,
        payment_status TEXT,
        paid_amount REAL,
        remaining_amount REAL,
        notes TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        description TEXT,
        category TEXT,
        amount REAL
    )''')
    
    # Varsayılan fiyatlar
    default_prices = [
        ('Tam Protez', 0), ('Parsiyel Protez', 0), ('İmmediat Protez', 0),
        ('Tamir İşleri', 0), ('Sürgülü (Hassas Bağlantılı) Protez', 0),
        ('Ball Attachment Protez', 0), ('Dolder Barlı Protez', 0),
        ('Teleskop Kuronlu Protez', 0), ('Kafes İlavesi', 0),
        ('Kelebek Protez', 0), ('Total Protez Yumuşak Besleme', 0),
        ('Protez Tamiri', 0), ('Kafes Tamiri', 0), ('Döküm Kroşe İlavesi', 0),
        ('Büküm Kroşe İlavesi', 0), ('Sabit Yer Tutucu', 0),
        ('Hareketli Yer Tutucu', 0), ('Sürgülü Protez Lastik Değişimi', 0),
        ('Gece Plağı', 0), ('Kişisel Kaşık', 0), ('Kaide', 0),
        ('Protez Temizleme', 0), ('Diş İlavesi', 0),
        ('Daimi Ölçü Model Hazırlama', 0), ('Bilgisayar Destekli Geçici Kuron', 0),
        ('Takım Diş', 0), ('Total Protez', 0)
    ]
    
    for service, price in default_prices:
        try:
            cursor.execute('INSERT OR IGNORE INTO prices (service_name, price) VALUES (?, ?)', (service, price))
        except:
            pass
    
    conn.commit()
    conn.close()

try:
    init_db()
except:
    pass

# Login kontrolü
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giriş - Özel Zen Protez Laboratuvarı</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 400px;
            width: 100%;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            font-size: 24px;
            color: #366092;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #666;
            font-size: 14px;
        }
        
        .logo {
            font-size: 60px;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border 0.3s;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #366092;
        }
        
        .btn-login {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #366092 0%, #2a4a6f 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(54, 96, 146, 0.4);
        }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .login-info {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 13px;
            color: #666;
        }
        
        .login-info strong {
            color: #366092;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <div class="logo">🦷</div>
            <h1>Özel Zen Protez Laboratuvarı</h1>
            <p>Güvenli Giriş</p>
        </div>
        
        {% if error %}
        <div class="alert alert-error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label>Kullanıcı Adı</label>
                <input type="text" name="username" required autofocus>
            </div>
            
            <div class="form-group">
                <label>Şifre</label>
                <input type="password" name="password" required>
            </div>
            
            <button type="submit" class="btn-login">🔐 Giriş Yap</button>
        </form>
        
        <div class="login-info">
            <strong>💡 İlk Giriş Bilgileri:</strong><br>
            Kullanıcı Adı: <strong>admin</strong><br>
            Şifre: <strong>zen2025</strong><br>
            <small>(Giriş yaptıktan sonra değiştirebilirsiniz)</small>
        </div>
    </div>
</body>
</html>
'''

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Özel Zen Protez Laboratuvarı</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #366092 0%, #2a4a6f 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-left h1 {
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .header-left p {
            font-size: 12px;
            opacity: 0.9;
        }
        
        .header-right {
            text-align: right;
        }
        
        .user-info {
            font-size: 13px;
            margin-bottom: 8px;
        }
        
        .btn-logout {
            padding: 8px 16px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid white;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-logout:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .tabs {
            display: flex;
            background: #f5f5f5;
            border-bottom: 3px solid #366092;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .tab {
            padding: 12px 15px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 13px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            white-space: nowrap;
            flex-shrink: 0;
        }
        
        .tab:hover {
            background: #e0e0e0;
        }
        
        .tab.active {
            background: #366092;
            color: white;
        }
        
        .tab-content {
            padding: 20px;
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        
        .stat-card .value {
            font-size: 24px;
            font-weight: bold;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            color: #333;
            font-size: 13px;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #366092;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 12px;
            margin: 15px 0;
            max-height: 400px;
            overflow-y: auto;
            padding: 12px;
            background: #f9f9f9;
            border-radius: 10px;
        }
        
        .service-item {
            display: flex;
            align-items: center;
            padding: 10px;
            background: white;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s;
        }
        
        .service-item:hover {
            border-color: #366092;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .service-item input[type="checkbox"] {
            width: 18px;
            height: 18px;
            margin-right: 10px;
            cursor: pointer;
        }
        
        .service-item label {
            flex: 1;
            cursor: pointer;
            font-size: 13px;
        }
        
        .total-display {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 15px 0;
        }
        
        .total-display h3 {
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .total-display .amount {
            font-size: 28px;
            font-weight: bold;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #366092 0%, #2a4a6f 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(54, 96, 146, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 13px;
        }
        
        th {
            background: #366092;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }
        
        .badge-success {
            background: #4CAF50;
            color: white;
        }
        
        .badge-warning {
            background: #FF9800;
            color: white;
        }
        
        .badge-danger {
            background: #f44336;
            color: white;
        }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin: 12px 0;
            font-size: 13px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #366092;
            margin: 20px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 3px solid #366092;
        }
        
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                text-align: center;
            }
            .header-right {
                margin-top: 15px;
                text-align: center;
            }
            .header h1 {
                font-size: 18px;
            }
            .stat-card .value {
                font-size: 20px;
            }
            .total-display .amount {
                font-size: 24px;
            }
            .services-grid {
                grid-template-columns: 1fr;
            }
            table {
                font-size: 11px;
            }
            th, td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1>🦷 ÖZEL ZEN HAREKETLİ DİŞ PROTEZ LABORATUVARI</h1>
                <p>Profesyonel Laboratuvar Yönetim Sistemi - Güvenli Erişim</p>
            </div>
            <div class="header-right">
                <div class="user-info">👤 {{ username }}</div>
                <button class="btn-logout" onclick="window.location.href='/logout'">🚪 Çıkış</button>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('dashboard')">📊 Panel</button>
            <button class="tab" onclick="showTab('newjob')">➕ Yeni İş</button>
            <button class="tab" onclick="showTab('jobs')">📋 İşler</button>
            <button class="tab" onclick="showTab('dentists')">👨‍⚕️ Hekimler</button>
            <button class="tab" onclick="showTab('prices')">💰 Fiyatlar</button>
            <button class="tab" onclick="showTab('expenses')">💸 Giderler</button>
            <button class="tab" onclick="showTab('reports')">📈 Rapor</button>
        </div>
        
        <!-- Önceki HTML içeriği aynı kalacak, sadece header değişti -->
        <div id="dashboard" class="tab-content active">
            <h2 class="section-title">Genel Durum</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3>Toplam İş</h3>
                    <div class="value" id="stat-total">0</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);">
                    <h3>Bekleyen İş</h3>
                    <div class="value" id="stat-pending">0</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);">
                    <h3>Tahsil Edilen</h3>
                    <div class="value" id="stat-paid">0 ₺</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);">
                    <h3>Tahsil Edilecek</h3>
                    <div class="value" id="stat-remaining">0 ₺</div>
                </div>
            </div>
            <button class="btn btn-primary" onclick="loadDashboard()">🔄 Verileri Yenile</button>
        </div>
        
        <!-- Diğer sekmeler önceki haliyle aynı -->
        <div id="newjob" class="tab-content">
            <h2 class="section-title">Yeni İş Kaydı</h2>
            <div id="jobAlert"></div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>İş No *</label>
                    <input type="text" id="jobNo" placeholder="001">
                </div>
                <div class="form-group">
                    <label>Tarih *</label>
                    <input type="date" id="jobDate">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Diş Hekimi *</label>
                    <select id="jobDentist">
                        <option value="">Seçiniz...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Hasta Adı *</label>
                    <input type="text" id="jobPatient" placeholder="Hasta adı">
                </div>
            </div>
            
            <h3 class="section-title">Yapılacak İşlemler (Çoklu Seçim)</h3>
            <div class="services-grid" id="servicesGrid"></div>
            
            <div class="total-display">
                <h3>TOPLAM TUTAR</h3>
                <div class="amount" id="totalAmount">0 ₺</div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>İş Durumu</label>
                    <select id="jobStatus">
                        <option value="Alındı">Alındı</option>
                        <option value="Yapımda">Yapımda</option>
                        <option value="Teslim Edildi">Teslim Edildi</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Ödeme Durumu</label>
                    <select id="paymentStatus">
                        <option value="Bekliyor">Bekliyor</option>
                        <option value="Kısmi Ödendi">Kısmi Ödendi</option>
                        <option value="Tamamı Ödendi">Tamamı Ödendi</option>
                    </select>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Ödenen Tutar</label>
                    <input type="number" id="paidAmount" value="0" step="0.01">
                </div>
                <div class="form-group">
                    <label>Notlar</label>
                    <input type="text" id="jobNotes" placeholder="Ekstra notlar...">
                </div>
            </div>
            
            <button class="btn btn-success" onclick="saveJob()" style="width: 100%; margin-top: 15px; padding: 15px;">
                💾 İşi Kaydet
            </button>
        </div>
        
        <div id="jobs" class="tab-content">
            <h2 class="section-title">Tüm İşler</h2>
            <button class="btn btn-primary" onclick="loadJobs()">🔄 Yenile</button>
            <div style="overflow-x: auto;">
                <table id="jobsTable">
                    <thead>
                        <tr>
                            <th>İş No</th>
                            <th>Tarih</th>
                            <th>Hasta</th>
                            <th>Hekim</th>
                            <th>Tutar</th>
                            <th>Ödenen</th>
                            <th>Kalan</th>
                            <th>Ödeme</th>
                            <th>Durum</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div id="dentists" class="tab-content">
            <h2 class="section-title">Diş Hekimi Ekle</h2>
            <div id="dentistAlert"></div>
            <div class="form-row">
                <div class="form-group">
                    <label>Ad Soyad *</label>
                    <input type="text" id="dentistName" placeholder="Dr. Ahmet Yılmaz">
                </div>
                <div class="form-group">
                    <label>Klinik</label>
                    <input type="text" id="dentistClinic" placeholder="Smile Dental">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Telefon</label>
                    <input type="text" id="dentistPhone" placeholder="0532 123 4567">
                </div>
                <div class="form-group">
                    <label>E-posta</label>
                    <input type="email" id="dentistEmail" placeholder="ornek@email.com">
                </div>
            </div>
            <button class="btn btn-success" onclick="addDentist()">➕ Diş Hekimi Ekle</button>
            
            <h3 class="section-title">Kayıtlı Diş Hekimleri</h3>
            <div style="overflow-x: auto;">
                <table id="dentistsTable">
                    <thead>
                        <tr>
                            <th>Ad Soyad</th>
                            <th>Klinik</th>
                            <th>Telefon</th>
                            <th>E-posta</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div id="prices" class="tab-content">
            <h2 class="section-title">Fiyat Listesi</h2>
            <p style="color: #666; margin-bottom: 15px; font-size: 13px;">Fiyat değiştirmek için tabloda tıklayın</p>
            <div style="overflow-x: auto;">
                <table id="pricesTable">
                    <thead>
                        <tr>
                            <th>İşlem Adı</th>
                            <th>Fiyat (₺)</th>
                            <th>İşlem</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div id="expenses" class="tab-content">
            <h2 class="section-title">Yeni Gider Ekle</h2>
            <div id="expenseAlert"></div>
            <div class="form-row">
                <div class="form-group">
                    <label>Tarih *</label>
                    <input type="date" id="expenseDate">
                </div>
                <div class="form-group">
                    <label>Kategori *</label>
                    <select id="expenseCategory">
                        <option value="Sıcak Akrilik">Sıcak Akrilik</option>
                        <option value="Alçı">Alçı</option>
                        <option value="Mum">Mum</option>
                        <option value="Takım Diş">Takım Diş</option>
                        <option value="Elektrik">Elektrik</option>
                        <option value="Su">Su</option>
                        <option value="Kira">Kira</option>
                        <option value="Muhasebe Ödemesi">Muhasebe Ödemesi</option>
                        <option value="Telefon Faturaları">Telefon Faturaları</option>
                        <option value="Diğer">Diğer</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Tutar *</label>
                    <input type="number" id="expenseAmount" step="0.01" placeholder="0.00">
                </div>
                <div class="form-group">
                    <label>Açıklama</label>
                    <input type="text" id="expenseDesc" placeholder="Detaylı açıklama...">
                </div>
            </div>
            <button class="btn btn-success" onclick="addExpense()">➕ Gider Ekle</button>
            
            <h3 class="section-title">Gider Listesi</h3>
            <div style="overflow-x: auto;">
                <table id="expensesTable">
                    <thead>
                        <tr>
                            <th>Tarih</th>
                            <th>Kategori</th>
                            <th>Tutar</th>
                            <th>Açıklama</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div id="reports" class="tab-content">
            <h2 class="section-title">Raporlar ve Excel Aktarımı</h2>
            <div style="text-align: center; padding: 30px;">
                <button class="btn btn-success" onclick="exportExcel()" style="font-size: 16px; padding: 18px 40px; margin: 10px;">
                    📊 Excel'e Aktar
                </button>
            </div>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('jobDate').valueAsDate = new Date();
            document.getElementById('expenseDate').valueAsDate = new Date();
            loadDashboard();
            loadDentists();
            loadServices();
            loadPrices();
        });
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'jobs') loadJobs();
            if (tabName === 'dentists') loadDentistsList();
            if (tabName === 'expenses') loadExpenses();
        }
        
        function loadDashboard() {
            fetch('/api/dashboard')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('stat-total').textContent = data.total_jobs;
                    document.getElementById('stat-pending').textContent = data.pending_jobs;
                    document.getElementById('stat-paid').textContent = data.paid.toLocaleString('tr-TR') + ' ₺';
                    document.getElementById('stat-remaining').textContent = data.remaining.toLocaleString('tr-TR') + ' ₺';
                });
        }
        
        function loadDentists() {
            fetch('/api/dentists')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('jobDentist');
                    select.innerHTML = '<option value="">Seçiniz...</option>';
                    data.forEach(d => {
                        select.innerHTML += `<option value="${d.name}">${d.name}</option>`;
                    });
                });
        }
        
        function loadServices() {
            fetch('/api/prices')
                .then(r => r.json())
                .then(data => {
                    const grid = document.getElementById('servicesGrid');
                    grid.innerHTML = '';
                    data.forEach(s => {
                        grid.innerHTML += `
                            <div class="service-item">
                                <input type="checkbox" id="service_${s.id}" onchange="calculateTotal()">
                                <label for="service_${s.id}">${s.service_name} - ${s.price.toLocaleString('tr-TR')} ₺</label>
                            </div>
                        `;
                    });
                    window.servicesData = data;
                });
        }
        
        function calculateTotal() {
            let total = 0;
            window.servicesData.forEach(s => {
                if (document.getElementById('service_' + s.id).checked) {
                    total += s.price;
                }
            });
            document.getElementById('totalAmount').textContent = total.toLocaleString('tr-TR') + ' ₺';
        }
        
        function saveJob() {
            const selected = [];
            window.servicesData.forEach(s => {
                if (document.getElementById('service_' + s.id).checked) {
                    selected.push(s.service_name);
                }
            });
            
            const data = {
                job_no: document.getElementById('jobNo').value,
                dentist_name: document.getElementById('jobDentist').value,
                job_date: document.getElementById('jobDate').value,
                patient_name: document.getElementById('jobPatient').value,
                selected_services: JSON.stringify(selected),
                total_amount: parseFloat(document.getElementById('totalAmount').textContent.replace(/[^\d,]/g, '').replace(',', '.')),
                status: document.getElementById('jobStatus').value,
                payment_status: document.getElementById('paymentStatus').value,
                paid_amount: parseFloat(document.getElementById('paidAmount').value),
                notes: document.getElementById('jobNotes').value
            };
            
            if (!data.job_no || !data.dentist_name || !data.patient_name || selected.length === 0) {
                showAlert('jobAlert', 'Lütfen tüm zorunlu alanları doldurun!', 'error');
                return;
            }
            
            data.remaining_amount = data.total_amount - data.paid_amount;
            
            fetch('/api/jobs', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(r => r.json()).then(result => {
                showAlert('jobAlert', 'İş başarıyla kaydedildi!', 'success');
                clearJobForm();
                loadDashboard();
            });
        }
        
        function clearJobForm() {
            document.getElementById('jobNo').value = '';
            document.getElementById('jobPatient').value = '';
            document.getElementById('jobDentist').value = '';
            document.getElementById('paidAmount').value = '0';
            document.getElementById('jobNotes').value = '';
            window.servicesData.forEach(s => {
                document.getElementById('service_' + s.id).checked = false;
            });
            calculateTotal();
        }
        
        function loadJobs() {
            fetch('/api/jobs')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.querySelector('#jobsTable tbody');
                    tbody.innerHTML = '';
                    data.forEach(j => {
                        const paymentBadge = j.payment_status === 'Tamamı Ödendi' ? 'badge-success' : 
                                           j.payment_status === 'Kısmi Ödendi' ? 'badge-warning' : 'badge-danger';
                        tbody.innerHTML += `
                            <tr>
                                <td>${j.job_no}</td>
                                <td>${j.job_date}</td>
                                <td>${j.patient_name}</td>
                                <td>${j.dentist_name}</td>
                                <td>${j.total_amount.toLocaleString('tr-TR')} ₺</td>
                                <td>${j.paid_amount.toLocaleString('tr-TR')} ₺</td>
                                <td>${j.remaining_amount.toLocaleString('tr-TR')} ₺</td>
                                <td><span class="badge ${paymentBadge}">${j.payment_status}</span></td>
                                <td>${j.status}</td>
                            </tr>
                        `;
                    });
                });
        }
        
        function addDentist() {
            const data = {
                name: document.getElementById('dentistName').value,
                clinic: document.getElementById('dentistClinic').value,
                phone: document.getElementById('dentistPhone').value,
                email: document.getElementById('dentistEmail').value
            };
            
            if (!data.name) {
                showAlert('dentistAlert', 'Ad Soyad zorunludur!', 'error');
                return;
            }
            
            fetch('/api/dentists', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(r => r.json()).then(result => {
                showAlert('dentistAlert', 'Diş hekimi eklendi!', 'success');
                document.getElementById('dentistName').value = '';
                document.getElementById('dentistClinic').value = '';
                document.getElementById('dentistPhone').value = '';
                document.getElementById('dentistEmail').value = '';
                loadDentists();
                loadDentistsList();
            });
        }
        
        function loadDentistsList() {
            fetch('/api/dentists')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.querySelector('#dentistsTable tbody');
                    tbody.innerHTML = '';
                    data.forEach(d => {
                        tbody.innerHTML += `
                            <tr>
                                <td>${d.name}</td>
                                <td>${d.clinic || '-'}</td>
                                <td>${d.phone || '-'}</td>
                                <td>${d.email || '-'}</td>
                            </tr>
                        `;
                    });
                });
        }
        
        function loadPrices() {
            fetch('/api/prices')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.querySelector('#pricesTable tbody');
                    tbody.innerHTML = '';
                    data.forEach(p => {
                        tbody.innerHTML += `
                            <tr>
                                <td>${p.service_name}</td>
                                <td>${p.price.toLocaleString('tr-TR')} ₺</td>
                                <td><button class="btn btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="editPrice(${p.id}, '${p.service_name}', ${p.price})">Düzenle</button></td>
                            </tr>
                        `;
                    });
                });
        }
        
        function editPrice(id, name, currentPrice) {
            const newPrice = prompt(`${name}\n\nYeni fiyat girin:`, currentPrice);
            if (newPrice !== null) {
                fetch('/api/prices/' + id, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({price: parseFloat(newPrice)})
                }).then(r => r.json()).then(result => {
                    loadPrices();
                    loadServices();
                    alert('Fiyat güncellendi!');
                });
            }
        }
        
        function addExpense() {
            const data = {
                date: document.getElementById('expenseDate').value,
                category: document.getElementById('expenseCategory').value,
                amount: parseFloat(document.getElementById('expenseAmount').value),
                description: document.getElementById('expenseDesc').value
            };
            
            if (!data.date || !data.amount || data.amount <= 0) {
                showAlert('expenseAlert', 'Tarih ve tutar zorunludur!', 'error');
                return;
            }
            
            fetch('/api/expenses', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(r => r.json()).then(result => {
                showAlert('expenseAlert', 'Gider eklendi!', 'success');
                document.getElementById('expenseAmount').value = '';
                document.getElementById('expenseDesc').value = '';
                loadExpenses();
            });
        }
        
        function loadExpenses() {
            fetch('/api/expenses')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.querySelector('#expensesTable tbody');
                    tbody.innerHTML = '';
                    data.forEach(e => {
                        tbody.innerHTML += `
                            <tr>
                                <td>${e.date}</td>
                                <td>${e.category}</td>
                                <td>${e.amount.toLocaleString('tr-TR')} ₺</td>
                                <td>${e.description || '-'}</td>
                            </tr>
                        `;
                    });
                });
        }
        
        function exportExcel() {
            window.location.href = '/export/excel';
        }
        
        function showAlert(elementId, message, type) {
            const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
            document.getElementById(elementId).innerHTML = `<div class="alert ${alertClass}">${message}</div>`;
            setTimeout(() => {
                document.getElementById(elementId).innerHTML = '';
            }, 3000);
        }
    </script>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Kullanıcı adı veya şifre hatalı!')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template_string(HTML_TEMPLATE, username=session.get('username', 'Kullanıcı'))

# API routes (önceki gibi ama login_required eklenmiş)
@app.route('/api/dashboard')
@login_required
def dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    total = cursor.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
    pending = cursor.execute("SELECT COUNT(*) FROM jobs WHERE status != 'Teslim Edildi'").fetchone()[0]
    paid = cursor.execute('SELECT SUM(paid_amount) FROM jobs').fetchone()[0] or 0
    remaining = cursor.execute('SELECT SUM(remaining_amount) FROM jobs').fetchone()[0] or 0
    
    conn.close()
    return jsonify({
        'total_jobs': total,
        'pending_jobs': pending,
        'paid': paid,
        'remaining': remaining
    })

@app.route('/api/dentists', methods=['GET', 'POST'])
@login_required
def dentists():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        cursor.execute('INSERT INTO dentists (name, clinic, phone, email) VALUES (?, ?, ?, ?)',
                      (data['name'], data.get('clinic'), data.get('phone'), data.get('email')))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    cursor.execute('SELECT id, name, clinic, phone, email FROM dentists ORDER BY name')
    dentists = [{'id': r[0], 'name': r[1], 'clinic': r[2], 'phone': r[3], 'email': r[4]} 
                for r in cursor.fetchall()]
    conn.close()
    return jsonify(dentists)

@app.route('/api/prices', methods=['GET'])
@login_required
def get_prices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, service_name, price FROM prices ORDER BY service_name')
    prices = [{'id': r[0], 'service_name': r[1], 'price': r[2]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(prices)

@app.route('/api/prices/<int:price_id>', methods=['PUT'])
@login_required
def update_price(price_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE prices SET price = ? WHERE id = ?', (data['price'], price_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        cursor.execute('''INSERT INTO jobs 
            (job_no, dentist_name, job_date, patient_name, selected_services, 
             total_amount, status, payment_status, paid_amount, remaining_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (data['job_no'], data['dentist_name'], data['job_date'], data['patient_name'],
             data['selected_services'], data['total_amount'], data['status'],
             data['payment_status'], data['paid_amount'], data['remaining_amount'], data.get('notes', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    cursor.execute('''SELECT job_no, job_date, patient_name, dentist_name, 
                            total_amount, paid_amount, remaining_amount, payment_status, status
                     FROM jobs ORDER BY id DESC''')
    jobs = [{'job_no': r[0], 'job_date': r[1], 'patient_name': r[2], 'dentist_name': r[3],
             'total_amount': r[4], 'paid_amount': r[5], 'remaining_amount': r[6],
             'payment_status': r[7], 'status': r[8]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(jobs)

@app.route('/api/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        cursor.execute('INSERT INTO expenses (date, description, category, amount) VALUES (?, ?, ?, ?)',
                      (data['date'], data.get('description', ''), data['category'], data['amount']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    cursor.execute('SELECT date, category, amount, description FROM expenses ORDER BY id DESC')
    expenses = [{'date': r[0], 'category': r[1], 'amount': r[2], 'description': r[3]} 
                for r in cursor.fetchall()]
    conn.close()
    return jsonify(expenses)

@app.route('/export/excel')
@login_required
def export_excel():
    wb = Workbook()
    ws_jobs = wb.active
    ws_jobs.title = "İşler"
    
    headers = ['İş No', 'Tarih', 'Diş Hekimi', 'Hasta', 'Toplam', 'Ödenen', 'Kalan', 'Ödeme Durumu', 'Durum']
    for col, header in enumerate(headers, 1):
        cell = ws_jobs.cell(1, col, header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT job_no, job_date, dentist_name, patient_name, total_amount, paid_amount, remaining_amount, payment_status, status FROM jobs')
    
    for row_idx, row in enumerate(cursor.fetchall(), 2):
        for col_idx, value in enumerate(row, 1):
            ws_jobs.cell(row_idx, col_idx, value)
    
    conn.close()
    
    filename = f'zen_protez_rapor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    wb.save(filename)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
