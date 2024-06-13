{{/*
Expand the name of the chart.
*/}}
{{- define "semgr8s.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "semgr8s.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "semgr8s.labels" -}}
helm.sh/chart: {{ include "semgr8s.chart" . }}
{{ include "semgr8s.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "semgr8s.selectorLabels" -}}
app.kubernetes.io/name: {{ include "semgr8s.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service to use
*/}}
{{- define "semgr8s.serviceName" -}}
{{- include "semgr8s.name" . }}-service
{{- end }}

{{/*
Create the name of the webhook to use
*/}}
{{- define "semgr8s.webhookName" -}}
{{- include "semgr8s.name" . }}-webhook
{{- end }}

{{/*
Create the name of the TLS secret to use
*/}}
{{- define "semgr8s.TLSName" -}}
{{- include "semgr8s.name" . }}-tls
{{- end }}

{{/*
Create the name of the environments to use
*/}}
{{- define "semgr8s.envName" -}}
{{- include "semgr8s.name" . }}-env
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "semgr8s.serviceAccountName" -}}
{{- include "semgr8s.name" . }}-serviceaccount
{{- end }}

{{/*
Create the name of the environments to use
*/}}
{{- define "semgr8s.roleName" -}}
{{- include "semgr8s.name" . }}-role
{{- end }}

{{/*
Create the name of the environments to use
*/}}
{{- define "semgr8s.roleBindingName" -}}
{{- include "semgr8s.name" . }}-rolebinding
{{- end }}

{{- define "semgr8s.getFileName" -}}
{{- . | trimPrefix "rules/" | replace "/" "_" }}
{{- end }}
