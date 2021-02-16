import { TIME_LOADED } from "./types";
import axios from "axios";

export const test_action = () => async (dispatch) => {
  try {
    const res = await axios.get("/api/time");
    dispatch({
      type: TIME_LOADED,
      payload: res.data,
    });
  } catch (error) {
    console.log(error.message);
  }
};
