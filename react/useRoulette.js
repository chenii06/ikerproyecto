import { apiRest } from "./apiRest";

export const useRoulette = () => {

    const getLevels = async (roulette) => {
    
    try {
         const response = await apiRest.post(`roulette/${roulette}`, {"get_levels": true});
         console.log(response.data);
        return response.data;
    } catch (error) {
        console.log("Error en GetLEvels")
        console.error(error);
    }
    
    }

    const getInfo = async (roulette) => {
    
        try {
            const response = await apiRest.get(`roulette/${roulette}`);
            console.log(response.data);
            return response.data;
        } catch (error) {
            console.log("Error en getInfo")
            console.error(error);
        }
        
    }

    const newLevel = async (num, roulette, listInput) => {
        try {
            await apiRest.post(`roulette/${Number(roulette)}`, {"level_id": Number(num), "percentage": Number(listInput)});
            await getInfo(roulette)
        
        } catch (error) {
            console.log("Error en newLevel")
            console.error(error);
        }
        
    }

    const sendGg = async (roulette, listInput) => {
        try {
            await apiRest.post(`roulette/${Number(roulette)}`, {"gg": true, "percentage": Number(listInput)});
        
        } catch (error) {
            console.log("Error en newLevel")
            console.error(error);
        }
        
    }

    return {
      getLevels,
      newLevel,
      getInfo,
      sendGg,
    }
};