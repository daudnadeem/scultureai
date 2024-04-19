cd lambda
python3 -m venv lambda_env
source lambda_env/bin/activate
pip install -r requirements-infra.txt --target .
deactivate
zip -r ../dependencies.zip .
mv main.py ..
cd ..
rm -rf lambda/*
mv main.py lambda
python3 -m venv local_env
source local_env/bin/activate
pip install -r requirements.txt
cdk deploy --require-approval never