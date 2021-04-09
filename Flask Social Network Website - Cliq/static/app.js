// enable/disable register form
const register_form_container = document.querySelector('.bg-effect');

function registerForm() {
    register_form_container.classList.toggle('active');
}


// clique card flip
const clique_card1 = document.getElementsByClassName('clique-card')[0];
const clique_card2 = document.getElementsByClassName('clique-card')[1];
const clique_card3 = document.getElementsByClassName('clique-card')[2];

if (typeof clique_card1 !== 'undefined' && typeof clique_card2 !== 'undefined' && typeof clique_card3 !== 'undefined') {
    clique_card1.addEventListener('click', () => {
        clique_card1.classList.toggle('flip');
    })

    clique_card2.addEventListener('click', () => {
        clique_card2.classList.toggle('flip');
    })

    clique_card3.addEventListener('click', () => {
        clique_card3.classList.toggle('flip');
    })
}


// confirm card selection
const confirmation_box = document.querySelector('.confirm-box');

if (confirmation_box !== null) {
    confirmation_box.classList.toggle('off');
}

const clique1_form = document.getElementById('clique1');
const clique2_form = document.getElementById('clique2');
const clique3_form = document.getElementById('clique3');

if (clique1_form !== null && clique2_form !== null && clique3_form !== null) {
    clique1_form.addEventListener('submit', confirm_box_show_for_clique1);
    clique2_form.addEventListener('submit', confirm_box_show_for_clique2);
    clique3_form.addEventListener('submit', confirm_box_show_for_clique3);
}

function confirm_box_show_for_clique1(submission) {
    clique_card1.classList.toggle('flip');
    submission.preventDefault();
    confirmation_box.classList.toggle('off');
}

function confirm_box_show_for_clique2(submission) {
    clique_card2.classList.toggle('flip');
    submission.preventDefault();
    confirmation_box.classList.toggle('off');
}

function confirm_box_show_for_clique3(submission) {
    clique_card3.classList.toggle('flip');
    submission.preventDefault();
    confirmation_box.classList.toggle('off');
}

function confirmSelection(answer) {
    if (answer) {
        if (clique_card1.classList.contains('flip')) {
            document.getElementById('clique1').submit();
        } else if (clique_card2.classList.contains('flip')) {
            document.getElementById('clique2').submit();
        } else if (clique_card3.classList.contains('flip')) {
            document.getElementById('clique3').submit();
        }
    } else {
        if (clique_card1.classList.contains('flip') && !clique_card2.classList.contains('flip') && !clique_card3.classList.contains('flip')) {
            clique_card1.classList.toggle('flip');
        } else if (!clique_card1.classList.contains('flip') && clique_card2.classList.contains('flip') && !clique_card3.classList.contains('flip')) {
            clique_card2.classList.toggle('flip');
        } else if (!clique_card1.classList.contains('flip') && !clique_card2.classList.contains('flip') && clique_card3.classList.contains('flip')) {
            clique_card3.classList.toggle('flip');
        } else if (clique_card1.classList.contains('flip') && clique_card2.classList.contains('flip') && !clique_card3.classList.contains('flip')) {
            clique_card1.classList.toggle('flip');
            clique_card2.classList.toggle('flip');
        } else if (clique_card1.classList.contains('flip') && !clique_card2.classList.contains('flip') && clique_card3.classList.contains('flip')) {
            clique_card1.classList.toggle('flip');
            clique_card3.classList.toggle('flip');
        } else if (!clique_card1.classList.contains('flip') && clique_card2.classList.contains('flip') && clique_card3.classList.contains('flip')) {
            clique_card2.classList.toggle('flip');
            clique_card3.classList.toggle('flip');
        } else if (clique_card1.classList.contains('flip') && clique_card2.classList.contains('flip') && clique_card3.classList.contains('flip')) {
            clique_card1.classList.toggle('flip');
            clique_card2.classList.toggle('flip');
            clique_card3.classList.toggle('flip');
        }

        confirmation_box.classList.toggle('off');
    }
}


// enable/disable clique1 post form
const clique1_add_post_button = document.getElementById('clique1-add-post');
const post_form = document.getElementById('clique1-post');

if (post_form !== null && clique1_add_post_button !== null) {
    post_form.addEventListener('dblclick', clique1PostForm);
}

function clique1PostForm() {
    post_form.classList.toggle('post-form-active');
    clique1_add_post_button.classList.toggle('clique1-remove-post-button');
}


// upload pfp & cover
const pfp_submit = document.getElementById('pfp');
const cover_submit = document.getElementById('cover');

const pfp_form = document.getElementById('pfp-form');
const cover_form = document.getElementById('cover-form');

if (pfp_submit !== null && cover_submit !== null && pfp_form !== null && cover_form !== null) {
    pfp_submit.onchange = () => {
        if (pfp_submit.value) {
            pfp_form.submit();
        }
    }

    cover_submit.onchange = () => {
        if (cover_submit.value) {
            cover_form.submit();
        }
    }
}


// niche dropdown
const niche_dropdown = document.getElementById('niche-dropdown');
const niche_options = document.getElementById('niche-options');

if (niche_dropdown !== null && niche_options !== null) {
    niche_dropdown.addEventListener('click', () => {
        niche_options.classList.toggle('niche-dropdown-drop');
    })
}


// add URL input field
const myprofile_form = document.getElementById('myprofile-form');
const reference_element = document.getElementById('save-myprofile-form');

let URL_count = 0;
let field_count = 0;

function add_url() {
    if (field_count < 3) {
        let newURL = document.createElement('input');
        newURL.setAttribute('type', 'text')
        newURL.setAttribute('name', `link${URL_count}`);
        URL_count++;
        newURL.setAttribute('placeholder', 'Website URL');
        newURL.setAttribute('class', 'url-input');
        newURL.setAttribute('style', 'width: 70%; height: 20px; padding: 5px;');
        myprofile_form.insertBefore(newURL, reference_element);
        field_count++;
    }
}


// clique 2 post window
const clique2_post_window = document.getElementById('clique2-post-upload');

function clique2_post() {
    clique2_post_window.classList.toggle('active');
}
