# Usa una imagen base de Conda (Miniconda es más ligera)
FROM continuumio/miniconda3

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de entorno y el código de la aplicación
COPY environment.yml .
COPY . .

# Crea y activa el entorno Conda
# El entorno se llama 'curso_react' según tu archivo environment.yml
RUN conda env create -f environment.yml
ENV PATH="/opt/conda/envs/curso_react/bin:$PATH"

# Comando de ejecución: inicia Flask
# Usamos gunicorn, un servidor de producción, en lugar de flask run para Docker
CMD ["conda", "run", "-n", "curso_react", "gunicorn", "-b", "0.0.0.0:5000", "app:app"]