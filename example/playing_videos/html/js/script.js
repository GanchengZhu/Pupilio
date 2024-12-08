// Function to dynamically generate buttons
let videoDict = {};
let videosSelected = [];

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

function load() {
    if (window.location.search !== '') {
        const options = getQueryParam('options');
        const opts = options.split(',');

        for (const element of opts) {
            buttonClicked(element);
        }

        var buttons = document.querySelectorAll('.button-container a');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].onclick = null;
        }
    }
}

load();

function getSelectedButtonIndexes() {
    var selectedIndexes = [];
    var buttons = document.querySelectorAll('.button-container a');

    for (var i = 0; i < buttons.length; i++) {
        var button = buttons[i];

        if (button.classList.contains('button-selected')) {
            selectedIndexes.push(i + 1); // Add 1 to get 1-based index
        }
    }
    return selectedIndexes;
}

function getVideosSelected() {
    let videosSelected = [];
    let buttons = document.querySelectorAll('.button-container a');

    // 遍历按钮，获取选中按钮的 fname
    for (let i = 0; i < buttons.length; i++) {
        let button = buttons[i];
        if (button.classList.contains('button-selected')) {
            let fname = button.getAttribute('data-fname');  // 获取 fname
            videosSelected.push(fname);
        }
    }
    return videosSelected;

}

function buttonClicked(buttonNumber) {
    var button = document.querySelector('.button-container a:nth-child(' + buttonNumber + ')');
    var span = button.querySelector(".button-text");

    // 判断按钮是否已选中，添加或移除选中状态
    if (button.classList.contains('button-selected')) {
        button.classList.remove('button-selected');
    } else {
        button.classList.add('button-selected');
    }

    if (span.classList.contains('button-text-selected')) {
        span.classList.remove('button-text-selected');
    } else {
        span.classList.add('button-text-selected');
    }
}

function btnExitClicked() {
    pywebview.api.quit_all();
}

function btnNextClicked() {
    let videosSelected = getVideosSelected();
    if (videosSelected.length === 0) {
        alert("Please select at least 1 item.");
        return;
    }
    pywebview.api.set_test_item(videosSelected);
//    window.location.href = "par_info.html" + window.location.search;
      pywebview.api.start_task();
}

// Function to dynamically generate buttons from a list of names
function generateButtons(buttonDict) {
    const buttonContainer = document.getElementById('button-container');
    buttonContainer.innerHTML = '';  // Clear any existing buttons

    // If buttonNames list is empty, do not generate any buttons
    if (buttonDict.length === 0) {
        alert("没有查询到任何视频dict，请检查video文件夹下是否有视频");
        return;
    }

    let button_index = 0;
    for (let filename in buttonDict) {
        if (buttonDict.hasOwnProperty(filename)) {  // 确保是对象本身的属性
            const button = document.createElement('a');
            button.href = "#";
            button.classList.add('button');        // 为按钮添加 data-fname 属性，保存 fname
            button.setAttribute('data-fname', filename);
            button.setAttribute('onclick', `buttonClicked(${button_index + 1})`);  // Use 1-based index for onclick
            button_index += 1;

            const path = buttonDict[filename];
            console.log(`Filename: ${filename}, Path: ${path}`);
            const img = document.createElement('img');
            img.src = path; // Image source
            // img.alt = 'Button Icon';

            // Create the text element
            const span = document.createElement('span');
            span.classList.add('button-text');
            span.textContent = filename;  // Text content from the list

            // Append the image and text to the button
            button.appendChild(img);
            button.appendChild(span);

            // Append the button to the container
            buttonContainer.appendChild(button);
        }
    }

}

window.addEventListener('pywebviewready', function () {
    // 确保页面完全加载后再调用 pywebview API
    pywebview.api.get_video_dict().then(vDict => {
        // console.log(videoDict);  // 打印视频字典，检查数据是否正确
        videoDict = vDict;
        generateButtons(vDict);
    }).catch(error => {
        console.error("Error while fetching video dictionary:", error);
    });
})

// window.onbridge = function () {
//     // 确保页面完全加载后再调用 pywebview API
//     const videoDict = pywebview.api.get_video_dict();
//     console.log(videoDict);  // 打印视频字典
//     if (videoDict) {
//         generateButtons(videoDict.keys);  // 调用生成按钮的函数
//     } else {
//         console.error("Failed to retrieve video dictionary.");
//     }
// };