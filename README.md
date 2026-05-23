# Easy Config

Schema-driven visual configuration for [Hermes](https://github.com/NousResearch/hermes-agent) skills.

## Install

```bash
git clone git@github.com:aaron-x-ai/easy-config.git ~/.hermes/skills/easy-config
cd ~/.hermes/skills/easy-config
bash scripts/install.sh
```

## First use

对 Hermes 说：

- **配置 aaron-web-search**
- **用 Easy Config 配置 aaron-web-search**

## Development

```bash
cd easy-config
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m easy_config doctor
pytest
python -m easy_config serve --skill demo --dry-run
```

## Layout

- `src/easy_config/` — Python package (src layout)
- `scripts/` — runtime shell entrypoints
- `registry/` — fallback schemas for skills without their own protocol file
- `schemas/` — meta-schema and OpenAPI contracts

## License

MIT — see [LICENSE](LICENSE).
