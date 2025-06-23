-- UniSearch Database Schema
-- SQLite database for storing university information

CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT,
    country TEXT,
    qs_rank INTEGER,
    overall_quality REAL CHECK (overall_quality >= 0 AND overall_quality <= 10),
    academic_rigor REAL CHECK (academic_rigor >= 0 AND academic_rigor <= 10),
    openness REAL CHECK (openness >= 0 AND openness <= 10),
    cultural_diversity REAL CHECK (cultural_diversity >= 0 AND cultural_diversity <= 10),
    student_life REAL CHECK (student_life >= 0 AND student_life <= 10),
    campus_safety REAL CHECK (campus_safety >= 0 AND campus_safety <= 10),
    accommodation TEXT CHECK (accommodation IN ('Yes', 'No', 'Partial')),
    language TEXT,
    language_classes TEXT CHECK (language_classes IN ('Yes', 'No')),
    accessibility TEXT CHECK (accessibility IN ('Yes', 'No', 'Partial')),
    response_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_universities_name ON universities(name);
CREATE INDEX IF NOT EXISTS idx_universities_country ON universities(country);
CREATE INDEX IF NOT EXISTS idx_universities_qs_rank ON universities(qs_rank);
CREATE INDEX IF NOT EXISTS idx_universities_academic_rigor ON universities(academic_rigor);
CREATE INDEX IF NOT EXISTS idx_universities_cultural_diversity ON universities(cultural_diversity);
CREATE INDEX IF NOT EXISTS idx_universities_student_life ON universities(student_life);

-- Create a view for universities with complete data
CREATE VIEW IF NOT EXISTS universities_complete AS
SELECT *
FROM universities
WHERE qs_rank IS NOT NULL 
   AND academic_rigor IS NOT NULL 
   AND cultural_diversity IS NOT NULL 
   AND student_life IS NOT NULL;

-- Create a view for top universities by different criteria
CREATE VIEW IF NOT EXISTS top_universities AS
SELECT 
    name,
    city,
    country,
    qs_rank,
    academic_rigor,
    cultural_diversity,
    student_life,
    campus_safety,
    ROUND((academic_rigor + cultural_diversity + student_life + campus_safety) / 4, 2) as overall_score
FROM universities
WHERE qs_rank IS NOT NULL
ORDER BY qs_rank ASC
LIMIT 100;