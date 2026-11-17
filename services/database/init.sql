CREATE TABLE IF NOT EXISTS tasks (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    done       BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

INSERT INTO tasks (title) VALUES
    ('Set up the k3s cluster'),
    ('Wire the baseline pipeline');
