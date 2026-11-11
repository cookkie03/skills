---
vault_name: ""
language: it
---

# Taxonomy

Fonte di verità estesa per la struttura del vault. Il CLAUDE.md la richiama;
l'AI la legge prima di creare file in cartelle non ovvie. Aggiornala quando
aggiungi una cartella nuova.

| Cartella | Contenuto | Note |
|---|---|---|
| daily-notes/ | Note giornaliere (YYYY-MM-DD.md) | |
| _raw/ | Inbox: risorse grezze da processare | Non note di lavoro; svuotala via ingest |
| _meta/ | Stato e metadati del vault | Non creare note di lavoro qui |
| <tema-1>/ | … | |
| <tema-2>/ | … | |

## Tag per tema

| Tag | Dominio |
|---|---|
| <tag> | <dominio> |

## Convenzione frontmatter

Campi obbligatori per le pagine. Se il vault ha tipi di pagina eterogenei
(es. note knowledge vs item di lista vs schede), descrivili come "famiglie".
`_meta/check-frontmatter.py` è **data-driven**: legge lo schema dal blocco
machine-readable qui sotto, perciò validare costa zero manutenzione extra.

### Schema machine-readable

```yaml
# frontmatter-schema
exclude_dirs: [_raw, _models, _meta, _scratch, node_modules]
no_fm_expected: [AGENTS.md, CLAUDE.md, GEMINI.md]
families:
  - name: generica          # fallback (match_path vuoto)
    match_path: []
    required: [title, type, created, updated]
    type_enum: [concept, list, synthesis, source, overview, meta]
    status_enum: [draft, reviewed, verified, stale, archived]
  # aggiungi qui altre famiglie per cartelle con schema proprio, es.:
  # - name: item di lista
  #   match_path: ["lists/"]
  #   required: [title, type, status, created]
  #   type_enum: [list-item]
  #   status_enum: [idea, archived]
```

Se ometti il blocco, il validatore usa un default generico equivalente alla
famiglia "generica". `exclude_dirs` è usato anche da `sync.py` per non indicizzare
le cartelle di servizio.
