# Cómo subir esta entrega a GitHub

El repositorio local ya está inicializado en `main`, con los cambios preparados y con autor `Leandro Marin <lea.marin@duocuc.cl>`.

## 1. Crear el repositorio remoto

En GitHub → **New repository**:

- **Repository name:** `Ferrandes_Agente_EP3`
- **Visibility:** **Public** (recomendado para que el docente pueda verlo sin solicitar acceso)
- **No marcar** *Add a README file*, *.gitignore* ni *license* (evita conflictos con el historial local).

## 2. Conectar y subir

Desde esta carpeta:

```sh
cd /home/l480/Descargas/EP3_Ferrandes_Entrega
git remote add origin https://github.com/TU_USUARIO/Ferrandes_Agente_EP3.git
git branch -M main
git push -u origin main
```

Si creaste el repo con un README inicial y el `push` es rechazado:

```sh
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 3. Verificar

Abre `https://github.com/TU_USUARIO/Ferrandes_Agente_EP3` y confirma que aparecen:

- `README.md`
- `informe/Informe_Tecnico_EP3_Ferrandes.pdf`
- `informe/Evaluacion_Pauta_EP3_Ferrandes.pdf`
- `presentacion/Presentacion_EP3_Ferrandes.pptx`
- `presentacion/Guion_Presentacion_EP3.md`
- `dashboard/app.py` y `dashboard/dashboard.html`
- `evidencia/`

## 4. Enviar en AVA y al correo del docente

- Enlace al repositorio.
- `informe/Informe_Tecnico_EP3_Ferrandes.pdf`.
- `informe/Evaluacion_Pauta_EP3_Ferrandes.pdf` (si el docente la solicita como anexo).
- Recordatorio pendiente: completar el nombre del integrante B y las reflexiones individuales **sin IA** antes de la entrega final.
