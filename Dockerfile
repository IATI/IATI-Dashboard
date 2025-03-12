FROM python:3.12-bookworm

WORKDIR /work/IATI-Dashboard

COPY requirements.txt /work/IATI-Dashboard/requirements.txt

RUN git config --global --add safe.directory /work/IATI-Stats/data

RUN pip install -r /work/IATI-Dashboard/requirements.txt

COPY . /work/IATI-Dashboard

# 2024-03-20: Emergency fix
# We were seeing cert errors inside the docker container after a new Lets Encrypt was issued.
#
# We know there are changes coming about root certificates and the error may be caused by that:
# https://blog.cloudflare.com/upcoming-lets-encrypt-certificate-chain-change-and-impact-for-cloudflare-customers
#
# I tried installing the LE root cert's manually but that didn't work.
# As live is broken for now we need this emergency fix, but we should remove it in the future.
RUN echo "check_certificate=off" > /root/.wgetrc

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "iati_dashboard.ui.wsgi:application"]
