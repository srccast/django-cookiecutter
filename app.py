import io
import os
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import docker
import yaml
from dotenv import load_dotenv
from flask import Flask, render_template, send_file
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)


class YesNoField(SelectField):
    def __init__(self, *args, default="n", **kwargs):
        super().__init__(
            *args,
            choices=[
                ("y", "yes"),
                ("n", "no"),
            ],
            default=default,
            **kwargs,
        )


class CookieCutterForm(FlaskForm):
    project_name = StringField(validators=[DataRequired()])
    project_slug = StringField(validators=[DataRequired()])
    description = StringField(validators=[DataRequired()])
    author_name = StringField(validators=[DataRequired()])
    domain_name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    version = StringField(validators=[DataRequired()])
    open_source_license = SelectField(
        choices=[
            "MIT",
            "BSD",
            "GPLv3",
            "Apache Software License 2.0",
            "Not open source",
        ],
        validators=[DataRequired()],
    )
    username_type = SelectField(
        choices=[
            "username",
            "email",
        ],
        validators=[DataRequired()],
    )
    timezone = StringField(default="UTC")
    windows = YesNoField()
    editor = SelectField(
        choices=[
            "None",
            "PyCharm",
            "VS Code",
        ],
        validators=[DataRequired()],
    )
    use_docker = YesNoField()
    postgresql_version = SelectField(
        choices=[
            "16",
            "15",
            "14",
            "13",
            "12",
        ]
    )
    cloud_provider = SelectField(
        choices=[
            "AWS",
            "GCP",
            "Azure",
            "None",
        ],
        validators=[DataRequired()],
    )
    mail_service = SelectField(
        choices=[
            "Mailgun",
            "Amazon SES",
            "Mailjet",
            "Mandrill",
            "Postmark",
            "Sendgrid",
            "Brevo",
            "SparkPost",
            "Other SMTP",
        ],
        validators=[DataRequired()],
    )
    use_async = YesNoField(default="no")
    use_drf = YesNoField(default="no")
    frontend_pipeline = SelectField(
        choices=[
            "None",
            "Django Compressor",
            "Gulp",
            "Webpack",
        ],
        validators=[DataRequired()],
    )
    use_celery = YesNoField()
    use_mailpit = YesNoField()
    use_sentry = YesNoField()
    use_whitenoise = YesNoField()
    use_heroku = YesNoField()
    ci_tool = SelectField(
        choices=[
            "None",
            "Travis",
            "Gitlab",
            "Github",
            "Drone",
        ],
        validators=[DataRequired()],
    )
    keep_local_envs_in_vcs = YesNoField()
    debug = YesNoField()
    submit = SubmitField("Submit")


@app.route("/")
def index_get():
    return render_template("index.html", form=CookieCutterForm())


@app.route("/", methods=["POST"])
def index_post():
    form = CookieCutterForm()
    if not form.validate_on_submit():
        raise ValueError("validation error")

    client = docker.DockerClient.from_env()

    data = {"default_context": form.data}

    with TemporaryDirectory(dir="/tmp", delete=False) as temp_dir:
        temp_dir_path = Path(temp_dir)
        with open(temp_dir_path / "config.yaml", "w") as cookiecutter_file:
            yaml.dump(data, cookiecutter_file)

        client.containers.run(
            image="python3.12_cookiecutter",
            volumes=[f"{temp_dir}:/data"],
        )

        out_f = io.BytesIO()

        with ZipFile(out_f, mode="x", compression=zipfile.ZIP_DEFLATED) as zip:
            for entry in temp_dir_path.glob("**/*"):
                zip.write(entry, arcname=entry.relative_to(temp_dir_path))

        out_f.seek(0)
        return send_file(
            path_or_file=out_f,
            mimetype="application/zip",
            download_name="django-cookiecutter.zip",
        )
