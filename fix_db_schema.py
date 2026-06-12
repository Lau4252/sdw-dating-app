#!/usr/bin/env python3
"""
Sicheres DB-Schema-Update für StipConnect.
Fügt fehlende Spalten zur profiles_profile Tabelle hinzu.
BACKUP wird automatisch erstellt.
"""
import sqlite3
import shutil
import os
from datetime import datetime

DB_PATH = '/home/laurensmain/stip-dating/db.sqlite3'
BACKUP_DIR = '/home/laurensmain/stip-dating'

def backup_db():
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = f'{BACKUP_DIR}/db.sqlite3.backup-{ts}'
    shutil.copy2(DB_PATH, backup_path)
    print(f'✅ Backup erstellt: {backup_path}')
    return backup_path

def add_missing_columns(conn):
    c = conn.cursor()
    
    # Prüfe aktuelle Spalten
    c.execute("PRAGMA table_info(profiles_profile)")
    existing_cols = {row[1] for row in c.fetchall()}
    print(f'Vorhandene Spalten: {sorted(existing_cols)}')
    
    # Neue Spalten definieren
    new_columns = {
        'alter': 'INTEGER DEFAULT 20',
        'stadt': 'TEXT DEFAULT ""',
        'geschlecht': 'TEXT DEFAULT ""',
        'sucht': 'TEXT DEFAULT ""',
    }
    
    for col, def_val in new_columns.items():
        if col not in existing_cols:
            try:
                c.execute(f'ALTER TABLE profiles_profile ADD COLUMN "{col}" {def_val}')
                print(f'➕ Spalte hinzugefügt: {col}')
            except Exception as e:
                print(f'Error adding {col}: {e}')
        else:
            print(f'✓ Spalte existiert bereits: {col}')
    # Verify
    c.execute("PRAGMA table_info(profiles_profile)")
    final_cols = [row[1] for row in c.fetchall()]
    print(f'\nFinal Spalten ({len(final_cols)}): {sorted(final_cols)}')

def insert_demo_profiles(conn):
    c = conn.cursor()
    
    demos = [
        ('anna.mueller@tu-berlin.de', 'Anna', 'Müller', 22, 'F', 'M', 'Maschinenbau', 'TU Berlin', 
         '["Berlin"]', '["Deutsch","Englisch"]', 'Berlin', 'Fortschritt braucht Mut.', 
         'Im 4. Semester Maschinenbau.', 'Technik begeistert.', 'manchmal', 'nie',
         '["Musik","Reisen"]', '["https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400"]',
         '[{"q":"Perfektes Date?","a":"Picknick bei Sonnenuntergang."}]', '+49***15678'),
        ('lisa.schmidt@hu-berlin.de', 'Lisa', 'Schmidt', 21, 'F', 'M', 'Psychologie', 'HU Berlin',
         '["Berlin"]', '["Deutsch","Englisch"]', 'Berlin', 'Lebe, lache, liebe.',
         'Psychologie-Studentin.', 'Humor und Empathie.', 'ja', 'nie',
         '["Fitness","Lesen"]', '["https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400"]',
         '[{"q":"In 5 Jahren?","a":"Master + Katze."}]', '+49***15432'),
        ('max.neumann@kit.edu', 'Max', 'Neumann', 24, 'M', 'F', 'Informatik', 'KIT Karlsruhe',
         '["Karlsruhe"]', '["Deutsch","Englisch"]', 'Karlsruhe', 'Stay hungry.',
         'Informatiker mit Startup-DNA.', 'Offen für neue Ideen.', 'ja', 'manchmal',
         '["Tech","Startups"]', '["https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400"]',
         '[{"q":"Was antreibt?","a":"Welt besser machen."}]', '+49***22109'),
        ('lea.weber@uni-hamburg.de', 'Lea', 'Weber', 21, 'F', 'M', 'Journalistik', 'Uni Hamburg',
         '["Hamburg"]', '["Deutsch","Englisch"]', 'Hamburg', 'Schreibe, was wichtig ist.',
         'Journalismus-Studentin.', 'Meinung und Herz.', 'manchmal', 'nie',
         '["Schreiben","Musik"]', '["https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400"]',
         '[{"q":"Mein Traum?","a":"Welt bereisen."}]', '+49***26789'),
    ]
    
    created = 0
    for email, fn, ln, age, gender, seeking, stud, hs, reg, spr, city, quote, about, lf, trink, rauch, ints, photos, prompts, phone in demos:
        # Prüfe ob User existiert
        c.execute("SELECT id FROM auth_user WHERE username=?", (email,))
        row = c.fetchone()
        
        if not row:
            # Erstelle User
            c.execute("""
                INSERT INTO auth_user (username, first_name, last_name, email, password, is_staff, is_active, is_superuser, date_joined, last_login)
                VALUES (?, ?, ?, ?, 'unusable', 0, 1, 0, datetime('now'), datetime('now'))
            """, (email, fn, ln, email))
            user_id = c.lastrowid
            created += 1
        else:
            user_id = row[0]
            # Update User Info
            c.execute("UPDATE auth_user SET first_name=?, last_name=? WHERE id=?", (fn, ln, user_id))
        
        # Prüfe ob Profile existiert
        c.execute("SELECT id FROM profiles_profile WHERE user_id=?", (user_id,))
        prof_row = c.fetchone()
        
        if not prof_row:
            c.execute("""
                INSERT INTO profiles_profile (user_id, gender, seeking, birth_date, studienfach, hochschule, 
                    regionen, sprachen, quote, about, looking_for, trinken, rauchen, interests, photos, 
                    prompts, phone, visible, pending, consent_given, "alter", stadt, geschlecht, sucht)
                VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, 1, ?, ?, ?, ?)
            """, (user_id, gender, seeking, stud, hs, reg, spr, quote, about, lf, trink, rauch, ints, photos, prompts, phone, age, city, gender, seeking))
        else:
            c.execute("""
                UPDATE profiles_profile SET 
                    "alter"=?, stadt=?, geschlecht=?, sucht=?, gender=?, seeking=?,
                    studienfach=?, hochschule=?, regionen=?, sprachen=?, quote=?,
                    about=?, looking_for=?, trinken=?, rauchen=?, interests=?,
                    photos=?, prompts=?, phone=?, visible=1, pending=0, consent_given=1
                WHERE user_id=?
            """, (age, city, gender, seeking, gender, seeking, stud, hs, reg, spr, quote, about, lf, trink, rauch, ints, photos, prompts, phone, user_id))
    
    conn.commit()
    print(f'✅ {created} neue User, {len(demos)} Demo-Profile aktualisiert/erstellt')

if __name__ == '__main__':
    print(f'Starte DB-Update: {DB_PATH}')
    backup = backup_db()
    
    conn = sqlite3.connect(DB_PATH)
    try:
        add_missing_columns(conn)
        insert_demo_profiles(conn)
    finally:
        conn.close()
    
    print('\n🎉 DB-Update abgeschlossen!')
    print(f'📦 Backup: {backup}')
