FROM node:20

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential curl git tmux asciinema \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

RUN npm run build
RUN chmod +x /app/run_tests.sh

# CMD ["./run_tests.sh"]

