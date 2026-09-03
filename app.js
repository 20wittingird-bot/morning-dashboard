// 必要であれば "owner/repo" 形式で直接指定してください。
// 空のままなら、GitHub Pagesの現在のURLから自動推測します。
const REPO_OVERRIDE = "";

function detectRepo() {
  if (REPO_OVERRIDE) return REPO_OVERRIDE;
  const host = location.hostname; // 例: username.github.io
  const owner = host.split(".")[0];
  const pathParts = location.pathname.split("/").filter(Boolean);
  const repoName = pathParts[0] || `${owner}.github.io`;
  return `${owner}/${repoName}`;
}

async function loadJSON(path) {
  try {
    const res = await fetch(`${path}?_=${Date.now()}`);
    if (!res.ok) throw new Error(res.statusText);
    return await res.json();
  } catch (e) {
    console.error(`failed to load ${path}`, e);
    return null;
  }
}

function escapeHTML(str) {
  return String(str ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function setGreeting() {
  const hour = new Date().getHours();
  let text = "おはようございます";
  if (hour >= 11 && hour < 17) text = "こんにちは";
  else if (hour >= 17) text = "こんばんは";
  document.getElementById("greeting").textContent = text;

  const dateStr = new Date().toLocaleDateString("ja-JP", {
    year: "numeric", month: "long", day: "numeric", weekday: "long",
  });
  document.getElementById("dateLine").textContent = dateStr;
}

function weatherIconSVG(code) {
  const stroke = "#eeeae2";
  const sun = "#e7a348";
  if (code === 0 || code === 1) {
    return `<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="5" stroke="${sun}" stroke-width="1.6"/>
      <g stroke="${sun}" stroke-width="1.6" stroke-linecap="round">
        <line x1="12" y1="1.5" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22.5"/>
        <line x1="1.5" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22.5" y2="12"/>
        <line x1="4.5" y1="4.5" x2="6.2" y2="6.2"/><line x1="17.8" y1="17.8" x2="19.5" y2="19.5"/>
        <line x1="4.5" y1="19.5" x2="6.2" y2="17.8"/><line x1="17.8" y1="6.2" x2="19.5" y2="4.5"/>
      </g></svg>`;
  }
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) {
    return `<svg viewBox="0 0 24 24" fill="none"><path d="M6 10.5a4.5 4.5 0 0 1 8.7-1.6A3.8 3.8 0 0 1 18.5 12.5 3.5 3.5 0 0 1 15 16H6.5a3.5 3.5 0 0 1-.5-6.95Z" stroke="${stroke}" stroke-width="1.4"/>
      <g stroke="${sun}" stroke-width="1.5" stroke-linecap="round"><line x1="8" y1="18" x2="7" y2="21"/><line x1="12" y1="18" x2="11" y2="21"/><line x1="16" y1="18" x2="15" y2="21"/></g></svg>`;
  }
  if (code >= 71 && code <= 86) {
    return `<svg viewBox="0 0 24 24" fill="none"><path d="M6 10.5a4.5 4.5 0 0 1 8.7-1.6A3.8 3.8 0 0 1 18.5 12.5 3.5 3.5 0 0 1 15 16H6.5a3.5 3.5 0 0 1-.5-6.95Z" stroke="${stroke}" stroke-width="1.4"/>
      <g stroke="${stroke}" stroke-width="1.5" stroke-linecap="round"><line x1="8" y1="18" x2="8" y2="21"/><line x1="12" y1="18" x2="12" y2="21"/><line x1="16" y1="18" x2="16" y2="21"/></g></svg>`;
  }
  if (code >= 95) {
    return `<svg viewBox="0 0 24 24" fill="none"><path d="M6 9.5a4.5 4.5 0 0 1 8.7-1.6A3.8 3.8 0 0 1 18.5 11.5 3.5 3.5 0 0 1 15 15H6.5a3.5 3.5 0 0 1-.5-5.95Z" stroke="${stroke}" stroke-width="1.4"/>
      <path d="M13 16l-2.4 4h2.6L11 24" stroke="${sun}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }
  return `<svg viewBox="0 0 24 24" fill="none"><path d="M6 10.5a4.5 4.5 0 0 1 8.7-1.6A3.8 3.8 0 0 1 18.5 12.5 3.5 3.5 0 0 1 15 16H6.5a3.5 3.5 0 0 1-.5-6.95Z" stroke="${stroke}" stroke-width="1.4"/></svg>`;
}

function renderWeather(weather) {
  if (!weather) return;
  document.getElementById("weatherIcon").innerHTML = weatherIconSVG(weather.weather_code);
  document.getElementById("weatherTemp").textContent =
    `${Math.round(weather.temp_min)}° / ${Math.round(weather.temp_max)}°`;
  const rain = weather.precipitation_probability != null
    ? `・降水確率${weather.precipitation_probability}%` : "";
  document.getElementById("weatherText").textContent =
    `${weather.city} ${weather.weather_text}${rain}`;
}

function renderOutfit(outfit) {
  const el = document.getElementById("outfitBody");
  if (!outfit || !outfit.suggestion) {
    el.innerHTML = `<p class="empty">${escapeHTML(outfit?.note || "コーデ提案がまだありません。")}</p>`;
    return;
  }
  const items = outfit.suggestion.items.map(i => `<li>${escapeHTML(i)}</li>`).join("");
  el.innerHTML = `
    <ul class="outfit__items">${items}</ul>
    <p class="outfit__reason">${escapeHTML(outfit.suggestion.reason || "")}</p>
  `;
}

function renderCompat(outfit, wardrobe) {
  const select = document.getElementById("compatSelect");
  const result = document.getElementById("compatResult");
  const items = wardrobe?.items || [];

  items.forEach(it => {
    const opt = document.createElement("option");
    opt.value = it.name;
    opt.textContent = `${it.name}(${it.category})`;
    select.appendChild(opt);
  });

  select.addEventListener("change", () => {
    const name = select.value;
    if (!name) { result.innerHTML = ""; return; }
    const compat = outfit?.compatibility?.[name] || [];
    if (compat.length === 0) {
      result.innerHTML = `<p class="empty">相性データがまだありません。</p>`;
      return;
    }
    result.innerHTML = `<ul>${compat.map(c => `<li>${escapeHTML(c)}</li>`).join("")}</ul>`;
  });
}

function renderToday(today) {
  const el = document.getElementById("todayBody");
  const items = today?.items || [];
  const memo = today?.memo || "";

  if (items.length === 0 && !memo) {
    el.innerHTML = `<p class="empty">予定はありません。</p>`;
    return;
  }

  const rows = items.map(i =>
    `<span class="today-line__row">${escapeHTML(i.time)} ${escapeHTML(i.title)}</span>`
  ).join("");
  const memoLine = memo ? `<span class="today-line__memo">${escapeHTML(memo)}</span>` : "";

  el.innerHTML = `<p class="today-line">${rows}${memoLine}</p>`;
}

function renderNews(news) {
  const el = document.getElementById("newsBody");
  const general = news?.general || [];
  const topics = news?.topics || {};
  const hasAny = general.length > 0 || Object.values(topics).some(v => v.length > 0);

  if (!hasAny) {
    el.innerHTML = `<p class="empty">ニュースがまだ取得されていません。</p>`;
    return;
  }

  let html = "";
  if (general.length > 0) {
    html += `<div class="news__group">
      <p class="news__group-title">主要ニュース</p>
      <ul class="news__list">${general.map(newsItem).join("")}</ul>
    </div>`;
  }
  const topicEntries = Object.entries(topics).filter(([, list]) => list.length > 0);
  topicEntries.forEach(([topic, list], i) => {
    const extraClass = i === 0 ? " news__group--extra" : " news__group--extra";
    html += `<div class="news__group${extraClass}">
      <p class="news__group-title">${escapeHTML(topic)}</p>
      <ul class="news__list">${list.map(newsItem).join("")}</ul>
    </div>`;
  });
  el.innerHTML = html;
}

function newsItem(item) {
  return `<li><a href="${escapeHTML(item.link)}" target="_blank" rel="noopener">${escapeHTML(item.title)}</a></li>`;
}

function renderWardrobe(wardrobe) {
  const el = document.getElementById("wardrobeBody");
  const items = wardrobe?.items || [];
  document.getElementById("wardrobeCount").textContent = `(${items.length}点)`;

  if (items.length === 0) {
    el.innerHTML = `<p class="empty">持ち服が登録されていません。</p>`;
    return;
  }
  const byCategory = {};
  items.forEach(it => { (byCategory[it.category] ||= []).push(it.name); });
  el.innerHTML = Object.entries(byCategory).map(([cat, names]) => `
    <div class="wardrobe__category">
      <p class="wardrobe__category-title">${escapeHTML(cat)}</p>
      <ul class="wardrobe__items">${names.map(n => `<li>${escapeHTML(n)}</li>`).join("")}</ul>
    </div>
  `).join("");
}

function buildIssueUrl(title, body, label) {
  const repo = detectRepo();
  const params = new URLSearchParams({ title, body, labels: label });
  return `https://github.com/${repo}/issues/new?${params.toString()}`;
}

function showNote(el, message) {
  el.textContent = message;
  el.style.display = "block";
  setTimeout(() => { el.style.display = "none"; }, 4000);
}

function setupSubmitButtons() {
  document.getElementById("memoSubmit").addEventListener("click", () => {
    const text = document.getElementById("memoInput").value.trim();
    const note = document.getElementById("scheduleNote");
    if (!text) { showNote(note, "メモを入力してください。"); return; }
    window.open(buildIssueUrl("今日のメモ登録", text, "schedule-memo"), "_blank");
    showNote(note, "GitHubのタブを開きました。内容を確認して送信してください。");
  });

  document.getElementById("animeSubmit").addEventListener("click", () => {
    const text = document.getElementById("animeInput").value.trim();
    const note = document.getElementById("scheduleNote");
    if (!text) { showNote(note, "登録するアニメを入力してください。"); return; }
    window.open(buildIssueUrl("アニメ一括登録", text, "schedule-anime"), "_blank");
    showNote(note, "GitHubのタブを開きました。内容を確認して送信してください。");
  });

  document.getElementById("wardrobeSubmit").addEventListener("click", () => {
    const text = document.getElementById("wardrobeInput").value.trim();
    const note = document.getElementById("wardrobeNote");
    if (!text) { showNote(note, "登録するアイテムを入力してください。"); return; }
    window.open(buildIssueUrl("持ち服を追加", text, "wardrobe-add"), "_blank");
    showNote(note, "GitHubのタブを開きました。内容を確認して送信してください。");
  });
}

function setupToggles() {
  document.querySelectorAll(".add-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const panel = document.getElementById(btn.dataset.toggle);
      const isOpen = panel.classList.toggle("is-open");
      btn.classList.toggle("is-open", isOpen);
    });
  });

  // 今日の予定 / ニュース: タップで横幅いっぱいに展開
  document.querySelectorAll(".row-cards .section__label").forEach(label => {
    label.addEventListener("click", () => {
      const card = label.closest(".section");
      const row = card.closest(".row-cards");
      const alreadyExpanded = card.classList.contains("is-expanded");
      row.querySelectorAll(".section").forEach(c => c.classList.remove("is-expanded", "is-hidden"));
      row.classList.remove("has-expanded");
      if (!alreadyExpanded) {
        card.classList.add("is-expanded");
        row.classList.add("has-expanded");
        row.querySelectorAll(".section").forEach(c => {
          if (c !== card) c.classList.add("is-hidden");
        });
      }
    });
  });

  // 持ち服リスト: タップで開閉
  document.querySelectorAll("[data-toggle-collapse]").forEach(label => {
    label.addEventListener("click", () => {
      const target = document.getElementById(label.dataset.toggleCollapse);
      const chevron = label.querySelector(".chevron");
      const collapsed = target.classList.toggle("is-collapsed");
      chevron.classList.toggle("is-open", !collapsed);
    });
  });
}

async function init() {
  setGreeting();
  setupToggles();
  setupSubmitButtons();

  const [weather, outfit, news, wardrobe, today] = await Promise.all([
    loadJSON("data/weather.json"),
    loadJSON("data/outfit.json"),
    loadJSON("data/news.json"),
    loadJSON("data/wardrobe.json"),
    loadJSON("data/today.json"),
  ]);

  renderWeather(weather);
  renderOutfit(outfit);
  renderCompat(outfit, wardrobe);
  renderToday(today);
  renderNews(news);
  renderWardrobe(wardrobe);
}

init();
