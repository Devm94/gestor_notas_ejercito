document.addEventListener("DOMContentLoaded", function () {
    const selectDocumento = document.getElementById(Select_Revisar);
    const visorDocumento = document.getElementById(Visor_Revisar);
    if (selectDocumento.options.length > 0) {
      visorDocumento.src = selectDocumento.value;
    }
    selectDocumento.addEventListener("change", function () {
      visorDocumento.src = this.value;
    });
});
  document.addEventListener("DOMContentLoaded", function () {
    let fileInput = document.getElementById(fileInput_Agregar);
    let dropzone = document.getElementById(dropzone_Agregar);
    let fileList = document.getElementById(fileList_Agregar);
    let selectedFiles = new DataTransfer(); // 📌 Para manejar archivos correctamente

    // 📌 Detectar archivos desde el input
    fileInput.addEventListener("change", function (event) {
      handleFiles(event.target.files);
    });
    // 📌 Manejar archivos cuando se arrastran al área
    dropzone.addEventListener("drop", function (event) {
      event.preventDefault();
      handleFiles(event.dataTransfer.files);
    });
    dropzone.addEventListener("dragover", function (event) {
      event.preventDefault();
    });
    // 📌 Función para manejar los archivos seleccionados
    function handleFiles(files) {
      for (let file of files) {
        if (!fileExists(file)) {
          selectedFiles.items.add(file); // Agrega el archivo a la lista de DataTransfer
          let listItem = document.createElement("li");
          listItem.className =
            "d-flex justify-content-between align-items-center p-2 border rounded mt-1";
          listItem.innerHTML = `
                  ${file.name}
                  <button type="button" class="btn btn-danger btn-sm ms-2" onclick="removeFile('${file.name}')">✖</button>`;
          fileList.appendChild(listItem);
        }
      }
      fileInput.files = selectedFiles.files; // Actualiza los archivos en el input
    }
    function fileExists(file) {
      for (let i = 0; i < selectedFiles.files.length; i++) {
        if (selectedFiles.files[i].name === file.name) {
          return true;
        }
      }
      return false;
    }
    window.removeFile = function (fileName) {
      for (let i = 0; i < selectedFiles.items.length; i++) {
        if (selectedFiles.items[i].getAsFile().name === fileName) {
          selectedFiles.items.remove(i); // Elimina el archivo de la lista
          break;
        }
      }
      fileInput.files = selectedFiles.files; // Actualiza los archivos en el input
      updateFileList();
    };
    function updateFileList() {
      fileList.innerHTML = "";
      for (let i = 0; i < selectedFiles.files.length; i++) {
        let file = selectedFiles.files[i];

        let listItem = document.createElement("li");
        listItem.className =
          "d-flex justify-content-between align-items-center p-2 border rounded mt-1";

        listItem.innerHTML = `
              ${file.name}
              <button type="button" class="btn btn-danger btn-sm ms-2" onclick="removeFile('${file.name}')">✖</button>`;
        fileList.appendChild(listItem);
      }
    }
  });
  document.addEventListener("DOMContentLoaded", function () {
    let fileInput = document.getElementById(fileInput_Completar);
    let dropzone = document.getElementById(dropzone_Completar );
    let fileList = document.getElementById(fileList_Completar);
    let selectedFiles = new DataTransfer(); // 📌 Para manejar archivos correctamente

    // 📌 Detectar archivos desde el input
    fileInput.addEventListener("change", function (event) {
      handleFiles(event.target.files);
    });
    // 📌 Manejar archivos cuando se arrastran al área
    dropzone.addEventListener("drop", function (event) {
      event.preventDefault();
      handleFiles(event.dataTransfer.files);
    });
    dropzone.addEventListener("dragover", function (event) {
      event.preventDefault();
    });
    // 📌 Función para manejar los archivos seleccionados
    function handleFiles(files) {
      for (let file of files) {
        if (!fileExists(file)) {
          selectedFiles.items.add(file); // Agrega el archivo a la lista de DataTransfer
          let listItem = document.createElement("li");
          listItem.className =
            "d-flex justify-content-between align-items-center p-2 border rounded mt-1";
          listItem.innerHTML = `
                  ${file.name}
                  <button type="button" class="btn btn-danger btn-sm ms-2" onclick="removeFile('${file.name}')">✖</button>`;
          fileList.appendChild(listItem);
        }
      }
      fileInput.files = selectedFiles.files; // Actualiza los archivos en el input
    }
    function fileExists(file) {
      for (let i = 0; i < selectedFiles.files.length; i++) {
        if (selectedFiles.files[i].name === file.name) {
          return true;
        }
      }
      return false;
    }
    window.removeFile = function (fileName) {
      for (let i = 0; i < selectedFiles.items.length; i++) {
        if (selectedFiles.items[i].getAsFile().name === fileName) {
          selectedFiles.items.remove(i); // Elimina el archivo de la lista
          break;
        }
      }
      fileInput.files = selectedFiles.files; // Actualiza los archivos en el input
      updateFileList();
    };
    function updateFileList() {
      fileList.innerHTML = "";
      for (let i = 0; i < selectedFiles.files.length; i++) {
        let file = selectedFiles.files[i];

        let listItem = document.createElement("li");
        listItem.className =
          "d-flex justify-content-between align-items-center p-2 border rounded mt-1";

        listItem.innerHTML = `
              ${file.name}
              <button type="button" class="btn btn-danger btn-sm ms-2" onclick="removeFile('${file.name}')">✖</button>`;
        fileList.appendChild(listItem);
      }
    }
  });

    document.addEventListener("DOMContentLoaded", function () {
    const btnAgregar = document.getElementById("btnAgregar");
    const documentBlock = document.getElementById("Block");
    const btnRevisar = document.getElementById("btnRevisar");
    btnAgregar.addEventListener("click", function () {
      Block.style.display = "none"; 
      document.querySelector('[name="itemId"]').value = "";
      document.querySelector('[name="fch_env"]').value = "";
      document.querySelector('[name="numExpediente"]').value = "";
      document.querySelector('[name="tp_documentacion"]').value = "";
      document.querySelector('[name="tp_medio"]').value = "";
      document.querySelector('[name="contenido"]').value = "";
      document.querySelector('[name="procedencia_sup"]').value = "";
      document.querySelector('[name="sub_procedencia"]').value = "";
    });
  });

    document.addEventListener("DOMContentLoaded", function () {
    const selectDocumento = document.getElementById("selectDocumento");
    const visorDocumento = document.getElementById("visorDocumento");

    // Mostrar el primero por defecto
    if (selectDocumento.options.length > 0) {
      visorDocumento.src = selectDocumento.value;
    }

    // Cambiar el PDF al seleccionar otro
    selectDocumento.addEventListener("change", function () {
      visorDocumento.src = this.value;
    });
  });
