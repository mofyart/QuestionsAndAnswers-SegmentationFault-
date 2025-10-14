(function(){
  const nav = document.querySelector('.navbar-glass');
  const onScroll = () => {
    if (!nav) return;
    if (window.scrollY > 20) nav.classList.add('scrolled'); else nav.classList.remove('scrolled');
  };
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
})();
(function(){
  const els = document.querySelectorAll('.feature-card, .hero-figure, .about-media');
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return;
  els.forEach(el => el.classList.add('reveal'));
  const io = new IntersectionObserver(entries=>{
    entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {threshold:.12});
  els.forEach(el=>io.observe(el));
})();
