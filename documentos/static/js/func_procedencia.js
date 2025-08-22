
$(document).ready(function () {
    $("#disp_procedencia_sup").change(function () {
      var procedencia_id = $(this).val();
      var url = loadSubProcedenciasUrl;
      alert("entro");
      if (procedencia_id) {
        $.ajax({
          url: url,
          data: { procedencia_id: procedencia_id },
          success: function (data) {
            $("#disp_sub_procedencia").empty(); // Limpiar el combobox de modelos
            $("#disp_sub_procedencia").append(
              '<option value="" selected >Selecciona una procedencia</option>'
            );
            $.each(data, function (key, value) {
              $("#disp_sub_procedencia").append(
                '<option value="' +
                  value.id +
                  '">' +
                  value.descrip_corta +
                  "</option>"
              );
            });
          },
        });
      } else {
        $("#disp_sub_procedencia").empty();
        $("#disp_sub_procedencia").append(
          '<option value="">Selecciona una procedencia</option>'
        );
      }
    });
  });

  
$(document).ready(function () {
    $("#procedencia_sup").change(function () {
      var procedencia_id = $(this).val();
      var url = loadSubProcedenciasUrl;
      if (procedencia_id) {
        $.ajax({
          url: url,
          data: { procedencia_id: procedencia_id },
          success: function (data) {
            $("#sub_procedencia").empty(); // Limpiar el combobox de modelos
            $("#sub_procedencia").append(
              '<option value="" selected >Selecciona una procedencia</option>'
            );
            $.each(data, function (key, value) {
              $("#sub_procedencia").append(
                '<option value="' +
                  value.id +
                  '">' +
                  value.descrip_corta +
                  "</option>"
              );
            });
          },
        });
      } else {
        $("#sub_procedencia").empty();
        $("#sub_procedencia").append(
          '<option value="">Selecciona una procedencia</option>'
        );
      }
    });
  });