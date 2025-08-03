# 🧪 Simple Backend Test Suite

Testy dla minimalnego RunPod backendu.

## Cel
Sprawdzić czy RunPod Serverless w ogóle działa z najprostszym możliwym backendem.

## Konfiguracja

1. **Build & Deploy Backend:**
   ```bash
   cd ../SimpleBackend
   chmod +x build_and_deploy.sh
   ./build_and_deploy.sh
   ```

2. **Stwórz RunPod Endpoint:**
   - Docker Image: `mateoxin/simple-runpod-test:v1`
   - Min Workers: 1, Max Workers: 1
   - Container Disk: 5 GB, Memory: 4096 MB

3. **Update Test Script:**
   ```python
   # W test_simple_backend.py zmień:
   ENDPOINT_ID = "your-endpoint-id-here"
   ```

## Uruchomienie Testów

```bash
cd SimpleTest
pip install -r requirements.txt
python test_simple_backend.py
```

## Typy Testów

1. **Endpoint Health** - Sprawdza dostępność endpoint
2. **Health Job** - Test job typu "health"
3. **Ping Job** - Test job typu "ping" 
4. **Echo Job** - Test odbicia danych
5. **Slow Job** - Test 2s job
6. **Unknown Job** - Test obsługi nieznanych typów

## Oczekiwane Wyniki

✅ **Sukces:** Wszystkie 6 testów PASS  
⚠️ **Częściowy:** 3-5 testów PASS  
❌ **Błąd:** 0-2 testy PASS  

## Diagnostyka

### Jeśli żaden test nie przechodzi:
- Sprawdź endpoint ID
- Sprawdź RunPod token
- Sprawdź czy endpoint ma aktywnych workerów

### Jeśli endpoint health PASS ale job testy FAIL:
- Problem z container startup
- Sprawdź worker logs w RunPod Console

### Jeśli niektóre job testy PASS:
- Backend działa częściowo
- Sprawdź konkretne błędy w output

## Pliki Wyjściowe

- `simple_test_results.json` - Szczegółowe wyniki testów
- Logs w konsoli z timestampami 