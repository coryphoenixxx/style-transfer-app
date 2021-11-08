"use strict";


fetch('/getimages')
    .then(function (response) {
        return response.json();
    }).then(function (images_urls) {
        createContentsContainer(images_urls['contents_urls']);
        createStylesContainer(images_urls['styles_urls']);
})


const contentsContainer = document.getElementById('contents-container');
const stylesContainer = document.getElementById('styles-container');
const stylizedResultBox = document.getElementById('stylized-result-box');
const resultStylesContainer = document.getElementById('result-styles-container');
resultStylesContainer.addEventListener('wheel', e => {
         e.preventDefault();
         resultStylesContainer.scrollLeft += e.deltaY;
    })
const stylizeButton = document.getElementById('stylize-btn');
const contentDropZone = document.getElementById('content-drop-zone');


// Improve weird scrolling when resizing
const scrollBoxes = [contentsContainer, stylizedResultBox, resultStylesContainer]
let boxScrollPct = 0;
let ignoreScroll = false;
stylizedResultBox.classList.add('stylized-result-box__scroll')

scrollBoxes.forEach(scrollBox =>
    scrollBox.addEventListener('scroll', ({ target: t }) => {
    if (ignoreScroll) return;
    boxScrollPct = t.scrollLeft / (t.scrollWidth - t.clientWidth);
}));

let timeOutId = null;

window.addEventListener('resize', e => {
  ignoreScroll = true;
  stylizedResultBox.classList.remove('stylized-result-box__scroll')
  scrollBoxes.forEach(scrollBox =>
      scrollBox.scrollLeft = boxScrollPct * (scrollBox.scrollWidth - scrollBox.clientWidth));
      clearTimeout(timeOutId);
      timeOutId = setTimeout(() => {
          stylizedResultBox.classList.add('stylized-result-box__scroll')
          ignoreScroll = false;
          }, 100);
});


// Add event listeners to drop zones
document.querySelectorAll('.drop-zone').forEach(dropZoneElement => {
    const inputElement = dropZoneElement.querySelector('.drop-zone__input')
    const promptElement = dropZoneElement.querySelector('.drop-zone__prompt');

    dropZoneElement.addEventListener('click', e => {
        inputElement.click();
    })

    inputElement.addEventListener('change', e => {
        if (inputElement.files.length) {
            if (dropZoneElement.id === 'content-drop-zone') {
                // updateContentImgBox(inputElement.files[0]);
                const smallDropZone = contentsContainer.querySelector('.drop-zone')
                insertUploadImages(smallDropZone, inputElement.files);
            } else {
                insertUploadImages(dropZoneElement, inputElement.files);
            }
        }
    })

    dropZoneElement.addEventListener('dragover', e => {
        e.preventDefault();
        promptElement.classList.add('drop-zone__prompt--over');
    })

    dropZoneElement.addEventListener('dragleave', e => {
        promptElement.classList.remove('drop-zone__prompt--over');
    })

    dropZoneElement.addEventListener('dragend', e => {
        promptElement.classList.remove('drop-zone__prompt--over');
    })

    dropZoneElement.addEventListener('drop', e => {
        e.preventDefault();
        promptElement.classList.remove('drop-zone__prompt--over');
        if (e.dataTransfer.files.length) {
            if (dropZoneElement.id === 'content-drop-zone') {
                updateContentImgBox(e.dataTransfer.files[0]);
                const smallDropZone = contentsContainer.querySelector('.drop-zone')
                insertUploadImages(smallDropZone, e.dataTransfer.files);
            } else {
                insertUploadImages(dropZoneElement, e.dataTransfer.files);
            }
        }
    });
})


function PXToVW(px) {
	return px * (100 / document.documentElement.clientWidth);
}


function fileToUrl(file, callback) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
        callback(reader.result);
    }
}


function getBackgroundImageUrl(element) {
    const bgImgUrl = element.style.backgroundImage;
    return bgImgUrl.slice(4, -1).replace(/"/g, "");
}


function downloadImage(url, content_label, style_label) {
    const link = document.createElement('a');
    link.href = url;
    link.download = content_label.split('.')[0] + ' + ' + style_label.split('.')[0] + '.jpg'
    document.body.appendChild(link);
    link.click();
    link.remove()
}


function setBackgroundImageByFile(element, file) {
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onload = () => {
            element.style.backgroundImage = `url('${reader.result}')`;
        };
    }
}


function updateContentImgBox(image, name) {
    if (typeof image === 'string' || image.type.startsWith('image/')) {

        let contentImgBox = document.body.querySelector('.content-img-box');

        // First time - remove the prompt
        let contentDropZonePrompt = contentDropZone.querySelector('.drop-zone__prompt')
        if (contentDropZonePrompt) contentDropZonePrompt.remove();

        // First time - there is content box element, so let's create it
        if (!contentImgBox) {
            contentImgBox = document.createElement('div');
            contentImgBox.classList.add('content-img-box');
            contentDropZone.appendChild(contentImgBox);
        }

        if (typeof image === 'string') { // Image as DataURL
            contentImgBox.dataset.label = name;
            contentImgBox.style.backgroundImage = `url('${image}')`;
        } else { // Image as File obj
            if (image.type.startsWith('image/')) {
                contentImgBox.dataset.label = image.name;
                setBackgroundImageByFile(contentImgBox, image)
            }
        }
    } else {
        alert('Only images!');
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
    const preview = document.createElement('div');
    preview.classList.add('preview');

    const offsets = styleElem.getBoundingClientRect();

    const image = new Image();

    image.onload = () => {
        let [new_width, new_height] = getNewSizes(image.width, image.height)

        preview.style.width = new_width + 'vw'
        preview.style.height = new_height + 'vw'

        preview.style.left = PXToVW(offsets.left) + 10 + 'vw'

        if (offsets.top < window.innerHeight / 2) {
            preview.style.top = PXToVW(offsets.top) - 8 + 'vw'
        } else {
            preview.style.top = PXToVW(offsets.top) - 16 + 'vw'
        }

        preview.style.backgroundImage = `url('${url}')`;
        preview.dataset.label = styleElem.dataset.label;
    }
    image.src = url;

    document.body.appendChild(preview);

    setTimeout(function () {
        preview.style.visibility = 'visible'
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


function createContentThumbnail(url, name) {
    const thumb = document.createElement('div');
    thumb.classList.add('thumb', 'content-thumb' +
        '');
    thumb.style.backgroundImage = `url('${url}')`;

    thumb.addEventListener('click', e => {
        updateContentImgBox(url, name);

        document.querySelectorAll('.content-thumb' +
            '').forEach(elem => {
            elem.classList.remove('thumb__onclick');
        })
        thumb.classList.add('thumb__onclick');
    })
    return thumb;
}


function createContentsContainer(urls) {
    for (let url of urls) {
        const name = url.split('/').pop();
        const thumb = createContentThumbnail(url, name);
        contentsContainer.appendChild(thumb);
    }

    contentsContainer.addEventListener('wheel', e => {
        e.preventDefault();
        contentsContainer.scrollLeft += e.deltaY;
    })
}

function createStylesContainer(urls) {
    for (let url of urls) {
        let name = url.split('/').pop();
        const styleImgElement = createStyleThumbnail(url, name);
        stylesContainer.appendChild(styleImgElement);
    }
}

function createStyleThumbnail(url, name) {
    const thumb = document.createElement('div');
    thumb.dataset.label = name;
    thumb.classList.add('thumb', 'style-thumb');
    thumb.style.backgroundImage = `url('${url}')`;

    thumb.addEventListener('mouseover', e => {
        displayPreview(thumb, url);
    })

    thumb.addEventListener('mouseout', e => {
        const previewElem = document.querySelector('.preview');
        document.body.removeChild(previewElem);
    })

    thumb.addEventListener('click', e => {
        if (thumb.classList.contains('thumb__onclick')) {
            thumb.classList.remove('thumb__onclick');
            return;
        }
        thumb.classList.add('thumb__onclick');
    })
    return thumb;
}

function insertUploadImages(smallDropZoneElement, files) {
    const imageContainer = smallDropZoneElement.parentElement;
    for (let file of files) {
        if (file.type.startsWith('image/')) {
                fileToUrl(file, function (url) {
                    if (imageContainer.id === 'contents-container') {
                        let newImgElement = createContentThumbnail(url, file.name)
                        newImgElement.click()
                        imageContainer.insertBefore(newImgElement, imageContainer.childNodes[2])
                    } else {
                        let newImgElement = createStyleThumbnail(url, file.name)
                        imageContainer.insertBefore(newImgElement, imageContainer.childNodes[2])
                    }
                })
        } else {
            alert('Only images!');
        }
    }
}

function createResultImgBox() {
    const box = document.createElement('div');
    box.classList.add('result-img-box');
    return box;
}

function selectAllStyles() {
    document.body.querySelectorAll('.style-thumb').forEach(styleImgElement => {
        styleImgElement.classList.add('thumb__onclick');
    })
}

function cancelSelectedStyles() {
    document.body.querySelectorAll('.style-thumb').forEach(styleImgElement => {
        styleImgElement.classList.remove('thumb__onclick');
    })
}

function scrollToLast() {
    const resultThumbs = stylizedResultBox.getElementsByTagName('div');
    const resultStyles = resultStylesContainer.getElementsByTagName('div');
    stylizedResultBox.scrollLeft = resultThumbs[resultThumbs.length-1].offsetLeft;
    resultStylesContainer.scrollLeft = resultStyles[resultStyles.length-1].offsetLeft;
}

function scrollToIndex(index) {
    const resultThumbs = document.querySelectorAll('.result-img-box');
    resultThumbs[index].scrollIntoView()
}

function upgradeResultStyleThumb(resultStyleThumb) {
    resultStyleThumb.classList.remove('style-thumb', 'thumb__onclick');
    resultStyleThumb.classList.add('content-thumb', 'result-style-thumb');

    resultStylesContainer.appendChild(resultStyleThumb);

    resultStyleThumb.addEventListener('click', e => {
            const resultStyleThumbs = document.body.querySelectorAll('.result-style-thumb');
            resultStyleThumbs.forEach(thumb => {
                thumb.classList.remove('result-style-thumb__onclick');
            })
            const index = Array.from(resultStyleThumb.parentNode.children).indexOf(resultStyleThumb);
            scrollToIndex(index);
            resultStyleThumb.classList.add('result-style-thumb__onclick');
        })

    return resultStyleThumb;
}

async function sendRequest() {
    // Check for content and style images
    const contentImgBox = document.body.querySelector('.content-img-box');
    if (!contentImgBox) { alert('Select content!'); return; }

    const selectedStyleElements = stylesContainer.querySelectorAll('.thumb__onclick');
    if (selectedStyleElements.length === 0) { alert('Select style!'); return; }

    // Clear result section
    const resultThumbs = stylizedResultBox.querySelectorAll('.result-img-box');
    if (resultThumbs) { resultThumbs.forEach(thumb => stylizedResultBox.removeChild(thumb)); }

    const resultStyles = resultStylesContainer.querySelectorAll('.thumb')
    if (resultStyles) { resultStyles.forEach( style => resultStylesContainer.removeChild(style)); }

    // Show style thumbnails under stylized
    if (selectedStyleElements.length > 1) {
        resultStylesContainer.classList.add('result-styles-container__display');
    } else {
        resultStylesContainer.classList.remove('result-styles-container__display');
    }

    const contentImgUrl = getBackgroundImageUrl(contentImgBox);
    const contentFile = await urlToFile(contentImgUrl, 'content.jpg');
    stylizeButton.classList.add('stylize-btn__onclick');

    for (let selectedStyleElement of selectedStyleElements) {
        const styleImageUrl = getBackgroundImageUrl(selectedStyleElement);
        const styleFile = await urlToFile(styleImageUrl, 'style.jpg');
        const resultImageBox = createResultImgBox();

        const data = new FormData();
        data.append('content', contentFile);
        data.append('style', styleFile);

        await fetch('/', {
            method: 'POST',
            body: data
        }).then(response => {response.arrayBuffer()
            .then(stylizedImageObj => {
                // Image object -> data url
                const arrayBufferView = new Uint8Array(stylizedImageObj);
                const blob = new Blob([arrayBufferView], {type: 'image/jpeg'});
                const urlCreator = window.URL || window.webkitURL;
                const stylizedImageUrl = urlCreator.createObjectURL(blob);

                resultImageBox.style.backgroundImage = `url('${stylizedImageUrl}')`;
                resultImageBox.dataset.label = 'CLICK TO DOWNLOAD';

                stylizedResultBox.appendChild(resultImageBox);

                resultImageBox.addEventListener('click', e => {
                    downloadImage(stylizedImageUrl, contentImgBox.dataset.label, selectedStyleElement.dataset.label);
                })

                // Copy selected style thumb
                let resultStyleThumb = selectedStyleElement.cloneNode(true);
                resultStyleThumb = upgradeResultStyleThumb(resultStyleThumb);
                resultStyleThumb.click();

                // Change style of prev thumb
                if (resultStylesContainer.children.length > 1) {
                    resultStylesContainer.children[resultStylesContainer.children.length - 2]
                        .classList.remove('result-style-thumb__onclick');
                }

                scrollToLast();
            })
        })
    }
    resultStylesContainer.style.transition = 'none'
    stylizeButton.classList.remove('stylize-btn__onclick');
}

