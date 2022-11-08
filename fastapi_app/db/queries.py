CREATE_USERS_TABLE_QUERY = '''
CREATE TABLE users (
    id INT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    description TEXT,
    created_at TEXT
)
'''

CREATE_TEMPLATE_KPGZ_TABLE_QUERY = '''
CREATE TABLE kpgz_template (
    id INT AUTO_INCREMENT,
    kpgz_code TEXT NOT NULL,
    kpgz_name TEXT NOT NULL,
    template_name TEXT NOT NULL,
    PRIMARY KEY (id)
)
'''

CREATE_TEMPLATE_JOBS_TABLE_QUERY = '''
CREATE TABLE jobs_template (
    id INT AUTO_INCREMENT,
    job_code TEXT NOT NULL,
    job_name TEXT NOT NULL,
    kpgz_id TEXT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (kpgz_id) REFERENCES kpgz_template(id)
)
'''

CREATE_KPGZ_TABLE_QUERY = '''
CREATE TABLE kpgz (
    id INT,
    kpgz_name TEXT NOT NULL,
    kpgz_code TEXT,
    description TEXT,
    PRIMARY KEY (id)
)
'''

CREATE_JOBS_TABLE_QUERY = '''
CREATE TABLE jobs (
    id INT,
    kpgz_id INT
    job_name TEXT NOT NULL,
    job_code TEXT,
    units INT,
    PRIMARY KEY (id),
    FOREIGN KEY (kpgz_id) REFERENCES kpgz(id)
)
'''