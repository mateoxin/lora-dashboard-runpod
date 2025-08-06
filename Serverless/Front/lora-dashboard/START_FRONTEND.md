# 🚀 **Jak uruchomić Frontend po instalacji Node.js**

## 📋 **Kroki:**

### 1. **Sprawdź instalację Node.js:**
```bash
node --version  # Should show v18+ or v20+
npm --version   # Should show 8+ or 9+
```

### 2. **Przejdź do folderu frontend:**
```bash
cd /Users/mateuszmoczulski/Documents/Repos/Serverless/Front/lora-dashboard
```

### 3. **Zainstaluj dependencies (jeśli potrzeba):**
```bash
npm install
```

### 4. **Uruchom frontend - WYBIERZ TRYB:**

#### 🔥 **RunPod Production Mode (RECOMMENDED):**
```bash
npm run start:runpod
```
- Łączy się z RunPod endpoint: `x64wt6hgrh9sai`
- Używa prawdziwego tokena: `rpa_368WKEP3YB46OY691TYZFO4GZ2DTDQ081NUCICGEi5luyf`
- URL: http://localhost:4200

#### 🏠 **Local Development Mode:**
```bash
npm run start:local
```
- Localhost development
- URL: http://localhost:4200

#### 🧪 **Mock Mode (for testing UI):**
```bash
npm run start:mock
```
- Fake data, no real backend calls
- URL: http://localhost:4200

### 5. **Otwórz browser:**
Frontend będzie dostępny na: **http://localhost:4200**

---

## ✅ **NAJLEPSZY WYBÓR:**
```bash
npm run start:runpod
```

**Ten tryb łączy frontend z twoim działającym RunPod backend! 🚀**