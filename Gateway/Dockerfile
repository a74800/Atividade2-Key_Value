# Etapa 1: Build da aplicação com Maven
FROM maven:3.9.6-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# Etapa 2: Imagem final com apenas o JAR gerado
FROM eclipse-temurin:21-jdk
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
# Expondo a porta 8080
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
