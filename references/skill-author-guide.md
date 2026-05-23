# Skill author guide

## Where to put `easy-config-schema.json`

**Primary (recommended):**

```
<skill-root>/easy-config-schema.json
```

**Optional alias (grouped with config):**

```
<skill-root>/config/easy-config-schema.json
```

Update this file in the **same PR** as `config.yaml` when fields change.

## Registry fallback

If you cannot modify a third-party skill repo, maintain a copy under:

```
easy-config/registry/<skill-name>.easy-config-schema.json
```

Do **not** duplicate schemas in both places long term. When the skill ships its own schema, remove the registry entry.

## Reload

Default: user sends「重新加载 \<skill\>」in chat; Agent reads `easy_config_result.json`.

Optional: provide `scripts/reload.sh` only if programmatic reload is required.

## Validate (P1+)

```bash
python -m easy_config validate-schema --file ./easy-config-schema.json
```
