import streamlit as st
import pandas as pd
import numpy as np
import io
import re

# 1. Sayfa Konfigürasyonu
st.set_page_config(
    page_title="SmartDataSanitizer — Data Cleaning Suite",
    page_icon="🧹",
    layout="wide"
)

# 2. CSS Injected (Dark Glassmorphic UI)
CUSTOM_CSS = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap" rel="stylesheet">

<style>
    :root {
        --bg-dark: #090A0F;
        --card-bg: rgba(18, 20, 29, 0.7);
        --accent-purple: #8A2BE2;
        --accent-cyan: #00F2FE;
        --text-muted: #94A3B8;
    }

    body, .stApp {
        background-color: var(--bg-dark) !important;
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-image: 
            radial-gradient(circle at 15% 20%, rgba(138, 43, 226, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 85% 80%, rgba(0, 242, 254, 0.12) 0%, transparent 40%) !important;
    }

    header, footer { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #FFFFFF 30%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--accent-cyan);
    }
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .feature-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
    }
    .feature-ring {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        border: 1px solid var(--accent-purple);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.3);
        margin-bottom: 1rem;
        color: #00F2FE;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# 3. GELİŞMİŞ TEMİZLEME MOTORU
def advanced_data_cleaner(df, global_num_strategy, custom_col_strategies, clean_special_chars, handle_outliers, capitalize_text):
    df_clean = df.copy()
    
    initial_rows = len(df_clean)
    initial_nulls = df_clean.isnull().sum().sum()
    initial_memory = df_clean.memory_usage(deep=True).sum() / 1024  # KB
    
    report_stats = {
        "duplicates_removed": 0,
        "missing_filled": 0,
        "outliers_clipped": 0,
        "special_chars_cleaned": 0,
        "initial_nulls": initial_nulls,
        "final_nulls": 0,
        "initial_rows": initial_rows,
        "final_rows": 0,
        "memory_saved_percent": 0.0,
        "health_score": 100
    }
    
    # 1. Çift Kayıtlar
    df_clean = df_clean.drop_duplicates().reset_index(drop=True)
    report_stats["duplicates_removed"] = initial_rows - len(df_clean)
    
    # 2. Metin Temizliği (Type-safe Regex & Strip)
    text_cols = df_clean.select_dtypes(include=['object', 'string']).columns
    for col in text_cols:
        df_clean[col] = df_clean[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
        if clean_special_chars:
            df_clean[col] = df_clean[col].apply(
                lambda x: re.sub(r'[^\w\s\.-]', '', x) if isinstance(x, str) else x
            )
            report_stats["special_chars_cleaned"] += 1
            
        if capitalize_text:
            df_clean[col] = df_clean[col].apply(lambda x: x.title() if isinstance(x, str) else x)
            
    # 3. Tarih Standartlaştırma
    for col in text_cols:
        try:
            converted = pd.to_datetime(df_clean[col], format="mixed", dayfirst=True, errors='coerce')
            if not converted.isnull().all():
                df_clean[col] = converted.dt.strftime("%Y-%m-%d")
        except Exception:
            pass
            
    # 4. Sayısal Eksik Veri & Özel Sütun Kuralları
    num_cols = df_clean.select_dtypes(include=['number']).columns
    
    for col in num_cols:
        strategy = custom_col_strategies.get(col, global_num_strategy)
        
        missing_count = df_clean[col].isnull().sum()
        if missing_count > 0:
            if strategy == "zero":
                df_clean[col] = df_clean[col].fillna(0)
            elif strategy == "ffill":
                df_clean[col] = df_clean[col].ffill().bfill()
            elif strategy == "median":
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            elif strategy == "mean":
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            elif strategy == "drop":
                df_clean = df_clean.dropna(subset=[col]).reset_index(drop=True)
            
            if strategy != "keep":
                report_stats["missing_filled"] += missing_count

        # 5. Aykırı Değer (Outlier) Temizliği (IQR Yöntemi)
        if handle_outliers and len(df_clean[col].dropna()) > 0:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_count = ((df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)).sum()
            if outliers_count > 0:
                df_clean[col] = np.clip(df_clean[col], lower_bound, upper_bound)
                report_stats["outliers_clipped"] += outliers_count

    # Rapor ve Metrik Hesaplamaları
    final_memory = df_clean.memory_usage(deep=True).sum() / 1024
    report_stats["final_nulls"] = df_clean.isnull().sum().sum()
    report_stats["final_rows"] = len(df_clean)
    
    if initial_memory > 0:
        report_stats["memory_saved_percent"] = max(0, round(((initial_memory - final_memory) / initial_memory) * 100, 1))
        
    null_penalty = (initial_nulls / (initial_rows * len(df.columns) + 1e-5)) * 50
    dup_penalty = (report_stats["duplicates_removed"] / (initial_rows + 1e-5)) * 50
    report_stats["health_score"] = max(10, int(100 - (null_penalty + dup_penalty)))

    return df_clean, report_stats


# 4. ARAYÜZ (HEADER)
st.markdown("""
<div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom border-secondary border-opacity-25">
    <h3 class="fw-bold m-0" style="background: linear-gradient(135deg, #FFF, #00F2FE); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        <i class="fa-solid fa-wand-magic-sparkles me-2" style="color: #00F2FE;"></i>SmartDataSanitizer
    </h3>
    <div class="badge bg-dark border border-secondary text-light rounded-pill px-3 py-2">
        <i class="fa-solid fa-bolt text-warning me-2"></i>Sıfır Kurulum & Üyeliksiz
    </div>
</div>

<div class="row align-items-center mb-4">
    <div class="col-lg-8">
        <h1 class="hero-title mb-2">Verilerinizi Saniyeler İçinde Temizleyin</h1>
        <p class="text-secondary fs-5 mb-0">
            Akıllı motorumuz aykırı değerleri baskılar, özel karakter gürültülerini temizler ve veri kalitenizi anında raporlar.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# --- ÇALIŞMA ALANI ---
col_settings, col_upload = st.columns([1, 2], gap="large")

with col_settings:
    st.markdown('<h5 class="fw-bold mb-3"><i class="fa-solid fa-sliders me-2 text-info"></i>Temizlik Ayarları</h5>', unsafe_allow_html=True)
    
    global_strategy = st.selectbox(
        "Eksik Sayısal Veri Stratejisi",
        options=["drop", "keep", "zero", "ffill", "median", "mean"],
        format_func=lambda x: {
            "drop": "🚫 Eksik Satırları Sil (Önerilen)",
            "keep": "🙈 Dokunma / Olduğu Gibi Bırak",
            "zero": "0️⃣ Sıfır (0) ile Doldur",
            "ffill": "⏩ Önceki Satırın Değeriyle Doldur",
            "median": "📊 Medyan (Ortanca Değer)",
            "mean": "📈 Ortalama Değer"
        }[x]
    )
    
    st.markdown('<h6 class="fw-bold mt-4 mb-3 text-light"><i class="fa-solid fa-gears me-2" style="color: #8A2BE2;"></i>Zeki Dişliler (Otomatik Temizlik)</h6>', unsafe_allow_html=True)
    
    clean_spec = st.toggle("Özel Karakter Gürültü Temizliği", value=True, help="Metinlerdeki garip simgeleri (@, #, $ vb.) otomatik temizler.")
    handle_out = st.toggle("Aykırı Değer (Outlier) Baskılama", value=True, help="İstatistiği bozan aşırı uç değerleri IQR yöntemiyle sınırlar.")
    cap_text = st.toggle("Metin Baş Harflerini Büyüt (Title Case)", value=True, help="Tüm metin sütunlarını Baş Harfi Büyük formata getirir.")

with col_upload:
    st.markdown('<h5 class="fw-bold mb-3"><i class="fa-solid fa-cloud-arrow-up me-2 text-primary"></i>Dosya Yükleme</h5>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Bir CSV dosyası yükleyin", type=["csv"], label_visibility="collapsed")


# 5. DOSYA YÜKLENDİĞİNDE ÇALIŞACAK MANTIK
if uploaded_file is not None:
    try:
        # Sadece CSV okuma (Dış kütüphane bağımlılığı yok)
        df_raw = pd.read_csv(uploaded_file)
            
        num_columns = df_raw.select_dtypes(include=['number']).columns.tolist()
        custom_strategies = {}

        # Sütun Bazlı Özel Ayarlar Akordeon Menüsü
        if len(num_columns) > 0:
            with st.expander("🛠️ Sütun Bazlı Özel Temizlik Kuralları Tanımla (Opsiyonel)"):
                st.caption("Genel stratejiden farklı muamele etmek istediğiniz sayısal sütunları buradan özelleştirebilirsiniz:")
                cols_grid = st.columns(min(3, len(num_columns)))
                for idx, col_name in enumerate(num_columns):
                    with cols_grid[idx % 3]:
                        choice = st.selectbox(
                            f"📌 {col_name}",
                            options=["default", "drop", "keep", "zero", "ffill", "median", "mean"],
                            format_func=lambda x: "Genel Kuralı Kullan" if x == "default" else x,
                            key=f"custom_{col_name}"
                        )
                        if choice != "default":
                            custom_strategies[col_name] = choice

        # Temizleme Motorunu Çalıştır
        df_clean, stats = advanced_data_cleaner(
            df_raw, 
            global_num_strategy=global_strategy, 
            custom_col_strategies=custom_strategies,
            clean_special_chars=clean_spec,
            handle_outliers=handle_out,
            capitalize_text=cap_text
        )
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # --- VERİ KALİTESİ & DÖNÜŞÜM RAPORU ---
        st.markdown('<h4 class="fw-bold mb-4"><i class="fa-solid fa-chart-line me-2 text-warning"></i>Gelişmiş Veri Kalite & Dönüşüm Raporu</h4>', unsafe_allow_html=True)
        
        # Üst Metrik Kartları
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="metric-val">{stats["health_score"]} / 100</div><div class="metric-label">Veri Sağlık Skoru</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="metric-val">{stats["duplicates_removed"]}</div><div class="metric-label">Silinen Çift Satır</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="metric-val">{stats["missing_filled"]}</div><div class="metric-label">İşlenen Eksik Hücre</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="metric-val">{stats["outliers_clipped"]}</div><div class="metric-label">Baskılanan Aykırı Değer</div></div>', unsafe_allow_html=True)

        st.markdown("<div class='my-3'></div>", unsafe_allow_html=True)

        # Dönüşüm Analiz Detayları
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown(f"""
            <div class="p-3 rounded-3" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);">
                <h6 class="fw-bold text-info"><i class="fa-solid fa-scale-balanced me-2"></i>Satır & Hücre Boyutu Karşılaştırması</h6>
                <ul class="list-unstyled mb-0 small text-secondary">
                    <li>• Başlangıç Satır Sayısı: <b class="text-light">{stats["initial_rows"]}</b> ➔ Temizlenen: <b class="text-success">{stats["final_rows"]}</b></li>
                    <li>• Başlangıç Boş Hücre: <b class="text-light">{stats["initial_nulls"]}</b> ➔ Kalan Boş: <b class="text-success">{stats["final_nulls"]}</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with c_right:
            st.markdown(f"""
            <div class="p-3 rounded-3" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);">
                <h6 class="fw-bold text-info"><i class="fa-solid fa-microchip me-2"></i>Sistem & Bellek (RAM) Kazanımı</h6>
                <ul class="list-unstyled mb-0 small text-secondary">
                    <li>• Bellek Tasarrufu: <b class="text-success">%{stats["memory_saved_percent"]}</b> optimize edildi.</li>
                    <li>• Özel Karakter Temizliği: <b class="text-light">{stats["special_chars_cleaned"]} metin sütununa</b> uygulandı.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Önizleme
        st.markdown('<h6 class="fw-bold text-secondary mt-4 mb-2">Temizlenmiş Veri Önizleme (İlk 10 Satır)</h6>', unsafe_allow_html=True)
        st.dataframe(df_clean.head(10), use_container_width=True)
        
        # İHRACAT / İNDİRME (SADECE CSV)
        st.markdown('<h6 class="fw-bold text-light mt-4 mb-2"><i class="fa-solid fa-download me-2 text-success"></i>Temizlenmiş Veriyi İndir</h6>', unsafe_allow_html=True)
        
        csv_bytes = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Temizlenmiş CSV Dosyasını İndir",
            data=csv_bytes,
            file_name="temizlenmis_veri.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Dosya işlenirken bir hata oluştu: {e}")

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 3rem 0 2rem 0;'>", unsafe_allow_html=True)

# ALT ÖZELLİK KARTLARI
st.markdown("""
<div class="row g-4">
    <div class="col-md-4">
        <div class="feature-card h-100">
            <div class="feature-ring">01</div>
            <h5 class="fw-bold text-light">Aykırı Değer (Outlier) Algılama</h5>
            <p class="text-secondary small mb-0">IQR analiziyle aşırı uç değerleri tespit eder ve istatistiği bozmaması için sınırlandırır.</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="feature-card h-100">
            <div class="feature-ring">02</div>
            <h5 class="fw-bold text-light">Veri Sağlık Raporlaması</h5>
            <p class="text-secondary small mb-0">Verinizin kalite skorunu, bellek optimizasyonunu ve dönüşüm oranlarını anlık hesaplar.</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="feature-card h-100">
            <div class="feature-ring">03</div>
            <h5 class="fw-bold text-light">Hızlı CSV İhracatı</h5>
            <p class="text-secondary small mb-0">Temizlenmiş verinizi standart UTF-8 kodlamasında CSV olarak saniyeler içinde indirebilirsiniz.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)