FROM --platform=linux/arm64 python:3.12-slim


RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    pkg-config \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    liblapacke-dev \
    python3-pip \
    curl \
    git \
    clang \
    libclang-dev


RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

RUN git clone https://github.com/ml-explore/mlx.git && \
    cd mlx && mkdir -p build && cd build && \
    cmake .. \
      -DCMAKE_PREFIX_PATH="/usr/lib/aarch64-linux-gnu" \
      -DMLX_BUILD_METAL=ON && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    pip install --no-cache-dir .



COPY setup.py .
COPY exo ./exo

RUN sed -i '/mlx==/d' setup.py && \
    pip install --no-cache-dir .

RUN pip install --no-cache-dir --no-deps mlx-lm==0.18.2
RUN pip install --upgrade mlx_lm
CMD ["exo","--inference-engine","mlx"]