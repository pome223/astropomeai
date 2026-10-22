(() => {
  // A reader's play action pauses another recording on the same page.
  for (const video of document.querySelectorAll('video')) video.addEventListener('play', () => {
    document.querySelectorAll('video').forEach(other => {
      if (other !== video) other.pause();
    });
  });
  const links = [...document.querySelectorAll('[data-zoom]')];
  if (!links.length || !window.HTMLDialogElement) return;
  const dialog = document.createElement('dialog');
  dialog.className = 'image-dialog';
  dialog.setAttribute('aria-label', 'Enlarged research figure');
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'image-dialog-close';
  close.textContent = 'Close ×';
  const image = document.createElement('img');
  const caption = document.createElement('p');
  caption.id = 'enlarged-figure-caption';
  dialog.setAttribute('aria-describedby', caption.id);
  dialog.append(close, image, caption);
  document.body.append(dialog);
  let trigger = null;
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) {
      const r = dialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
    }
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('image-open');
    trigger?.focus({preventScroll: true});
  });
  for (const link of links) link.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    trigger = link;
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    const figureCaption = link.closest('figure').querySelector('figcaption');
    caption.textContent = [figureCaption.querySelector('strong').textContent,
      figureCaption.querySelector('p').textContent].join(' — ');
    dialog.showModal();
    document.body.classList.add('image-open');
    close.focus();
  });
})();
