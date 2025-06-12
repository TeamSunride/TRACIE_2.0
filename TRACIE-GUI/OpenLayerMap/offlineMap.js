import ImageLayer from 'ol/layer/Image.js'
import Static from 'ol/source/ImageStatic';

/*
const MRC = {
    locationName: "MRC",
    layerMin: 13,
    layerMax : 16,
    extents : {

    }
};

const EARS = {
    locationName: "EARS",
    layerMin: 13,
    layerMax : 16,
    extents : {

    }
};

const MACH_X = {
    locationName: "MACH_X",
    layerMin: 13,
    layerMax : 16,
    extents : {

    }
};
*/

const Mojave = {                        // Each location as an object
    name: "Mojave",
    layerMin: 12,
    layerMax : 16,
    extents : {                          // In web mercator
        extent12: [-13194658.0652, 4139616.1298, -13032520.1392, 4270744.0700],       
        extent13: [-13137914.4843, 4187662.9390, -13088629.3423, 4234362.6309],
        extent14: [-13127113.6819, 4200418.7942, -13102347.0714, 4223648.1668],
        extent15: [-13121523.1318, 4208011.9415, -13107833.1230, 4215213.6335],
        extent16: [-13116437.0000, 4210739.0000, -13113002.0000, 4212507.0000],
    }
};


const locationObjectArray = [/*MRC, EARS*/Mojave/*, MACH_X*/];

export const Mojave_Layers = createOfflineLayerArray(Mojave);
//export const Mach_X_Layers = createOfflineLayerArray(Mach_X);
//export const MRC_Layers = createOfflineLayerArray(MRC);
//export const EARS_Layers = createOfflineLayerArray(EARS);


// ==== FUNCTIONS ====
function createOfflineLayerArray(dataArray) {
    const locationName = dataArray.name;
    const outputArray = [];
    for (let zoomLevel = dataArray.layerMin; zoomLevel <= dataArray.layerMax; zoomLevel++) {
        const layer = createImageLayer(
            locationName, 
            zoomLevel, 
            dataArray.extents[`extent${zoomLevel}`]        // E.g. Takes argument Mojave.extents['extent13']
        );
        outputArray.push(layer);
    }
    console.log(outputArray);
    return outputArray;
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