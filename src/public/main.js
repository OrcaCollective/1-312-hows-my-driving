$(function() {
  $('#main_form').submit(function(event) {
    event.preventDefault();
    var license = $('input').val();
    $.post('/license-lookup?' + $.param({'license': license}), function(data) {
      console.log('Data: ' + data);
      $('#license').html(data);
      $('input').val('');
      $('input').focus();
    });
  });

});
