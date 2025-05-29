document.addEventListener('DOMContentLoaded', function () {
    const textarea = document.querySelector('#id_text');
    const preview = document.querySelector('#mathjax-preview');
  
    if (!textarea || !preview) return;
  
    const renderMath = () => {
      const raw = textarea.value.trim();
      const safe = raw.startsWith('\\(') || raw.startsWith('$$') ? raw : `\\(${raw}\\)`;
      preview.innerHTML = safe;
      if (window.MathJax && window.MathJax.typeset) {
        MathJax.typeset([preview]);
      }
    };
  
    textarea.addEventListener('input', renderMath);
    renderMath();
  });
  