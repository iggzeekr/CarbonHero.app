# Carbon Hero 

Bu proje, karbon ayak izini takip eden Collabrative Filtering ve Random Forest algoritmalarıyla geliştirilmiş model sayesinde hesaplamaları ve önerileri sunan  mobil uygulamadır.

## 🚀 Kurulum

### Gereksinimler
- Android Studio
- Python 3.8+
- Firebase hesabı

### Backend Kurulumu
```bash
cd backend
pip install -r requirements.txt
```

### Android Uygulaması
1. Android Studio'da projeyi açın
2. `app/google-services.json` dosyasını Firebase Console'dan indirin
3. Projeyi derleyin ve çalıştırın

## 🔐 Güvenlik

### API Anahtarları
Bu proje Firebase kullanmaktadır. Güvenlik için:

1. **Firebase Console**'dan kendi projenizi oluşturun
2. `google-services.json` dosyasını indirin
3. Bu dosyayı `app/` klasörüne yerleştirin

### Environment Variables
Backend için `.env` dosyası oluşturun:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
```

## 📱 Özellikler
- Kullanıcı kaydı ve girişi
- Karbon ayak izi hesaplama
- Veri görselleştirme
- AI destekli öneriler
- Challenge önerileri
- Oyunlaştırma

![Screenshot 2025-06-15 230915](https://github.com/user-attachments/assets/e95abf9e-9d9d-4987-b3d6-a19465722953)

