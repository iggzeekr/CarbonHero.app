# Carbon Hero Upload

Bu proje, karbon ayak izini takip eden bir mobil uygulama ve backend API'sini içerir.

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

## 🤝 Katkıda Bulunma
1. Fork yapın
2. Feature branch oluşturun
3. Commit yapın
4. Push yapın
5. Pull Request açın

## 📄 Lisans
Bu proje MIT lisansı altında lisanslanmıştır. 