CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  project_id INTEGER REFERENCES projects(id),
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS action_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT 0,
  project_id INTEGER REFERENCES projects(id),
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  color TEXT,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS note_tags (
  note_id INTEGER REFERENCES notes(id),
  tag_id INTEGER REFERENCES tags(id),
  PRIMARY KEY (note_id, tag_id)
);

CREATE TABLE IF NOT EXISTS action_item_tags (
  action_item_id INTEGER REFERENCES action_items(id),
  tag_id INTEGER REFERENCES tags(id),
  PRIMARY KEY (action_item_id, tag_id)
);

INSERT INTO projects (name, description) VALUES
  ('Default Project', 'Default project for notes and action items');

INSERT INTO notes (title, content, project_id) VALUES
  ('Welcome', 'This is a starter note. TODO: explore the app!', 1),
  ('Demo', 'Click around and add a note. Ship feature!', 1);

INSERT INTO action_items (description, completed, project_id) VALUES
  ('Try pre-commit', 0, 1),
  ('Run tests', 0, 1);

INSERT INTO tags (name, color) VALUES
  ('urgent', '#FF5733'),
  ('feature', '#33FF57'),
  ('bug', '#3357FF'),
  ('documentation', '#F033FF');


