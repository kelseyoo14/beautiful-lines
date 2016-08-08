// Save Pinterest Board to db -----------------------------------------------------------

function saveBoard(evt) {
    evt.preventDefault();
    $('body').css('cursor', 'wait');
    $('#pause-user-modal-save').modal('show');

    formInputs = {
        'board_url': $(this).find('.board-url').val()
    };

    $.post('/save_board',
            formInputs,
            successMessage);

    function successMessage(result) {
        $('#non-reload-success-message').text('Your board has been successfully saved.');
        $('#non-reload-alert-container').css('display', 'block');
        $('body').css('cursor', 'default');
        $('#pause-user-modal-save').modal('hide');
    }
}


$(".save-pinterest-board").on('submit', saveBoard);


// Delete Board from db -----------------------------------------------------------

function deleteBoard(evt) {
    evt.preventDefault();
    $('body').css('cursor', 'wait');
    $('#pause-user-modal-delete').modal('show');

    formInputs = {
        'board_id': $(this).find('.delete-board-id').val()
    };

    $.post('/delete_board.json',
            formInputs,
            reloadPage);

    function reloadPage() {
        $('body').css('cursor', 'default');
        location.reload(true);
        // $(document).ready(function () {
        //     $('#success-message').text('Your board has been successfully deleted.');
        //     $('.alert-container').css('display', 'block');
        // });
    }
}


$(".delete-board-from-db").on('submit', deleteBoard);

// Save Image to db ------------------------------------------------------------

// Pass pinid and imageid to #saveImageModal form hidden inputs,
// to pass to '/save_image' route when form is submitted
$(".save-button").click(function() {
    var pinid = $(this).data('pinid');
    var imageid = $(this).data('imageid');

    $("#hidden-pinid").val(pinid);
    $("#hidden-imageid").val(imageid);
});


function saveToBoard(evt) {
    evt.preventDefault();
    $('body').css('cursor', 'wait');

    var formInputs = {
        'board': $('input[name="board-to-save-image"]:checked').val(),
        'pin_id': $('#hidden-pinid').val(),
        'image_id': $('#hidden-imageid').val()
    };

    $.post('/save_image.json',
            formInputs,
            successMessage);

    function successMessage(result) {
        $('#non-reload-success-message').text('Your image has been successfully saved.');
        $('#non-reload-alert-container').css('display', 'block');
        $('body').css('cursor', 'default');
        $("#saveImageModal").modal("hide");
    }
}

$("#save-image-to-board").on('submit', saveToBoard);

// FIX ME
// Delete image from db ------------------------------------------------------------

function reloadPage(result) {
    $('body').css('cursor', 'default');
    location.reload(true);
}

function deleteFromBoard(evt) {
    evt.preventDefault();
    $('body').css('cursor', 'wait');

    var formInputs = {
        'board_id': $(this).find('.board_id').val(),
        'image_id': $(this).find('.image_id').val()
    };

    $.post('/delete_image.json',
            formInputs,
            reloadPage
            );
}

$(".delete-image-from-board").on('submit', deleteFromBoard);


// Start and run study session ------------------------------------------------------

function startStudy(evt) {
    evt.preventDefault();

    var time_intervals = $('#time-intervals').val();
    var num_of_images = $('#num-of-images').val();
    var formInputs = {
        'board_id': $('#board_id').val()
    };

    // shuffle list of image urls
    function shuffle_images(images) {
        // var i = 0;
        var j = 0;
        var temp;

        for (var i = images.length - 1; i > 0; i--) {
            j = Math.floor(Math.random() * (i + 1));
            temp = images[i];
            images[i] = images[j];
            images[j] = temp;
        }
        
        return images;
    }

    // get images from database through /study_images route
    function get_images() {
        $.post('/study_images.json',
            formInputs,
            parse_results);

        function parse_results(result) {
            var original_images = JSON.parse(result);
            var images = original_images.slice();

            shuffled_images = shuffle_images(images);

            // if user wants to study more images than exist in board, 
            // reshuffle images and add to shuffled_images list
            while (num_of_images > shuffled_images.length) {
                var more_shuffled_images = shuffle_images(original_images);
                shuffled_images.push.apply(shuffled_images, more_shuffled_images);
            }

            $('.stop-study').on('click', function() {
                clearTimeout(study_timeout);
                $('#study-modal').modal('hide');
            });

            var count_images = 0;
            var study_timeout;
            $('#study-modal').modal('show');
            function displayImages(shuffled_images, count_images) {
                $('#study-modal-image').attr('src', shuffled_images[count_images]);

                if (count_images < num_of_images) {
                    study_timeout = setTimeout(function() {
                        // recursively call displayImages to loop through images in shuffled list
                        displayImages(images, count_images+1);
                    }, time_intervals * 1000);
                } else {
                    $('#study-modal').modal('hide');
                }
            }
            // Start displaying images
            displayImages(shuffled_images, count_images);
        }
    }
    get_images();
}

// When user clicks on 'Start Drawing' button, start displaying images
$('#study-form').on('submit', startStudy);

$('#study-modal .modal-body').height($('#study-modal-image').height());

// Image Zoom Modal -------------------------------------------------------------

$('body').on('click', 'img', function() {
    var pinsrc = $(this).attr('src');
    $('#zoomed-image').attr('src', pinsrc);
    $('#zoom-modal').modal('show');
});

$(document).ready(function () {
    $('#zoom-modal .modal-body').height($('#zoomed-image').height());
    $('#zoom-modal .modal-body').width($('#zoomed-image').width());
});



// Edit Board -------------------------------------------------------------------

function showEditBoardForm(evt) {
    evt.preventDefault();
    console.log('function started');
    var title = $(this).find('.new-board-title').val();
    var image_url = $(this).find('.new-image-url').val();
    var description = $(this).find('.new-board-description').val();
    var board_id = $(this).find('.board-id').val();

    $('#edit-board-title').val(title);
    $('#edit-board-image').val(image_url);
    $('#edit-board-description').val(description);
    $('#board-id-to-edit').val(board_id);

    $('#edit-board-modal').modal('show');
}


$('.edit-board-form').on('submit', showEditBoardForm);


function editBoard(evt) {
    evt.preventDefault();
    $('body').css('cursor', 'wait');

    function reloadHomePage() {
        $('body').css('cursor', 'default');
        location.reload(true);
    }

    var formInputs = {'new_board_title': $(this).find('#edit-board-title').val(),
                      'new_image_url': $(this).find('#edit-board-image').val(),
                      'new_board_description': $(this).find('#edit-board-description').val(),
                      'board_id':$(this).find('#board-id-to-edit').val()};

    $.post('/edit_board.json',
            formInputs,
            reloadHomePage);
}

$('#edit-board-modal-form').on('submit', editBoard);


// Edit Image -------------------------------------------------------------------

function showEditImageForm(evt) {
    evt.preventDefault();
    console.log('function started');
    var description = $(this).find('.new-image-description').val();
    var image_id = $(this).find('.image-id').val();

    $('#edit-image-description').val(description);
    $('#image-id-to-edit').val(image_id);

    $('#edit-image-modal').modal('show');
}

$('.edit-image-form').on('submit', showEditImageForm);


function editImage(evt) {
    evt.preventDefault();
    $('body').css('cursor', 'wait');

    function reloadBoardPage() {
        $('body').css('cursor', 'default');
        location.reload(true);
    }

    var formInputs = {'new_image_description': $(this).find('#edit-image-description').val(),
                      'image_id':$(this).find('#image-id-to-edit').val()};

    $.post('/edit_image.json',
            formInputs,
            reloadBoardPage);
}

$('#edit-image-modal-form').on('submit', editImage);



// Display Form for Creating a New Board
$('#new-board-button').on('click', function() {
    $('#create-board-modal').modal("show");
});

// Display Form for Creating a New Image
$('#new-image-button').on('click', function() {
    $('#create-image-modal').modal("show");
});



// Change Search 

$('#search-bl-form').on('click', function() {
    $('#search-form').attr('action', '/search_bl');
    $('#search-form-input').attr('placeholder', 'Search Beautiful Lines');
});

$('#search-user-form').on('click', function() {
    $('#search-form').attr('action', '/search_user');
    $('#search-form-input').attr('placeholder', 'Search Your Images');

});


// Making Navbar Responsive and Aligned

$(window).on('resize', function navbarUpdate () {
    var viewportWidth = $(window).width();
    if (viewportWidth < 768) {
        $(".nav-list-items").removeClass('pull-right');
    } else {
        $(".nav-list-items").addClass('pull-right');
    }
});


// Make image-container width equal to image width

$(document).ready(function() {
    var imageWidth = $('.pin-image').width();
    $('.image-container').width(imageWidth);
});

// Board/Image buttons display on hover

$('.board').hover(function() {
    $(this).find('.board-actions').css('visibility', 'visible');
}, function() {
    $(this).find('.board-actions').css('visibility', 'hidden');
})


$('.image-container').hover(function() {
    $(this).find('.image-actions').css('visibility', 'visible');
}, function() {
    $(this).find('.image-actions').css('visibility', 'hidden');
})




