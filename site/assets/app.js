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

  const state = { data: null, tab: "skills", q: "", group: "all", domain: "all",
                  sort: "default", filtersOpen: false };
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
    if (lower.includes(needle)) {
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
    // CJK 宽松命中（词序不同，如「合同审查」命中「审查合同」）：逐字标出，
    // 避免"命中了却看不到高亮"
    const set = new Set((needle.match(/[\u4e00-\u9fff]/g) || []));
    if (set.size) {
      const frag = document.createDocumentFragment();
      for (const ch of text) {
        if (set.has(ch.toLowerCase())) frag.append(el("mark", null, ch));
        else frag.append(document.createTextNode(ch));
      }
      return frag;
    }
    return document.createTextNode(text);
  }

  /* ---------- 命中判定：ASCII 子串；CJK 另允许"字符集包含"（词序无关） ---------- */
  function termHit(haystackLower, needleLower) {
    if (!needleLower) return true;
    if (haystackLower.includes(needleLower)) return true;
    const chars = [...new Set(needleLower.match(/[\u4e00-\u9fff]/g) || [])];
    return chars.length > 0 && chars.every((c) => haystackLower.includes(c));
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
    // 口径统一：全站以「入包技能数」(n_skills) 为准（与 manifest / README 徽章同源）；
    // 磁盘上另有 sample/good-skill 等模板参考技能，只在脚注说明，不再混进主口径
    const total = m.n_skills;
    const tpl = Math.max((m.n_skills_on_disk || total) - total, 0);
    document.title = `${m.hub} — ${total} Skills / ${m.n_packs} Scene Packs`;
    $("#brand").textContent = m.hub;
    const stats = $("#stats");
    stats.innerHTML = "";
    const items = [
      [total, "skills"],
      [m.n_packs, "scene packs"],
      [m.n_domains, "domains"],
      [m.n_chains, "skill chains"],
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
    $("#footMeta").textContent = `${total} skills · ${m.n_packs} packs · v${m.version}${m.updated ? " · updated " + m.updated : ""}`;
    $("#cSkills").textContent = total;
    $("#cPacks").textContent = m.n_packs;
    $("#cChains").textContent = m.n_chains;
    $("#tagline").textContent =
      `${total} skills · ${m.n_packs} scene packs · ${m.n_domains} domains · ` +
      `${m.n_chains} skill chains — grab a single SKILL.md or a full-pack zip, drop it in, done.`;
    $("#statsNote").textContent = tpl > 0
      ? `${total} skills are shipped across ${m.n_packs} packs; ${tpl} template-only fixtures stay on disk and ship in no pack.`
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

  /* ---------- 工具栏：紧凑模式 / 滚动提示 / 选中项回视 ---------- */
  const COMPACT_AT = 340; // 滚过首屏后收起两级 chips，避免 sticky 遮住内容

  function syncToolbar() {
    // 窄屏工具栏是 static（不粘顶），无需折叠；回到顶部时重置"手动展开"状态
    const isNarrow = window.matchMedia("(max-width: 720px)").matches;
    if (window.scrollY < 120) state.filtersOpen = false;
    const compact = !isNarrow && window.scrollY > COMPACT_AT && !state.filtersOpen;
    $("#toolbar").classList.toggle("compact", compact);
    $("#filterSummary").hidden = !compact;
    if (!compact) return;
    const g = groupOf(state.group);
    const bits = [
      "场景 " + (g ? g.label : "全部"),
      "域 " + (state.domain === "all" ? "全部" : domainLabel(state.domain)),
    ];
    if (state.q) bits.push(`“${state.q}”`);
    $("#sumText").textContent = bits.join(" · ");
  }

  function updateScrollHint(box) {
    if (!box) return;
    box.classList.toggle("can-left", box.scrollLeft > 4);
    box.classList.toggle("can-right", box.scrollLeft + box.clientWidth < box.scrollWidth - 6);
  }

  function revealActiveChip(sel) {
    const active = $(sel).querySelector(".chip.active");
    if (active) active.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
  }

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
        state.filtersOpen = false; // 选完即收，滚回去看结果
        renderGroups();
        renderChips();
        render();
        revealActiveChip("#groupChips");
      });
      if (state.group === id) c.classList.add("active");
      return c;
    };
    box.append(mk("all", "全部场景", state.data.meta.n_skills, "显示全部场景库"));
    groups().forEach((g) =>
      box.append(mk(g.id, (g.emoji ? g.emoji + " " : "") + g.label, g.n_skills, g.desc)));
    requestAnimationFrame(() => updateScrollHint(box));
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
        state.filtersOpen = false;
        renderChips();
        render();
        revealActiveChip("#domainChips");
      });
      if (state.domain === id) c.classList.add("active");
      return c;
    };
    box.append(mk("all", "全部能力域", total));
    doms.forEach((d) => box.append(mk(d.id, domainLabel(d.id), packCount(d))));
    requestAnimationFrame(() => updateScrollHint(box));
  }

  /* ---------- 过滤 ---------- */
  function matches(s) {
    const q = state.q.trim().toLowerCase();
    const groupOk = domainInGroup(s.domain);
    const domainOk = state.domain === "all" || s.domain === state.domain;
    if (!q) return groupOk && domainOk;
    return groupOk && domainOk &&
      termHit((s.name + " " + s.desc + " " + (s.desc_zh || "") + " " + s.domain + " " +
        domainLabel(s.domain) + " " + s.packs.join(" ")).toLowerCase(), q);
  }
  function matchesPack(p) {
    const q = state.q.trim().toLowerCase();
    const g = groupOfPack(p.id);
    const groupOk = state.group === "all" || (g && g.id === state.group);
    const domainOk = state.domain === "all" ||
      p.skills.some((n) => (state.data.skills.find((s) => s.name === n) || {}).domain === state.domain);
    if (!q) return groupOk && domainOk;
    return groupOk && domainOk && termHit((p.id + " " + p.name + " " + p.name_zh + " " + p.desc + " " +
      p.desc_zh + " " + (g ? g.label : "") + " " + p.skills.join(" ")).toLowerCase(), q);
  }

  /* ---------- 渲染：技能 ---------- */
  function renderSkills() {
    const box = $("#view-skills");
    box.innerHTML = "";
    const q = state.q.trim();
    const list = state.data.skills.filter(matches);
    const TIER_RANK = { powerful: 3, standard: 2, minimal: 1 };
    if (state.sort === "name")
      list.sort((a, b) => a.name.localeCompare(b.name));
    else if (state.sort === "tier")
      list.sort((a, b) => (TIER_RANK[b.tier] || 0) - (TIER_RANK[a.tier] || 0) ||
        a.name.localeCompare(b.name));
    else if (state.sort === "verified")
      list.sort((a, b) => (b.verified || "").localeCompare(a.verified || ""));
    list.forEach((s, i) => {
      const c = el("article", "card");
      const dc = domainColor(s.domain);
      if (dc) c.style.setProperty("--dc", dc);
      c.style.animationDelay = Math.min(i * 14, 280) + "ms";

      const h = el("h3");
      const name = el("span", null);
      name.append(highlight(s.name, q));
      // 已按能力域筛选时，右上角不再重复同一个域标签（整屏同词，无信息量）
      if (state.domain === "all") {
        const domTag = el("span", "dom", domainLabel(s.domain));
        domTag.title = s.domain;
        h.append(name, domTag);
      } else {
        h.append(name);
      }
      // 展示优先中文描述（desc_zh），无则回退英文 desc；匹配与高亮必须同一字符串，
      // 否则命中关键词的词被截断后，卡片上找不到高亮
      const p = el("p");
      p.append(highlight(s.desc_zh || s.desc, q));
      c.append(h, p);

      // 版本/标准/模式/许可压缩为一行等宽摘要；包归属保留为可扫读的 pill
      const bits = [];
      if (s.version) bits.push("v" + s.version);
      if (s.tier) bits.push(s.tier);
      if (s.pattern) bits.push(s.pattern);
      if (s.license) bits.push(s.license);
      if (bits.length) c.append(el("div", "meta-line", bits.join(" · ")));
      if (s.packs.length) {
        const meta = el("div", "meta-row");
        s.packs.forEach((pk) => meta.append(el("span", "tag pack", "📦 " + pk)));
        c.append(meta);
      }

      const act = el("div", "actions");
      act.append(dlBtn("skills-zip/" + s.name + ".zip", "↓ 整包 zip", "act dl", s.name + ".zip"));
      act.append(dlBtn(s.file, "↓ SKILL.md", "act", s.name + ".SKILL.md"));
      const det = el("button", "act sm", "详情");
      det.addEventListener("click", () => openSkillModal(s));
      act.append(det);
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


  /* ---------- 详情弹窗：技能市场核心交互 ---------- */
  function jumpToPack(id) {
    state.tab = "packs";
    state.group = "all";
    state.domain = "all";
    state.q = id;
    $("#q").value = id;
    $("#clearQ").hidden = false;
    $("#kbdHint").hidden = true;
    syncTabs();
    render();
    window.scrollTo({ top: document.querySelector(".toolbar").offsetTop, behavior: "smooth" });
  }

  function openSkillModal(s) {
    document.querySelector(".modal-overlay")?.remove();
    const ov = el("div", "modal-overlay");
    const m = el("div", "modal");
    const close = el("button", "close", "×");
    close.setAttribute("aria-label", "关闭");
    close.addEventListener("click", () => ov.remove());
    ov.addEventListener("click", (e) => { if (e.target === ov) ov.remove(); });

    const h = el("h3", null, null);
    h.append(el("span", null, s.name), el("span", "dom", domainLabel(s.domain)));
    m.append(close, h);

    if (s.desc_zh) m.append(el("p", "m-desc", s.desc_zh));
    if (s.desc) m.append(el("p", "m-desc en", s.desc));

    const bits = [];
    if (s.version) bits.push("v" + s.version);
    if (s.tier) bits.push("层级 " + s.tier);
    if (s.pattern) bits.push("模式 " + s.pattern);
    if (s.license) bits.push(s.license);
    if (s.verified) bits.push("验证于 " + s.verified);
    if (bits.length) m.append(el("div", "meta-line", bits.join(" · ")));
    if (s.compatibility) m.append(el("p", "m-compat", "⚙ " + s.compatibility));

    if (s.packs.length) {
      const row = el("div", "meta-row");
      row.append(el("span", "tag", "隶属场景包："));
      s.packs.forEach((id) => {
        const b = el("button", "tag pack", "📦 " + id);
        b.addEventListener("click", () => { ov.remove(); jumpToPack(id); });
        row.append(b);
      });
      m.append(row);
    }

    const inst = el("div", "m-install");
    inst.append(el("div", "m-label", "一键安装（skills.sh 生态）"));
    const cmdRow = el("div", "cmd-row");
    const cmd = "npx skills add x33834/awesome-skillkit -s " + s.name;
    cmdRow.append(el("code", null, cmd));
    const cb = el("button", "act sm", "复制");
    cb.addEventListener("click", () => copy(cmd));
    cmdRow.append(cb);
    inst.append(cmdRow);

    const dl = el("div", "cmd-row");
    dl.append(dlBtn("skills-zip/" + s.name + ".zip", "↓ 整技能 zip（含 scripts/references）", "act dl", s.name + ".zip"));
    dl.append(dlBtn(s.file, "↓ 仅 SKILL.md", "act", s.name + ".SKILL.md"));
    dl.append(extLink(s.raw_github, "raw GitHub"));
    dl.append(extLink(s.raw_gitcode, "raw GitCode"));
    inst.append(dl);
    m.append(inst);

    const prevBtn = el("button", "act wide", "展开 SKILL.md 正文预览 ▾");
    const pre = el("pre", "m-pre");
    pre.hidden = true;
    prevBtn.addEventListener("click", async () => {
      if (pre.hidden && !pre.textContent) {
        try {
          const res = await fetch(s.file);
          pre.textContent = await res.text();
        } catch (_) {
          pre.textContent = "（正文加载失败，请用上面的 raw 链接查看）";
        }
      }
      pre.hidden = !pre.hidden;
      prevBtn.textContent = pre.hidden ? "展开 SKILL.md 正文预览 ▾" : "收起正文 ▴";
    });
    m.append(prevBtn, pre);

    ov.append(m);
    document.body.append(ov);
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

      const h = el("h3", "pack-head");
      h.append(el("span", "glyph", "📦"));
      const name = el("span", null);
      name.append(highlight(p.name || p.name_zh, q));
      h.append(name, el("span", "pack-n", p.n_skills + " skills"));
      const d = el("p");
      d.append(highlight(p.desc || p.desc_zh, q));
      c.append(h, el("div", "pack-id", p.id + ".zip"), d);

      const meta = el("div", "meta-row");
      const gp = groupOfPack(p.id);
      if (gp) meta.append(el("span", "tag", (gp.emoji ? gp.emoji + " " : "") + gp.label));
      meta.append(el("span", "tag", p.size_kb + " KB"));
      c.append(meta);

      const act = el("div", "actions");
      act.append(dlBtn(p.local_url, "↓ 下载 zip（站内镜像）", "act dl", p.id + ".zip"));
      const alt = el("span", "alt");
      alt.append(document.createTextNode("Release: "), extLink(p.release_github, "GitHub"),
        document.createTextNode(" "), extLink(p.release_gitcode, "GitCode"),
        document.createTextNode(" "), extLink(p.release_gitee, "Gitee"));
      act.append(alt);
      c.append(act);

      const dis = el("button", "disclose wide", `查看包含的 ${p.n_skills} 个技能 ▾`);
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
          $("#kbdHint").hidden = true;
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
          ? "收起技能列表 ▴" : `查看包含的 ${p.n_skills} 个技能 ▾`;
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
        !q || termHit((c.name + " " + c.steps.join(" ") + " " + d.id + " " + domainLabel(d.id))
          .toLowerCase(), q));
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
  function hintText(count) {
    const m = state.data.meta;
    const g = groupOf(state.group);
    if (state.q || state.group !== "all" || state.domain !== "all") {
      const label = { skills: "技能", packs: "场景包", chains: "技能链" }[state.tab];
      return `筛选中：${label} ${count} 项` +
        (g ? " · 场景 " + g.label : "") +
        (state.domain !== "all" ? " · 能力域 " + domainLabel(state.domain) : "") +
        (state.q ? " · 关键词 “" + state.q + "”" : "");
    }
    // 无筛选时：每个视图给一句"这个视图怎么用"，替代此前三个视图共用的一句话
    return {
      skills: `${m.n_skills} 个技能按能力域归类：先选「场景」（我在做什么）→ 再选「能力域」（用什么能力）→ 点卡片下载 SKILL.md。`,
      packs: `${m.n_packs} 个场景包 = 一个真实场景的成套技能：下载 zip 解压即用；点卡片底部「查看包含的技能」可展开包内技能。`,
      chains: `${m.n_chains} 条技能链 = 多步任务的推荐工序：从链头进入，按 → 顺序推进；虚线步骤为可选（带 ?）。`,
    }[state.tab];
  }

  function render() {
    let count = 0;
    if (state.tab === "skills") count = renderSkills();
    else if (state.tab === "packs") count = renderPacks();
    else count = renderChains();
    $("#empty").hidden = count > 0;
    $("#hint").textContent = hintText(count);
    syncToolbar();
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

  function setSearchUI(hasText) {
    $("#clearQ").hidden = !hasText;
    $("#kbdHint").hidden = hasText;
  }

  function clearSearch() {
    $("#q").value = "";
    setSearchUI(false);
    if (state.q) { state.q = ""; render(); }
    $("#q").focus();
  }

  let debounce = null;
  $("#q").addEventListener("input", (e) => {
    const v = e.target.value;
    setSearchUI(!!v);
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      state.q = v;
      render();
    }, 130);
  });
  $("#clearQ").addEventListener("click", () => {
    $("#q").value = "";
    setSearchUI(false);
    state.q = "";
    render();
    $("#q").focus();
  });

  /* 紧凑工具栏：滚动折叠两级 chips，点摘要展开筛选 */
  $("#sumToggle").addEventListener("click", () => {
    state.filtersOpen = true;
    syncToolbar();
  });
  window.addEventListener("scroll", syncToolbar, { passive: true });
  $("#groupChips").addEventListener("scroll", () => updateScrollHint($("#groupChips")), { passive: true });
  $("#domainChips").addEventListener("scroll", () => updateScrollHint($("#domainChips")), { passive: true });
  $("#sortChips").addEventListener("click", (e) => {
    const b = e.target.closest("[data-sort]");
    if (!b) return;
    state.sort = b.dataset.sort;
    document.querySelectorAll("#sortChips .chip").forEach((c) =>
      c.classList.toggle("active", c === b));
    render();
  });
  window.addEventListener("resize", () => {
    updateScrollHint($("#groupChips"));
    updateScrollHint($("#domainChips"));
    syncToolbar();
  }, { passive: true });

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
