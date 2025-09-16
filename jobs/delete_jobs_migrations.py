import os
import glob

# Delete all migration files except __init__.py
migration_dir = os.path.join(os.path.dirname(__file__), 'migrations')
for f in glob.glob(os.path.join(migration_dir, '*.py')):
    if not f.endswith('__init__.py'):
        os.remove(f)
for f in glob.glob(os.path.join(migration_dir, '*.pyc')):
    os.remove(f)
print('Deleted old migration files in jobs/migrations.')
