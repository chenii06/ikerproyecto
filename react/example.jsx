import React, { useEffect, useState } from "react";
import VerticalCarousel from "./VerticalCarousel";
import { config } from "@react-spring/web";
import { useRoulette } from "./useRoulette";

export default function Example(props) {
  
  
  const { setModalIsOpen, listRoulette, newLevel, setRender, roulette, listInput, maxIntervalDuration, setlevelAnimation, listData} = props;

  if (listRoulette.length == 0) {
          <div>
          Loading...
      </div>
  }

  return (
    <div
      style={{
        position: "absolute",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        width: "100%",
        height: "100%",
        margin: "0 auto"
      }}
    >
      <VerticalCarousel
        maxIntervalDuration={maxIntervalDuration}
        listLevels={listRoulette}
        newLevel={newLevel}
        setRender={setRender}
        roulette={roulette}
        setModalIsOpen={setModalIsOpen}
        offsetRadius={3}
        showNavigation={false}
        animationConfig={config.gentle}
        listInput={listInput}
        setlevelAnimation={setlevelAnimation}
        listData={listData}
      />
    </div>
  );
}