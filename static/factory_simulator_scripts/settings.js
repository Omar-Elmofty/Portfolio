// Function to display the settings drawer
function showSettingsDrawer(e, obj) {
    var node = obj.part;
    const settingsDrawer = document.getElementById('settings-drawer');
    // Clear previous settings
    settingsDrawer.innerHTML = '';

    // Generate and display settings based on the selected element
    if (node.data.type === 'Source') {
        // Code to generate and display source settings
        // ...

    } else if (node.data.type === 'Sink') {
        // Code to generate and display sink settings
        // ...

    } else if (node.data.type === 'Process') {
        createProcessSettings(settingsDrawer, node);
    } else if (node.data.type === 'Combinor') {
        // Code to generate and display combinator settings
        // ...

    } else if (node.data.type === 'Separator') {
        // Code to generate and display separator settings
        // ...

    } else if (node.data.type === 'Buffer') {
        // Code to generate and display buffer settings
        // ...

    } else {
        // Handle unknown element type
        settingsDrawer.innerHTML = '<p>Unknown element type</p>';
    }

    // Show the settings drawer
    settingsDrawer.classList.add("open");

}

function createProcessSettings(settingsDrawer, node) {
    // Code to generate and display process settings
    const processName = (node.data.processName ? node.data.processName : node.key);
    const cycleTime = (node.data.ct ? node.data.ct : '10');
    const ttr_dist = (node.data.ttr_dist ? node.data.ttr_dist : { type: 'EXPONENTIAL', params: { mean: '10' } });
    const tbf_dist = (node.data.tbf_dist ? node.data.tbf_dist : { type: 'EXPONENTIAL', params: { mean: '10' } });

    settingsDrawer.innerHTML = '<h3>Settings</h3>' +
        '<button id="drawer-close-button" class="close-button">X</button>' +
        '<label>Process Name:</label>' +
        '<input type="text" name="processName" value="' + processName + '"><br>' +
        '<label>Cycle Time:</label>' +
        '<input type="number" name="cycleTime" step="0.01" min="0" value="' + cycleTime + '"><br>' +
        '<br>' +
        createDowntimeDistributionSettings(ttr_dist.type, tbf_dist.type) +
        '<br>' +
        '<button id="drawer-save-button">Save</button>';

    createDropDownListener('ttr-distribution-settings', 'ttr-distribution-type', ttr_dist.type, ttr_dist.params, node);
    createDropDownListener('tbf-distribution-settings', 'tbf-distribution-type', tbf_dist.type, tbf_dist.params, node);

    const saveButton = document.getElementById('drawer-save-button');
    saveButton.addEventListener('click', () => saveSettings(node));

    const closeButton = document.getElementById('drawer-close-button');
    closeButton.addEventListener('click', () => {
        // Close the settings drawer
        const settingsDrawer = document.getElementById('settings-drawer');
        settingsDrawer.classList.remove("open");
    });
}

function createDowntimeDistributionSettings(ttr_dist_type, tbf_dist_type) {
    return '<label>Time to Repair Distribution:</label>' +
        '<br>' +
        '<select name="ttr-distribution-type">' +
        createDistributionOptions(ttr_dist_type) +
        '</select>' +
        '<div id="ttr-distribution-settings"></div>' +
        '<br>' +
        '<label>Time Between Failures Distribution:</label>' +
        '<br>' +
        '<select name="tbf-distribution-type">' +
        createDistributionOptions(tbf_dist_type) +
        '</select>' +
        '<div id="tbf-distribution-settings"></div>';
}

function createDistributionOptions(dist_type) {
    return '<option value="EXPONENTIAL" ' + (dist_type === 'EXPOENTIAL' ? 'selected' : '') + '>Exponential</option>' +
        '<option value="CONSTANT" ' + (dist_type === 'CONSTANT' ? 'selected' : '') + '>Constant</option>' +
        '<option value="NORMAL" ' + (dist_type === 'NORMAL' ? 'selected' : '') + '>Normal</option>' +
        '<option value="ERLANG" ' + (dist_type === 'ERLANG' ? 'selected' : '') + '>Erlang</option>' +
        '<option value="UNIFORM" ' + (dist_type === 'UNIFORM' ? 'selected' : '') + '>Uniform</option>';
}

function createDropDownListener(div_id, select_id, dist_type, dist_params, node) {
    // Handle additional settings based on the selected distribution type
    const distributionSettings = document.getElementById(div_id);
    // Clear previous settings
    distributionSettings.innerHTML = '';
    distributionSettings.innerHTML = getDistributionSettings(dist_type, dist_params, div_id + '-');
    // Add event listener to distribution dropdown
    const distributionDropdown = document.querySelector('select[name="' + select_id + '"]');
    distributionDropdown.addEventListener('change', function () {
        const selectedDistribution = this.value;
        const updatedDistributionSettings = getDistributionSettings(selectedDistribution, node.data, div_id + '-');
        const distributionSettings = document.getElementById(div_id);
        distributionSettings.innerHTML = '';
        distributionSettings.innerHTML = updatedDistributionSettings;
    });
}

// Function to generate the additional distribution settings HTML based on the selected distribution type
function getDistributionSettings(distributionType, dist_params, prefix) {
    let settingsHTML = '';

    if (distributionType === 'EXPONENTIAL') {
        const mean = (dist_params.mean != undefined ? dist_params.mean : '10');
        settingsHTML = '<label>Mean:</label>' +
            '<input type="number" name="' + prefix + 'mean" step="0.01" min="0" value="' + mean + '">';

    } else if (distributionType === 'CONSTANT') {
        const value = (dist_params.value != undefined ? dist_params.value : '10');
        settingsHTML = '<label>Value:</label>' +
            '<input type="number" name="' + prefix + 'value" step="0.01" min="0" value="' + value + '">';

    } else if (distributionType === 'NORMAL') {
        const mean = (dist_params.mean != undefined ? dist_params.mean : '10');
        const standardDeviation = (dist_params.std_dev != undefined ? dist_params.std_dev : '10');
        settingsHTML = '<label>Mean:</label>' +
            '<input type="number" name="' + prefix + 'mean" step="0.01" min="0" value="' + mean + '"><br>' +
            '<label>Standard Deviation:</label>' +
            '<input type="number" name="' + prefix + 'standardDeviation" step="0.01" min="0" value="' + standardDeviation + '">';

    } else if (distributionType === 'ERLANG') {
        const mean = (dist_params.mean != undefined ? dist_params.mean : '10');
        const k = (dist_params.k != undefined ? dist_params.k : '2');
        settingsHTML = '<label>Mean:</label>' +
            '<input type="number" name="' + prefix + 'mean" step="0.01" min="0" value="' + mean + '"><br>' +
            '<label>k:</label>' +
            '<input type="number" name="' + prefix + 'k" step="0.01" min="0" value="' + k + '">';

    } else if (distributionType === 'UNIFORM') {
        const min = (dist_params.min != undefined ? dist_params.min : '0');
        const max = (dist_params.max != undefined ? dist_params.max : '10');
        settingsHTML = '<label>Min:</label>' +
            '<input type="number" name="' + prefix + 'min" step="0.01" min="0" value="' + min + '"><br>' +
            '<label>Max:</label>' +
            '<input type="number" name="' + prefix + 'max" step="0.01" min="0" value="' + max + '">';
    }

    return settingsHTML;
}

function getDistributionParams(div_id, select_id) {
    const distributionType = document.querySelector('select[name="' + select_id + '"]').value;
    const prefix = div_id + '-';
    // Get additional distribution settings based on the selected distribution type
    let additionalSettings = {};
    if (distributionType === 'EXPONENTIAL') {
        const mean = parseFloat(document.querySelector('input[name="' + prefix + 'mean"]').value);
        additionalSettings.mean = mean;
    } else if (distributionType === 'CONSTANT') {
        const value = parseFloat(document.querySelector('input[name="' + prefix + 'value"]').value);
        additionalSettings.value = value;
    } else if (distributionType === 'NORMAL') {
        const mean = parseFloat(document.querySelector('input[name="' + prefix + 'mean"]').value);
        const standardDeviation = parseFloat(document.querySelector('input[name="' + prefix + 'standardDeviation"]').value);
        additionalSettings.mean = mean;
        additionalSettings.std_dev = standardDeviation;
    } else if (distributionType === 'ERLANG') {
        const mean = parseFloat(document.querySelector('input[name="' + prefix + 'mean"]').value);
        const k = parseFloat(document.querySelector('input[name="' + prefix + 'k"]').value);
        additionalSettings.mean = mean;
        additionalSettings.k = k;
    } else if (distributionType === 'UNIFORM') {
        const min = parseFloat(document.querySelector('input[name="' + prefix + 'min"]').value);
        const max = parseFloat(document.querySelector('input[name="' + prefix + 'max"]').value);
        additionalSettings.min = min;
        additionalSettings.max = max;
    }

    return { "type": distributionType, "params": additionalSettings };
}

// Function to handle saving the settings
function saveSettings(node) {
    const processName = document.querySelector('input[name="processName"]').value;
    const cycleTime = parseFloat(document.querySelector('input[name="cycleTime"]').value);


    // Save the settings to the GOJS node
    // Replace the following code with your GOJS logic to update the node properties
    node.data.processName = processName;
    node.data.ct = cycleTime;
    node.data.ttr_dist = getDistributionParams('ttr-distribution-settings', 'ttr-distribution-type');
    node.data.tbf_dist = getDistributionParams('tbf-distribution-settings', 'tbf-distribution-type');

    // Close the settings drawer
    const settingsDrawer = document.getElementById('settings-drawer');
    settingsDrawer.classList.remove("open");
}
