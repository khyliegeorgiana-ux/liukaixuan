document.documentElement.classList.add('js');

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.nav-links');

function closeMenu() {
  if (!menuButton || !navigation) return;
  menuButton.setAttribute('aria-expanded', 'false');
  navigation.classList.remove('is-open');
}

if (menuButton && navigation) {
  menuButton.addEventListener('click', () => {
    const expanded = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!expanded));
    navigation.classList.toggle('is-open', !expanded);
  });

  navigation.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeMenu();
      menuButton.focus();
    }
  });
}

const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}

const portfolioTabs = document.querySelectorAll('.portfolio-tab');
const portfolioVideos = document.querySelectorAll('.portfolio-video');
const portfolioPlayButtons = document.querySelectorAll('.portfolio-play');

function pausePortfolioVideos() {
  portfolioVideos.forEach((video) => {
    video.pause();
    video.closest('.portfolio-card')?.classList.remove('is-playing');
  });
}

function activatePortfolioCategory(categoryName) {
  portfolioTabs.forEach((tab) => {
    const isActive = tab.dataset.category === categoryName;
    tab.setAttribute('aria-selected', String(isActive));
    tab.classList.toggle('is-active', isActive);
    const panel = document.getElementById(tab.getAttribute('aria-controls'));
    if (panel) panel.hidden = !isActive;
  });
  pausePortfolioVideos();
}

portfolioTabs.forEach((tab) => {
  tab.addEventListener('click', () => activatePortfolioCategory(tab.dataset.category));
});

portfolioPlayButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const card = button.closest('.portfolio-card');
    const video = card?.querySelector('.portfolio-video');
    if (!video) return;
    card.classList.add('is-playing');
    video.play().catch(() => card.classList.remove('is-playing'));
  });
});

portfolioVideos.forEach((activeVideo) => {
  activeVideo.addEventListener('play', () => {
    portfolioVideos.forEach((video) => {
      if (video !== activeVideo) video.pause();
    });
    activeVideo.closest('.portfolio-card')?.classList.add('is-playing');
  });
  activeVideo.addEventListener('ended', () => {
    activeVideo.closest('.portfolio-card')?.classList.remove('is-playing');
  });
});
