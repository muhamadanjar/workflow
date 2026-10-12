# Design Doc Grilling

Interview-driven design docs. The `grilling` skill runs the interview (design tree worked in rounds) to extract the technical context, then the result is written into the project's existing design-docs template.

## Guides

- [SKILL.md](SKILL.md) — the four phases: recon, grill, confirm, write. Phase 1 delegates to the installed `grilling` skill read-only; `grill-me` is only the user-invoked front door that runs it. Project terms are read from the repo's `CONTEXT.md`/`GLOSSARY.md` and reused verbatim — never invented, never written back. Includes when a design doc is required and the fill rules for each template section.
- [TEMPLATE.md](TEMPLATE.md) — fallback design-doc template. The target project's own `docs/design-docs/TEMPLATE.md` wins when present.

## Why both halves

A PRD says what the business wants. It does not say what breaks, what was rejected, or where the migration is irreversible. Those only come out under questioning — the installed `grilling` skill supplies that protocol (design tree, facts looked up from the repo instead of asked, decisions left to the user). This skill only adds the design-doc deltas on top: code recon first, the risk axes and rejected alternative that the template demands, and the decision log that becomes the doc. The template then makes the answers reviewable.

```
design-doc-grilling
├── Phase 0  recon (repo, PRD, code)
├── Phase 1  /grilling  ← the interview itself
├── Phase 2  confirm shared understanding
├── Phase 3  write into TEMPLATE.md
└── Phase 4  register in design-docs README, status Draft
```

## Cara pakai langkah demi langkah

1. **Persiapan** — pastikan repo target punya `docs/design-docs/` (berisi `TEMPLATE.md` dan `README.md` index). Kalau belum ada, bilang dulu; jangan memaksakan skill ini ke repo yang belum menganut design-docs.
2. **Minta** — beri satu perintah natural yang menyebut skill dan feature-nya:

   ```
   Gunakan skill design-doc-grilling untuk feature <nama feature>.
   Recon repo-nya dulu, lalu grill, baru tulis design doc-nya.
   ```

   Agent akan melakukan Phase 0 (recon: baca `AGENTS.md`, template, PRD/ticket, kode yang tersentuh, `CONTEXT.md`) *sebelum* bertanya apa pun.
3. **Saat di-grill (Phase 1)** — jawab pertanyaannya. Petunjuk untukmu:
   - Jawab sesuai fakta & keputusanmu, bukan tebakan.
   - Jangan dijawab hal yang sudah ada di repo/kode — minta agent cek sendiri. Grill adalah untuk keputusan, bukan untuk fakta.
   - Setiap pertanyaan biasanya disertai rekomendasi; kamu tetap yang memutuskan.
4. **Konfirmasi (Phase 2)** — agent memutar ulang log keputusan sebagai daftar singkat, lalu minta konfirmasi. Belum sepakat? Sebut yang salah. Agent **tidak menulis doc sebelum kamu konfirmasi** — kalau dia tulis duluan, itu bug.
5. **Baca hasilnya (Phase 3)** — doc ditulis ke `<design-docs-dir>/YYYY-MM-DD-judul-singkat.md`, `Status: Draft`, pakai bahasa dokumentasi proyek. Perhatikan:
   - Bagian yang tidak dijawab/diverifikasi ditandai `[perlu konfirmasi: ...]` — isi sendiri yang kamu tahu.
   - Seksi template tidak boleh hilang — bagian yang tak berlaku ditulis `N/A` + alasan.
   - Istilah pakai kata persis dari `CONTEXT.md`/`GLOSSARY.md` proyek.
6. **Review & status (Phase 4)** — koreksi seperlunya; kalau sudah siap, ubah `Draft → In Review` (manual, bukan skill), tunjuk reviewer, teruskan lewat PR/MR. Jangan tulis nama reviewer/tiket yang kamu tidak tahu.
7. **Setelah disetujui** — status jadi `Approved` lalu `Implemented`; doc **tidak dihapus** (keputusan `Rejected`/`Deprecated` dicatat sebagai status terminal). Update barisnya di index `README.md` design-docs.

Aturan kunci: skill berhenti di `Draft` — pergerakan status selanjutnya milik manusia. Yang tersisa `[perlu konfirmasi: ...]` disebutkan ke kamu di akhir, lengkap dengan pertanyaan terbuka yang butuh reviewer tertentu.

## Grill chain (mattpocock skills)

| Skill | Who invokes | Role |
|---|---|---|
| `grill-me` | user only (`disable-model-invocation: true`) | front door; whole content is "Run a `/grilling` session." |
| `grilling` | model | the interview primitive — this is what actually runs, as installed |
| `grill-with-docs` | user only | same interview wired to `CONTEXT.md`/ADRs — not used here |
| `design-doc-grilling` | model | adds design-doc recon + template output around `grilling` |

Integration rule: the grill skills are read-only. This skill reads and runs the installed `grilling`; it never edits, syncs, or replaces `grilling`, `grill-me`, or `grill-with-docs`. Upstream (`github.com/mattpocock/skills`) may move ahead of the installed copies; leave the installed copies untouched regardless.

Status flow: `Draft → In Review → Approved → Implemented`, with `Rejected` and `Deprecated` terminal. The skill stops at `Draft` — human review moves it forward.
