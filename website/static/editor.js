document.addEventListener("DOMContentLoaded", function () {
  var editor = document.getElementById("editor");
  var form = document.getElementById("form-edicao");
  var hidden = document.getElementById("conteudo_html");
  var preview = document.getElementById("preview");
  var toolbar = document.getElementById("toolbar");

  function sincronizar() {
    hidden.value = editor.innerHTML;
    preview.srcdoc = editor.innerHTML;
  }

  if (toolbar) {
    toolbar.addEventListener("click", function (ev) {
      var botao = ev.target.closest("button");
      if (!botao) return;
      ev.preventDefault();
      var cmd = botao.getAttribute("data-cmd");
      var val = botao.getAttribute("data-val");
      if (cmd === "createLink") {
        var url = window.prompt("URL do link:", "https://");
        if (url) document.execCommand(cmd, false, url);
      } else {
        document.execCommand(cmd, false, val || null);
      }
      editor.focus();
      sincronizar();
    });
  }

  if (editor) {
    var timer = null;
    editor.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(sincronizar, 300);
    });
    sincronizar();
  }

  if (form) {
    form.addEventListener("submit", function () {
      hidden.value = editor.innerHTML;
    });
  }
});
