package com.distribuitedKV.Gateway.config;

import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.util.Map;

@Configuration
public class RabbitMQConfig {

    public static final String STORE_QUEUE = "store-events";

    @Bean
    public Queue storeQueue() {
        return new Queue(STORE_QUEUE, true, false, false, Map.of(
            "x-queue-type", "quorum",
            "x-quorum-initial-group-size", 3,
            "x-quorum-group-size", 3
        ));
    }
    

    @Bean
    public Jackson2JsonMessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory,
                                         Jackson2JsonMessageConverter converter) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(converter);
        return template;
    }
}
