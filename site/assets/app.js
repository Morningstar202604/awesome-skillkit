/* awesome-skillkit 站点逻辑 — 零依赖 */
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

  const state = { data: null, tab: "skills", q: "", group: "all", domain: "all" };
  let toastTimer = null;

  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (t.hidden = true), 1900);
  }

  async function copy(text) {
    try {
      await navigator.clipboard.writeText(text);
      toast("已复制：" + text);
    } catch (_) {
      toast("复制失败，请手动选择");
    }
  }

  /* ---------- 域色板：每个技能域一个识别色（缺省回退主题色） ---------- */
  const DOMAIN_COLORS = {
    programming: "#22d3ee", writing: "#a78bfa", video: "#f472b6",
    paper: "#34d399", chat: "#60a5fa", audio: "#fbbf24",
    design: "#fb7185", education: "#4ade80", marketing: "#f97316",
    music: "#e879f9", office: "#94a3b8", ppt: "#facc15",
  };
  const domainColor = (d) => DOMAIN_COLORS[d] || "";

  /* ---------- 主题 ---------- */
  const THEME_KEY = "sk-theme", ACCENT_KEY = "sk-accent";
  function applyTheme() {
    const theme = localStorage.getItem(THEME_KEY) || "dark";
    const accent = localStorage.getItem(ACCENT_KEY) || "cyan";
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.accent = accent;
    document.querySelectorAll(".dot").forEach((d) =>
      d.setAttribute("aria-pressed", String(d.dataset.setAccent === accent)));
  }
  $("#themeToggle").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_KEY, next);
    applyTheme();
  });
  document.querySelectorAll(".dot").forEach((d) =>
    d.addEventListener("click", () => {
      localStorage.setItem(ACCENT_KEY, d.dataset.setAccent);
      applyTheme();
    }));

  /* ---------- 下载按钮 ---------- */
  function dlBtn(href, label, cls = "act dl", filename) {
    const a = el("a", cls, label);
    a.href = href;
    a.setAttribute("download", filename || href.split("/").pop());
    return a;
  }
  function extLink(href, label) {
    const a = el("a", "act sm", label);
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener";
    return a;
  }

  /* ---------- 搜索词高亮：对文本做 <mark> 包裹（大小写不敏感，多处命中） ---------- */
  function highlight(text, q) {
    if (!q) return document.createTextNode(text);
    const lower = text.toLowerCase(), needle = q.toLowerCase();
    const frag = document.createDocumentFragment();
    let i = 0, hit;
    while ((hit = lower.indexOf(needle, i)) >= 0) {
      if (hit > i) frag.append(text.slice(i, hit));
      frag.append(el("mark", null, text.slice(hit, hit + needle.length)));
      i = hit + needle.length;
    }
    if (i < text.length) frag.append(text.slice(i));
    return frag;
  }

  /* ---------- 数字滚动：stat 从 0 数到目标值 ---------- */
  function countUp(node, target, dur = 700) {
    const t0 = performance.now();
    const tick = (t) => {
      const k = Math.min((t - t0) / dur, 1);
      node.textContent = String(Math.round(target * (1 - Math.pow(1 - k, 3))));
      if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  /* ---------- 渲染：统计 / 头部 ---------- */
  function renderHead() {
    const m = state.data.meta;
    // 口径：n_skills 为入包技能数，n_skills_on_disk 含 sample-skill 等不入包模板
    const total = m.n_skills_on_disk || m.n_skills;
    const tpl = total - m.n_skills;
    document.title = `${m.hub} — ${total} Skills / ${m.n_packs} Scene Packs`;
    $("#brand").textContent = m.hub;
    const stats = $("#stats");
    stats.innerHTML = "";
    const items = [
      [total, "SKILL.md files"],
      [m.n_packs, "scene packs (.zip)"],
      [m.n_domains, "skill domains"],
      [m.n_chains, "skill chains"],
      ["v" + m.version, "version"],
    ];
    items.forEach(([v, label]) => {
      const s = el("div", "stat");
      const b = el("b", null, "0");
      s.append(b, el("span", null, label));
      stats.append(s);
      if (typeof v === "number") countUp(b, v);
      else b.textContent = v;
    });
    $("#ghBtn").href = m.github.url;
    $("#gcBtn").href = m.gitcode.url;
    $("#footGh").href = m.github.url;
    $("#footGc").href = m.gitcode.url;
    $("#footMeta").textContent = `${m.n_skills} skills · ${m.n_packs} packs · v${m.version}${m.updated ? " · updated " + m.updated : ""}`;
    $("#cSkills").textContent = m.n_skills;
    $("#cPacks").textContent = m.n_packs;
    $("#cChains").textContent = m.n_chains;
    // Hero tagline: English primary, Chinese subtitle lives in .tagline-zh (static in HTML)
    $("#tagline").textContent = m.desc || $("#tagline").textContent;
    $("#statsNote").textContent = tpl > 0
      ? `${m.n_skills} are packaged into scene packs; ${tpl} are template-only reference skills (not shipped in any pack).`
      : "";
  }

  /* ---------- 场景库（一级）→ 能力域（二级）：taxonomy 由 build_site 注入 site.json ---------- */
  const groups = () => (state.data && state.data.groups) || [];
  const groupOf = (id) => groups().find((g) => g.id === id) || null;
  const groupOfPack = (pid) => groups().find((g) => g.packs.includes(pid)) || null;
  const domainInGroup = (d) =>
    state.group === "all" || (groupOf(state.group) || { domains: [] }).domains.includes(d);
  const domainLabel = (d) => {
    const hit = ((state.data && state.data.domains) || []).find((x) => x.id === d);
    return (hit && hit.label_zh) || d;
  };

  function renderGroups() {
    const box = $("#groupChips");
    if (!box) return;
    box.innerHTML = "";
    const mk = (id, label, count, title) => {
      const c = el("button", "chip l1");
      c.append(document.createTextNode(label + " "), el("i", null, String(count)));
      if (title) c.title = title;
      c.addEventListener("click", () => {
        state.group = id;
        const g = groupOf(id);
        // 换场景后旧能力域不属于该场景 → 归零，避免出现"空列表"误导
        if (state.domain !== "all" && (!g || !g.domains.includes(state.domain))) {
          state.domain = "all";
        }
        renderGroups();
        renderChips();
        render();
      });
      if (state.group === id) c.classList.add("active");
      return c;
    };
    box.append(mk("all", "全部场景", state.data.meta.n_skills, "显示全部场景库"));
    groups().forEach((g) =>
      box.append(mk(g.id, (g.emoji ? g.emoji + " " : "") + g.label, g.n_skills, g.desc)));
  }

  function renderChips() {
    const box = $("#domainChips");
    box.innerHTML = "";
    const g = state.group === "all" ? null : groupOf(state.group);
    const doms = state.data.domains.filter((d) => !g || g.domains.includes(d.id));
    // n_packed：与技能网格实际渲染口径一致（n_skills 是链域声明口径，仅 chains 视图用）
    const packCount = (d) => (d.n_packed != null ? d.n_packed : d.n_skills);
    const total = g ? doms.reduce((n, d) => n + packCount(d), 0) : state.data.meta.n_skills;
    const mk = (id, label, count) => {
      const c = el("button", "chip");
      c.append(document.createTextNode(label + " "), el("i", null, String(count)));
      c.title = id === "all" ? "当前范围内的全部能力域" : id;
      c.addEventListener("click", () => {
        state.domain = id;
        renderChips();
        render();
      });
      if (state.domain === id) c.classList.add("active");
      return c;
    };
    box.append(mk("all", "全部能力域", total));
    doms.forEach((d) => box.append(mk(d.id, domainLabel(d.id), packCount(d))));
  }

  /* ---------- 过滤 ---------- */
  function matches(s) {
    const q = state.q.trim().toLowerCase();
    const groupOk = domainInGroup(s.domain);
    const domainOk = state.domain === "all" || s.domain === state.domain;
    if (!q) return groupOk && domainOk;
    return groupOk && domainOk &&
      (s.name + " " + s.desc + " " + s.domain + " " + domainLabel(s.domain) + " " + s.packs.join(" "))
        .toLowerCase().includes(q);
  }
  function matchesPack(p) {
    const q = state.q.trim().toLowerCase();
    const g = groupOfPack(p.id);
    const groupOk = state.group === "all" || (g && g.id === state.group);
    const domainOk = state.domain === "all" ||
      p.skills.some((n) => (state.data.skills.find((s) => s.name === n) || {}).domain === state.domain);
    if (!q) return groupOk && domainOk;
    return groupOk && domainOk && (p.id + " " + p.name + " " + p.name_zh + " " + p.desc + " " +
      p.desc_zh + " " + (g ? g.label : "") + " " + p.skills.join(" ")).toLowerCase().includes(q);
  }

  /* ---------- 渲染：技能 ---------- */
  function renderSkills() {
    const box = $("#view-skills");
    box.innerHTML = "";
    const q = state.q.trim();
    const list = state.data.skills.filter(matches);
    list.forEach((s, i) => {
      const c = el("article", "card");
      const dc = domainColor(s.domain);
      if (dc) c.style.setProperty("--dc", dc);
      c.style.animationDelay = Math.min(i * 14, 280) + "ms";

      const h = el("h3");
      const name = el("span", null);
      name.append(highlight(s.name, q));
      const domTag = el("span", "dom", domainLabel(s.domain));
      domTag.title = s.domain;
      h.append(name, domTag);
      // 用完整 desc（CSS line-clamp 截 3 行展示）——匹配与高亮必须同一字符串，
      // 否则命中关键词的词被 short 截断后，卡片上找不到高亮
      const p = el("p");
      p.append(highlight(s.desc, q));
      c.append(h, p);

      const meta = el("div", "meta-row");
      if (s.version) meta.append(el("span", "tag", "v" + s.version));
      if (s.tier) meta.append(el("span", "tag", s.tier));
      if (s.pattern) meta.append(el("span", "tag", s.pattern));
      if (s.license) meta.append(el("span", "tag", s.license));
      s.packs.forEach((pk) => meta.append(el("span", "tag pack", "📦 " + pk)));
      c.append(meta);

      const act = el("div", "actions");
      act.append(dlBtn(s.file, "↓ SKILL.md", "act dl", s.name + ".SKILL.md"));
      const cp = el("button", "act sm", "复制路径");
      cp.addEventListener("click", () => copy(s.name));
      act.append(cp);
      const alt = el("span", "alt");
      alt.append(document.createTextNode("raw: "), extLink(s.raw_github, "GitHub"),
        document.createTextNode(" "), extLink(s.raw_gitcode, "GitCode"));
      act.append(alt);
      c.append(act);
      box.append(c);
    });
    return list.length;
  }

  /* ---------- 渲染：场景包 ---------- */
  function renderPacks() {
    const box = $("#view-packs");
    box.innerHTML = "";
    const q = state.q.trim();
    const list = state.data.packs.filter(matchesPack);
    list.forEach((p, i) => {
      const c = el("article", "card");
      const dc = domainColor(state.domain !== "all" ? state.domain : "");
      if (dc) c.style.setProperty("--dc", dc);
      c.style.animationDelay = Math.min(i * 14, 280) + "ms";

      const h = el("h3");
      const name = el("span", null);
      name.append(highlight(p.name || p.name_zh, q));
      h.append(name, el("span", "dom", p.id));
      const d = el("p");
      d.append(highlight(p.desc || p.desc_zh, q));
      c.append(h, d);

      const meta = el("div", "meta-row");
      const gp = groupOfPack(p.id);
      if (gp) meta.append(el("span", "tag", (gp.emoji ? gp.emoji + " " : "") + gp.label));
      meta.append(el("span", "tag", p.n_skills + " skills"));
      meta.append(el("span", "tag", p.size_kb + " KB"));
      meta.append(el("span", "tag", p.id + ".zip"));
      c.append(meta);

      const act = el("div", "actions");
      act.append(dlBtn(p.local_url, "↓ 下载 zip（站内镜像）", "act dl", p.id + ".zip"));
      const alt = el("span", "alt");
      alt.append(document.createTextNode("Release: "), extLink(p.release_github, "GitHub"),
        document.createTextNode(" "), extLink(p.release_gitcode, "GitCode"),
        document.createTextNode(" "), extLink(p.release_gitee, "Gitee"));
      act.append(alt);
      c.append(act);

      const dis = el("button", "disclose", `View ${p.n_skills} skills ▾`);
      const sl = el("div", "skill-list");
      p.skills.forEach((n) => {
        const b = el("button", null, n);
        b.addEventListener("click", () => {
          state.tab = "skills";
          state.group = "all"; // 从包内跳技能：清掉场景/域过滤，保证一定能看到命中的技能
          state.domain = "all";
          state.q = n;
          $("#q").value = n;
          $("#clearQ").hidden = false;
          syncTabs();
          renderGroups();
          renderChips();
          render();
          window.scrollTo({ top: document.querySelector(".toolbar").offsetTop, behavior: "smooth" });
        });
        sl.append(b);
      });
      dis.addEventListener("click", () => {
        sl.classList.toggle("open");
        dis.textContent = sl.classList.contains("open")
          ? `Hide ▴` : `View ${p.n_skills} skills ▾`;
      });
      c.append(dis, sl);
      box.append(c);
    });
    return list.length;
  }

  /* ---------- 渲染：链条 ---------- */
  function renderChains() {
    const box = $("#view-chains");
    box.innerHTML = "";
    const q = state.q.trim().toLowerCase();
    let n = 0;
    state.data.domains.forEach((d, di) => {
      if (state.domain !== "all" && d.id !== state.domain) return;
      if (!domainInGroup(d.id)) return;
      const chains = d.chains.filter((c) =>
        !q || (c.name + " " + c.steps.join(" ") + " " + d.id + " " + domainLabel(d.id))
          .toLowerCase().includes(q));
      if (!chains.length) return;
      const wrap = el("div", "chain-domain");
      const dc = domainColor(d.id);
      if (dc) wrap.style.setProperty("--dc", dc);
      wrap.style.animationDelay = Math.min(di * 40, 200) + "ms";
      const h3 = el("h3", null, domainLabel(d.id));
      h3.title = d.id;
      wrap.append(h3);
      wrap.append(el("div", "sub", `${d.n_skills} 技能 · ${d.n_chains} 条链${d.entry ? " · 编排器 " + d.entry.split("/").pop() : ""}`));
      chains.forEach((c) => {
        n += 1;
        const row = el("div", "chain");
        row.append(el("div", "name", c.name));
        const steps = el("div", "steps");
        c.steps.forEach((s, i) => {
          if (i) steps.append(el("span", "arrow", "→"));
          const opt = s.endsWith("?");
          const st = el("span", "step" + (opt ? " opt" : ""), opt ? s.slice(0, -1) : s);
          if (opt) st.append(el("span", "q", "?"));
          steps.append(st);
        });
        row.append(steps);
        wrap.append(row);
      });
      box.append(wrap);
    });
    return n;
  }

  /* ---------- 主渲染 ---------- */
  function render() {
    let count = 0;
    if (state.tab === "skills") count = renderSkills();
    else if (state.tab === "packs") count = renderPacks();
    else count = renderChains();
    $("#empty").hidden = count > 0;
    const label = { skills: "技能", packs: "场景包", chains: "技能链" }[state.tab];
    const g = groupOf(state.group);
    if (state.q || state.group !== "all" || state.domain !== "all") {
      $("#hint").textContent = `筛选中：${label} ${count} 项` +
        (g ? " · 场景 " + g.label : "") +
        (state.domain !== "all" ? " · 能力域 " + domainLabel(state.domain) : "") +
        (state.q ? " · 关键词 “" + state.q + "”" : "");
    } else {
      $("#hint").textContent =
        "用法：一级选「场景」（我在做什么）→ 二级选「能力域」（用什么能力）→ 点卡片下载。" +
        "技能按能力域归类，场景包按使用场景归类。";
    }
  }

  function syncTabs() {
    document.querySelectorAll(".tab").forEach((t) =>
      t.classList.toggle("active", t.dataset.tab === state.tab));
    $("#view-skills").hidden = state.tab !== "skills";
    $("#view-packs").hidden = state.tab !== "packs";
    $("#view-chains").hidden = state.tab !== "chains";
  }

  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => {
      state.tab = t.dataset.tab;
      syncTabs();
      render();
    }));

  function clearSearch() {
    $("#q").value = "";
    $("#clearQ").hidden = true;
    if (state.q) { state.q = ""; render(); }
    $("#q").focus();
  }

  let debounce = null;
  $("#q").addEventListener("input", (e) => {
    const v = e.target.value;
    $("#clearQ").hidden = !v;
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      state.q = v;
      render();
    }, 130);
  });
  $("#clearQ").addEventListener("click", () => {
    $("#q").value = "";
    $("#clearQ").hidden = true;
    state.q = "";
    render();
    $("#q").focus();
  });

  /* 键盘：/ 聚焦搜索，Esc 清空 */
  document.addEventListener("keydown", (e) => {
    const typing = document.activeElement === $("#q");
    if (e.key === "/" && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) {
      e.preventDefault();
      $("#q").focus();
    } else if (e.key === "Escape" && typing) {
      clearSearch();
    }
  });

  /* 回到顶部 */
  const toTop = $("#toTop");
  window.addEventListener("scroll", () => { toTop.hidden = window.scrollY < 600; }, { passive: true });
  toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  /* ---------- 启动 ---------- */
  applyTheme();
  fetch("data/site.json")
    .then((r) => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then((d) => {
      state.data = d;
      renderHead();
      renderGroups();
      renderChips();
      syncTabs();
      render();
    })
    .catch((e) => {
      $("#stats").innerHTML = "";
      $("#view-skills").innerHTML = "";
      $("#hint").textContent =
        "数据加载失败（" + e.message + "）。若你是直接双击打开的 index.html，请改用本地 HTTP 服务：" +
        "python3 -m http.server 8000，然后访问 http://localhost:8000/";
      $("#empty").hidden = false;
      $("#empty").textContent = "⚠ site.json 未能加载";
    });
})();
