(function($) {
  $(function() {
    function toggleChoiceOptions($questionBlock) {
      const select = $questionBlock.find('select[name$="-question_type"]');
      const qtype = select.val();
      const choiceBlock = $questionBlock.find('.nested-inline[data-inline-type="ChoiceOption"]');

      if (qtype === 'input') {
        // скрываем и отмечаем все формы как удалённые
        choiceBlock.hide();
        choiceBlock.find('.inline-related').each(function() {
          const deleteCheckbox = $(this).find('input[type="checkbox"][name$="-DELETE"]');
          if (deleteCheckbox.length) deleteCheckbox.prop('checked', true);
        });
      } else {
        choiceBlock.show();
        choiceBlock.find('.inline-related input[type="checkbox"][name$="-DELETE"]').prop('checked', false);
      }
    }

    function handleAllQuestions() {
      $('.djn-inline-form[data-inline-formset="questions"]').each(function() {
        toggleChoiceOptions($(this));
      });
    }

    // при изменении типа вопроса
    $(document).on('change', 'select[name$="-question_type"]', function() {
      const block = $(this).closest('.djn-inline-form');
      toggleChoiceOptions(block);
    });

    // при загрузке
    setTimeout(handleAllQuestions, 500);
  });
})(django.jQuery);
