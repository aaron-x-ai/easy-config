---
name: easy-config
description: 用图形界面配置其它 Skill 的 YAML/JSON/ENV。当用户说「配置 xxx」「用 Easy Config 配置 xxx」「Easy Config」时使用。启动本地网页，保存后自动关闭。
---

# Easy Config

## 何时使用

- 用户说：**配置 \<skill-name\>**
- 用户说：**用 Easy Config 配置 xxx**
- 用户要可视化修改某 Skill 的配置文件

## 工作流（Agent 必须遵守）

1. 确认目标 Skill 名称；若含糊则追问。
2. 在 Easy Config 安装目录执行：

   ```bash
   bash scripts/launch_config_ui.sh --skill <skill-name>
   ```

   或：

   ```bash
   python -m easy_config serve --skill <skill-name>
   ```

3. 将 stdout 中 JSON 的 **`url`** 原样发给用户（可点击）。
4. 用户保存后，读取 `session_dir` 下的 **`easy_config_result.json`**（P1 起）或等待用户确认。
5. 按成功页 / result 中的 **`reload_hint`** 引导用户重新加载目标 Skill。

## 依赖

首次安装后执行一次：

```bash
bash scripts/install.sh
```

## 安全

- 仅监听 `127.0.0.1`
- 不读取目标 Skill 的 `.py` 源码
- 配置备份写在目标 Skill 配置目录旁（`.bak_*`）

## 目标 Skill 接入

- 推荐在目标 Skill 根目录提供 **`easy-config-schema.json`**
- 可选别名：`<skill-root>/config/easy-config-schema.json`
- **`scripts/reload.sh` 可选**；默认用聊天提示 + `easy_config_result.json`

详见仓库 `references/skill-author-guide.md`。
