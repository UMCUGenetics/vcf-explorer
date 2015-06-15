from flask import Flask

from vcfexplorer import frontend, api

app = Flask(__name__)
app.config.update(
    MONGODB_HOST='localhost',
    MONGODB_PORT=27017,
    MONGODB_NAME='vcf_explorer',
)

app.register_blueprint(frontend.bp, url_prefix='/')
app.register_blueprint(api.bp, url_prefix='/api')

if __name__ == '__main__':
    app.run()
