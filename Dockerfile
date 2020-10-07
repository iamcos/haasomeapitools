# base image
FROM python:3.8

# streamlit-specific commands
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"prostocosmos@protonmail.com\"\n\
" > /root/.streamlit/credentials.toml'
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

# exposing default port for streamlit
EXPOSE 8501

# copy over and install packages
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# copying everything over
COPY . .

# run app
CMD streamlit run Market_Data_downloader.py