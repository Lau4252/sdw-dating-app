#!/usr/bin/env python3
"""
StipConnect DB Schema Fix + Demo Profiles
Fügt fehlende Spalten hinzu + erstellt Demo-Profile.
ACHTUNG: 'alter' ist SQLite reserviertes Wort → immer in Quotes!
"""
import sqlite3
import shutil
from datetime import datetime

DB = '/home/laurensmain/stip-dating/db.sqlite3'

# Backup
shutil.copy2(DB, f"{DB}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Prüfe existierende Spalten
c.execute("PRAGMA table_info(profiles_profile)")
existing = {row[1] for row in c.fetchall()}
print('Existierend:', sorted(existing))

# 2. Neue Spalten (SQLite reserved words in Quotes!)
NEW_COLS = [
    ('"alter"', 'INTEGER DEFAULT 20'),
    ('stadt', 'TEXT DEFAULT ""'),
    ('geschlecht', 'TEXT DEFAULT ""'),
    ('sucht', 'TEXT DEFAULT ""'),
]

for col, ctype in NEW_COLS:
    col_name = col.strip('"')
    if col_name not in existing:
        try:
            c.execute(f'ALTER TABLE profiles_profile ADD COLUMN {col} {ctype}')
            print(f'✅ Hinzugefügt: {col_name}')
        except Exception as e:
            print(f'⚠️ {col_name}: {e}')
    else:
        print(f'✓ Existiert: {col_name}')

conn.commit()

# Verify
c.execute("PRAGMA table_info(profiles_profile)")
final = [row[1] for row in c.fetchall()]
print(f'\n📊 Final ({len(final)} Spalten):', sorted(final))

# 3. Demo Profiles
demos = [
    ('anna.mueller@tu-berlin.de','Anna','Müller',22,'F','M','Maschinenbau','TU Berlin',
     '["Berlin"]','["Deutsch","Englisch"]','Berlin','Fortschritt braucht Mut.',
     '4. Semester Maschinenbau.','Technik begeistert.','manchmal','nie',
     '["Musik","Reisen"]','["https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400"]',
     '[{"q":"Perfektes Date?","a":"Picknick bei Sonnenuntergang."}]','+49***15678'),
    ('lisa.schmidt@hu-berlin.de','Lisa','Schmidt',21,'F','M','Psychologie','HU Berlin',
     '["Berlin"]','["Deutsch","Englisch"]','Berlin','Lebe, lache, liebe.',
     'Psychologie-Studentin.','Humor und Empathie.','ja','nie',
     '["Fitness","Lesen"]','["https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400"]',
     '[{"q":"In 5 Jahren?","a":"Master + Katze."}]','+49***15432'),
    ('max.neumann@kit.edu','Max','Neumann',24,'M','F','Informatik','KIT Karlsruhe',
     '["Karlsruhe"]','["Deutsch","Englisch"]','Karlsruhe','Stay hungry.',
     'Informatiker mit Startup-DNA.','Offen für neue Ideen.','ja','manchmal',
     '["Tech","Startups"]','["https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400"]',
     '[{"q":"Was antreibt?","a":"Welt besser machen."}]','+49***22109'),
    ('lea.weber@uni-hamburg.de','Lea','Weber',21,'F','M','Journalistik','Uni Hamburg',
     '["Hamburg"]','["Deutsch","Englisch"]','Hamburg','Schreibe, was wichtig ist.',
     'Journalismus-Studentin.','Meinung und Herz.','manchmal','nie',
     '["Schreiben","Musik"]','["https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400"]',
     '[{"q":"Mein Traum?","a":"Welt bereisen."}]','+49***26789'),
    ('tom.schulz@tu-muenchen.de','Tom','Schulz',23,'M','F','BWL','TU München',
     '["München"]','["Deutsch","Englisch","Spanisch"]','München','Carpe Diem.',
     'BWL-Student mit Startup-Ambitionen.','Jemanden der motiviert ist.','ja','nie',
     '["Business","Sport","Reisen"]','["https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"]',
     '[{"q":"Mein Ziel?","a":"Eigene Firma gründen."}]','+49***34567'),
    ('emma.fischer@uni-koeln.de','Emma','Fischer',20,'F','M','Medienwissenschaft','Uni Köln',
     '["Köln"]','["Deutsch","Englisch"]','Köln','Kreativität ist Intelligenz.',
     'Medienwissenschaft, Film-Liebhaberin.','Film-Buff gesucht!','manchmal','nie',
     '["Film","Musik","Kunst"]','["https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400"]',
     '[{"q":"Lieblingsfilm?","a":"Amélie — magisches Paris."}]','+49***45678'),
    ('felix.klein@tu-dresden.de','Felix','Klein',22,'M','F','Elektrotechnik','TU Dresden',
     '["Dresden"]','["Deutsch","Englisch"]','Dresden','Nerds gewinnen.',
     'Elte-Student und Hobby-Bassist.','Jemanden der Musik liebt.','ja','nie',
     '["Tech","Musik","Gaming"]','["https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400"]',
     '[{"q":"Band oder Solo?","a":"Bassist in einer Uni-Band!"}]','+49***56789'),
    ('mia.bauer@hu-berlin.de','Mia','Bauer',21,'F','M','Soziologie','HU Berlin',
     '["Berlin"]','["Deutsch","Englisch","Französisch"]','Berlin','Gemeinschaft zählt.',
     'Soziologie mit Fokus auf Stadtentwicklung.','Offener Geist.','manchmal','nie',
     '["Stadt","Kultur","Lesen"]','["https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400"]',
     '[{"q":"Stadt oder Land?","a":"Großstädterin durch und durch."}]','+49***67890'),
]

for data in demos:
    email = data[0]
    # User erstellen/updaten
    c.execute("SELECT id FROM auth_user WHERE username=?", (email,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO auth_user (username,first_name,last_name,email,password,is_staff,is_active,is_superuser,date_joined,last_login) VALUES (?,?,?,?,'unusable',0,1,0,datetime('now'),datetime('now'))", (email, data[1], data[2], email))
        uid = c.lastrowid
    else:
        uid = row[0]
        c.execute("UPDATE auth_user SET first_name=?,last_name=? WHERE id=?", (data[1], data[2], uid))
    
    # Profile erstellen/updaten
    c.execute("SELECT id FROM profiles_profile WHERE user_id=?", (uid,))
    prof = c.fetchone()
    if not prof:
        c.execute('''INSERT INTO profiles_profile 
            (user_id,gender,seeking,birth_date,studienfach,hochschule,regionen,sprachen,stadt,quote,about,looking_for,trinken,rauchen,interests,photos,prompts,phone,visible,pending,consent_given,created_at,updated_at,"alter",geschlecht,sucht)
            VALUES (?,?,?,NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,0,1,datetime('now'),datetime('now'),?,?,?)''',
            (uid,data[4],data[5],data[6],data[7],data[8],data[9],data[10],data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],
             data[3],data[4],data[5]))
    else:
        c.execute('''UPDATE profiles_profile SET 
            "alter"=?,stadt=?,geschlecht=?,sucht=?,gender=?,seeking=?,
            studienfach=?,hochschule=?,regionen=?,sprachen=?,quote=?,
            about=?,looking_for=?,trinken=?,rauchen=?,interests=?,
            photos=?,prompts=?,phone=?,visible=1,pending=0,consent_given=1,updated_at=datetime('now')
            WHERE user_id=?''',
            (data[3],data[10],data[4],data[5],data[4],data[5],data[6],data[7],data[8],data[9],
             data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],uid))

conn.commit()

# Count
for label, qry in [('Users','SELECT COUNT(*) FROM auth_user'), ('Profiles','SELECT COUNT(*) FROM profiles_profile'), ('Visible','SELECT COUNT(*) FROM profiles_profile WHERE visible=1')]:
    c.execute(qry)
    print(f'{label}: {c.fetchone()[0]}')

conn.close()
print('\n✅ Fertig!')
