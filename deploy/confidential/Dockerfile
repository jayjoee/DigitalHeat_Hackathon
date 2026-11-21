# Build on trusted CI/customer infrastructure, never on the household server.
# Supply a reviewed Linux Python base by immutable digest; no floating default.
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
WORKDIR /app
COPY requirements/confidential.txt requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY src/confidential ./src/confidential
USER 10001:10001
ENTRYPOINT ["python", "-m", "src.confidential.guest"]
