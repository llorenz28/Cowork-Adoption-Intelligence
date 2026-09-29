FROM mcr.microsoft.com/powershell:lts-7.4-ubuntu-22.04

ARG PAX_VERSION=1.11.15
ARG PAX_SHA256=13a8d41a70c462650207e452eb0ccab274729eb65b0d640bc0a52d6a40ad46c9

ENV DEBIAN_FRONTEND=noninteractive \
    POWERSHELL_TELEMETRY_OPTOUT=1 \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    PAX_NONINTERACTIVE=1 \
    PAX_BOOTSTRAP_LOG_DIR=/data/logs/bootstrap \
    COWORK_DATA_ROOT=/data \
    PSModulePath=/usr/local/share/powershell/Modules:/opt/microsoft/powershell/7/Modules

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl python3 python3-pip tini \
 && pip3 install --no-cache-dir orjson "pyarrow>=14" "deltalake>=0.15" \
 && rm -rf /var/lib/apt/lists/*

RUN pwsh -NoLogo -NoProfile -Command " \
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
    \$ProgressPreference='SilentlyContinue'; \
    Install-Module Microsoft.Graph -RequiredVersion 2.25.0 -Scope AllUsers -Force -AllowClobber; \
    Install-Module Az.Accounts -RequiredVersion 3.0.4 -Scope AllUsers -Force -AllowClobber; \
    Install-Module ExchangeOnlineManagement -RequiredVersion 3.6.0 -Scope AllUsers -Force -AllowClobber"

WORKDIR /app

RUN curl -fSL --retry 5 --retry-delay 2 \
        "https://github.com/microsoft/PAX/releases/download/purview-v${PAX_VERSION}/PAX_Purview_Audit_Log_Processor_v${PAX_VERSION}.ps1" \
        -o /app/PAX_Purview_Audit_Log_Processor.ps1 \
 && echo "${PAX_SHA256}  /app/PAX_Purview_Audit_Log_Processor.ps1" | sha256sum -c -

RUN mkdir -p /licenses \
 && curl -fSL --retry 5 --retry-delay 2 \
        "https://raw.githubusercontent.com/microsoft/PAX/945b634705f355ffaada4310de096af47adf44c5/LICENSE" \
        -o /licenses/PAX-LICENSE

COPY Cowork_Purview_Preprocessor_v0.1.0.py /app/Cowork_Purview_Preprocessor_v0.1.0.py
COPY cowork-contract.json /app/cowork-contract.json
COPY Validate-CoworkCompatibility.py /app/Validate-CoworkCompatibility.py
COPY Invoke-CoworkPipeline.ps1 /app/Invoke-CoworkPipeline.ps1
COPY Cowork-LICENSE /licenses/Cowork-LICENSE

RUN mkdir -p /data/logs/bootstrap \
 && groupadd --system --gid 10001 cowork \
 && useradd --system --uid 10001 --gid 10001 --home-dir /home/cowork --create-home --shell /usr/sbin/nologin cowork \
 && chown -R cowork:cowork /app /home/cowork /data \
 && chmod 0555 /app/Invoke-CoworkPipeline.ps1 /app/Validate-CoworkCompatibility.py \
 && chmod 0444 /app/Cowork_Purview_Preprocessor_v0.1.0.py /app/cowork-contract.json /licenses/*

VOLUME ["/data"]
USER cowork

ENTRYPOINT ["/usr/bin/tini", "--", "pwsh", "-NoLogo", "-NoProfile", "-File", "/app/Invoke-CoworkPipeline.ps1"]
