pip install "jax[tpu]" -f https://storage.googleapis.com/jax-releases/libtpu_releases.html
python -c 'import jax; print("Global device count:", jax.device_count())'
sleep 60