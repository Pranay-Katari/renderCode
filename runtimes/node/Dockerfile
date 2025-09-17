FROM node:20-slim

WORKDIR /app
RUN npm install express body-parser

COPY run.js /app/run.js

CMD ["node", "run.js"]