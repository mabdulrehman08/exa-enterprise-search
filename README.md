# Meridian — enterprise knowledge research, powered by Exa

**Why this exists:** growing companies lose answers between Slack decisions, document policies, and database status. This demo applies Exa’s purpose-built index for AI to that problem: natural-language retrieval, source content, and structured synthesis in one API call. It demonstrates the customer-solution work of a forward deployed engineer: normalize fragmented knowledge, constrain retrieval to the customer corpus, and make answers auditable.

Ask **“What is blocking the Atlas EU launch, and who owns the next steps?”** The evidence spans a Slack decision, an infrastructure update, a launch policy, and dependency tickets. An older September 30 estimate deliberately conflicts with the newer October 14 decision.

## Run in 30 seconds

Python 3.12+, no packages or build step:

```bash
cp .env.example .env
python3 app.py
```

Open **http://localhost:8000**. The default **Local preview** works without credentials: lexical retrieval and verbatim excerpts, explicitly labeled. It is an inspectable baseline, not a simulated Exa response. Try the SSO and outage questions too. Expand evidence or click a citation to read the complete record.

## Live Exa search

**The product boundary matters:** Exa’s public Search API searches its web index; it does not accept local JSON uploads or search your private Slack directly. This demo uses an indexed public mirror of **fictional** company knowledge. It makes no claim to provide a private enterprise index or real Slack/database connectors.

1. Run `python3 app.py export`. This generates `public/corpus/`: 16 HTML pages, source IDs, dates, and a linked index.
2. Publish that folder on a public HTTPS static host. For example, deploy `public/` as the publish directory on your static hosting service; the corpus URL is then your site's `/corpus` path. Do not publish real internal data. No deployment is performed by this project.
3. Set `EXA_API_KEY` and `CORPUS_BASE_URL` in `.env` or the process environment. The base URL must point to the published folder containing `index.html` and the 16 record pages. Environment variables take precedence over `.env`.
4. Ensure those pages are discoverable in Exa’s index before switching to **Exa · live AI**. Publishing alone does not guarantee indexing, and there is no fictional ingestion endpoint here. If Exa cannot find the pages, the interface reports no validated evidence. For a newly published corpus, confirm discovery with Exa before presenting a live demo.
5. Restart the app and choose **Exa · live AI**. Queries consume Exa API credits. No second LLM provider is needed.

The server calls [`POST /search`](https://exa.ai/docs/reference/search) with `type: auto`, an `includeDomains` path restriction, content and highlights, and an `outputSchema` for findings with source IDs and exact quotes. Exa supplies retrieval and AI synthesis. The server accepts only citations whose URLs exactly match known corpus pages and whose quotes occur in the local source text. Unknown sources, invented quotes, and stale quotations are discarded. Errors never silently switch to local retrieval.

Quote validation checks provenance, **not** whether an AI paraphrase is logically entailed by its quote. Review the visible evidence, especially for conflicting dates. The local preview can surface outdated excerpts because it performs no semantic reasoning. Neither mode answers unsupported questions with invented facts.

## Small by design

- `corpus/`: 6 Slack-like messages, 5 company documents, 5 database records, all JSON. Meridian and its customers are fictional.
- `app.py`: local HTTP server, Exa client, citation validation, local baseline, static corpus exporter.
- `web/`: responsive research interface, source links, expandable evidence, explicit modes and error states.
- `tests/`: API contract and evidence-boundary tests; no paid calls.

```bash
python3 -m unittest discover -s tests -v
```

The app binds to localhost and keeps the API key server-side. It is a single-user demo, not a production service: real deployments need authentication, per-document access controls enforced before retrieval, secret management, rate limits, and a contracted private-index strategy. Public URL filtering is not an authorization system.

API behavior follows the [Exa Search reference](https://exa.ai/docs/reference/search); [content retrieval](https://exa.ai/docs/contents/quickstart) is separate from private ingestion. The exported corpus is intentionally disposable; JSON is the source of truth.
