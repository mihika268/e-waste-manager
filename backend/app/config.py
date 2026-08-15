# ============================================================
# BASE DIRECTORIES
# ============================================================

base_dir = os.path.dirname(
    os.path.dirname(__file__)
)

# Vercel functions have writable temporary storage in /tmp.
# Local development continues to use backend/instance.
if os.environ.get('VERCEL'):

    instance_dir = '/tmp/ewaste-instance'

else:

    instance_dir = os.path.join(
        base_dir,
        'instance'
    )

os.makedirs(
    instance_dir,
    exist_ok=True
)


# ============================================================
# DATABASE
# ============================================================

db_url = os.environ.get(
    'DATABASE_URL'
)


if db_url:

    if db_url.startswith('sqlite:///'):

        db_path = db_url.replace(
            'sqlite:///',
            '',
            1
        )

        if os.environ.get('VERCEL'):

            SQLALCHEMY_DATABASE_URI = (
                'sqlite:////tmp/ewaste.db'
            )

        elif not os.path.isabs(db_path):

            SQLALCHEMY_DATABASE_URI = (
                'sqlite:///'
                + os.path.join(
                    instance_dir,
                    os.path.basename(db_path)
                )
            )

        else:

            SQLALCHEMY_DATABASE_URI = db_url

    else:

        SQLALCHEMY_DATABASE_URI = db_url

else:

    if os.environ.get('VERCEL'):

        SQLALCHEMY_DATABASE_URI = (
            'sqlite:////tmp/ewaste.db'
        )

    else:

        SQLALCHEMY_DATABASE_URI = (
            'sqlite:///'
            + os.path.join(
                instance_dir,
                'ewaste.db'
            )
        )


SQLALCHEMY_TRACK_MODIFICATIONS = False