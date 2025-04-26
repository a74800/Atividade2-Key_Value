package com.distribuitedKV.Gateway;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Objeto usado para representar uma entrada chave-valor")
public class Mensagem {

    @Schema(
            description = "Chave da entrada",
            example = "curso",
            required = true
    )
    private String key;

    @Schema(
            description = "Valor associado à chave",
            example = "Engenharia Informática",
            required = true
    )
    private String value;

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }
}
