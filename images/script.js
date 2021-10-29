"use strict";

fetch("/getimages")
    .then(function (response) {
        return response.json();
    }).then(function (images_urls) {
        createContentsBox(images_urls['contents_urls']);
        createStylesBox(images_urls['styles_urls']);
})


const contentsBox = document.getElementById('contents-box');
const stylizedOutputZone = document.getElementById('stylized-output-zone');
const resultsBox = document.getElementById('results-box');
const stylesBox = document.getElementById("style-select-box");


const scrollBoxes = [contentsBox, stylizedOutputZone, resultsBox]
let boxScrollPct = 0;
let ignoreScroll = false;
scrollBoxes.forEach(scrollBox =>
    scrollBox.addEventListener('scroll', ({ target: t }) => {
    if (ignoreScroll) return;
    boxScrollPct = t.scrollLeft / (t.scrollWidth - t.clientWidth);
}));

let timeOutId = null;

window.addEventListener('resize', e => {
  ignoreScroll = true;
  scrollBoxes.forEach(scrollBox =>
      scrollBox.scrollLeft = boxScrollPct * (scrollBox.scrollWidth - scrollBox.clientWidth));
      clearTimeout(timeOutId);
      timeOutId = setTimeout(() => {
          ignoreScroll = false;
          }, 100);
});

function PXToVW(px) {
	return px * (100 / document.documentElement.clientWidth);
}

function fileToUrl(file, callback) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
        callback(reader.result)
    }
}

function getBackgroundImageUrl(element) {
    const backgroundImage = element.style.backgroundImage;
    return backgroundImage.slice(4, -1).replace(/"/g, "");
}

document.addEventListener('scroll', e => {

})

function downloadImage(url) {
    const thumbnailElements = document.body.querySelectorAll(".drop-zone__thumb")
    const contentFilename = thumbnailElements[0].dataset.label
    const link = document.createElement('a');
    link.href = url;
    link.download = contentFilename.split('.')[0] + '_stylized.jpg'
    document.body.appendChild(link);
    link.click();
    link.remove()
}


function setBackgroundImageByFile(element, file) {
    if (file.type.startsWith('image/')) { // TODO: what if not image?
        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onload = () => {
            element.style.backgroundImage = `url('${reader.result}')`;
        };
    }
}

function updateThumbnail(dropZoneElement, image, name) {
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

    if (typeof image === 'string') {
        thumbnailElement.dataset.label = name;
        thumbnailElement.style.backgroundImage = `url('${image}')`;
    } else {
        thumbnailElement.dataset.label = image.name;
        setBackgroundImageByFile(thumbnailElement, image)
    }
}


function getNewSizes(width, height) {
    const defaultSize = 30;
    const ratio =  width / height;
    let new_width, new_height;

    if (width < height) {
        new_width = defaultSize * ratio;
        new_height = defaultSize;
    } else {
        new_width = defaultSize;
        new_height = defaultSize / ratio;
    }
    return [new_width, new_height]
}


function displayPreview(styleElem, url) {
    const previewElem = document.createElement("div");
    previewElem.classList.add("preview");

    const offsets = styleElem.getBoundingClientRect();

    let image = new Image();

    image.onload = () => {
        let [new_width, new_height] = getNewSizes(image.width, image.height)

        previewElem.style.width = new_width + 'vw'
        previewElem.style.height = new_height + 'vw'

        previewElem.style.left = PXToVW(offsets.left) + 10 + 'vw'

        if (offsets.top < window.innerHeight / 2) {
            previewElem.style.top = PXToVW(offsets.top) - 8 + 'vw'
        } else {
            previewElem.style.top = PXToVW(offsets.top) - 16 + 'vw'
        }

        previewElem.style.backgroundImage = `url('${url}')`;

        previewElem.dataset.label = styleElem.dataset.label;
    }

    image.src = url;

    document.body.appendChild(previewElem)

    setTimeout(function () {
        previewElem.style.visibility = 'visible'
    }, 750)
}


function urlToFile(url, filename){
        return (fetch(url)
            .then(function(res){
                return res.arrayBuffer();})
                .then(function(buf){
                    return new File([buf], filename, { type: 'image/jpeg'}); })
        );
    }


function createContentImgElement(url, name) {
    const contentImgElement = document.createElement('div');
    contentImgElement.classList.add('image-element', 'content-img-elem');
    contentImgElement.style.backgroundImage = `url('${url}')`;

    contentImgElement.addEventListener("click", e => {
        const contentZone = document.getElementById('content-drop-zone');
        updateThumbnail(contentZone, url, name);

        document.querySelectorAll('.content-img-elem').forEach(elem => {
            elem.classList.remove('img-elem__onclick');
        })
        contentImgElement.classList.add("img-elem__onclick");
    })
    return contentImgElement;
}


function createContentsBox(urls) {
    for (let url of urls) {
        let name = url.split('/').pop();
        const contentImgElement = createContentImgElement(url, name);
        contentsBox.appendChild(contentImgElement);
        }

    contentsBox.addEventListener("wheel", e => {
             e.preventDefault();
             contentsBox.scrollLeft += e.deltaY;
        })
}

function createStylesBox(urls) {
    for (let url of urls) {
        let name = url.split('/').pop();
        const styleImgElement = createStyleImgElement(url, name);
        stylesBox.appendChild(styleImgElement);
    }
}

function createStyleImgElement(url, name) {
    const styleImgElement = document.createElement('div');
    styleImgElement.dataset.label = name;
    styleImgElement.classList.add('image-element', 'style-img-elem');
    styleImgElement.style.backgroundImage = `url('${url}')`;

    styleImgElement.addEventListener("mouseover", e => {
        displayPreview(styleImgElement, url)
    })

    styleImgElement.addEventListener("mouseout", e => {
        const previewElem = document.querySelector(".preview")
        document.body.removeChild(previewElem)
    })

    styleImgElement.addEventListener('click', e => {
        if (styleImgElement.classList.contains("img-elem__onclick")) {
            styleImgElement.classList.remove("img-elem__onclick")
            return;
        }
        styleImgElement.classList.add("img-elem__onclick")
    })
    return styleImgElement;
}

function insertUploadImages(smallDropZoneElement, files) {
    const imageBox = smallDropZoneElement.parentElement;
    for (let file of files) {
        if (file.type.startsWith('image/')) {
                fileToUrl(file, function (url) {
                    if (imageBox.id === "contents-box") {
                        let newImgElement = createContentImgElement(url, file.name)
                        imageBox.insertBefore(newImgElement, imageBox.childNodes[2])
                    } else {
                        let newImgElement = createStyleImgElement(url, file.name)
                        imageBox.insertBefore(newImgElement, imageBox.childNodes[2])
                    }
                })
        }
    }
}

document.querySelectorAll(".drop-zone").forEach(dropZoneElement => {
    const inputElement = dropZoneElement.querySelector('.drop-zone__input')
    const promptElement = dropZoneElement.querySelector(".drop-zone__prompt");

    dropZoneElement.addEventListener('click', e => {
        inputElement.click();
    })

    inputElement.addEventListener('change', e => {
        if (inputElement.files.length) {
            if (dropZoneElement.id === 'content-drop-zone') {
                updateThumbnail(dropZoneElement, inputElement.files[0]);
                const smallDropZone = contentsBox.querySelector('.drop-zone')

                insertUploadImages(smallDropZone, inputElement.files);
            } else {
                insertUploadImages(dropZoneElement, inputElement.files);
            }
        }
    })

    dropZoneElement.addEventListener("dragover", e => {
        e.preventDefault();
        promptElement.classList.add("drop-zone__prompt--over");
    })

    dropZoneElement.addEventListener("dragleave", e => {
        promptElement.classList.remove("drop-zone__prompt--over");
    })

    dropZoneElement.addEventListener("dragend", e => {
        promptElement.classList.remove("drop-zone__prompt--over");
    })

    dropZoneElement.addEventListener("drop", e => {
        e.preventDefault();
        if (e.dataTransfer.files.length) {
            if (dropZoneElement.id === 'content-drop-zone') {
                updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
            } else {
                insertUploadImages(dropZoneElement, e.dataTransfer.files);
            }
        }
        promptElement.classList.remove("drop-zone__prompt--over");
    });
})

function createResultElement() {
    let thumb = document.createElement("div")
    thumb.classList.add('result-thumb');
    return thumb;
}

function getImageSize(url) {
    return new Promise((resolve, reject) => {
        let img = new Image();
        img.onload = () => resolve([img.width, img.height]);
        img.onerror = () => reject();
        img.src = url;
    });
}

function selectAllStyles() {
    document.body.querySelectorAll('.style-img-elem').forEach(styleImgElement => {
        styleImgElement.classList.add("img-elem__onclick")
    })
}

function cancelSelectedStyles() {
    document.body.querySelectorAll('.style-img-elem').forEach(styleImgElement => {
        styleImgElement.classList.remove("img-elem__onclick")
    })
}

function scrollToLast() {
    const container = document.getElementById('stylized-output-zone');
    const tags = container.getElementsByTagName('div');
    container.scrollLeft = tags[tags.length-1].offsetLeft;
}

function scrollToIndex(index) {
    const resultThumbs = document.querySelectorAll('.result-thumb');
    resultThumbs[index].scrollIntoView()
}

async function sendRequest() {
    const stylizeBtn = document.getElementById('stylize-btn');
    stylizeBtn.classList.add('stylize-btn__onclick')

    const contentImageThumb = document.body.querySelectorAll('.drop-zone__thumb')[0];
    const contentImageUrl = getBackgroundImageUrl(contentImageThumb);

    // const [w, h] = await getImageSize(contentImageUrl);
    // const [new_w, new_h] = getNewSizes(w, h);

    const contentFile = await urlToFile(contentImageUrl, 'content.jpg')

    const styleBox = document.getElementById('style-select-box')
    const selectedStyleElements = styleBox.querySelectorAll('.img-elem__onclick')

    // TODO: check existing content and style image

    resultsBox.addEventListener("wheel", e => {
         e.preventDefault();
         resultsBox.scrollLeft += e.deltaY;
    })

    const resultThumbs = stylizedOutputZone.querySelectorAll('.result-thumb')
    if (resultThumbs) {
        resultThumbs.forEach(thumb => stylizedOutputZone.removeChild(thumb))
    }

    const styleImageElements = resultsBox.querySelectorAll('.image-element')
    if (styleImageElements) {
        styleImageElements.forEach( style => resultsBox.removeChild(style))
    }

    for (let selectedStyleElement of selectedStyleElements) {

        let styleImageUrl = getBackgroundImageUrl(selectedStyleElement)

        let styleFile = await urlToFile(styleImageUrl, 'style.jpg')

        let resultThumb = createResultElement()
        // thumb.style.minWidth = new_w + 'vw'
        // thumb.style.height = new_h + 'vw'

        const data = new FormData();
        data.append("content", contentFile);
        data.append("style", styleFile);

        await fetch('/', {
            method: 'POST',
            body: data
        }).then(response => {response.arrayBuffer()
            .then(stylizedImage => {
                const styleImg = selectedStyleElement.cloneNode(true)
                styleImg.classList.remove('style-img-elem', 'img-elem__onclick')
                styleImg.classList.add('content-img-elem', 'result-style-img')


                // styleImg.addEventListener('click', e => {
                //     const index = Array.from(styleImg.parentNode.children).indexOf(styleImg)
                //     scrollToIndex(index)
                // })

                resultsBox.appendChild(styleImg)

                const arrayBufferView = new Uint8Array(stylizedImage);
                const blob = new Blob([arrayBufferView], {type: 'image/jpeg'});
                const urlCreator = window.URL || window.webkitURL;
                const imageUrl = urlCreator.createObjectURL(blob);

                resultThumb.style.backgroundImage = `url('${imageUrl}')`;
                resultThumb.dataset.label = 'CLICK TO DOWNLOAD';

                stylizedOutputZone.appendChild(resultThumb);

                resultThumb.addEventListener('click', e => {
                    downloadImage(imageUrl);
                })

                scrollToLast()
            }).then( a => {
                document.body.querySelectorAll('.result-style-img').forEach(styleImgElement => {
                styleImgElement.addEventListener('click', e => {
                    const index = Array.from(styleImgElement.parentNode.children).indexOf(styleImgElement)
                    scrollToIndex(index)
                    })
                })
                }
            )
        })
    }

    stylizeBtn.classList.remove('stylize-btn__onclick');
}

