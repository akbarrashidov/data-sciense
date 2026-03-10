/* ═══════════════════════════════════════════════════════
   TECHBLOG — Main JS
   ═══════════════════════════════════════════════════════ */

// ── Theme ──────────────────────────────────────────────
const root = document.documentElement;
const themeBtn = document.getElementById('themeToggle');
const iconSun = themeBtn?.querySelector('.icon-sun');
const iconMoon = themeBtn?.querySelector('.icon-moon');
const hlLight = document.getElementById('hljs-light');
const hlDark  = document.getElementById('hljs-dark');

function applyTheme(dark) {
  root.setAttribute('data-theme', dark ? 'dark' : 'light');
  localStorage.setItem('theme', dark ? 'dark' : 'light');
  if (iconSun)  iconSun.style.display  = dark ? 'none' : 'block';
  if (iconMoon) iconMoon.style.display = dark ? 'block' : 'none';
  if (hlLight) hlLight.disabled = dark;
  if (hlDark)  hlDark.disabled  = !dark;
}

const saved = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
applyTheme(saved === 'dark' || (!saved && prefersDark));

themeBtn?.addEventListener('click', () => {
  applyTheme(root.getAttribute('data-theme') !== 'dark');
});

// ── Scroll: sticky header shadow ──────────────────────
const header = document.getElementById('siteHeader');
window.addEventListener('scroll', () => {
  header?.classList.toggle('scrolled', window.scrollY > 8);
}, { passive: true });

// ── Top banner close ───────────────────────────────────
document.getElementById('bannerClose')?.addEventListener('click', () => {
  document.getElementById('topBanner')?.classList.add('hidden');
  sessionStorage.setItem('bannerClosed', '1');
});
if (sessionStorage.getItem('bannerClosed')) {
  document.getElementById('topBanner')?.classList.add('hidden');
}

// ── Search bar toggle ──────────────────────────────────
const searchToggle = document.getElementById('searchToggle');
const searchBar    = document.getElementById('searchBar');
const searchInput  = document.getElementById('searchBarInput');
const searchClose  = document.getElementById('searchBarClose');

searchToggle?.addEventListener('click', () => {
  searchBar?.classList.toggle('open');
  if (searchBar?.classList.contains('open')) searchInput?.focus();
});
searchClose?.addEventListener('click', () => {
  searchBar?.classList.remove('open');
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') searchBar?.classList.remove('open');
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    searchBar?.classList.toggle('open');
    if (searchBar?.classList.contains('open')) searchInput?.focus();
  }
});

// ── Mobile hamburger ───────────────────────────────────
const hamburger = document.getElementById('hamburger');
const headerNav = document.getElementById('headerNav');

hamburger?.addEventListener('click', () => {
  const open = headerNav?.classList.toggle('open');
  const spans = hamburger.querySelectorAll('span');
  if (open) {
    spans[0].style.transform = 'rotate(45deg) translate(4px, 4px)';
    spans[1].style.opacity = '0';
    spans[2].style.transform = 'rotate(-45deg) translate(4px, -4px)';
  } else {
    spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
  }
});

// ── Load categories/topics ─────────────────────────────
async function loadTopics() {
  try {
    const res = await fetch('/api/categories/');
    const cats = await res.json();

    // Top dropdown
    const panel = document.getElementById('topicsPanel');
    if (panel) {
      panel.innerHTML = cats.map(c => `
        <a href="/category/${c.slug}/" class="drop-item">
          <span class="drop-item-dot" style="background:${c.color}"></span>
          ${c.icon || ''} ${c.name}
          <span class="drop-item-count">${c.article_count}</span>
        </a>
      `).join('') || '<div class="drop-item" style="color:var(--ink-4)">Hali yo\'q</div>';
    }

    // Topics strip
    const strip = document.getElementById('topicsStrip');
    if (strip) {
      const params = new URLSearchParams(location.search);
      const active = params.get('category');
      strip.innerHTML = `
        <a href="/articles/" class="ts-item ${!active ? 'active' : ''}">Barchasi</a>
        ${cats.map(c => `
          <a href="/articles/?category=${c.slug}" class="ts-item ${active === c.slug ? 'active' : ''}">
            ${c.icon || ''} ${c.name}
          </a>
        `).join('')}
      `;
    }

    // Footer
    const footerTopics = document.getElementById('footerTopics');
    if (footerTopics) {
      footerTopics.innerHTML = cats.slice(0, 7).map(c =>
        `<a href="/category/${c.slug}/">${c.name}</a>`
      ).join('');
    }
  } catch(e) {
    const panel = document.getElementById('topicsPanel');
    if (panel) panel.innerHTML = '<div class="drop-item" style="color:var(--ink-4)">Yuklab bo\'lmadi</div>';
  }
}
loadTopics();

// ── Flash messages auto-dismiss ────────────────────────
document.querySelectorAll('.flash').forEach((el, i) => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s, transform .4s';
    el.style.opacity = '0';
    el.style.transform = 'translateX(20px)';
    setTimeout(() => el.remove(), 400);
  }, 4000 + i * 600);
});

// ── Toast ──────────────────────────────────────────────
function showToast(msg, type = 'success', ms = 3000) {
  document.querySelectorAll('.toast').forEach(t => t.remove());
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => {
    t.style.transition = 'opacity .3s, transform .3s';
    t.style.opacity = '0';
    t.style.transform = 'translateY(10px)';
    setTimeout(() => t.remove(), 300);
  }, ms);
}
window.showToast = showToast;

// ── CSRF ───────────────────────────────────────────────
function getCookie(name) {
  for (const c of document.cookie.split(';')) {
    const [k, v] = c.trim().split('=');
    if (k === name) return decodeURIComponent(v);
  }
  return null;
}
window.getCookie = getCookie;

// ── Reading progress bar ───────────────────────────────
const artBody = document.getElementById('artBodyEl');
if (artBody) {
  const bar = document.createElement('div');
  bar.id = 'readProgress';
  document.body.prepend(bar);
  window.addEventListener('scroll', () => {
    const top    = artBody.getBoundingClientRect().top + scrollY;
    const height = artBody.offsetHeight;
    const pct = Math.min(100, Math.max(0, ((scrollY + innerHeight - top) / height) * 100));
    bar.style.width = pct + '%';
  }, { passive: true });
}

// ── Code copy buttons ──────────────────────────────────
document.querySelectorAll('pre').forEach(pre => {
  const btn = document.createElement('button');
  btn.className = 'copy-btn';
  btn.textContent = 'Nusxa';
  pre.appendChild(btn);
  btn.addEventListener('click', async () => {
    const code = pre.querySelector('code')?.textContent || pre.textContent;
    await navigator.clipboard.writeText(code).catch(() => {});
    btn.textContent = 'Kopiyalandi ✓';
    setTimeout(() => btn.textContent = 'Nusxa', 2000);
  });
});

// ── Active TOC link ────────────────────────────────────
const tocLinks = document.querySelectorAll('.toc-nav a');
if (tocLinks.length) {
  const headings = [...document.querySelectorAll('#artBodyEl h2, #artBodyEl h3')];
  window.addEventListener('scroll', () => {
    let current = '';
    headings.forEach(h => { if (scrollY + 100 >= h.offsetTop) current = h.id; });
    tocLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === `#${current}`));
  }, { passive: true });
}

// ── Smooth scroll for TOC ──────────────────────────────
document.addEventListener('click', e => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const target = document.querySelector(a.getAttribute('href'));
  if (target) {
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});

// ── User panel toggle (click fallback) ─────────────────
const userTrigger = document.getElementById('userTrigger');
const userPanel   = document.getElementById('userPanel');
if (userTrigger && userPanel) {
  userTrigger.addEventListener('click', e => {
    e.stopPropagation();
    userPanel.style.display = userPanel.style.display === 'block' ? 'none' : 'block';
  });
  document.addEventListener('click', () => {
    if (userPanel) userPanel.style.display = 'none';
  });
}
