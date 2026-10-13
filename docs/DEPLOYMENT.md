# Guía de Deployment - Aplicación Streamlit

Esta guía explica cómo deployar la aplicación web del Predictor de Precio del Cobre en diferentes plataformas cloud.

---

## Opción 1: Streamlit Cloud (RECOMENDADA - GRATIS)

### Prerequisitos
- Proyecto subido a GitHub (público o privado)
- Cuenta de GitHub

### Pasos para Deploy

#### 1. Acceder a Streamlit Cloud
- Ve a [share.streamlit.io](https://share.streamlit.io)
- Click en "Sign up" o "Continue with GitHub"
- Autoriza el acceso a tu cuenta de GitHub

#### 2. Crear Nueva App
- Click en "New app"
- Completa los campos:
  - **Repository**: `BastianBerriosalarcon/predictor-precio-cobre` (o tu repo)
  - **Branch**: `main`
  - **Main file path**: `predictor-precio-cobre/app.py`
  - **App URL**: Elige un nombre único (ej: `predictor-cobre-chile`)

#### 3. Configuración Avanzada (Opcional)
- Click en "Advanced settings"
- **Python version**: 3.9 o 3.10
- **Secrets**: Dejar vacío (no necesitamos secrets por ahora)

#### 4. Deploy
- Click en "Deploy!"
- Espera 2-5 minutos mientras Streamlit Cloud:
  - Clona tu repositorio
  - Instala dependencias de `requirements.txt`
  - Inicia la aplicación

#### 5. Obtener URL
Una vez completado, tendrás una URL pública:
```
https://predictor-cobre-chile.streamlit.app
```

### Actualizar la App
Cada vez que hagas `git push` a la rama `main`, Streamlit Cloud automáticamente:
- Detecta los cambios
- Redeploya la aplicación
- Actualiza la app en vivo

---

## Opción 2: Google Cloud Platform (GCP) - Región Chile

### Prerequisitos
- Cuenta en [Google Cloud](https://cloud.google.com)
- Créditos gratuitos ($300 USD para nuevos usuarios)
- Google Cloud SDK instalado

### Pasos

#### 1. Crear archivo `Dockerfile`
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY predictor-precio-cobre/ ./predictor-precio-cobre/

EXPOSE 8080

CMD streamlit run predictor-precio-cobre/app.py --server.port=8080 --server.address=0.0.0.0
```

#### 2. Deploy en Cloud Run (Región Sudamérica)
```bash
# Autenticarse
gcloud auth login

# Configurar proyecto
gcloud config set project TU-PROYECTO-ID

# Build y deploy en región southamerica-west1 (Santiago, Chile)
gcloud run deploy predictor-cobre \
  --source . \
  --region southamerica-west1 \
  --allow-unauthenticated
```

#### 3. Obtener URL
GCP te dará una URL pública:
```
https://predictor-cobre-xxxxx-rj.a.run.app
```

**Región disponible en Chile**: `southamerica-west1` (Santiago)

**Costo**: Free tier 2 millones de requests/mes

---

## Opción 3: Oracle Cloud Infrastructure (OCI)

### Prerequisitos
- Cuenta en [Oracle Cloud](https://www.oracle.com/cloud/free/)
- Always Free tier (sin expiración)

### Pasos

#### 1. Crear Compute Instance (Always Free)
- VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM)
- Oracle Linux 8
- **Región**: `sa-santiago-1` (Santiago, Chile) o `sa-valparaiso-1` (Valparaíso, Chile)
- Configurar puerto 8501 en Security List

#### 2. Conectar por SSH y configurar
```bash
# Conectar a la VM
ssh opc@<IP-PUBLICA>

# Instalar Python y dependencias
sudo yum install python39 git -y

# Clonar repositorio
git clone https://github.com/BastianBerriosalarcon/predictor-precio-cobre.git
cd predictor-precio-cobre

# Instalar dependencias
pip3.9 install -r requirements.txt

# Ejecutar Streamlit
streamlit run predictor-precio-cobre/app.py --server.port=8501 --server.address=0.0.0.0
```

#### 3. Configurar como servicio (systemd)
```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/streamlit-app.service
```

Contenido:
```ini
[Unit]
Description=Streamlit Copper Predictor
After=network.target

[Service]
User=opc
WorkingDirectory=/home/opc/predictor-precio-cobre
ExecStart=/usr/local/bin/streamlit run predictor-precio-cobre/app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y arrancar
sudo systemctl enable streamlit-app
sudo systemctl start streamlit-app
```

**Acceso**: `http://<IP-PUBLICA>:8501`

**Costo**: GRATIS (Always Free tier)

**Región**: OCI tiene 2 regiones en Chile - Santiago (`sa-santiago-1`) y Valparaíso (`sa-valparaiso-1`)
**Latencia**: < 5ms desde Chile

---

## Opción 4: Azure Container Instances - Región Chile

### Prerequisitos
- Cuenta en [Azure](https://azure.microsoft.com/free/)
- Azure CLI instalado

### Pasos

#### 1. Login y configurar (Región Chile Central)
```bash
az login
az group create --name predictor-cobre-rg --location chilecentral
```

#### 2. Crear Container Registry
```bash
az acr create --resource-group predictor-cobre-rg \
  --name predictorcobre --sku Basic
```

#### 3. Build y push Docker image
```bash
# Build localmente
docker build -t predictor-cobre:latest .

# Tag
docker tag predictor-cobre:latest predictorcobre.azurecr.io/predictor-cobre:latest

# Push
az acr login --name predictorcobre
docker push predictorcobre.azurecr.io/predictor-cobre:latest
```

#### 4. Deploy Container Instance
```bash
az container create \
  --resource-group predictor-cobre-rg \
  --name predictor-app \
  --image predictorcobre.azurecr.io/predictor-cobre:latest \
  --dns-name-label predictor-cobre \
  --ports 8501 \
  --location chilecentral
```

**Acceso**: `http://predictor-cobre.chilecentral.azurecontainer.io:8501`

**Región**: `chilecentral` (Chile Central - Santiago, inaugurado Junio 2025)

**Costo**: Aproximadamente $15 USD/mes (tier básico)

**Latencia**: < 5ms desde Chile

---

## Opción 5: AWS (Amazon Web Services) - Región Sudamérica

### A. AWS App Runner (Recomendado - Más fácil)

```bash
# Crear archivo apprunner.yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: streamlit run predictor-precio-cobre/app.py --server.port=8080
  network:
    port: 8080
```

Deploy desde AWS Console → App Runner → Create service → GitHub

**Región**: `us-east-1-scl-1` (AWS Local Zone Santiago) o `sa-east-1` (Sao Paulo)

**Costo**: Pay-as-you-go (aproximadamente $5-10/mes uso bajo)

**Nota**: AWS tiene Local Zone en Santiago (capacidades limitadas). Región completa planificada para 2026.

### B. AWS EC2 (Free Tier)

Similar a OCI, pero con:
- t2.micro instance (Free tier 12 meses)
- Security Group: puerto 8501 abierto
- Amazon Linux 2
- **Región**: `sa-east-1` (Sao Paulo, Brasil) - región completa más cercana

**Nota**: AWS Local Zone en Santiago (`us-east-1-scl-1`) tiene capacidades limitadas. Región completa viene en 2026.

---

## Notas sobre Datacenters en Chile y Latencia

### Proveedores con datacenter COMPLETO en Chile (2025):

**Oracle Cloud Infrastructure (OCI)** - PRIMER hyperscaler en Chile:
- **Región Santiago**: `sa-santiago-1` (Inaugurado 2020)
- **Región Valparaíso**: `sa-valparaiso-1` (Inaugurado 2023)
- Latencia desde Chile: < 5ms
- 100% energía renovable
- **Único con 2 regiones completas en Chile**

**Microsoft Azure**:
- **Región**: `Chile Central` (Inaugurado Junio 2025)
- Ubicación: Región Metropolitana de Santiago
- 3 zonas de disponibilidad
- Latencia desde Chile: < 5ms
- Inversión: $3.3 mil millones USD

**Google Cloud Platform (GCP)**:
- **Región**: `southamerica-west1` (Santiago, Chile)
- Inaugurado en 2021
- Latencia desde Chile: < 10ms

**AWS (Amazon Web Services)**:
- **Local Zone Santiago**: `us-east-1-scl-1` (Disponible desde Enero 2023)
- Latencia desde Chile: < 10ms (single-digit milliseconds)
- **Infraestructura adicional en Chile**:
  - CloudFront Edge Location (2019)
  - AWS Direct Connect Santiago (2023)
  - AWS Ground Station Punta Arenas (2021)
- **Región completa planificada para finales de 2026**
- Inversión: $4 mil millones USD
- **Nota**: Local Zone tiene capacidades limitadas vs región completa (no todos los servicios)

### Recomendación por latencia para usuarios en Chile (2025):
1. **OCI Santiago/Valparaíso** - Latencia excelente (<5ms), 2 regiones completas, GRATIS
2. **Azure Chile Central** - Latencia excelente (<5ms), región completa
3. **AWS Local Zone Santiago** - Latencia excelente (<10ms), capacidades limitadas
4. **GCP southamerica-west1** - Latencia excelente (<10ms), región completa, free tier

---

## Troubleshooting Común

### Error: "ModuleNotFoundError"
**Causa**: Falta dependencia en `requirements.txt`
**Solución**: Agregar la librería faltante y hacer `git push`

### Error: "File not found: app.py"
**Causa**: Ruta incorrecta en configuración
**Solución**: Verificar que la ruta sea `predictor-precio-cobre/app.py`

### Error: "Memory limit exceeded"
**Causa**: Modelos muy grandes (>500MB)
**Solución**:
- Usar modelos más pequeños
- Streamlit Cloud tiene límite de 1GB RAM
- Considera GCP/AWS con más recursos

### App muy lenta
**Causa**: Carga de datos pesados en cada request
**Solución**: Usar `@st.cache_data` y `@st.cache_resource` (ya implementado)

---

## Monitoreo y Mantenimiento

### Ver Logs
- **Streamlit Cloud**: Click en "Manage app" → "Logs"
- **GCP**: Cloud Logging
- **OCI**: `/var/log/messages` o journalctl
- **Azure/AWS**: Container logs en portal

### Uso de Recursos
- **Streamlit Cloud**: Ver en dashboard (CPU, RAM)
- **Cloud providers**: Métricas en consola

### Redeployar Manualmente
Si hay problemas:
1. Ve al dashboard de tu plataforma
2. Click en "Reboot"/"Restart" o "Redeploy"

---

## Recursos Adicionales

- [Documentación Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [GCP Cloud Run Docs](https://cloud.google.com/run/docs)
- [OCI Always Free](https://www.oracle.com/cloud/free/)
- [Azure Container Instances](https://learn.microsoft.com/azure/container-instances/)
- [AWS App Runner](https://docs.aws.amazon.com/apprunner/)
- [GCP Región Santiago](https://cloud.google.com/about/locations#southamerica)

---

## Próximos Pasos Post-Deploy

1. **Actualizar README**
   - Reemplazar URL de demo con la pública
   - Agregar badge de Streamlit

2. **Compartir**
   - Agrega link en tu CV
   - Publica en LinkedIn
   - Agrega a tu portafolio

3. **Monitorear**
   - Revisa analytics
   - Chequea logs si hay errores

---

**Última actualización**: Octubre 2025
**Autor**: Bastian Berrios
