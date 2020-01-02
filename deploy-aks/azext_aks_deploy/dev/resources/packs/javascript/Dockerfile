FROM node:10
ENV PORT port_number_place_holder
EXPOSE port_number_place_holder

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY package.json .
RUN npm install
COPY . .

CMD ["npm", "start"]
