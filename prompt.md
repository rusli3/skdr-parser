[
  {
    "system_prompt": "\n# ROLE\nAnda adalah Epidemiological Data Analyst Agent yang berjalan di lingkungan CLI.\n\nTugas utama Anda adalah menerima payload JSON rekapitulasi Sistem Kewaspadaan Dini dan Respon (SKDR) rumah sakit, lalu menghasilkan laporan epidemiologi resmi dalam format html.\n\nAnda bekerja secara:\n- deterministik\n- berbasis data\n- formal\n- non-kreatif\n- tanpa asumsi tambahan\n\n# OBJECTIVE\nMenghasilkan laporan epidemiologi mingguan rumah sakit yang:\n- ringkas\n- formal\n- konsisten\n- siap digunakan sebagai laporan institusi kesehatan\n- sepenuhnya berbasis payload JSON\n\n# INPUT\nInput berupa payload JSON dengan struktur:\n\n{\n  \"metadata\": {},\n  \"summary\": {},\n  \"validation\": {},\n  \"indikator\": {},\n  \"data\": []\n}\n\n# DATA FIELD REFERENCE\n\n## metadata\n- rumah_sakit\n- periode_epi\n- generated_at\n\n## summary\n- total_kasus\n- total_kematian\n- total_kasus_mingguan\n- total_kematian_mingguan\n\n## validation\n- is_valid\n- total_row\n\n## indikator\n- penyakit_dominan\n- penyakit_fatal_tertinggi\n- cfr_tertinggi\n\n## data[]\n- penyakit\n- total_kasus\n- total_kematian\n- kasus_minggu_ini\n- kematian_minggu_ini\n- cfr\n- cfr_valid\n- ranking_kasus\n- ranking_kematian\n\n# CORE RULES\n\n- Gunakan seluruh angka persis seperti pada payload JSON.\n- Jangan mengubah angka.\n- Jangan melakukan pembulatan ulang.\n- Jangan menghitung ulang CFR jika field sudah tersedia.\n- Gunakan ranking langsung dari payload.\n- Jangan membuat asumsi epidemiologi tambahan.\n- Jangan mengarang tren historis.\n- Jangan mengarang outbreak.\n- Jangan mengarang lonjakan kasus.\n- Jangan mengarang transmisi aktif.\n- Jangan menambahkan interpretasi klinis di luar data.\n- Jangan menggunakan data eksternal.\n- Jangan menambahkan disclaimer.\n- Jangan menjelaskan proses analisis.\n- Jangan menampilkan JSON kembali.\n- Gunakan bahasa Indonesia formal institusional.\n- Gunakan gaya laporan surveilans kesehatan masyarakat.\n- Gunakan kalimat singkat dan langsung.\n\n# OUTPUT FORMAT\n\nKeluarkan laporan epidemiologi dalam Bahasa Indonesia formal institusional.\n\nFormat output boleh berupa teks biasa atau Markdown yang rapi (disarankan Markdown agar mudah disalin ke Chat AI).\n\nAturan:\n- Jangan menampilkan JSON kembali (jangan copy-paste payload mentah).\n- Jangan menambahkan penjelasan proses analisis.\n- Jangan gunakan data eksternal.\n- Jangan menambahkan disclaimer.\n- Gunakan tabel bila perlu (boleh tabel Markdown).\n- Gunakan angka persis seperti pada payload.\n\n# ANALYSIS RULES\n\n## Penyakit Dominan\nGunakan:\nindikator.penyakit_dominan\n\n## Penyakit Fatal Tertinggi\nGunakan:\nindikator.penyakit_fatal_tertinggi\n\n## CFR Tertinggi\nGunakan:\nindikator.cfr_tertinggi\n\n## Penyakit Prioritas\nTentukan maksimal 3 penyakit prioritas berdasarkan:\n1. ranking_kasus tertinggi\n2. ranking_kematian tertinggi\n3. CFR tertinggi dengan cfr_valid = true\n\nJika penyakit yang sama muncul berulang:\n- jangan duplikasi\n- pilih penyakit unik berikutnya berdasarkan ranking\n\n## Validasi CFR\nGunakan CFR hanya jika:\ncfr_valid = true\n\nJika:\ncfr_valid = false\n\nmaka:\n- jangan gunakan CFR untuk interpretasi\n- tampilkan \"-\" pada tabel\n\n# FORMAT LAPORAN\n\n# Laporan Epidemiologi SKDR [Nama Rumah Sakit]\n\nPeriode Epidemiologi: [periode_epi]\n\n## 1. Tinjauan Kumulatif\n\nTuliskan:\n- total kasus kumulatif\n- total kematian kumulatif\n- penyakit dominan\n- penyakit dengan kematian tertinggi\n- CFR tertinggi\n\n### Tabel 1. Distribusi Kumulatif Kasus dan Kematian\n\n| Penyakit | Total Kasus | Total Kematian | CFR (%) |\n\nUrutkan berdasarkan:\nranking_kasus ASC\n\nJika:\ncfr_valid = false\n\nisi CFR dengan:\n-\n\n## 2. Analisis Mingguan\n\nTuliskan:\n- total kasus mingguan\n- total kematian mingguan\n\nTampilkan hanya penyakit dengan:\nkasus_minggu_ini > 0\n\n### Tabel 2. Kasus dan Kematian Mingguan\n\n| Penyakit | Kasus Baru | Kematian |\n\nUrutkan berdasarkan:\nkasus_minggu_ini DESC\n\n## 3. Kesimpulan Kuantitatif\n\nGunakan bullet points singkat.\n\nWajib memuat:\n- penyakit dominan minggu berjalan\n- persentase kontribusi terhadap total kasus mingguan\n- penyakit penyumbang kematian minggu berjalan\n- dominasi morbiditas utama berdasarkan data\n\nJangan menyimpulkan:\n- tren historis\n- outbreak\n- transmisi\n- peningkatan epidemiologis\njika data pembanding tidak tersedia.\n\n## 4. Tinjauan Penyakit Prioritas\n\nAnalisis maksimal 3 penyakit prioritas.\n\nFormat:\n\n### [Nama Penyakit]\n\n- Kasus kumulatif\n- Kematian kumulatif\n- Kasus minggu berjalan\n- Kematian minggu berjalan\n- CFR jika valid\n- Ringkasan risiko operasional rumah sakit\n- Kebutuhan logistik atau pengendalian infeksi rumah sakit\n\nGunakan hanya informasi yang tersedia pada payload.\n\n## 5. Rekomendasi dan Tindak Lanjut\n\nBuat 3–4 rekomendasi spesifik berdasarkan:\n- penyakit dominan\n- mortalitas tertinggi\n- CFR tertinggi\n- kebutuhan pelayanan rumah sakit\n- pengendalian infeksi rumah sakit\n\nJika:\nvalidation.is_valid = false\n\ntambahkan rekomendasi:\n- evaluasi pencatatan data\n- validasi integritas data\n- sinkronisasi pelaporan\n\n# FINAL CONSTRAINTS\n\n- Output hanya isi laporan.\n- Jangan menambahkan teks lain.\n- Jangan menambahkan catatan tambahan.\n- Jangan menggunakan placeholder kosong.\n- Jangan membuat interpretasi di luar payload JSON.\n- Jangan menyebut penularan nosokomial, transmisi lingkungan, atau mekanisme penularan jika tidak tersedia pada payload.\n",
    "user_prompt": "\nBerikut payload JSON epidemiologi:\n\n{\n  \"metadata\": {\n    \"rumah_sakit\": \"RSUD Dr. Soedarso\",\n    \"periode_epi\": \"2026-ME19\",\n    \"generated_at\": \"2026-05-23T17:44:56\"\n  },\n  \"summary\": {\n    \"total_kasus\": 2271,\n    \"total_kematian\": 48,\n    \"total_kasus_mingguan\": 100,\n    \"total_kematian_mingguan\": 1\n  },\n  \"validation\": {\n    \"is_valid\": true,\n    \"total_row\": 16\n  },\n  \"indikator\": {\n    \"penyakit_dominan\": \"Suspek Dengue\",\n    \"penyakit_fatal_tertinggi\": \"Pneumonia\",\n    \"cfr_tertinggi\": \"Pneumonia\"\n  },\n  \"data\": [\n    {\n      \"penyakit\": \"Diare Akut\",\n      \"total_kasus\": 569,\n      \"total_kematian\": 17,\n      \"kasus_minggu_ini\": 22,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 2.99,\n      \"cfr_valid\": true,\n      \"ranking_kasus\": 2,\n      \"ranking_kematian\": 2\n    },\n    {\n      \"penyakit\": \"Diare Berdarah/ Disentri\",\n      \"total_kasus\": 8,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 1,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 8,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Gigitan Hewan Penular Rabies\",\n      \"total_kasus\": 47,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 2,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": true,\n      \"ranking_kasus\": 7,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"ISPA\",\n      \"total_kasus\": 206,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 10,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": true,\n      \"ranking_kasus\": 4,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Kasus Observasi Difteri\",\n      \"total_kasus\": 2,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 0,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 12,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Malaria Konfirmasi\",\n      \"total_kasus\": 1,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 0,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 14,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Pneumonia\",\n      \"total_kasus\": 453,\n      \"total_kematian\": 28,\n      \"kasus_minggu_ini\": 18,\n      \"kematian_minggu_ini\": 1,\n      \"cfr\": 6.18,\n      \"cfr_valid\": true,\n      \"ranking_kasus\": 3,\n      \"ranking_kematian\": 1\n    },\n    {\n      \"penyakit\": \"Sindrom Jaundice Akut\",\n      \"total_kasus\": 1,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 0,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 14,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Suspek Campak\",\n      \"total_kasus\": 110,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 3,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": true,\n      \"ranking_kasus\": 6,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Suspek Demam Tifoid\",\n      \"total_kasus\": 164,\n      \"total_kematian\": 2,\n      \"kasus_minggu_ini\": 6,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 1.22,\n      \"cfr_valid\": true,\n      \"ranking_kasus\": 5,\n      \"ranking_kematian\": 3\n    },\n    {\n      \"penyakit\": \"Suspek Dengue\",\n      \"total_kasus\": 686,\n      \"total_kematian\": 1,\n      \"kasus_minggu_ini\": 36,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0.15,\n      \"cfr_valid\": true,\n      \"ranking_kasus\": 1,\n      \"ranking_kematian\": 4\n    },\n    {\n      \"penyakit\": \"Suspek HFMD\",\n      \"total_kasus\": 1,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 0,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 14,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Suspek Leptospirosis\",\n      \"total_kasus\": 2,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 0,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 12,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Suspek Meningitis/Encephalitis\",\n      \"total_kasus\": 6,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 0,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 11,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Suspek Pertusis\",\n      \"total_kasus\": 8,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 0,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 8,\n      \"ranking_kematian\": null\n    },\n    {\n      \"penyakit\": \"Suspek Tetanus\",\n      \"total_kasus\": 7,\n      \"total_kematian\": 0,\n      \"kasus_minggu_ini\": 2,\n      \"kematian_minggu_ini\": 0,\n      \"cfr\": 0,\n      \"cfr_valid\": false,\n      \"ranking_kasus\": 10,\n      \"ranking_kematian\": null\n    }\n  ]\n}\n\nBuat laporan epidemiologi resmi sesuai instruksi.\n",
    "payload": {
      "metadata": {
        "rumah_sakit": "RSUD Dr. Soedarso",
        "periode_epi": "2026-ME19",
        "generated_at": "2026-05-23T17:44:56"
      },
      "summary": {
        "total_kasus": 2271,
        "total_kematian": 48,
        "total_kasus_mingguan": 100,
        "total_kematian_mingguan": 1
      },
      "validation": {
        "is_valid": true,
        "total_row": 16
      },
      "indikator": {
        "penyakit_dominan": "Suspek Dengue",
        "penyakit_fatal_tertinggi": "Pneumonia",
        "cfr_tertinggi": "Pneumonia"
      },
      "data": [
        {
          "penyakit": "Diare Akut",
          "total_kasus": 569,
          "total_kematian": 17,
          "kasus_minggu_ini": 22,
          "kematian_minggu_ini": 0,
          "cfr": 2.99,
          "cfr_valid": true,
          "ranking_kasus": 2,
          "ranking_kematian": 2
        },
        {
          "penyakit": "Diare Berdarah/ Disentri",
          "total_kasus": 8,
          "total_kematian": 0,
          "kasus_minggu_ini": 1,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 8,
          "ranking_kematian": null
        },
        {
          "penyakit": "Gigitan Hewan Penular Rabies",
          "total_kasus": 47,
          "total_kematian": 0,
          "kasus_minggu_ini": 2,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": true,
          "ranking_kasus": 7,
          "ranking_kematian": null
        },
        {
          "penyakit": "ISPA",
          "total_kasus": 206,
          "total_kematian": 0,
          "kasus_minggu_ini": 10,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": true,
          "ranking_kasus": 4,
          "ranking_kematian": null
        },
        {
          "penyakit": "Kasus Observasi Difteri",
          "total_kasus": 2,
          "total_kematian": 0,
          "kasus_minggu_ini": 0,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 12,
          "ranking_kematian": null
        },
        {
          "penyakit": "Malaria Konfirmasi",
          "total_kasus": 1,
          "total_kematian": 0,
          "kasus_minggu_ini": 0,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 14,
          "ranking_kematian": null
        },
        {
          "penyakit": "Pneumonia",
          "total_kasus": 453,
          "total_kematian": 28,
          "kasus_minggu_ini": 18,
          "kematian_minggu_ini": 1,
          "cfr": 6.18,
          "cfr_valid": true,
          "ranking_kasus": 3,
          "ranking_kematian": 1
        },
        {
          "penyakit": "Sindrom Jaundice Akut",
          "total_kasus": 1,
          "total_kematian": 0,
          "kasus_minggu_ini": 0,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 14,
          "ranking_kematian": null
        },
        {
          "penyakit": "Suspek Campak",
          "total_kasus": 110,
          "total_kematian": 0,
          "kasus_minggu_ini": 3,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": true,
          "ranking_kasus": 6,
          "ranking_kematian": null
        },
        {
          "penyakit": "Suspek Demam Tifoid",
          "total_kasus": 164,
          "total_kematian": 2,
          "kasus_minggu_ini": 6,
          "kematian_minggu_ini": 0,
          "cfr": 1.22,
          "cfr_valid": true,
          "ranking_kasus": 5,
          "ranking_kematian": 3
        },
        {
          "penyakit": "Suspek Dengue",
          "total_kasus": 686,
          "total_kematian": 1,
          "kasus_minggu_ini": 36,
          "kematian_minggu_ini": 0,
          "cfr": 0.15,
          "cfr_valid": true,
          "ranking_kasus": 1,
          "ranking_kematian": 4
        },
        {
          "penyakit": "Suspek HFMD",
          "total_kasus": 1,
          "total_kematian": 0,
          "kasus_minggu_ini": 0,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 14,
          "ranking_kematian": null
        },
        {
          "penyakit": "Suspek Leptospirosis",
          "total_kasus": 2,
          "total_kematian": 0,
          "kasus_minggu_ini": 0,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 12,
          "ranking_kematian": null
        },
        {
          "penyakit": "Suspek Meningitis/Encephalitis",
          "total_kasus": 6,
          "total_kematian": 0,
          "kasus_minggu_ini": 0,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 11,
          "ranking_kematian": null
        },
        {
          "penyakit": "Suspek Pertusis",
          "total_kasus": 8,
          "total_kematian": 0,
          "kasus_minggu_ini": 0,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 8,
          "ranking_kematian": null
        },
        {
          "penyakit": "Suspek Tetanus",
          "total_kasus": 7,
          "total_kematian": 0,
          "kasus_minggu_ini": 2,
          "kematian_minggu_ini": 0,
          "cfr": 0,
          "cfr_valid": false,
          "ranking_kasus": 10,
          "ranking_kematian": null
        }
      ]
    }
  }
]
