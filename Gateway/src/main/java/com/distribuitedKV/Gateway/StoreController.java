package com.distribuitedKV.Gateway;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CachePut;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import io.swagger.v3.oas.annotations.Operation;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.amqp.rabbit.core.RabbitTemplate;


@RestController
@RequestMapping("/store")
public class StoreController {

    private final ChaveValorRepository repositorio;

    private final RabbitTemplate rabbitTemplate;

    public StoreController(ChaveValorRepository repositorio, RabbitTemplate rabbitTemplate) {
        this.repositorio = repositorio;
        this.rabbitTemplate = rabbitTemplate;
    }

    @PutMapping
    @Operation(summary = "Guarda ou atualiza uma chave-valor")
    public String guardar(@RequestBody Mensagem mensagem) throws JsonProcessingException {
//        ObjectMapper mapper = new ObjectMapper();
//        String json = mapper.writeValueAsString(mensagem);

        rabbitTemplate.convertAndSend(RabbitMQConfig.STORE_QUEUE, mensagem);
        return mensagem.getValue();
    }

    @PostMapping
    @Operation(summary = "Cria uma nova chave-valor (se ainda não existir)")
    public String criar(@RequestBody Mensagem mensagem) throws JsonProcessingException {
        if (repositorio.existsById(mensagem.getKey())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Chave já existe");
        }

//        ObjectMapper mapper = new ObjectMapper();
//        String json = mapper.writeValueAsString(mensagem);

        rabbitTemplate.convertAndSend(RabbitMQConfig.STORE_QUEUE, mensagem);
        return mensagem.getValue();
    }



    @Cacheable(value = "store", key = "#key", unless = "#result == null || #result == 'NÃO ENCONTRADO'")
    @GetMapping("/{key}")
    public String ler(@PathVariable String key) {
        return repositorio.findById(key)
                .map(ChaveValor::getValue)
                .orElse("NÃO ENCONTRADO");
    }



    @DeleteMapping("/{key}")
    @CacheEvict(value = "store", key = "#key")
    @Operation(summary = "Apaga uma chave existente")
    public ResponseEntity<?> apagar(@PathVariable String key) {
        repositorio.deleteById(key);
        return ResponseEntity.noContent().build();
    }

    @GetMapping
    @Operation(summary = "Lista todas as chaves e valores armazenados")
    public ResponseEntity<?> listarTudo() {
        List<ChaveValor> todos = repositorio.findAll();
        Map<String, String> resultado = new HashMap<>();
        for (ChaveValor reg : todos) {
            resultado.put(reg.getKey(), reg.getValue());
        }
        return ResponseEntity.ok().body(resultado);
    }
}
