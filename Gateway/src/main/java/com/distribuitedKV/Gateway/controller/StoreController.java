package com.distribuitedKV.Gateway.controller;

import com.distribuitedKV.Gateway.model.ChaveValor;
import com.distribuitedKV.Gateway.ChaveValorRepository;
import com.distribuitedKV.Gateway.model.Mensagem;
import com.distribuitedKV.Gateway.config.RabbitMQConfig;
import com.fasterxml.jackson.core.JsonProcessingException;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;
import io.swagger.v3.oas.annotations.Operation;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import javax.sql.DataSource;
import java.sql.Connection;


@RestController
@RequestMapping("/store")
public class StoreController {

    private final ChaveValorRepository repositorio;

    private final RabbitTemplate rabbitTemplate;

    public StoreController(ChaveValorRepository repositorio, RabbitTemplate rabbitTemplate) {
        this.repositorio = repositorio;
        this.rabbitTemplate = rabbitTemplate;
    }

    @Autowired
    private DataSource dataSource;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        try (Connection conn = dataSource.getConnection()) {
            // Testa ligação ao Redis (simples leitura)
            redisTemplate.opsForValue().get("verificacao-health");
            return ResponseEntity.ok("✅ Serviço operacional: DB + Redis OK");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("❌ Falha de saúde: " + e.getMessage());
        }
    }

    @PutMapping
    @Operation(
            summary = "Guarda ou atualiza uma chave-valor",
            description = "Guarda ou atualiza o valor associado à chave fornecida. A operação é enviada para o RabbitMQ.",
            requestBody = @io.swagger.v3.oas.annotations.parameters.RequestBody(
                    required = true,
                    description = "Objeto com chave e valor a guardar",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = Mensagem.class),
                            examples = @ExampleObject(
                                    value = "{\"key\": \"curso\", \"value\": \"Engenharia Informática\"}"
                            )
                    )
            ),
            responses = {
                    @ApiResponse(responseCode = "200", description = "Chave-valor enviada com sucesso"),
                    @ApiResponse(responseCode = "500", description = "Erro interno")
            }
    )
    public String guardar(@RequestBody Mensagem mensagem) throws JsonProcessingException {
        rabbitTemplate.convertAndSend(RabbitMQConfig.STORE_QUEUE, mensagem);
        return mensagem.getValue();
    }


    @PostMapping
    @Operation(summary = "Não disponível", hidden = true)
    public String criar(@RequestBody Mensagem mensagem) {
        throw new ResponseStatusException(
                HttpStatus.METHOD_NOT_ALLOWED,
                "Método POST não permitido neste endpoint"
        );
    }






    @Cacheable(value = "store", key = "#key", unless = "#result == null || #result == 'NÃO ENCONTRADO'")
    @GetMapping("/{key}")
@Operation(
        summary = "Lê o valor associado a uma chave",
        description = "Procura o valor correspondente à chave indicada.",
        responses = {
                @ApiResponse(responseCode = "200", description = "Valor encontrado"),
                @ApiResponse(responseCode = "404", description = "Chave não encontrada"),
                @ApiResponse(responseCode = "500", description = "Erro interno")
        }
)
public String ler(@PathVariable String key)
    {
        try {
            return repositorio.findById(key)
                    .map(ChaveValor::getValue)
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Chave não encontrada"));
        } catch (ResponseStatusException e) {
            throw e; // 404 ou outro já tratado
        } catch (Exception e) {
            // Log opcional: e.printStackTrace();
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Erro inesperado: " + e.getMessage());
        }
    }


    @DeleteMapping("/{key}")
    @CacheEvict(value = "store", key = "#key")
    @Operation(
            summary = "Apaga uma chave existente",
            description = "Remove a chave fornecida da base de dados e envia a operação para RabbitMQ.",
            responses = {
                    @ApiResponse(responseCode = "202", description = "Pedido aceite para remoção"),
                    @ApiResponse(responseCode = "500", description = "Erro interno")
            }
    )
    public ResponseEntity<?> apagar(@PathVariable String key)
    {
        Map<String, String> mensagem = new HashMap<>();
        mensagem.put("op", "delete");
        mensagem.put("key", key);

        // ✅ ENVIA O MAP DIRETAMENTE — não faças toString nem writeValueAsString
        rabbitTemplate.convertAndSend(RabbitMQConfig.STORE_QUEUE, mensagem);

        return ResponseEntity.accepted().build();
    }





//    @DeleteMapping("/{key}")
//    @CacheEvict(value = "store", key = "#key")
//    @Operation(summary = "Apaga uma chave existente")
//    public ResponseEntity<?> apagar(@PathVariable String key) {
//        repositorio.deleteById(key);
//        return ResponseEntity.noContent().build();
//    }

//    @GetMapping
//    @Operation(summary = "Lista todas as chaves e valores armazenados")
//    public ResponseEntity<?> listarTudo() {
//        List<ChaveValor> todos = repositorio.findAll();
//        Map<String, String> resultado = new HashMap<>();
//        for (ChaveValor reg : todos) {
//            resultado.put(reg.getKey(), reg.getValue());
//        }
//        return ResponseEntity.ok().body(resultado);
//    }

    @GetMapping("/cache-check")
    @Operation(
            summary = "Verifica se o cache está a funcionar",
            description = "Retorna uma string fixa e só executa se não houver 'cache hit'.",
            responses = {
                    @ApiResponse(responseCode = "200", description = "Cache testada com sucesso")
            }
    )
    public String verificarCache() {
        return "valor da cache";
    }


}
