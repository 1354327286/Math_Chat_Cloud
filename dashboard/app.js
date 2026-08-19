import { katex } from "/vendor/katex/katex.js";

"use strict";

const token = new URLSearchParams(window.location.search).get("token") || "";

const state = {
  overview: null,
  detail: null,
  activeTab: "state",
  viewer: null,
  viewerMode: "rendered",
};

const elements = {
  generatedAt: document.getElementById("generatedAt"),
  metrics: document.getElementById("metrics"),
  projectSearch: document.getElementById("projectSearch"),
  roleFilter: document.getElementById("roleFilter"),
  refreshButton: document.getElementById("refreshButton"),
  projectCount: document.getElementById("projectCount"),
  projectRows: document.getElementById("projectRows"),
  emptyProjects: document.getElementById("emptyProjects"),
  listView: document.getElementById("listView"),
  detailView: document.getElementById("detailView"),
  backButton: document.getElementById("backButton"),
  detailName: document.getElementById("detailName"),
  detailRole: document.getElementById("detailRole"),
  detailDescription: document.getElementById("detailDescription"),
  detailStatus: document.getElementById("detailStatus"),
  detailConfidence: document.getElementById("detailConfidence"),
  detailUpdated: document.getElementById("detailUpdated"),
  detailTarget: document.getElementById("detailTarget"),
  detailNext: document.getElementById("detailNext"),
  detailBlocker: document.getElementById("detailBlocker"),
  detailTabs: document.getElementById("detailTabs"),
  detailContent: document.getElementById("detailContent"),
  fileDialog: document.getElementById("fileDialog"),
  viewerType: document.getElementById("viewerType"),
  viewerName: document.getElementById("viewerName"),
  viewerPath: document.getElementById("viewerPath"),
  viewerModes: document.getElementById("viewerModes"),
  viewerBody: document.getElementById("viewerBody"),
  copyPathButton: document.getElementById("copyPathButton"),
  openPublicButton: document.getElementById("openPublicButton"),
  openRawButton: document.getElementById("openRawButton"),
  closeViewerButton: document.getElementById("closeViewerButton"),
  toast: document.getElementById("toast"),
};

function withToken(path, params = {}) {
  const url = new URL(path, window.location.origin);
  url.searchParams.set("token", token);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  return `${url.pathname}${url.search}`;
}

async function getJSON(path, params = {}) {
  const response = await fetch(withToken(path, params), { cache: "no-store" });
  const payload = await response.json().catch(() => ({ error: "Invalid server response" }));
  if (!response.ok) {
    throw new Error(payload.error || `Request failed (${response.status})`);
  }
  return payload;
}

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMath(tex, displayMode, source) {
  if (!tex.trim()) return escapeHTML(source);
  try {
    const rendered = katex.renderToString(tex, {
      displayMode,
      throwOnError: false,
      strict: "ignore",
      trust: false,
      maxSize: 30,
      maxExpand: 1000,
      output: "htmlAndMathml",
    });
    return displayMode
      ? `<div class="math-block">${rendered}</div>`
      : `<span class="math-inline">${rendered}</span>`;
  } catch (error) {
    return `<span class="math-fallback" title="${escapeHTML(error.message)}">${escapeHTML(source)}</span>`;
  }
}

function isEscaped(text, index) {
  let backslashes = 0;
  for (let cursor = index - 1; cursor >= 0 && text[cursor] === "\\"; cursor -= 1) {
    backslashes += 1;
  }
  return backslashes % 2 === 1;
}

function parseInlineMath(text, start) {
  if (text.startsWith("\\(", start)) {
    const end = text.indexOf("\\)", start + 2);
    if (end >= 0) {
      const source = text.slice(start, end + 2);
      return {
        html: renderMath(text.slice(start + 2, end), false, source),
        end: end + 2,
      };
    }
  }

  if (text[start] !== "$" || text[start + 1] === "$" || isEscaped(text, start)) return null;
  for (let cursor = start + 1; cursor < text.length; cursor += 1) {
    if (text[cursor] !== "$" || text[cursor + 1] === "$" || isEscaped(text, cursor)) continue;
    const source = text.slice(start, cursor + 1);
    return {
      html: renderMath(text.slice(start + 1, cursor), false, source),
      end: cursor + 1,
    };
  }
  return null;
}

function parseDisplayMath(lines, start) {
  const first = lines[start].trim();
  const opener = first.startsWith("$$") ? "$$" : "\\[";
  const closer = opener === "$$" ? "$$" : "\\]";
  const body = [];
  let current = first.slice(opener.length);
  let index = start;

  if (current.endsWith(closer)) {
    body.push(current.slice(0, -closer.length));
    return {
      html: renderMath(body.join("\n"), true, first),
      next: start + 1,
    };
  }

  body.push(current);
  index += 1;
  while (index < lines.length) {
    current = lines[index].trimEnd();
    if (current.endsWith(closer)) {
      body.push(current.slice(0, -closer.length));
      const source = [lines[start], ...lines.slice(start + 1, index + 1)].join("\n");
      return {
        html: renderMath(body.join("\n"), true, source),
        next: index + 1,
      };
    }
    body.push(lines[index]);
    index += 1;
  }

  const source = lines.slice(start).join("\n");
  return {
    html: `<pre class="math-fallback">${escapeHTML(source)}</pre>`,
    next: lines.length,
  };
}

function formatDate(value) {
  if (!value) return "Not recorded";
  const parsed = new Date(`${value}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("en-CA", { year: "numeric", month: "short", day: "2-digit" }).format(parsed);
}

function formatGenerated(value) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Local state loaded";
  return `Updated ${new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "short" }).format(parsed)}`;
}

function fileType(path) {
  const extension = (path.split(".").pop() || "file").toUpperCase();
  if (extension === "MARKDOWN") return "MD";
  return extension.length <= 4 ? extension : "FILE";
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("is-visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 1800);
}

function renderMetrics(totals) {
  const items = [
    [totals.projects, "Registered projects"],
    [totals.recent, "Updated in 7 days"],
    [totals.open_problems, "Open obligations"],
    [totals.pending_handoffs, "Pending Pro handoffs"],
    [totals.inbox, "Inbox files"],
  ];
  elements.metrics.innerHTML = items.map(([value, label]) => `
    <div class="metric">
      <span class="metric-value">${escapeHTML(value)}</span>
      <span class="metric-label">${escapeHTML(label)}</span>
    </div>
  `).join("");
}

function renderRoleOptions(projects) {
  const current = elements.roleFilter.value;
  const roles = [...new Set(projects.map((project) => project.role))].sort();
  elements.roleFilter.innerHTML = `<option value="all">All</option>${roles.map((role) => `<option value="${escapeHTML(role)}">${escapeHTML(role)}</option>`).join("")}`;
  elements.roleFilter.value = roles.includes(current) ? current : "all";
}

function filteredProjects() {
  const query = elements.projectSearch.value.trim().toLowerCase();
  const role = elements.roleFilter.value;
  return state.overview.projects.filter((project) => {
    const roleMatch = role === "all" || project.role === role;
    const text = [project.title, project.path, project.description, project.target, project.next_action, project.status].join(" ").toLowerCase();
    return roleMatch && (!query || text.includes(query));
  });
}

function renderProjects() {
  const projects = filteredProjects();
  elements.projectCount.textContent = `${projects.length} of ${state.overview.projects.length}`;
  elements.emptyProjects.hidden = projects.length > 0;
  elements.projectRows.innerHTML = projects.map((project) => {
    const pending = project.handoff.pending;
    const handoffValue = project.handoff.total ? `${pending}/${project.handoff.total}` : "0";
    return `
      <tr tabindex="0" data-project="${escapeHTML(project.path)}">
        <td>
          <div class="project-name">${escapeHTML(project.title)}</div>
          <div class="project-description">${escapeHTML(project.description)}</div>
        </td>
        <td><span class="role-label" data-role="${escapeHTML(project.role)}">${escapeHTML(project.role)}</span></td>
        <td class="date-cell">${escapeHTML(formatDate(project.last_updated))}</td>
        <td><p class="cell-clamp">${escapeHTML(project.target)}</p></td>
        <td><p class="cell-clamp">${escapeHTML(project.next_action)}</p></td>
        <td class="count-cell">${escapeHTML(project.counts.open_problems)}<span class="subcount">${escapeHTML(project.counts.closed_problems)} closed</span></td>
        <td class="count-cell">${escapeHTML(handoffValue)}<span class="subcount">pending / total</span></td>
      </tr>
    `;
  }).join("");
}

function parseInlineLink(text, start) {
  const labelEnd = text.indexOf("](", start);
  if (labelEnd < 0) return null;
  let cursor = labelEnd + 2;
  let depth = 1;
  let escaped = false;
  while (cursor < text.length) {
    const char = text[cursor];
    if (!escaped) {
      if (char === "(") depth += 1;
      if (char === ")") {
        depth -= 1;
        if (depth === 0) break;
      }
    }
    escaped = char === "\\" && !escaped;
    if (char !== "\\") escaped = false;
    cursor += 1;
  }
  if (depth !== 0) return null;
  return {
    label: text.slice(start + 1, labelEnd),
    target: text.slice(labelEnd + 2, cursor).trim(),
    end: cursor + 1,
  };
}

function inlineMarkdown(text, context) {
  let output = "";
  let index = 0;
  while (index < text.length) {
    if (text.startsWith('<a id="', index)) {
      const anchor = text.slice(index).match(/^<a id="([A-Za-z0-9:._-]+)"><\/a>/);
      if (anchor) {
        output += `<span id="${escapeHTML(anchor[1])}" class="markdown-anchor" aria-hidden="true"></span>`;
        index += anchor[0].length;
        continue;
      }
    }
    if (text[index] === "[" && context) {
      const parsed = parseInlineLink(text, index);
      if (parsed) {
        const label = inlineMarkdown(parsed.label, null);
        if (/^(https?:|mailto:)/i.test(parsed.target)) {
          output += `<a href="${escapeHTML(parsed.target)}" target="_blank" rel="noopener">${label}</a>`;
        } else {
          output += `<button class="local-file-link" type="button" data-file-project="${escapeHTML(context.project)}" data-file-source="${escapeHTML(context.source)}" data-file-target="${escapeHTML(parsed.target)}" data-file-new-tab="true">${label}</button>`;
        }
        index = parsed.end;
        continue;
      }
    }
    if (text[index] === "`" && text.indexOf("`", index + 1) > index) {
      const end = text.indexOf("`", index + 1);
      output += `<code>${escapeHTML(text.slice(index + 1, end))}</code>`;
      index = end + 1;
      continue;
    }
    const math = parseInlineMath(text, index);
    if (math) {
      output += math.html;
      index = math.end;
      continue;
    }
    if (text.startsWith("**", index) && text.indexOf("**", index + 2) > index) {
      const end = text.indexOf("**", index + 2);
      output += `<strong>${inlineMarkdown(text.slice(index + 2, end), context)}</strong>`;
      index = end + 2;
      continue;
    }
    if (text[index] === "*" && text[index + 1] !== "*" && !isEscaped(text, index)) {
      let end = index + 1;
      while (end < text.length) {
        if (
          text[end] === "*"
          && text[end - 1] !== "*"
          && text[end + 1] !== "*"
          && !isEscaped(text, end)
        ) break;
        end += 1;
      }
      if (end < text.length) {
        output += `<em>${inlineMarkdown(text.slice(index + 1, end), context)}</em>`;
        index = end + 1;
        continue;
      }
    }
    output += escapeHTML(text[index]);
    index += 1;
  }
  return output;
}

function splitTableRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

function isTableSeparator(line) {
  const cells = splitTableRow(line);
  return cells.length > 0 && cells.every((cell) => /^:?-{3,}:?$/.test(cell.replaceAll(" ", "")));
}

function slugifyHeading(value) {
  return value.toLowerCase().replace(/[`*_]/g, "").replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "");
}

function isBlockStart(lines, index) {
  const line = lines[index] || "";
  const next = lines[index + 1] || "";
  return !line.trim()
    || /^```/.test(line)
    || /^#{1,4}\s+/.test(line)
    || /^\s*[-*+]\s+/.test(line)
    || /^\s*\d+\.\s+/.test(line)
    || /^>\s?/.test(line)
    || /^\s*(\$\$|\\\[)/.test(line)
    || /^\s*---+\s*$/.test(line)
    || (line.includes("|") && isTableSeparator(next));
}

function renderMarkdown(markdown, context) {
  const lines = String(markdown || "").replaceAll("\r\n", "\n").split("\n");
  const output = [];
  let index = 0;
  while (index < lines.length) {
    const line = lines[index];
    if (line.trim().startsWith("<!--")) {
      while (index < lines.length && !lines[index].includes("-->")) index += 1;
      index += index < lines.length ? 1 : 0;
      continue;
    }
    if (!line.trim()) {
      index += 1;
      continue;
    }
    if (line.startsWith("```")) {
      const language = line.slice(3).trim();
      const body = [];
      index += 1;
      while (index < lines.length && !lines[index].startsWith("```")) {
        body.push(lines[index]);
        index += 1;
      }
      index += index < lines.length ? 1 : 0;
      output.push(`<pre data-language="${escapeHTML(language)}"><code>${escapeHTML(body.join("\n"))}</code></pre>`);
      continue;
    }
    if (/^\s*(\$\$|\\\[)/.test(line)) {
      const math = parseDisplayMath(lines, index);
      output.push(math.html);
      index = math.next;
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const title = heading[2].trim();
      output.push(`<h${level} id="${escapeHTML(slugifyHeading(title))}">${inlineMarkdown(title, context)}</h${level}>`);
      index += 1;
      continue;
    }
    if (line.includes("|") && index + 1 < lines.length && isTableSeparator(lines[index + 1])) {
      const header = splitTableRow(line);
      const rows = [];
      index += 2;
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
        rows.push(splitTableRow(lines[index]));
        index += 1;
      }
      output.push(`<table><thead><tr>${header.map((cell) => `<th>${inlineMarkdown(cell, context)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${inlineMarkdown(cell, context)}</td>`).join("")}</tr>`).join("")}</tbody></table>`);
      continue;
    }
    if (/^\s*[-*+]\s+/.test(line)) {
      const items = [];
      while (index < lines.length && /^\s*[-*+]\s+/.test(lines[index])) {
        let item = lines[index].replace(/^\s*[-*+]\s+/, "");
        const checkbox = item.match(/^\[([ xX])\]\s+(.*)$/);
        if (checkbox) {
          item = `<input type="checkbox" disabled ${checkbox[1].toLowerCase() === "x" ? "checked" : ""}> ${inlineMarkdown(checkbox[2], context)}`;
        } else {
          item = inlineMarkdown(item, context);
        }
        items.push(`<li>${item}</li>`);
        index += 1;
      }
      output.push(`<ul>${items.join("")}</ul>`);
      continue;
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = [];
      while (index < lines.length && /^\s*\d+\.\s+/.test(lines[index])) {
        items.push(`<li>${inlineMarkdown(lines[index].replace(/^\s*\d+\.\s+/, ""), context)}</li>`);
        index += 1;
      }
      output.push(`<ol>${items.join("")}</ol>`);
      continue;
    }
    if (/^>\s?/.test(line)) {
      const body = [];
      while (index < lines.length && /^>\s?/.test(lines[index])) {
        body.push(lines[index].replace(/^>\s?/, ""));
        index += 1;
      }
      output.push(`<blockquote>${renderMarkdown(body.join("\n"), context)}</blockquote>`);
      continue;
    }
    if (/^\s*---+\s*$/.test(line)) {
      output.push("<hr>");
      index += 1;
      continue;
    }

    const paragraph = [line.trim()];
    index += 1;
    while (index < lines.length && !isBlockStart(lines, index)) {
      paragraph.push(lines[index].trim());
      index += 1;
    }
    output.push(`<p>${inlineMarkdown(paragraph.join(" "), context)}</p>`);
  }
  return `<div class="markdown-body">${output.join("")}</div>`;
}

function renderSource(content, locator = null) {
  return `<pre class="source-code">${String(content).replaceAll("\r\n", "\n").split("\n").map((line, index) => {
    const lineNumber = index + 1;
    const highlighted = locator && lineNumber >= locator.start && lineNumber <= locator.end;
    return `<span id="source-L${lineNumber}" class="source-line${highlighted ? " is-target" : ""}" data-line="${lineNumber}">${escapeHTML(line) || " "}</span>`;
  }).join("")}</pre>`;
}

const tabs = [
  ["state", "Research state", "Research State", null],
  ["theorems", "Known theorems", "Known Theorems", "known_theorems"],
  ["open", "Open problems", "Open Problems", "open_problems"],
  ["failures", "Failed attempts", "Failed Attempts", "failed_attempts"],
  ["references", "References", "References", "references"],
  ["files", "Files", null, null],
];

function renderTabs() {
  elements.detailTabs.innerHTML = tabs.map(([key, label, , countKey]) => {
    const count = countKey ? `<span class="tab-count">${escapeHTML(state.detail.counts[countKey])}</span>` : "";
    return `<button class="tab-button" type="button" role="tab" data-tab="${key}" aria-selected="${state.activeTab === key}">${label}${count}</button>`;
  }).join("");
}

function fileRow({ project, source, target, label, kind = "text", disabled = false, meta = "" }) {
  const type = kind === "pdf" ? "PDF" : fileType(target);
  const tag = disabled ? "div" : "button";
  const attributes = disabled
    ? ""
    : `type="button" data-file-project="${escapeHTML(project)}" data-file-source="${escapeHTML(source)}" data-file-target="${escapeHTML(target)}"`;
  return `<${tag} class="file-row file-row-button${disabled ? " is-disabled" : ""}" ${attributes}>
    <span class="file-type">${escapeHTML(type)}</span>
    <span>
      <span class="file-name">${escapeHTML(label || target.split("/").pop())}</span>
      <span class="file-path">${escapeHTML(target)}</span>
    </span>
    <span class="file-kind">${escapeHTML(meta || kind)}</span>
    <span class="file-open-mark">${disabled ? "–" : "↗"}</span>
  </${tag}>`;
}

function renderFiles() {
  const detail = state.detail;
  const localLinks = detail.links.filter((link) => link.kind !== "external");
  const externalLinks = detail.links.filter((link) => link.kind === "external");
  const referenced = localLinks.length
    ? localLinks.map((link) => fileRow({
        project: detail.path,
        source: link.source || "research_state.md",
        target: link.relative_path || link.target,
        label: link.label,
        kind: link.kind,
        disabled: link.kind === "missing" || link.kind === "directory",
        meta: link.kind === "missing" ? "missing" : link.kind,
      })).join("")
    : `<div class="empty-state">No referenced files</div>`;

  const projectFiles = [
    ...detail.core_files.map((path) => ({ path, meta: "core" })),
    ...detail.daily_notes.slice(0, 12).map((path) => ({ path, meta: "daily note" })),
    ...detail.memory_files.map((path) => ({ path, meta: "memory" })),
  ];
  const projectRows = projectFiles.map((item) => fileRow({
    project: detail.path,
    source: "research_state.md",
    target: item.path,
    label: item.path.split("/").pop(),
    kind: "text",
    meta: item.meta,
  })).join("");

  const external = externalLinks.length ? `
    <section class="file-section">
      <h3>External links</h3>
      <div class="file-list">${externalLinks.map((link) => `
        <a class="file-row file-row-button" href="${escapeHTML(link.href)}" target="_blank" rel="noopener">
          <span class="file-type">URL</span>
          <span><span class="file-name">${escapeHTML(link.label)}</span><span class="file-path">${escapeHTML(link.href)}</span></span>
          <span class="file-kind">external</span><span class="file-open-mark">↗</span>
        </a>`).join("")}</div>
    </section>` : "";

  return `
    <section class="file-section"><h3>Referenced files</h3><div class="file-list">${referenced}</div></section>
    <section class="file-section"><h3>Project files</h3><div class="file-list">${projectRows}</div></section>
    ${external}
  `;
}

function renderDetailContent() {
  if (!state.detail) return;
  if (state.activeTab === "files") {
    elements.detailContent.innerHTML = renderFiles();
    return;
  }
  const tab = tabs.find(([key]) => key === state.activeTab);
  const sectionName = tab?.[2] || "Research State";
  const content = state.detail.sections[sectionName] || "No content recorded.";
  elements.detailContent.innerHTML = renderMarkdown(content, { project: state.detail.path, source: "research_state.md" });
}

function renderDetail() {
  const detail = state.detail;
  elements.detailName.textContent = detail.title;
  elements.detailRole.textContent = detail.role;
  elements.detailRole.dataset.role = detail.role;
  elements.detailDescription.textContent = detail.description;
  elements.detailStatus.innerHTML = inlineMarkdown(detail.status, null);
  elements.detailConfidence.innerHTML = inlineMarkdown(detail.confidence, null);
  elements.detailUpdated.textContent = formatDate(detail.last_updated);
  elements.detailTarget.innerHTML = inlineMarkdown(detail.target, null);
  elements.detailNext.innerHTML = inlineMarkdown(detail.next_action, null);
  elements.detailBlocker.innerHTML = inlineMarkdown(detail.blocker, null);
  renderTabs();
  renderDetailContent();
}

async function loadOverview() {
  elements.refreshButton.disabled = true;
  try {
    state.overview = await getJSON("/api/overview");
    elements.generatedAt.textContent = formatGenerated(state.overview.generated_at);
    renderMetrics(state.overview.totals);
    renderRoleOptions(state.overview.projects);
    renderProjects();
  } catch (error) {
    elements.metrics.innerHTML = `<div class="error-state">${escapeHTML(error.message)}</div>`;
    elements.projectRows.innerHTML = "";
  } finally {
    elements.refreshButton.disabled = false;
  }
}

async function openProject(slug, updateHash = true) {
  elements.listView.hidden = true;
  elements.detailView.hidden = false;
  elements.detailContent.innerHTML = `<div class="loading-state">Loading project state</div>`;
  try {
    state.detail = await getJSON(`/api/projects/${encodeURIComponent(slug)}`);
    state.activeTab = "state";
    renderDetail();
    if (updateHash) window.location.hash = `project/${encodeURIComponent(slug)}`;
    window.scrollTo({ top: 0, behavior: "instant" });
  } catch (error) {
    elements.detailContent.innerHTML = `<div class="error-state">${escapeHTML(error.message)}</div>`;
  }
}

function showProjectList(updateHash = true) {
  state.detail = null;
  elements.detailView.hidden = true;
  elements.listView.hidden = false;
  if (updateHash) window.location.hash = "";
  window.scrollTo({ top: 0, behavior: "instant" });
}

function rawPDFUrl(project, relativePath, fragment = "") {
  const base = withToken(`/raw/${encodeURIComponent(project)}`, { path: relativePath });
  return fragment ? `${base}#${encodeURI(fragment)}` : base;
}

function directFileUrl(project, source, target) {
  return withToken("/", {
    viewer_project: project,
    viewer_source: source || "research_state.md",
    viewer_path: target,
  });
}

function scrollToLocator() {
  if (!state.viewer?.locator) return;
  window.requestAnimationFrame(() => {
    elements.viewerBody.querySelector(".source-line.is-target")?.scrollIntoView({ block: "center" });
  });
}

function setViewerMode(mode) {
  if (!state.viewer || state.viewer.kind !== "markdown") return;
  state.viewerMode = mode;
  elements.viewerModes.querySelectorAll("button").forEach((button) => {
    button.setAttribute("aria-pressed", button.dataset.viewerMode === mode ? "true" : "false");
  });
  if (mode === "rendered") {
    elements.viewerBody.innerHTML = renderMarkdown(state.viewer.content, { project: state.viewer.project, source: state.viewer.relative_path });
    if (state.viewer.fragment) {
      window.requestAnimationFrame(() => {
        const target = elements.viewerBody.querySelector(`#${CSS.escape(state.viewer.fragment)}`);
        target?.scrollIntoView({ block: "start" });
      });
    }
  } else {
    elements.viewerBody.innerHTML = renderSource(state.viewer.content, state.viewer.locator);
    scrollToLocator();
  }
}

async function openFile(project, source, target) {
  if (!target || /^(https?:|mailto:)/i.test(target)) return;
  if (!elements.fileDialog.open) elements.fileDialog.showModal();
  elements.viewerName.textContent = "Loading";
  elements.viewerPath.textContent = target;
  elements.viewerType.textContent = fileType(target);
  elements.viewerModes.hidden = true;
  elements.openPublicButton.hidden = true;
  elements.openRawButton.hidden = true;
  elements.viewerBody.innerHTML = `<div class="loading-state">Opening local file</div>`;
  try {
    state.viewer = await getJSON(`/api/files/${encodeURIComponent(project)}`, { source, path: target });
    elements.viewerName.textContent = state.viewer.name;
    elements.viewerPath.textContent = state.viewer.relative_path;
    elements.viewerType.textContent = state.viewer.kind === "pdf" ? "PDF" : fileType(state.viewer.relative_path);
    if (state.viewer.public_source) {
      elements.openPublicButton.href = state.viewer.public_source;
      elements.openPublicButton.hidden = false;
    }
    if (state.viewer.kind === "pdf") {
      const rawUrl = rawPDFUrl(project, state.viewer.relative_path, state.viewer.fragment);
      elements.openRawButton.href = rawUrl;
      elements.openRawButton.hidden = false;
      elements.viewerBody.innerHTML = `<iframe class="pdf-frame" src="${escapeHTML(rawUrl)}" title="${escapeHTML(state.viewer.name)}"></iframe>`;
    } else if (state.viewer.kind === "markdown") {
      elements.viewerModes.hidden = false;
      setViewerMode("rendered");
    } else {
      elements.viewerBody.innerHTML = renderSource(state.viewer.content, state.viewer.locator);
      scrollToLocator();
    }
  } catch (error) {
    state.viewer = null;
    elements.viewerBody.innerHTML = `<div class="error-state">${escapeHTML(error.message)}</div>`;
  }
}

async function copyViewerPath() {
  if (!state.viewer?.absolute_path) return;
  try {
    await navigator.clipboard.writeText(state.viewer.absolute_path);
  } catch {
    const input = document.createElement("textarea");
    input.value = state.viewer.absolute_path;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    input.remove();
  }
  showToast("Path copied");
}

document.addEventListener("click", (event) => {
  const row = event.target.closest("tr[data-project]");
  if (row) openProject(row.dataset.project);

  const localFile = event.target.closest("[data-file-target]");
  if (localFile) {
    event.preventDefault();
    const project = localFile.dataset.fileProject;
    const source = localFile.dataset.fileSource || "research_state.md";
    const target = localFile.dataset.fileTarget;
    if (localFile.dataset.fileNewTab === "true") {
      window.open(directFileUrl(project, source, target), "_blank", "noopener");
    } else {
      openFile(project, source, target);
    }
  }

  const tab = event.target.closest("[data-tab]");
  if (tab) {
    state.activeTab = tab.dataset.tab;
    renderTabs();
    renderDetailContent();
  }

  const viewerMode = event.target.closest("[data-viewer-mode]");
  if (viewerMode) setViewerMode(viewerMode.dataset.viewerMode);
});

document.addEventListener("keydown", (event) => {
  if ((event.key === "Enter" || event.key === " ") && event.target.matches("tr[data-project]")) {
    event.preventDefault();
    openProject(event.target.dataset.project);
  }
});

elements.projectSearch.addEventListener("input", renderProjects);
elements.roleFilter.addEventListener("change", renderProjects);
elements.refreshButton.addEventListener("click", async () => {
  await loadOverview();
  if (state.detail) await openProject(state.detail.path, false);
});
elements.backButton.addEventListener("click", () => showProjectList());
elements.closeViewerButton.addEventListener("click", () => elements.fileDialog.close());
elements.copyPathButton.addEventListener("click", copyViewerPath);
elements.fileDialog.addEventListener("click", (event) => {
  if (event.target === elements.fileDialog) elements.fileDialog.close();
});
elements.fileDialog.addEventListener("close", () => {
  elements.viewerBody.innerHTML = "";
  state.viewer = null;
});

window.addEventListener("hashchange", () => {
  const match = window.location.hash.match(/^#project\/(.+)$/);
  if (match) {
    const slug = decodeURIComponent(match[1]);
    if (!state.detail || state.detail.path !== slug) openProject(slug, false);
  } else if (!elements.listView.hidden) {
    return;
  } else {
    showProjectList(false);
  }
});

async function start() {
  if (!token) {
    elements.metrics.innerHTML = `<div class="error-state">Dashboard session token is missing</div>`;
    return;
  }
  await loadOverview();
  const directParams = new URLSearchParams(window.location.search);
  const directProject = directParams.get("viewer_project");
  const directSource = directParams.get("viewer_source") || "research_state.md";
  const directPath = directParams.get("viewer_path");
  if (directProject && directPath) {
    await openProject(directProject, false);
    await openFile(directProject, directSource, directPath);
    return;
  }
  const match = window.location.hash.match(/^#project\/(.+)$/);
  if (match) await openProject(decodeURIComponent(match[1]), false);
}

start();
