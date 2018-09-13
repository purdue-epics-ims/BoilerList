//------------------ organization searching ----------------

// update <select> element with #org_selected items
function update_select() {
    $('#id_organizations').val($("#org_selected").children().map(function(){ return $(this).attr('org_pk') }))
}

 //select an org
function select_org(button){
    $(button).removeClass("btn-success")
    $(button).addClass("btn-danger")
    $(button).attr("onclick","deselect_org(this);")
    $(button).html("Remove")

    elem = $(button).closest('.org_item')
    $(elem).appendTo("#org_selected")
    update_select()
}

function deselect_org(button){
    $(button).removeClass("btn-danger")
    $(button).addClass("btn-success")
    $(button).attr("onclick","select_org(this);")
    $(button).html("Add")

    elem = $(button).closest('.org_item')
    $(elem).appendTo("#org_results")
    update_select()
}


//handle tag click action
$('#org_results').find('.category').click(function(){
    $('#search').val($(this).text())
    filter()
})

//filter org_results list by name and category
function filter(){
    console.log('keypress')
    var search_text = $('#search').val().toLowerCase();

    $('#org_results').find('.org_item').each(function(i,org_item){
        var show = 0;
        //check for match in each category, highlight match
        console.log($(org_item).find('.organization'))
        $(org_item).find('.category').each(function(i,cat_item){
            if (search_text && $(cat_item).text().search(search_text) >=0) {
                show = 1;
                $(cat_item).removeClass('label-default')
                $(cat_item).addClass('label-warning')
            }
            else {
                $(cat_item).removeClass('label-warning')
                $(cat_item).addClass('label-default')
            }
        })

        //check for match in name
        var name_str = $(org_item).children('.org_name').text().toLowerCase();
        if (name_str.search(search_text) >= 0){
            show = 1
        }

        //hide or show
        if (show) {
            $(org_item).show()
        }
        else {
            $(org_item).hide()
        }
    })
}

//filter for every keypress
$('#search').keyup(function() {
    filter()
});

