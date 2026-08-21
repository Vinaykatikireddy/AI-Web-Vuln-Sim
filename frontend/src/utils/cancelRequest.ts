import axios, { CancelTokenSource } from 'axios';

export const cancelRequest = (): {
    cancelTokenSource: CancelTokenSource;
    cancelRequest: () => void;
} => {
    const cancelTokenSource = axios.CancelToken.source();

    const cancelRequest = () => {
        cancelTokenSource.cancel('Request cancelled by user');
    };

    return { cancelTokenSource, cancelRequest };
};

// AbortController wrapper for fetch API
interface AbortControllerWrapper {
    controller: AbortController;
    cancelRequest: () => void;
}

export const abortableRequest = (): AbortControllerWrapper => {
    const controller = new AbortController();

    const cancelRequest = () => {
        controller.abort();
    };

    return { controller, cancelRequest };
};