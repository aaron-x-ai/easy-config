# Easy Config

Schema-driven visual configuration for [Hermes](https://github.com/NousResearch/hermes-agent) skills.

## Install

```bash
git clone git@github.com:aaron-x-ai/easy-config.git ~/.hermes/skills/easy-config
cd ~/.hermes/skills/easy-config
bash scripts/install.sh --dev    # 开发/测试必加 --dev（含 pytest）
```

安装完成后，依赖在 **`.venv/`** 里。macOS 上未激活 venv 时通常没有 `python` 命令，请用下面任一方式：

```bash
# 方式 A：激活虚拟环境（推荐日常开发）
source .venv/bin/activate
python -m easy_config doctor
pytest -q

# 方式 B：不激活，用脚本或 .venv 绝对路径
bash scripts/doctor.sh
bash scripts/pytest.sh          # 需先 install.sh --dev
bash scripts/serve.sh --skill demo --dry-run
```

对 Hermes 说：

- **配置 aaron-web-search**
- **用 Easy Config 配置 aaron-web-search**

## Development

```bash
cd easy-config
bash scripts/install.sh --dev
source .venv/bin/activate
python -m easy_config doctor
pytest -q
python -m easy_config serve --skill demo --dry-run
```

## Try P1 demo (local)

```bash
# 使用内置 demo skill fixture
export EASY_CONFIG_SKILLS_ROOT="$PWD/tests/fixtures"
bash scripts/serve.sh --skill demo-skill
# 打开 stdout 里的 url，修改 Max results 后保存
```

## P2: session lifecycle & e2e

- **Idle timeout**: 默认 15 分钟无操作自动退出（`EASY_CONFIG_IDLE_TIMEOUT_SEC`）
- **保存后关闭**: 保存成功约 10 秒后进程退出（`EASY_CONFIG_SHUTDOWN_DELAY_SEC`）
- **Token 安全**: 前端加载后从 URL 移除 `?token=...`
- **测试**:
  ```bash
  bash scripts/pytest.sh -q -m "not e2e"   # 单元 + 集成
  bash scripts/e2e.sh                       # Playwright 浏览器 e2e（首次会装 chromium）
  ```

- `src/easy_config/` — Python package (src layout)
- `scripts/` — runtime shell entrypoints
- `registry/` — fallback schemas for skills without their own protocol file
- `schemas/` — meta-schema and OpenAPI contracts

## License

MIT — see [LICENSE](LICENSE).
