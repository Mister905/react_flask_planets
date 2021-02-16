import React, { useState, useEffect } from "react";
import { BrowserRouter, Switch, Route } from "react-router-dom";

// COMPONENTS
import Test from "./components/test/Test";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Switch>
          <Route exact path="/" component={Test} />
        </Switch>
      </BrowserRouter>
    </div>
  );
}

export default App;
