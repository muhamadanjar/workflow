# AI Coding Skills & Agents

Kumpulan skill, panduan, dan profil agent untuk membantu pekerjaan rekayasa perangkat lunak dengan asisten AI. Materi repo mencakup backend, frontend, API, database, infrastruktur, testing, dokumentasi, dan desain sistem.

## Isi repository

- [`skills/`](skills/) — direktori skill dan panduan terkait. Metadata skill tersedia di [`skills/manifest.json`](skills/manifest.json), indeks di [`skills/INDEX.md`](skills/INDEX.md), dan matriks agent di [`skills/SKILLS_AGENTS_MATRIX.md`](skills/SKILLS_AGENTS_MATRIX.md).
- [`agents/`](agents/) — profil agent untuk peran seperti arsitektur backend/frontend, full-stack, QA, dokumentasi, dan security.
- [`scripts/`](scripts/) — utilitas, termasuk `api-standard` dan `security-scan.sh`.
- [`prd_templates/`](prd_templates/) — template PRD bahasa Indonesia dan Inggris.

## Memulai

1. Pilih topik di [indeks skill](skills/INDEX.md) atau cari ID skill di [manifest](skills/manifest.json).
2. Buka `SKILL.md` atau `skill.md` dalam direktori skill terkait untuk melihat instruksi dan panduannya.
3. Gunakan skill dan/atau profil agent yang relevan sebagai konteks pada asisten AI Anda.
4. Untuk integrasi platform, ikuti panduan di [`skills/INTEGRATION.md`](skills/INTEGRATION.md) dan pilih panduan di [`skills/adapters/`](skills/adapters/).

Contoh: untuk merancang REST API, mulai dari [`skills/api-design/SKILL.md`](skills/api-design/SKILL.md). Untuk merujuk langsung ke konten, gunakan path file panduannya dalam prompt.

## Pengembangan dan pemeriksaan

Repositori ini terutama berisi dokumen Markdown dan utilitas. Ikuti petunjuk di skill yang sedang Anda ubah; tidak ada satu perintah build atau test umum yang didokumentasikan untuk seluruh repo.

## Lisensi

Lihat [`skills/LICENSE`](skills/LICENSE) untuk informasi lisensi.
