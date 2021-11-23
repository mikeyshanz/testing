const chromium = require('chrome-aws-lambda');


// Send keys to an element on the page
async function sendKeys(page, identifier, text){
    console.log(`Sending keys: ${text} to selector ${identifier}`);
    try {
        await page.type(identifier, text);
        return true;
    }catch(err){
        console.log(err.message);
        return false;
    }  
}

// Get the value of an element on a page
async function getValue(page, identifier){
    console.log(`Getting Value ${identifier}`);
    try {
        const list = await page.evaluateHandle((identifier) => {
            return Array.from(document.querySelectorAll(identifier)).map(i => i.innerText);
          }, identifier);
          let data = await list.jsonValue();
          return data;
    }catch(err){
        console.log(err.message);
        return false;
    }  
}

// Click a button or an element
async function clickButton(page, identifier, isNavigation){
    console.log(`Clicking Button: ${identifier}`);
    try{
        if (isNavigation){
            await Promise.all([
                page.waitForNavigation(),
                page.click(identifier)
              ]);
              await page.waitFor(3000);
        }else{
            await Promise.all([
                page.waitForNavigation({timeout: 1500}),
                page.click(identifier)
              ]);
        }
        return true;
    }catch(err){ 
        if (!isNavigation && err.message === 'Navigation timeout of 1500 ms exceeded'){
            return true;
        }else {
            console.log(err.message);
            return false;
        }
    }
}

// Check if there are any elements with the given query selector value
async function doesElementExist(page, identifier){
    console.log(`Checking if Element: ${identifier} exists`);
    try{
        const list = await page.evaluateHandle((identifier) => {
            return Array.from(document.querySelectorAll(identifier)).map(i => i.textContent);
          }, identifier);
          let data = await list.jsonValue();
        var dataLength = 0;
        for (var key in data){
            dataLength ++;
        }
        if (dataLength > 0){
            return true;
        }else {
            return false;
        }
    }catch(err){
        console.log(err.message);
        return false;
    }
}

// Get all inner texts of elements of a given tag
async function getTagElementsValue(page, identifier){
    console.log(`Getting Values from Tag: ${identifier}`);
    try {
        const list = await page.evaluateHandle((identifier) => {
            return Array.from(document.getElementsByTagName(identifier)).map(i => i.innerText);
          }, identifier);
          let data = await list.jsonValue();
          return data;
    }catch(err){
        console.log(err.message);
        return false;
    }
}

async function isElementVisible(page, identifier){
    console.log(`Checking if Element: ${identifier} is visible`);
    try{
        let data = await page.evaluate((identifier) => { 
            return window.getComputedStyle(document.querySelector(identifier)).display;
        }, identifier);
        if (data === "none"){
            return false;
        }else {
            return true;
        }
    }catch(err){
        console.log(err.message);
        return false;
    }
}

async function parseCommand(page, dictIn) {
    let url = dictIn['url'];
    if (url !== undefined){
        var currentUrl = await page.url();
        if (currentUrl !== url){
            console.log(`Navigating to ${url}...`);
            await page.goto(url);
        }
    }
    var caseOptions = ['getValue', 'getTagValues', 'doesElementExist', 'clickButton', 'sendKeys', 'isElementVisible'];
    var results = `Bad Request Type! Options are: ${caseOptions}`;
    switch(dictIn['type']){
        case 'getValue':
            results = await getValue(page, dictIn['identifier']);
            break;
        case 'getTagValues':
            results = await getTagElementsValue(page, dictIn['identifier']);
            break;
        case 'doesElementExist':
            results = await doesElementExist(page, dictIn['identifier']);
            break;
        case 'clickButton':
            if (dictIn['isNavigation'] !== undefined){
                var isNavigation = dictIn['isNavigation'];
            }else {
                var isNavigation = false;
            }
            results = await clickButton(page, dictIn['identifier'], isNavigation);
            break;
        case 'sendKeys':
            results = await sendKeys(page, dictIn['identifier'], dictIn['keys']);
            break;
        case 'isElementVisible':
            results = await isElementVisible(page, dictIn['identifier']);
            break;
    }
    return results;
}

async function parseCommands(page, commandList){
    var outputList = [];
    for (var i=0; i < commandList.length; i++){
        var output = await parseCommand(page, commandList[i]);
        outputList.push(output);
    }
    return outputList;
}
// Initiate the Browser object
async function startBrowser(){
    let browser;
    try {
        console.log("Opening the browser......");
        browser = await chromium.puppeteer.launch({
          args: chromium.args,
          defaultViewport: chromium.defaultViewport,
          executablePath: await chromium.executablePath,
          headless: chromium.headless,
          ignoreHTTPSErrors: true,
        });
    } catch (err) {
        console.log("Could not create a browser instance => : ", err);
    }
    return browser;
}

exports.handler = async (event, context, callback) => {
    let browser = await startBrowser();
    let page = await browser.newPage();
    try{
        var commandList = JSON.parse(event['body']);   
    }catch(err){
        return {'statusCode': 401, 'body': JSON.stringify('Bad Request JSON!')};
    }
    try{
        var responseList = await parseCommands(page, commandList);
    }catch(err){
        return {'statusCode': 500, 'body': JSON.stringify(err.message)};
    }
    return {'statusCode': 200, 'body': JSON.stringify(responseList)};
};
