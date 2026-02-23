# Sonic Screwdriver - ISO/USB builder container
# Build: docker build -t udos-sonic ./sonic
# Run:   docker run --rm udos-sonic --help

FROM alpine:3.19

RUN apk add --no-cache \
    python3 py3-pip \
    bash coreutils \
    squashfs-tools \
    xorriso \
    syslinux \
    dosfstools \
    e2fsprogs \
    parted

WORKDIR /sonic
COPY . /sonic

RUN pip3 install --no-cache-dir --break-system-packages \
    pyyaml jsonschema

ENTRYPOINT ["python3", "core/sonic_cli.py"]
CMD ["--help"]
