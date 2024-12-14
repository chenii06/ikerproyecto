import axios from "axios";


export const apiRest = axios.create({
    baseURL: window.location.origin + "/",
});

apiRest.interceptors.request.use(config => {
    config.headers = {
        ...config.headers,
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Content-Type": "application/json"
    }
    console.log("config.headers");
    console.log(config.headers);
    return config;
});
