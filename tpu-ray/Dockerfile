FROM rayproject/ray:2.46.0-py310

RUN python -m pip install --upgrade pip

RUN pip install -U --pre jax jaxlib libtpu-nightly requests -i https://us-python.pkg.dev/ml-oss-artifacts-published/jax/simple/ -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
#RUN pip install -U kithara[tpu] -f https://storage.googleapis.com/jax-releases/libtpu_releases.html --extra-index-url  https://download.pytorch.org/whl/cpu

USER root
