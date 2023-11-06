import cv2

# Obtén la lista de modelos preentrenados disponibles
available_models = cv2.data.haarcascades

# Imprime la lista de modelos
for model_name in available_models:
    print(model_name)
