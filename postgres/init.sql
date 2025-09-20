CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(255) UNIQUE NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    schedule_settings JSONB DEFAULT '{
        "base_url": "https://rshu.ru",
        "schedule_url": "/schedule",
        "files": {
            "schedule": {"output": "schedule.pdf", "hash": "schedule_hash.txt"},
            "exams": {"output": "exams.pdf", "hash": "exams_hash.txt"}
        }
    }',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telegram_id ON user_settings(telegram_id);
CREATE INDEX IF NOT EXISTS idx_group_name ON user_settings(group_name);