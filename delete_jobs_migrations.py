# This script deletes all migration files except __init__.py in jobs/migrations.
import os
import glob

migration_dir = os.path.join(os.path.dirname(__file__), 'jobs', 'migrations')
for f in glob.glob(os.path.join(migration_dir, '*.py')):
    if not f.endswith('__init__.py'):
        os.remove(f)
print('Deleted all migration files except __init__.py.')
