
function switchTab(tabName) {
  const all = document.querySelectorAll('.tab-content');
  all.forEach(t => t.style.display = 'none');
  const active = document.getElementById(tabName);
  if (active) active.style.display = 'block';
  const buttons = document.querySelectorAll('.tab-btn');
  buttons.forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('btn-' + tabName);
  if (btn) btn.classList.add('active');
}
document.addEventListener('DOMContentLoaded', function () {
  if (document.getElementById('autorizaciones')) {
    switchTab('autorizaciones');
  }
});
