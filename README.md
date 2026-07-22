# 🧹 SmartDataSanitizer — Automated Data Cleaning & Quality Suite

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

**SmartDataSanitizer**, ham ve kirli veri kümelerini (CSV) hızlı, güvenilir ve veri kaybını en aza indirecek şekilde işlemek için geliştirilmiş uçtan uca bir **Veri Temizleme ve Kalite Analiz Motorudur**. 

Bu proje; veri analizi ve veri bilimi süreçlerinde karşılaşılan **eksik veri, gürültülü metinler, çift kayıtlar ve aykırı değerler (outliers)** gibi temel problemleri otomatik olarak çözmek üzere tasarlanmıştır.

---

## 🛠️ Bu Projede Uygulanan Veri Analizi Konseptleri & Teknolojiler

Bu projeyi geliştirirken aşağıdaki veri manipülasyonu, istatistik ve yazılım prensipleri aktif olarak uygulanmıştır:

### 1. 📊 Pandas ile İleri Düzey Veri Manipülasyonu
* **Eksik Veri (Null/NaN) İmpütasyonu:** Sütun tipine ve dağılıma bağlı olarak `mean`, `median`, `zero` veya `ffill/bfill` teknikleriyle veri doldurma stratejileri.
* **Toptan Temizlik & De-duplication:** `drop_duplicates()` ve bellek boyutunu optimize eden indeks sıfırlama işlemleri.
* **Tip Dönüşümleri & Filtreleme:** Metin (`object`) ve sayısal (`numeric`) sütunların otomatik tespiti ve dinamik ayrıştırılması.

### 2. 📐 NumPy ile İstatistiki Aykırı Değer (Outlier) Analizi
* **IQR (Interquartile Range) Algoritması:** Veri setindeki aşırı uç değerleri silip veri kaybı yaşatmak yerine, $Q1$ (25. yüzdelik) ve $Q3$ (75. yüzdelik) çeyrek aralıklarını hesaplayarak veri sınırlandırma.
* **Vectorized Clipping (`np.clip`):** Alt ($Q1 - 1.5 \times IQR$) ve üst ($Q3 + 1.5 \times IQR$) sınırların dışında kalan verileri yüksek performanslı NumPy vektör operasyonlarıyla sınırlara çekme.

### 3. 🛡️ Metin Temizliği & Type-Safe Regex
* **Regex ile Gürültü Temizliği:** Metin alanlarındaki istenmeyen özel karakterlerin ayıklanması.
* **Runtime Hata Yönetimi (Type-Safety):** Pandas'ın varsayılan `NaN` değerlerini arka planda `float` tutmasından kaynaklanan tip hatalarını `isinstance(x, str)` kontrolleriyle engelleme.

### 4. 🎨 Streamlit & Custom UI/UX
* Glassmorphic arayüz tasarımı, özelleştirilmiş Bootstrap 5 bileşenleri ve anlık **Veri Sağlık Skoru (Data Health Score)** hesaplama metriği.

---

## 🔄 Veri İşleme Akışı (Data Cleaning Pipeline)
