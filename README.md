# SKDR Web App

Aplikasi web untuk:
- Upload 4 file SKDR (`ALL`, `MD`, `MGU_ALL`, `MGU_MD`)
- Validasi konsistensi minggu epidemiologi
- Bentuk payload JSON (`metadata`, `summary`, `indikator`, `data`)
- Kirim payload langsung ke webhook (`application/json`)

## Jalankan

```bash
pip install -r requirements.txt
export SKDR_WEBHOOK_URL="https://your-webhook.example/webhook/..."
python app.py
```

Buka: http://localhost:5000
