
pip install  https://storage.googleapis.com/jax-releases/libtpu_releases.html
pip install --pre jax jaxlib libtpu-nightly requests -i https://us-python.pkg.dev/ml-oss-artifacts-published/jax/simple/
python test-tpu.py
    