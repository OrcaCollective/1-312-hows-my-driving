$(function() {
  $('#main_form').submit(function(event) {
    event.preventDefault();
    var badge = $('input').val();
    $.post('/badge-lookup?' + $.param({'badge': badge}), function(data) {
      console.log('Data: ' + data);
      $('#badge').html(data);
      $('input').val('');
      $('input').focus();
    });
  });

});
