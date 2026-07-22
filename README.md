# 🧹 SmartDataSanitizer — Automated Data Cleaning Suite

SmartDataSanitizer, kirli CSV verilerini analiz eden, eksik verileri işleyen, aykırı değerleri (outlier) IQR yöntemiyle baskılayan ve veri sağlık raporu sunan yüksek performanslı bir Streamlit uygulamasıdır.

## 🚀 Özellikler

- **Eksik Veri Stratejileri:** Sütun bazlı veya genel medyan, ortalama, sıfırlama veya silme seçenekleri.
- **Zeki Dişliler (Otomatik Temizlik):** 
  - Özel karakter gürültüsü temizliği (Regex).
  - Aykırı değer (Outlier) tespiti ve IQR yöntemiyle baskılama (Clipping).
  - Metin standartlaştırma (Title Case).
- **Advanced Analytics & Raporlama:** 
  - Veri Sağlık Skoru (0-100).
  - RAM / Bellek tasarruf analizi.
  - Önce / Sonra satır ve hücre karşılaştırması.

## 🛠️ Kurulum & Çalıştırma

1. Repoyu klonlayın:
   ```bash
   git clone [https://github.com/KULLANICI_ADI/SmartDataSanitizer.git](https://github.com/KULLANICI_ADI/SmartDataSanitizer.git)
   cd SmartDataSanitizer