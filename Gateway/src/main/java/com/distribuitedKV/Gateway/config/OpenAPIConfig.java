package com.distribuitedKV.Gateway.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import io.swagger.v3.oas.models.servers.Server;

import java.util.List;

@Configuration
public class OpenAPIConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("API Chave-Valor")
                        .version("1.0")
                        .description("API para gerir pares chave-valor usando Redis, RabbitMQ e base de dados.")
                )
                .servers(List.of(new Server().url("http://localhost:8000"))); // Swagger aponta para o Nginx
    }
}
