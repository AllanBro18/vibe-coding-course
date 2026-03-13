/* ---------- helpers ---------- */
async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/* ---------- notes state ---------- */
let notesCache = [];

function renderNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  for (const n of notesCache) {
    const li = document.createElement('li');
    if (n._editing) {
      li.innerHTML =
        `<input class="edit-title" value="${n.title}" />` +
        `<input class="edit-content" value="${n.content}" />` +
        `<button class="save-btn">Save</button>` +
        `<button class="cancel-btn">Cancel</button>`;
      li.querySelector('.save-btn').onclick = () => saveNote(n.id, li);
      li.querySelector('.cancel-btn').onclick = () => { n._editing = false; renderNotes(); };
    } else {
      li.textContent = `${n.title}: ${n.content} `;
      const editBtn = document.createElement('button');
      editBtn.textContent = 'Edit';
      editBtn.onclick = () => { n._editing = true; renderNotes(); };
      const delBtn = document.createElement('button');
      delBtn.textContent = 'Delete';
      delBtn.onclick = () => deleteNote(n.id);
      li.appendChild(editBtn);
      li.appendChild(delBtn);
    }
    list.appendChild(li);
  }
}

async function loadNotes() {
  notesCache = await fetchJSON('/notes/');
  renderNotes();
}

async function saveNote(id, li) {
  const title = li.querySelector('.edit-title').value;
  const content = li.querySelector('.edit-content').value;
  const old = notesCache.find((n) => n.id === id);
  const prev = { title: old.title, content: old.content };
  // optimistic
  old.title = title;
  old.content = content;
  old._editing = false;
  renderNotes();
  try {
    await fetchJSON(`/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
  } catch {
    old.title = prev.title;
    old.content = prev.content;
    renderNotes();
  }
}

async function deleteNote(id) {
  const idx = notesCache.findIndex((n) => n.id === id);
  const removed = notesCache.splice(idx, 1)[0];
  renderNotes();
  try {
    await fetch(`/notes/${id}`, { method: 'DELETE' });
  } catch {
    notesCache.splice(idx, 0, removed);
    renderNotes();
  }
}

/* ---------- action items state ---------- */
let currentFilter = 'all';
let selectedIds = new Set();

function actionFilterParam() {
  if (currentFilter === 'open') return '?completed=false';
  if (currentFilter === 'done') return '?completed=true';
  return '';
}

function updateBulkBtn() {
  const btn = document.getElementById('bulk-complete-btn');
  btn.disabled = selectedIds.size === 0;
}

function renderActions(items) {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  for (const a of items) {
    const li = document.createElement('li');
    if (!a.completed) {
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = selectedIds.has(a.id);
      cb.onchange = () => {
        if (cb.checked) selectedIds.add(a.id);
        else selectedIds.delete(a.id);
        updateBulkBtn();
      };
      li.appendChild(cb);
    }
    const span = document.createElement('span');
    span.textContent = ` ${a.description} [${a.completed ? 'done' : 'open'}] `;
    li.appendChild(span);
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        selectedIds.delete(a.id);
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

async function loadActions() {
  const items = await fetchJSON('/action-items/' + actionFilterParam());
  renderActions(items);
  updateBulkBtn();
}

/* ---------- init ---------- */
window.addEventListener('DOMContentLoaded', () => {
  /* notes form */
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  /* action items form */
  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  /* filter buttons */
  document.querySelectorAll('.filter-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      selectedIds.clear();
      loadActions();
    });
  });

  /* bulk complete */
  document.getElementById('bulk-complete-btn').addEventListener('click', async () => {
    if (selectedIds.size === 0) return;
    await fetchJSON('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: [...selectedIds] }),
    });
    selectedIds.clear();
    loadActions();
  });

  loadNotes();
  loadActions();
});
