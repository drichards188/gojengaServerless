mkdir package
pip install --target ./package -r requirements.txt
cd package
zip -r ../my_deployment_package.zip .
cd ..
zip my_deployment_package lambda_function.py
echo 'prepare_zip.bash done'