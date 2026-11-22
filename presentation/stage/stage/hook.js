window.__v = {
  start(h, speed) {
    zeitH = S.zeit.findIndex(z => z.startsWith(h)); tempo = speed; spielt = speed > 0;
    setCloud(false); panelAuf(true); letzteStunde = -1;
    setTimeout(() => document.querySelectorAll('.label').forEach(l => l.textContent.includes('18 more houses') && l.classList.add('v-hide')), 300);
  },
  fly(at, from, ms) { fliegeZu(V(...at), V(...from), Math.max(1, ms)); },
  groups(list) {
    let g = 0;
    for (const e of el('jetzt').children) {
      const cut = e.classList.contains('trenn'); if (cut) g++;
      e.classList.toggle('off', !list.includes(g) || (cut && g === list[0]) || e.id === 'modell' || e.classList.contains('legende'));
    }
  },
  title(title, evidence) {
    for (const [id, text] of [['v-title', title], ['v-evidence', evidence]]) {
      let e = document.getElementById(id);
      if (!e) { e = document.createElement('div'); e.id = id; id === 'v-title' ? document.getElementById('kopf').prepend(e) : document.body.append(e); }
      e.textContent = text;
    }
  },
};
animiere();
</script>
