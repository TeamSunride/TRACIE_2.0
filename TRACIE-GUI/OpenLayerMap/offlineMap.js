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
    layerMin: 13,
    layerMax : 16,
    extents : {
        extent13: [-13128784, 4205183, -13101305, 4219324],         // Extents in Web Mercator 
        extent14: [-13121590, 4208088, -13107850, 4215158],
        extent15: [-13118155, 4209855, -13111285, 4213391],
        extent16: [-13116437, 4210739, -13113002, 4212507],
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
            dataArray.extents[`extent${zoomLevel}`]         // E.g. Takes argument Mojave.extents['extent13']
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
            imageExtent: extentNum,//convertExtent(extentNum),
        }), 
    })
}