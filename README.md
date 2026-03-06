# 🚀 SCALE 23X Demo: Kubernetes AI Toolchain Operator (KAITO)

A live demonstration of [KAITO](https://kaito-project.github.io/kaito/) — the Kubernetes AI Toolchain Operator. This demo showcases how to serve GPU-accelerated Large Language Models (LLMs), route inference requests intelligently using the [Gateway API Inference Extension](https://gateway-api-inference-extension.sigs.k8s.io/), and seamlessly add Retrieval-Augmented Generation (RAG) to any model using a single custom resource.

Everything runs on Azure Kubernetes Service (AKS) and is deployed via GitOps using Argo CD.

---

## 🎯 What You'll Learn

| Concept                             | How It's Demonstrated                                                                                                                                |
| :---------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| **KAITO InferenceSets**             | Deploy Phi-4 and Gemma-3 models. KAITO handles GPU node provisioning, model loading, and OpenAI-compatible serving automatically.                    |
| **Gateway API Inference Extension** | A single gateway routes requests to the correct model based on the `model` field in the request body — eliminating the need for per-model endpoints. |
| **KAITO RAGEngine**                 | One custom resource sets up an end-to-end RAG pipeline: embedding model, vector store, and retrieval — zero manual infrastructure required.          |
| **Direct → RAG in One Click**       | Switch the chat app from direct model inference to RAG-augmented inference by changing a single environment variable.                                |
| **GitOps Deployment**               | Argo CD deploys the entire stack; Argo Rollouts handles canary releases when configurations change.                                                  |

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│  AKS Cluster                                                        │
│                                                                     │
│  ┌──────────┐    ┌───────────────┐    ┌──────────────────────────┐  │
│  │ Web App  │───▶│  Agent (AI)   │───▶│  KAITO Gateway (Istio)   │  │
│  │ Next.js  │    │  FastAPI      │    │  Gateway API + Inference │  │
│  └──────────┘    └───────────────┘    │  Extension (body-based)  │  │
│                         │             └────────┬────────┬────────┘  │
│                         ▼                      │        │           │
│                  ┌──────────────┐      ┌───────▼──┐ ┌───▼───────┐   │
│                  │  RAGEngine   │      │ Phi-4    │ │ Gemma-3   │   │
│                  │ (embedding   │─────▶│ Mini     │ │ 27B       │   │
│                  │ + retrieval) │      │ Instruct │ │ Instruct  │   │
│                  └──────────────┘      └──────────┘ └───────────┘   │
│                         ▲                  GPU Nodes (KAITO)        │
│                         │                                           │
│                  ┌─────────────┐                                    │
│                  │ Argo        │                                    │
│                  │ Workflows   │  Schedule data ingestion pipeline  │
│                  └─────────────┘                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 🧠 Models

Both models are defined as KAITO `InferenceSet` resources. KAITO automatically provisions the right GPU node SKU, pulls the model weights, and exposes an OpenAI-compatible `/v1/chat/completions` endpoint.

| Model                  | GPU SKU                  | Gated          | Description                                        |
| :--------------------- | :----------------------- | :------------- | :------------------------------------------------- |
| `phi-4-mini-instruct`  | Standard_NV36ads_A10_v5  | No             | Fast, lightweight model for general inference.     |
| `gemma-3-27b-instruct` | Standard_NC24ads_A100_v4 | Yes (HF token) | High-quality model used with RAG for grounded Q&A. |

### 🧩 Key KAITO Resources

| Resource                | What It Does                                                                                                  |
| :---------------------- | :------------------------------------------------------------------------------------------------------------ |
| `InferenceSet`          | Declares a model to serve. KAITO handles GPU provisioning, model download, and serving.                       |
| `RAGEngine`             | Deploys an embedding model (`BAAI/bge-small-en-v1.5`), vector store, and retrieval endpoint as a single unit. |
| `Gateway` + `HTTPRoute` | Istio gateway with the Gateway API Inference Extension for body-based model routing.                          |

### 🛠️ Infrastructure Stack

| Component                      | Version                  |
| :----------------------------- | :----------------------- |
| KAITO GPU Provisioner          | 0.4.1                    |
| KAITO Workspace / RAGEngine    | 0.9.0                    |
| Istio + body-based router      | 1.28.3 / v1.3.0          |
| Gateway API CRDs               | v1.4.1                   |
| Argo CD / Rollouts / Workflows | v3.2.6 / v1.8.4 / v3.7.9 |
| cert-manager                   | v1.19.2                  |
| External Secrets Operator      | v2.0.1                   |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed and configured:

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) with an active subscription.
- [GitHub CLI](https://cli.github.com/) and a Personal Access Token (PAT) with repo permissions (for Argo CD GitOps).
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0.
- [kubectl](https://kubernetes.io/docs/tasks/tools/).
- A registered domain with nameservers pointed to Azure DNS.
- A [Hugging Face token](https://huggingface.co/settings/tokens) with access to `google/gemma-3-27b-it`.

> [!NOTE]
> **GitHub Authentication:** Terraform uses your GitHub CLI (`gh`) login to automatically create a read-only SSH deploy key for Argo CD. Ensure you are logged in (`gh auth login`) with `admin:repo` (classic PAT) or `Administration: write` (fine-grained PAT) permissions. _(Note: Once your repo is public, you can set `github_deploy_key_enabled = false` and re-apply)._
>
> **Custom Domains:** By default, this demo uses Let's Encrypt DNS-01 validation via Azure DNS, which requires a registered domain. If your domain is registered externally, update its nameservers to point to the Azure DNS nameservers shown in the Terraform output.
>
> **No Domain?** If you don't have a domain, you can use a wildcard DNS service like [nip.io](https://nip.io) (e.g., `<gateway-ip>.nip.io`). To do this, you will need to modify the `ClusterIssuer` in `k8s/cert-manager-clusterissuer.tmpl` to use `HTTP-01` validation instead of `DNS-01`, and update the hostnames in the Gateway and Argo CD configurations. Alternatively, you can configure `cert-manager` to use a `SelfSigned` issuer.

---

## 🚀 Setup Guide

### 1. Deploy Azure Infrastructure

This step creates the AKS cluster, installs KAITO, Istio, Argo CD, cert-manager, ESO, and stores the HF token in Key Vault.

```sh
cd infra/azure
export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
export TF_VAR_hf_token="hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
terraform init
terraform apply
```

> [!WARNING]
> The `hf_token` variable is marked as `sensitive` so it won't appear in plan output or logs, but it **will** be stored in the Terraform state file in plaintext. Treat your state file as a sensitive artifact.

### 2. Connect to the Cluster

Retrieve AKS credentials and install the Gateway API CRDs.

```sh
read -r RG_NAME AKS_NAME DNS_NAME <<< "$(
  terraform output -json | jq -r '[
    .rg_name.value,
    .aks_name.value,
    .dns_zone_name.value
  ] | @tsv'
)"
az aks get-credentials --resource-group $RG_NAME --name $AKS_NAME
kubectl apply --server-side -k "github.com/kubernetes-sigs/gateway-api/config/crd?ref=v1.4.1"
```

### 3. Deploy Kubernetes Resources

Configures the Argo CD gateway, creates the ClusterSecretStore, DNS records, and cert-manager ClusterIssuer.

```sh
cd ../k8s
terraform init
terraform apply
```

Wait for the Argo CD Gateway to be programmed and assigned a public IP, then create the DNS record:

```sh
kubectl wait --for=condition=Programmed gtw/argocd-gateway -n argocd --timeout=300s

az network dns record-set a delete \
  --resource-group $RG_NAME \
  --zone-name $DNS_NAME \
  --name argocd --yes 2>/dev/null

az network dns record-set a add-record \
  --resource-group $RG_NAME \
  --zone-name $DNS_NAME \
  --record-set-name argocd \
  --ttl 60 \
  --ipv4-address $(kubectl get gtw argocd-gateway -n argocd -ojsonpath='{.status.addresses[?(@.type=="IPAddress")].value}')
```

Restart the Argo CD server to refresh its cached OIDC provider state:

```sh
kubectl rollout restart deployment/argo-cd-argocd-server -n argocd
```

> [!NOTE]
> **Why is a restart needed?** The Argo CD server fetches and caches the OIDC provider metadata (from Microsoft Entra ID's `.well-known/openid-configuration` endpoint) at startup. When the Helm chart installed Argo CD in Step 1, the server started immediately — but the Entra ID federated identity credential and app registration may not have fully propagated yet (Microsoft Entra ID is eventually consistent). If the initial OIDC fetch fails or the workload identity token exchange isn't ready, Argo CD caches the error state and does not retry automatically. The restart forces a fresh OIDC initialization, which succeeds now that Microsoft Entra ID propagation is complete.

### 4. Bootstrap Everything

A single command deploys the entire stack via Argo CD's App of Apps pattern. All components sync automatically in dependency order — except the chat app, which is left for manual sync during the demo.

```sh
cd ../../
kubectl apply -f manifests/argocd/app-of-apps.yaml
```

### 5. Log into Argo CD CLI (Optional)

If you want to use the Argo CD CLI during the demo (e.g., `argocd app sync`), log in via SSO through a port-forward. The admin account is disabled — authentication uses Microsoft Entra ID.

Port-forward the Argo CD server:

```sh
kubectl port-forward -n argocd svc/argo-cd-argocd-server 9000:80 &
```

Authenticate with the CLI:

```sh
argocd login localhost:9000 --sso --sso-port 8085 --insecure
```

This opens a browser for SSO authentication. Once you see "Authentication successful" in the terminal, you can close the browser tab.

> [!NOTE]
> The `--insecure` flag skips server certificate verification and domain verification which is needed since we've port-forwarded to `localhost` instead of using the actual domain name. Do not use this flag in production.

Check the status of the applications:

```sh
argocd app get scale23x-demo
```

### 6. Configure DNS

Wait for the gateway to get a public IP, then create the DNS record:

```sh
kubectl wait --for=condition=Programmed gtw/kaito-gateway --timeout=300s

az network dns record-set a delete \
  --resource-group $RG_NAME \
  --zone-name $DNS_NAME \
  --name chat --yes 2>/dev/null

az network dns record-set a add-record \
  --resource-group $RG_NAME \
  --zone-name $DNS_NAME \
  --record-set-name chat \
  --ttl 60 \
  --ipv4-address $(kubectl get gtw kaito-gateway -ojsonpath='{.status.addresses[?(@.type=="IPAddress")].value}')
```

### 7. Wait for Models & RAG Engine

KAITO provisions GPU nodes and loads models — this takes several minutes:

```sh
kubectl wait --for=condition=InferenceSetReady inferenceset/phi-4-mini-instruct --timeout=10m
kubectl wait --for=condition=InferenceSetReady inferenceset/gemma-3-27b-instruct --timeout=10m
kubectl wait --for=condition=ServiceReady ragengine/scale23x --timeout=10m
```

Once all three are ready, you're set for the demo! 🎉

---

## 🎬 Demo Walkthrough

### Step 1 — KAITO Overview in Argo CD

Open `https://argocd.<your-domain>` and navigate to the **Applications** tab. You'll see eight applications deployed via the App of Apps pattern:

| Application       | Status                 | What It Deploys                                                                       |
| :---------------- | :--------------------- | :------------------------------------------------------------------------------------ |
| **scale23x-demo** | 🟢 Healthy · Synced    | The parent App of Apps — manages all other applications.                              |
| **inference**     | 🟢 Healthy · Synced    | KAITO `InferenceSet` resources for `phi-4-mini-instruct` and `gemma-3-27b-instruct`.  |
| **ragengine**     | 🟢 Healthy · Synced    | The `scale23x` RAGEngine CR (embedding model + vector store + retrieval).             |
| **gateway**       | 🟢 Healthy · Synced    | Istio gateway + HTTPRoutes with the Inference Extension for body-based model routing. |
| **o11y**          | 🟢 Healthy · Synced    | Observability stack (OTel Collector, Prometheus, Grafana, Loki, Tempo).               |
| **schedule**      | 🟢 Healthy · Synced    | Argo Workflow template for schedule data ingestion.                                   |
| **secrets**       | 🟢 Healthy · Synced    | ExternalSecret for the Hugging Face token.                                            |
| **chat**          | 🟡 Missing · OutOfSync | The web + agent app — intentionally not deployed yet.                                 |

**Highlights to show:**

- **inference**: The Application Details Tree view shows the full resource hierarchy: `InferenceSet` → `Workspace` → `HelmRelease` → `ControllerRevision` → `StatefulSet` → `Pod`. You can see both models with their HTTPRoutes, DestinationRules, OCI repositories, Services, and model-weights PVCs — all created automatically by KAITO.
- **ragengine**: The tree shows the `scale23x` RAGEngine CR alongside its HTTPRoute, and the resources KAITO created from it. One custom resource produced an entire RAG pipeline with no manual infrastructure.
- **gateway**: The tree shows the `kaito-gateway` Gateway and `kaito-tls` Certificate, with Istio's generated resources branching off. This is the single entry point for all inference requests.

### Step 2 — Body-Based Model Routing

Port-forward the gateway and send requests to different models:

```sh
kubectl port-forward svc/kaito-gateway-istio 5000:80
```

Send a chat completion request with `"model": "phi-4-mini-instruct"` — the request routes to Phi-4. Change it to `"model": "gemma-3-27b-instruct"` — it routes to Gemma-3. One gateway, multiple models, no per-model endpoints.

### Step 3 — Deploy the Chat App

In Argo CD, click **Sync** on the `chat` application. This deploys the `direct` overlay — the agent sends inference requests straight to the models through the gateway (no RAG).

> [!TIP]
> You can also sync from the CLI:
>
> ```sh
> argocd app sync chat --prune
> ```

The deployment uses Argo Rollouts for canary delivery. Open the Rollouts dashboard to watch the canary progress and promote:

```sh
kubectl argo rollouts dashboard
```

Open `http://localhost:3100` in a browser — you'll see the `agent` and `web` rollouts paused at 25% weight. Click **Promote** on each to advance through the canary steps.

> [!TIP]
> To skip all remaining canary steps and go straight to 100% from the terminal:
>
> ```sh
> kubectl argo rollouts promote --full agent
> kubectl argo rollouts promote --full web
> ```

Once promoted, ask a question about the **SCALE 23X schedule** — the model won't know the answer because it doesn't have that context.

### Step 4 — Ingest Data into the RAG Engine

The RAGEngine exposes an `/index` endpoint for loading documents. Trigger the Argo Workflow to ingest the SCALE 23X schedule:

```sh
argo submit --watch --from workflowtemplate/schedule-index-pipeline
```

The pipeline downloads the schedule JSON, formats it into documents, and uploads them to the RAGEngine's vector store. Once complete, the data is embedded and indexed — ready for retrieval.

### Step 5 — Switch from Direct Inference to RAG

This is the key moment: switching the chat app from direct model inference to RAG-augmented inference requires changing **one config value**.

Edit `manifests/argocd/apps/chat.yaml` to point to the `rag` overlay:

```sh
sed -i 's/overlays\/direct/overlays\/rag/' manifests/argocd/apps/chat.yaml
```

The only difference between the two overlays:

| Variable          | `direct`                        | `rag`                            |
| :---------------- | :------------------------------ | :------------------------------- |
| `OPENAI_BASE_URL` | `http://kaito-gateway-istio/v1` | `http://kaito-gateway-istio/rag` |
| `RAG_INDEX_NAME`  | _(not set)_                     | `schedule_index`                 |

Commit and push:

```sh
git add manifests/argocd/apps/chat.yaml
git commit -m "Route chat app through RAG engine"
git push
```

Argo CD detects the change → click **Sync** on the `chat` application.

Argo Rollouts manages the canary rollout. Open the Rollouts dashboard (if not already running) and promote from there:

```sh
kubectl argo rollouts dashboard
```

Optionally, you can sync and promote from the CLI:

```sh
argocd app sync scale23x-demo --resource argoproj.io:Application:chat --prune
argocd app sync chat --prune
kubectl argo rollouts get rollout agent
kubectl argo rollouts promote agent --full
```

### Step 6 — RAG-Powered Responses

Ask the same question about the SCALE 23X schedule. The request now flows through the RAGEngine:

```text
Agent → Gateway (/rag) → RAGEngine → retrieves relevant context
  → Gateway (/v1) → body-based router → model → grounded response
```

The model now has the relevant context from the schedule and answers correctly! 🚀

---

## 💻 Local Development

A Docker Compose setup is available for local development with a full observability stack:

```sh
docker compose up
```

| Service    | URL                     |
| :--------- | :---------------------- |
| Web app    | `http://localhost:3001` |
| Agent API  | `http://localhost:8001` |
| Grafana    | `http://localhost:3000` |
| Prometheus | `http://localhost:9090` |

---

## 📁 Project Structure

```text
├── infra/
│   ├── azure/          # Terraform: AKS, KAITO, Istio, Argo, Key Vault
│   └── k8s/            # Terraform: ClusterSecretStore, DNS, ClusterIssuer
├── manifests/
│   ├── argocd/         # App of Apps + individual Application CRs
│   └── apps/
│       ├── chat/       # Web + Agent (base with direct/rag overlays)
│       ├── gateway/    # KAITO Gateway + TLS
│       ├── inference/  # InferenceSets (Phi-4, Gemma-3)
│       ├── ragengine/  # RAGEngine CR
│       ├── o11y/       # Observability (OTel, Prometheus, Grafana, Loki, Tempo)
│       ├── schedule/   # Argo Workflow for data ingestion
│       └── secrets/    # ExternalSecret for HF token
├── src/
│   ├── agent/          # Python/FastAPI AI agent
│   ├── sched/          # Schedule data parser
│   └── web/            # Next.js frontend
└── tests/              # HTTP test files
```

---

## 🧹 Cleanup

**Keep the cluster, remove the apps:**

```sh
kubectl delete -f manifests/argocd/app-of-apps.yaml --wait=false
kubectl delete pod --field-selector=status.phase==Succeeded
```

**Destroy everything:**

```sh
cd infra/azure
terraform destroy
```

---

## 📚 Resources

- [KAITO Inference](https://kaito-project.github.io/kaito/docs/inference)
- [KAITO RAG API](https://kaito-project.github.io/kaito/docs/rag-api)
- [KAITO + Gateway API Inference Extension](https://kaito-project.github.io/kaito/docs/gateway-api-inference-extension)
- [Gateway API Inference Extension](https://gateway-api-inference-extension.sigs.k8s.io/)
