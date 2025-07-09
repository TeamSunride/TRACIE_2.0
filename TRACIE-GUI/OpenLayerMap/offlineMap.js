import ImageLayer from 'ol/layer/Image.js'
import Static from 'ol/source/ImageStatic';
import LayerGroup from 'ol/layer/Group.js';


 // Each location as an object. Extents in Web Mercator
const MRC = {
    name: "MRC",
    layerMin: 13,
    layerMax: 18,
    extents : {
        extent13: [-178834.3395, 6915081.5256, -158866.2630, 6928393.5767],
        extent14: [-174152.5791, 6918020.6531, -164645.7241, 6925368.1622],
        extent15: [-171457.2156, 6920336.0949, -167316.0521, 6924048.0213],
        extent16: [-170923.8310, 6921219.1877, -168025.1836, 6923415.4855],
        extent17: [-170123.7397, 6921770.1688, -169013.9497, 6922777.1287],
        extent18: [-169868.2310, 6921886.5322, -169354.8788, 6922359.2803],
    }
};

const EARS = {
    name: "EARS",
    layerMin: 13,
    layerMax : 17,
    extents : {
        extent13: [-19432.8177, 6834123.7404, -726.6255, 6853809.6350],
        extent14: [-16279.4007, 6839542.7192, -3053.4186, 6850839.9122],
        extent15: [-13629.3578, 6841879.8240, -6099.3160, 6848015.4136],
        extent16: [-12037.6191, 6843960.7770, -8485.6017, 6846979.5816],
        extent17: [-11355.1408, 6844426.6595, -8882.9231, 6846539.1428],
    }
};

const MACH_X = {
    name: "MACH-X",
    layerMin:14,
    layerMax : 18,
    extents : {
        extent14: [-645744.0650, 7437895.9519, -620004.9459, 7457110.5256],
        extent15: [-640777.5602, 7440814.5506, -624955.7974, 7453163.9800],
        extent16: [-637334.7479, 7443967.9116, -628958.1032, 7449907.3419],
        extent17: [-634772.6213, 7445605.2479, -631635.1131, 7447879.5988],
        extent18: [-633755.7500, 7446357.2652, -632794.3741, 7447107.3497],
    }
};

const Mojave = {
    name: "Mojave",
    layerMin: 12,
    layerMax : 16,
    extents : {
        extent12: [-13194658.0652, 4139616.1298, -13032520.1392, 4270744.0700],       
        extent13: [-13137914.4843, 4187662.9390, -13088629.3423, 4234362.6309],
        extent14: [-13127113.6819, 4200418.7942, -13102347.0714, 4223648.1668],
        extent15: [-13121523.1318, 4208011.9415, -13107833.1230, 4215213.6335],
        extent16: [-13116437.0000, 4210739.0000, -13113002.0000, 4212507.0000],
    }
}


const locationObjectArray = [MRC, EARS, Mojave, MACH_X];

export const MRC_Layers = createOfflineLayerArray(MRC);
export const EARS_Layers = createOfflineLayerArray(EARS);
export const Mojave_Layers = createOfflineLayerArray(Mojave);
export const MACH_X_Layers = createOfflineLayerArray(MACH_X);



// ==== FUNCTIONS ====
function createOfflineLayerArray(dataArray) {
    const locationName = dataArray.name;
    const layers = [];
    for (let zoomLevel = dataArray.layerMin; zoomLevel <= dataArray.layerMax; zoomLevel++) {
        const layer = createImageLayer(
            locationName, 
            zoomLevel, 
            dataArray.extents[`extent${zoomLevel}`]        // E.g. Takes argument Mojave.extents['extent13']
        );
        layers.push(layer);
    }
    const layerGroup = new LayerGroup({         // Wrap all layers in a LayerGroup
        layers: layers,
    });
    console.log(layerGroup);
    return layerGroup;                                      // Returns a LayerGroup instead of an array
}

function createImageLayer(locationName, zoomLevel, extentNum) {           // Create a SINGLE ImageLayer 
    return new ImageLayer({
        source: new Static({
            url: `./offline_map/${locationName}/zoom${zoomLevel}.png`,
            projection: 'EPSG:3857',
            imageExtent: extentNum,
        }), 
    })
}