# Arquitectura PathsAI en Huawei Cloud - Diagrama Mermaid

## Diagrama Completo de Arquitectura

```mermaid
graph TB
    subgraph "CAPA DISPOSITIVO IoT"
        IoT1[PathsAI Wearable<br/>Cámara HD + LiDAR<br/>HiSilicon Kirin NPU<br/>MindSpore Lite]
        IoT2[Audífonos Bluetooth<br/>Guía por Voz]
        Mobile[App Móvil PathsAI<br/>React Native/Flutter<br/>GPS + Bluetooth]
    end

    subgraph "CAPA EDGE COMPUTING"
        IEF[Huawei IEF<br/>Intelligent EdgeFabric<br/>Pre-procesamiento<br/>Inferencia Local]
    end

    subgraph "HUAWEI CLOUD"
        subgraph "IoT & Connectivity"
            IoTDA[IoT Platform IoTDA<br/>Gestión de Dispositivos<br/>MQTT/CoAP Protocol<br/>Device Auth & Security]
        end

        subgraph "AI & ML Services"
            ModelArts[ModelArts<br/>AI Development Platform<br/>Training & Deployment]
            MindSpore[MindSpore 2.6+<br/>Deep Learning Framework<br/>YOLOv8 + SAM + VLM]
            Ascend910[Ascend 910<br/>AI Training<br/>CANN Runtime]
            Ascend310[Ascend 310<br/>AI Inference<br/>MindSpore Serving]
        end

        subgraph "Compute Services"
            CCE[CCE Cloud Container Engine<br/>Kubernetes Cluster]
            RouteService[Route Service<br/>Pathfinding A*]
            MapService[Map Service<br/>GeoSpatial Queries]
            AlertService[Alert Service<br/>Real-time Monitoring]
            AIService[AI Inference Service<br/>Model Gateway]
        end

        subgraph "Database Services"
            GaussDBMySQL[GaussDB MySQL<br/>Users & Favorites<br/>Route History]
            GaussDBNoSQL[GaussDB NoSQL<br/>Urban Database<br/>Obstacles & POIs<br/>GeoJSON + GeoIndex]
            DCS[DCS Redis Cache<br/>Frequent Routes<br/>Map Cache]
        end

        subgraph "Application Services"
            APIG[API Gateway APIG<br/>REST APIs<br/>OAuth 2.0<br/>Rate Limiting]
            FunctionGraph[FunctionGraph<br/>Serverless Functions<br/>Event Processing]
            SIS_STT[SIS Speech-to-Text<br/>Voice Commands]
            SIS_TTS[SIS Text-to-Speech<br/>Navigation Voice]
        end

        subgraph "Storage & Messaging"
            OBS[OBS Object Storage<br/>Images & Logs<br/>Training Datasets]
            SMN[SMN Notifications<br/>Push Alerts<br/>Emergency Alerts]
        end

        subgraph "Big Data Analytics"
            MRS[MRS MapReduce Service<br/>Risk Zone Analysis<br/>Pattern Detection<br/>Route Optimization]
        end

        subgraph "Security & Monitoring"
            KMS[KMS Key Management<br/>Data Encryption]
            WAF[WAF Web Firewall<br/>API Security]
        end
    end

    %% Conexiones Dispositivo -> Edge
    IoT1 -->|Bluetooth| IoT2
    IoT1 -->|4G/5G/WiFi| IEF
    Mobile -->|HTTPS| APIG
    Mobile -->|Bluetooth| IoT1

    %% Conexiones Edge -> Cloud
    IEF -->|MQTT/CoAP| IoTDA

    %% Conexiones IoT Platform
    IoTDA -->|Device Events| FunctionGraph
    IoTDA -->|Telemetry Data| OBS

    %% Conexiones AI Services
    FunctionGraph -->|Image Frames| AIService
    AIService -->|Inference Request| Ascend310
    Ascend310 -.->|Uses| MindSpore
    ModelArts -->|Training| Ascend910
    Ascend910 -.->|Uses| MindSpore
    ModelArts -->|Deploy Model| Ascend310
    MindSpore -->|Stores Datasets| OBS

    %% Conexiones Microservices (CCE)
    APIG -->|Route to Services| CCE
    CCE -->|Contains| RouteService
    CCE -->|Contains| MapService
    CCE -->|Contains| AlertService
    CCE -->|Contains| AIService

    %% Conexiones Database
    RouteService -->|Query Routes| GaussDBNoSQL
    RouteService -->|User Data| GaussDBMySQL
    RouteService -->|Cache Check| DCS
    MapService -->|GeoSpatial Query| GaussDBNoSQL
    AlertService -->|Find Obstacles| GaussDBNoSQL
    AlertService -->|Send Alert| SMN
    AIService -->|Store Detection| GaussDBNoSQL

    %% Conexiones Voice Services
    APIG -->|Voice Input| SIS_STT
    RouteService -->|Voice Instructions| SIS_TTS
    SIS_TTS -->|Audio Response| APIG

    %% Conexiones FunctionGraph
    FunctionGraph -->|Update DB| GaussDBNoSQL
    FunctionGraph -->|Trigger Alert| AlertService
    FunctionGraph -->|Store Image| OBS

    %% Conexiones Big Data
    GaussDBNoSQL -->|Historical Data| MRS
    OBS -->|Data Lake| MRS
    MRS -->|Insights| RouteService

    %% Conexiones Notificaciones
    SMN -->|Push to Mobile| Mobile
    SMN -->|Alert to Device| IoTDA

    %% Conexiones Seguridad
    KMS -.->|Encrypt| GaussDBMySQL
    KMS -.->|Encrypt| GaussDBNoSQL
    WAF -.->|Protect| APIG

    %% Estilos
    classDef iotDevice fill:#FF6B35,stroke:#333,stroke-width:2px,color:#fff
    classDef edgeCompute fill:#F7931E,stroke:#333,stroke-width:2px,color:#fff
    classDef aiService fill:#00D4FF,stroke:#333,stroke-width:2px,color:#000
    classDef computeService fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef dbService fill:#50C878,stroke:#333,stroke-width:2px,color:#fff
    classDef appService fill:#9B59B6,stroke:#333,stroke-width:2px,color:#fff
    classDef storageService fill:#E67E22,stroke:#333,stroke-width:2px,color:#fff
    classDef securityService fill:#E74C3C,stroke:#333,stroke-width:2px,color:#fff

    class IoT1,IoT2,Mobile iotDevice
    class IEF edgeCompute
    class ModelArts,MindSpore,Ascend910,Ascend310,AIService aiService
    class CCE,RouteService,MapService,AlertService computeService
    class GaussDBMySQL,GaussDBNoSQL,DCS dbService
    class APIG,FunctionGraph,SIS_STT,SIS_TTS,IoTDA appService
    class OBS,SMN,MRS storageService
    class KMS,WAF securityService
```

---

## Diagrama Simplificado por Capas

```mermaid
graph TB
    subgraph "1. DISPOSITIVOS & USUARIOS"
        A1[PathsAI Wearable<br/>Cámara + LiDAR + NPU]
        A2[App Móvil<br/>iOS/Android]
    end

    subgraph "2. EDGE LAYER"
        B1[Huawei IEF<br/>Edge Processing]
    end

    subgraph "3. HUAWEI CLOUD PLATFORM"
        C1[IoT Platform]

        subgraph "AI & Compute"
            C2[ModelArts + MindSpore]
            C3[CCE Microservices]
        end

        subgraph "Data Layer"
            C4[GaussDB MySQL/NoSQL]
            C5[Redis Cache]
        end

        subgraph "Services"
            C6[API Gateway]
            C7[Speech Services]
            C8[FunctionGraph]
        end

        subgraph "Storage & Analytics"
            C9[OBS Storage]
            C10[MRS Big Data]
        end
    end

    A1 -->|MQTT| B1
    A2 -->|HTTPS| C6
    B1 -->|MQTT| C1
    C1 --> C8
    C8 --> C2
    C6 --> C3
    C3 --> C4
    C3 --> C5
    C2 --> C4
    C8 --> C9
    C4 --> C10
    C7 --> C6

    classDef layer1 fill:#FF6B35,stroke:#333,stroke-width:3px,color:#fff
    classDef layer2 fill:#F7931E,stroke:#333,stroke-width:3px,color:#fff
    classDef layer3 fill:#00D4FF,stroke:#333,stroke-width:2px,color:#000

    class A1,A2 layer1
    class B1 layer2
    class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 layer3
```

---

## Flujo de Datos - Detección de Obstáculos

```mermaid
sequenceDiagram
    participant Device as PathsAI Device
    participant Edge as IEF Edge
    participant IoT as IoT Platform
    participant AI as ModelArts AI
    participant DB as GaussDB
    participant Alert as Alert Service
    participant User as Mobile App

    Device->>Edge: Frame de cámara (30fps)
    Edge->>Edge: Pre-procesamiento local
    Edge->>Edge: Inferencia MindSpore Lite

    alt Obstáculo cercano (<5m)
        Edge->>Device: Alerta inmediata
        Device->>Device: Audio warning
    end

    Edge->>IoT: Enviar frame (cada 2s)
    IoT->>AI: Trigger inferencia
    AI->>AI: YOLOv8 + SAM detection
    AI-->>IoT: Detección: Bache (92%)

    IoT->>DB: Guardar obstáculo
    DB->>DB: Indexar geolocalización

    DB->>Alert: Verificar usuarios cercanos
    Alert->>Alert: Usuario a 30m detectado
    Alert->>User: Push notification
    Alert->>Device: Alerta de voz

    User->>User: Mostrar en mapa
    Device->>Device: "Bache en 30 metros"
```

---

## Flujo de Navegación - Ruta Segura

```mermaid
sequenceDiagram
    participant User as Usuario
    participant App as Mobile App
    participant API as API Gateway
    participant Voice as SIS Speech
    participant Route as Route Service
    participant DB as GaussDB NoSQL
    participant Cache as Redis Cache

    User->>App: "Ir a Hospital General"
    App->>API: POST /routes/calculate
    API->>Voice: Speech-to-Text
    Voice-->>API: Texto: "Hospital General"

    API->>Route: Calcular ruta
    Route->>Cache: Verificar caché

    alt Ruta en caché
        Cache-->>Route: Ruta cacheada
    else No en caché
        Route->>DB: Query obstáculos en área
        DB-->>Route: Lista de obstáculos
        Route->>Route: Algoritmo A* modificado
        Route->>Cache: Guardar en caché
    end

    Route->>Voice: Generar instrucciones voz
    Voice-->>Route: Audio generado

    Route-->>API: Ruta + instrucciones
    API-->>App: Response JSON
    App->>App: Mostrar mapa
    App->>User: Audio: "Ruta calculada, 850m, 11 min"
```

---

## Arquitectura de Microservicios en CCE

```mermaid
graph LR
    subgraph "CCE Kubernetes Cluster"
        subgraph "Route Namespace"
            R1[Route Service Pod 1]
            R2[Route Service Pod 2]
            R3[Route Service Pod 3]
        end

        subgraph "Map Namespace"
            M1[Map Service Pod 1]
            M2[Map Service Pod 2]
        end

        subgraph "Alert Namespace"
            A1[Alert Service Pod 1]
            A2[Alert Service Pod 2]
        end

        subgraph "AI Namespace"
            AI1[AI Inference Pod 1]
            AI2[AI Inference Pod 2]
        end

        LB[Load Balancer]
        Ingress[Ingress Controller]
    end

    API[API Gateway] --> Ingress
    Ingress --> LB
    LB --> R1 & R2 & R3
    LB --> M1 & M2
    LB --> A1 & A2
    LB --> AI1 & AI2

    R1 & R2 & R3 --> DB[(GaussDB)]
    M1 & M2 --> DB
    A1 & A2 --> DB
    AI1 & AI2 --> Ascend[Ascend 310]

    classDef pod fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef infra fill:#2C3E50,stroke:#333,stroke-width:2px,color:#fff

    class R1,R2,R3,M1,M2,A1,A2,AI1,AI2 pod
    class LB,Ingress infra
```

---

## Componentes de IA - MindSpore Stack

```mermaid
graph TD
    subgraph "MindSpore AI Stack"
        subgraph "Development"
            D1[ModelArts Studio<br/>Notebook Development]
            D2[Dataset Management<br/>OBS Integration]
            D3[Model Training<br/>Distributed Training]
        end

        subgraph "Training Infrastructure"
            T1[Ascend 910<br/>AI Training Chip]
            T2[CANN<br/>Compute Architecture]
            T3[MindSpore 2.6+<br/>Framework]
        end

        subgraph "Models"
            M1[YOLOv8<br/>Object Detection]
            M2[SAM<br/>Segmentation]
            M3[BLIP-2/LLaVA<br/>Vision-Language]
            M4[ResNet-50<br/>Classification]
        end

        subgraph "Deployment"
            P1[MindSpore Serving<br/>Model Server]
            P2[Ascend 310<br/>Inference Chip]
            P3[API Endpoint<br/>/api/v1/detect]
        end
    end

    D1 --> D3
    D2 --> D3
    D3 --> T1
    T1 --> T2
    T2 --> T3
    T3 --> M1 & M2 & M3 & M4
    M1 & M2 & M3 & M4 --> P1
    P1 --> P2
    P2 --> P3

    classDef dev fill:#9B59B6,stroke:#333,stroke-width:2px,color:#fff
    classDef train fill:#00D4FF,stroke:#333,stroke-width:2px,color:#000
    classDef model fill:#50C878,stroke:#333,stroke-width:2px,color:#fff
    classDef deploy fill:#E67E22,stroke:#333,stroke-width:2px,color:#fff

    class D1,D2,D3 dev
    class T1,T2,T3 train
    class M1,M2,M3,M4 model
    class P1,P2,P3 deploy
```

---

## Seguridad y Compliance

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Device Security"
            S1[X.509 Certificates]
            S2[Device Authentication]
            S3[Secure Boot]
        end

        subgraph "Network Security"
            N1[TLS 1.3 Encryption]
            N2[VPN Connection]
            N3[WAF Protection]
        end

        subgraph "Data Security"
            D1[KMS Encryption at Rest]
            D2[Data Anonymization]
            D3[Backup & DR]
        end

        subgraph "Application Security"
            A1[OAuth 2.0 / JWT]
            A2[API Rate Limiting]
            A3[RBAC Access Control]
        end

        subgraph "Compliance"
            C1[GDPR Compliance]
            C2[ISO 27001]
            C3[Data Residency]
        end
    end

    S1 & S2 & S3 --> N1
    N1 & N2 & N3 --> D1
    D1 & D2 & D3 --> A1
    A1 & A2 & A3 --> C1
    C1 & C2 & C3 --> Audit[Audit Logs]

    classDef security fill:#E74C3C,stroke:#333,stroke-width:2px,color:#fff
    class S1,S2,S3,N1,N2,N3,D1,D2,D3,A1,A2,A3,C1,C2,C3 security
```

---

## Uso de Recursos

Para visualizar estos diagramas:

1. **En GitHub/Gitee**: Los archivos `.md` renderizarán automáticamente los diagramas Mermaid
2. **En VS Code**: Instalar extensión "Markdown Preview Mermaid Support"
3. **Online**: Copiar el código en https://mermaid.live
4. **En presentaciones**: Exportar como PNG/SVG desde Mermaid Live Editor

## Comandos útiles

```bash
# Instalar Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generar PNG desde archivo
mmdc -i arquitectura-mermaid.md -o arquitectura.png

# Generar SVG
mmdc -i arquitectura-mermaid.md -o arquitectura.svg
```
