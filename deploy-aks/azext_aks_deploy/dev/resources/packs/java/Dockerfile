FROM maven:3-jdk-11 as BUILD

COPY . /usr/src/app
RUN mvn --batch-mode -f /usr/src/app/pom.xml clean package

FROM openjdk:11-jre-slim
ENV SERVER_PORT port_number_place_holder
EXPOSE port_number_place_holder
COPY --from=BUILD /usr/src/app/target/*.jar /opt/target/app.jar
WORKDIR /opt/target

CMD ["java", "-jar", "/opt/target/app.jar", "--server.port=port_number_place_holder" ]
