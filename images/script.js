let styles_container = document.body.querySelector("#styles_container")


// function makeFileFromUrl(url, filename) {
//     fetch(url)
//                     .then(r => r.blob())
//                     .then(blobFile => new File([blobFile], filename, { type: "image/jpeg" }))
//                     .then(file => {return file;})
// }

function urlToFile(url, filename){
        return (fetch(url)
            .then(function(res){return res.arrayBuffer();})
            .then(function(buf){return new File([buf], filename,{type: 'image/jpeg'});})
        );
    }


for (let i = 1; i <= 20; i++) {
    let style_box = document.createElement('div');
    style_box.classList.add('style_box');
    let style_img_url = `images/default_style/default_style_${i}.jpg`;
    style_box.style.backgroundImage = `url(${ style_img_url })`;


    style_box.addEventListener("click", e => {
        let sel_style = document.getElementById('sel_style');

        let filename = `default_style_${i}.jpg`
        urlToFile(style_img_url, filename)
            .then(function(file) {updateThumbnail(sel_style, file)})
    })
    styles_container.appendChild(style_box)
}


function download(url) {
    let thumbnailElements = document.body.querySelectorAll(".drop-zone__thumb")
    let contentFilename = thumbnailElements[0].dataset.label

    let link = document.createElement('a');
    link.href = url;
    link.download = contentFilename.split('.')[0] + '_stylized.jpg'
    document.body.appendChild(link);
    link.click();
    console.log('CLICK')
    link.remove()
}



function getBackgroundImageUrl(element) {
    const backgroundImage = element.style.backgroundImage;
    return backgroundImage.slice(4, -1).replace(/"/g, "");
}




async function sendRequest() {
    // const content = document.getElementById('content').files[0];
    // const style = document.getElementById('style').files[0];


    let Thumbs = document.body.querySelectorAll('.drop-zone__thumb')
    let contentImageUrl = getBackgroundImageUrl(Thumbs[0])
    let styleImageUrl = getBackgroundImageUrl(Thumbs[1])


    let contentFile = await urlToFile(contentImageUrl, 'content.jpg')
    let styleFile = await urlToFile(styleImageUrl, 'style.jpg')


    // if (typeof content == "undefined" || typeof style == "undefined") return;

    let stylized = document.getElementById('stylized');
    let thumb = stylized.querySelector('.drop-zone__thumb')

    if (stylized.querySelector(".drop-zone__prompt")) {
        stylized.querySelector(".drop-zone__prompt").remove();
    }

    if (!thumb) {
        thumb = document.createElement("div")
        thumb.classList.add('drop-zone__thumb')
        stylized.appendChild(thumb)
    }

    thumb.style.backgroundImage = "url('images/loader.gif')"

    let data = new FormData();
    data.append("content", contentFile);
    data.append("style", styleFile);

    return await fetch('/', {
        method: 'POST',
        body: data
    }).then(response => {
        response.arrayBuffer().then(stylized_image => {

            let arrayBufferView = new Uint8Array(stylized_image);
            let blob = new Blob([arrayBufferView], {type: 'image/jpeg'});
            let urlCreator = window.URL || window.webkitURL;
            let imageUrl = urlCreator.createObjectURL(blob);

            thumb.style.backgroundImage = `url('${ imageUrl }')`;
            thumb.dataset.label = 'CLICK TO DOWNLOAD';


            thumb.addEventListener('click', e => {
                download(imageUrl);
            })
        })
    })
}


document.querySelectorAll(".drop-zone__input").forEach(inputElement => {
    const dropZoneElement = inputElement.closest(".drop-zone");

    dropZoneElement.addEventListener("click", e => {
        inputElement.click()
    })

    inputElement.addEventListener("change", e => {
        if (inputElement.files.length) {
            updateThumbnail(dropZoneElement, inputElement.files[0]);
        }
    })

    dropZoneElement.addEventListener("dragover", e => {
        e.preventDefault()
        dropZoneElement.classList.add("drop-zone--over");
    });

    ["dragleave", "dragend"].forEach(type => {
        dropZoneElement.addEventListener(type, e => {
            dropZoneElement.classList.remove("drop-zone--over");
        })
    })

    dropZoneElement.addEventListener("drop", e => {
        e.preventDefault();

        if (e.dataTransfer.files.length) {
            inputElement.files = e.dataTransfer.files;
            updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
        }

        dropZoneElement.classList.remove("drop-zone--over");
    });
});

function updateThumbnail(dropZoneElement, file) {

    const style = document.getElementById('style');


    let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");

    // First time - remove the prompt
    if (dropZoneElement.querySelector(".drop-zone__prompt")) {
        dropZoneElement.querySelector(".drop-zone__prompt").remove();
    }

    // First time - there is no thumbnail element, so let's create it
    if (!thumbnailElement) {
        thumbnailElement = document.createElement("div");
        thumbnailElement.classList.add("drop-zone__thumb");
        dropZoneElement.appendChild(thumbnailElement);
    }

    thumbnailElement.dataset.label = file.name;

    // Show thumbnail for image files

    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onload = () => {
            let image = new Image();
            image.src = reader.result;
            thumbnailElement.style.backgroundImage = `url('${reader.result}')`;
        };
    } else {
        thumbnailElement.style.backgroundImage = null;
    }

}

