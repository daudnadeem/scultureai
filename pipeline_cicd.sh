cd lambda
python3 -m venv lambda_env
source lambda_env/bin/activate
pip install -r requirements.txt --target .
deactivate
zip -r ./../dependencies.zip *
cd ..
python3 -m venv local_env
pip install -r requirements.txt
source local_env/bin/activate
cdk deploy --require-approval never