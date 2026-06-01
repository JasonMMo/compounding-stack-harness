import org.springframework.boot.gradle.tasks.bundling.BootJar

plugins {
    java
    id("org.springframework.boot") version "3.2.5"
    id("io.spring.dependency-management") version "1.1.4"
}

group = "com.compounding.adapter"
version = "0.1.0-SNAPSHOT"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    // snakeyaml is already pulled in transitively by spring-boot-starter,
    // but declared explicitly so contract loading is clearly intentional.
    implementation("org.yaml:snakeyaml:2.2")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.withType<Test> {
    useJUnitPlatform()
}

// ── Contract + Catalog file copy (G-1 single-source principle) ───────────────
// Copies middle/contract/ into resources/contract/ — adapter reads at runtime,
// no Java constants redeclare the contract.
// Also copies presets/ddl/catalog.yaml into resources/catalog/ so
// CatalogValidator loads it via ClassPathResource("catalog/catalog.yaml").
// Path is relative to this subproject: ../../.. = repo root.
tasks.named<ProcessResources>("processResources") {
    from("../../../middle/contract") {
        into("contract")
    }
    from("../../../presets/ddl") {
        include("catalog.yaml")
        into("catalog")
    }
}

tasks.named<BootJar>("bootJar") {
    archiveFileName = "springboot-jakarta-adapter.jar"
}
