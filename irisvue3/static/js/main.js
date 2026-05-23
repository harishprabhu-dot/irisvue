// IRISVUE — main.js

document.addEventListener('DOMContentLoaded', () => {

  // ── Nav scroll state ─────────────────────────────────
  const nav = document.getElementById('nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

  // ── Nav search ────────────────────────────────────────
  const navBtn    = document.getElementById('nav-search-btn');
  const navPanel  = document.getElementById('nav-search-panel');
  const navInput  = document.getElementById('nav-search-input');
  const navRes    = document.getElementById('nav-search-results');

  if (navBtn && navPanel) {
    navBtn.addEventListener('click', () => {
      navPanel.classList.toggle('open');
      if (navPanel.classList.contains('open')) navInput?.focus();
    });
    document.addEventListener('click', e => {
      if (!e.target.closest('#nav-search-wrap')) navPanel.classList.remove('open');
    });
  }

  let navTimer;
  if (navInput) {
    navInput.addEventListener('input', () => {
      clearTimeout(navTimer);
      const q = navInput.value.trim();
      if (q.length < 2) { if (navRes) navRes.innerHTML = ''; return; }
      navTimer = setTimeout(() => fetchSearch(q, navRes), 300);
    });
    navInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const q = navInput.value.trim();
        if (q) window.location.href = `/search?q=${encodeURIComponent(q)}`;
      }
    });
  }

  // ── Hero search ───────────────────────────────────────
  const heroInput = document.getElementById('hero-input');
  const heroRes   = document.getElementById('hero-results');
  let heroTimer;

  if (heroInput) {
    heroInput.addEventListener('input', () => {
      clearTimeout(heroTimer);
      const q = heroInput.value.trim();
      if (q.length < 2) { if (heroRes) { heroRes.innerHTML = ''; heroRes.classList.remove('open'); } return; }
      heroTimer = setTimeout(() => fetchSearch(q, heroRes), 300);
    });
    heroInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const q = heroInput.value.trim();
        if (q) window.location.href = `/search?q=${encodeURIComponent(q)}`;
      }
    });
    document.addEventListener('click', e => {
      if (!e.target.closest('.hero-search') && heroRes) heroRes.classList.remove('open');
    });
  }

  // ── Search fetch ──────────────────────────────────────
  async function fetchSearch(q, container) {
    try {
      const res  = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!container) return;
      if (!data.length) { container.classList?.remove('open'); container.innerHTML = ''; return; }
      container.innerHTML = data.map(m => `
        <a href="/movie/${m.id}" class="sr-item">
          ${m.poster
            ? `<img src="${m.poster}" alt="${m.title}">`
            : `<div class="sr-no-img">${m.title[0]}</div>`}
          <div>
            <div class="sr-title">${m.title}</div>
            <div class="sr-meta"><span>${m.year}</span><span>${m.rating}</span></div>
          </div>
        </a>`).join('');
      container.classList?.add('open');
    } catch(e) { console.error(e); }
  }

  // ── Scroll reveal ─────────────────────────────────────
  const reveals = document.querySelectorAll('.section, .mv-section, .mv-data-strip');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.06 });
    reveals.forEach(el => {
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(20px)';
      el.style.transition = 'opacity 0.65s cubic-bezier(0.25,0.46,0.45,0.94), transform 0.65s cubic-bezier(0.25,0.46,0.45,0.94)';
      io.observe(el);
    });
  }

  // ── Film card stagger ─────────────────────────────────
  document.querySelectorAll('.film-card').forEach((card, i) => {
    card.style.opacity   = '0';
    card.style.transform = 'translateY(16px)';
    card.style.transition = `opacity 0.5s ease ${i * 0.04}s, transform 0.5s ease ${i * 0.04}s`;
    setTimeout(() => {
      card.style.opacity   = '1';
      card.style.transform = 'translateY(0)';
    }, 100 + i * 40);
  });

});
