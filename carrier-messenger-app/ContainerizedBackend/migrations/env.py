import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context

# Loads Alembic configuration and sets up logging
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Retrieves the SQLAlchemy engine from Flask's migrate extension
def get_engine():
    try:
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions['migrate'].db.engine

# Retrieves the SQLAlchemy engine URL, formatted for Alembic
def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')

# Configures the engine URL for Alembic autogeneration
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# Returns the target metadata used for schema generation
def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata

# Executes Alembic migrations in offline mode using the configured URL
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()

# Executes Alembic migrations in online mode with a live DB connection
def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )
        with context.begin_transaction():
            context.run_migrations()

# Determines migration mode (offline or online) and executes accordingly
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
