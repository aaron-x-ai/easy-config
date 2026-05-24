(function () {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");
  const skill = params.get("skill") || "";

  const loading = document.getElementById("loading");
  const form = document.getElementById("config-form");
  const alertEl = document.getElementById("alert");
  const success = document.getElementById("success");
  const skillLabel = document.getElementById("skill-label");
  const reloadHint = document.getElementById("reload-hint");

  function showError(msg) {
    loading.classList.add("hidden");
    alertEl.textContent = msg;
    alertEl.classList.remove("hidden");
  }

  function authHeaders() {
    return { "Content-Type": "application/json", "X-Easy-Config-Token": token };
  }

  function buildField(name, spec, ui, value) {
    const wrap = document.createElement("div");
    wrap.className = "field";
    const label = document.createElement("label");
    label.textContent = spec.title || name;
    label.setAttribute("for", name);
    wrap.appendChild(label);

    const widget = (ui[name] && ui[name].widget) || spec.format || spec.type;
    let input;
    if (spec.type === "boolean") {
      wrap.className = "field field-check";
      input = document.createElement("input");
      input.type = "checkbox";
      input.id = name;
      input.checked = !!value;
      label.textContent = spec.title || name;
      label.prepend(input);
      return wrap;
    }

    input = document.createElement("input");
    input.id = name;
    input.name = name;
    if (spec.type === "integer" || spec.type === "number") {
      input.type = "number";
      if (spec.minimum != null) input.min = spec.minimum;
      if (spec.maximum != null) input.max = spec.maximum;
      input.value = value != null ? value : spec.default != null ? spec.default : "";
    } else if (widget === "password" || spec.format === "password") {
      input.type = "password";
      input.autocomplete = "off";
      if (value && value.set) {
        input.placeholder = "已设置，留空则不修改";
      }
    } else {
      input.type = "text";
      input.value = value != null && typeof value !== "object" ? value : "";
    }
    wrap.appendChild(input);

    const help = (ui[name] && ui[name].help) || spec.description;
    if (help) {
      const p = document.createElement("p");
      p.className = "help";
      p.textContent = help;
      wrap.appendChild(p);
    }
    return wrap;
  }

  function collectFormData(schema) {
    const data = {};
    const props = schema.properties || {};
    for (const name of Object.keys(props)) {
      const spec = props[name];
      if (spec.type === "boolean") {
        const el = document.getElementById(name);
        data[name] = el.checked;
        continue;
      }
      const el = document.getElementById(name);
      let val = el.value;
      if (val === "" && (spec.format === "password" || spec.writeOnly)) {
        continue;
      }
      if (spec.type === "integer") data[name] = parseInt(val, 10);
      else if (spec.type === "number") data[name] = parseFloat(val);
      else data[name] = val;
    }
    return data;
  }

  async function init() {
    if (!token) {
      showError("缺少 token，请从 Agent 提供的链接打开此页面。");
      return;
    }
    // Remove token from address bar after reading (keep skill query only)
    try {
      const clean = new URL(window.location.href);
      clean.searchParams.delete("token");
      window.history.replaceState({}, "", clean.pathname + clean.search);
    } catch (_e) {
      /* ignore */
    }
    skillLabel.textContent = skill ? "Skill: " + skill : "";

    try {
      const res = await fetch("/api/session", { headers: authHeaders() });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail?.message || res.statusText);
      }
      const session = await res.json();
      const schema = session.schema || {};
      const ui = session.uiSchema || {};
      const formData = session.formData || {};

      for (const name of Object.keys(schema.properties || {})) {
        form.appendChild(buildField(name, schema.properties[name], ui, formData[name]));
      }

      const submit = document.createElement("button");
      submit.type = "submit";
      submit.textContent = "保存配置";
      form.appendChild(submit);

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        submit.disabled = true;
        try {
          const body = collectFormData(schema);
          const save = await fetch("/api/config", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify(body),
          });
          const out = await save.json().catch(() => ({}));
          if (!save.ok) {
            throw new Error(out.detail?.message || save.statusText);
          }
          form.classList.add("hidden");
          success.classList.remove("hidden");
          reloadHint.textContent = out.reload_hint || session.reloadHint || "";
        } catch (err) {
          showError(err.message || String(err));
          submit.disabled = false;
        }
      });

      loading.classList.add("hidden");
      form.classList.remove("hidden");
    } catch (err) {
      showError(err.message || String(err));
    }
  }

  init();
})();
