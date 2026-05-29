package com.compounding.adapter.springboot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Backend adapter: springboot-jakarta
 * Serves the 8 wire keys defined in middle/contract/wire-v1.yaml.
 * Jakarta EE namespace (Spring Boot 3.2.x, Java 17).
 */
@SpringBootApplication
public class SpringbootJakartaAdapterApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringbootJakartaAdapterApplication.class, args);
    }
}
