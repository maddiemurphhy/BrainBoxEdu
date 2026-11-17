# BrainBoxEdu

BrainBoxEdu is a study-aid web app: upload your lecture notes or slides, and it generates study questions that are grounded in your own material — every question comes with a source excerpt pulled from the document, and any question that can't be backed by the text is automatically dropped.

**Live site:** https://brainboxedu.vercel.app

## How it's built

This repo is a monorepo with two independent pieces:

```
BrainBoxEdu/
├── frontend/   static HTML/CSS/JS site, deployed to Vercel
└── backend/    FastAPI service that extracts text, checks confidence,
                and calls Claude to generate grounded questions
```

| Piece | Stack |
|---|---|
| `frontend/` | HTML, CSS, vanilla JS — no build step, no framework |
| `backend/` | Python, FastAPI, SQLAlchemy, Anthropic API (Claude) |

Each folder has its own README with setup instructions — start there if you want to run either piece locally:

- [`frontend/README.md`](frontend/) *(see folder for the plain HTML/CSS/JS source)*
- [`backend/README.md`](backend/README.md)

## What it does

1. **Upload** a PDF, Word doc, PowerPoint, or text file of lecture notes.
2. The backend **extracts the text** and runs a confidence check that flags material that's too thin or garbled to generate good questions from.
3. The backend sends the extracted text to **Claude** with strict grounding rules, and **drops any question that isn't backed by a real excerpt** from the source material.
4. The frontend displays the generated questions, each tied back to the part of the document it came from.

## Status

This is an in-progress solo project. The frontend is live; the backend API is still being wired up for production (it currently runs fine locally — see `backend/README.md`). Deliberately left out of this first pass: user accounts, persistent file storage, and database migrations — see the backend README for the full list and reasoning.

## License

MIT — see [LICENSE](LICENSE). Feel free to poke around, fork it, or use it as a reference for your own project.
