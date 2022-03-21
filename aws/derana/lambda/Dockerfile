#This dockerfile requires a file, which is the main executable to be passed in
ARG FILE_NAME

FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt  .

RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}/index.py"

COPY $FILE_NAME ${LAMBDA_TASK_ROOT}

CMD [ "index.lambda_handler" ]
