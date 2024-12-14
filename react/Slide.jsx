import styled from "@emotion/styled";
import PropTypes from "prop-types";
import { useSpring, animated } from "@react-spring/web";
import { useDrag } from "react-use-gesture";

const SlideContainer = styled(animated.div)`
  position: absolute;
  top: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform-origin: 50% 50%;
`;

const SlideCard = styled.div`
  position: relative;
  width: 800px;
  height: 200px;
  background: #1e1e27;
  font-size: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  transform-origin: 50% 50%;
  border-radius: 10px;

  @media (max-width: 970px) {
    width: 100%;
    height: 100px;
  }
`;

function Slide({
  content,
  offsetRadius,
  index,
  animationConfig,
  moveSlide,
  delta,
  down,
  up,
}) {
  const offsetFromMiddle = index - offsetRadius;
  const totalPresentables = 2 * offsetRadius + 1;
  const distanceFactor = 1 - Math.abs(offsetFromMiddle / (offsetRadius + 1));

  const translateYoffset =
    50 * (Math.abs(offsetFromMiddle) / (offsetRadius + 1));
  let translateY = -50;

  if (offsetRadius !== 0) {
    if (index === 0) {
      translateY = 0;
    } else if (index === totalPresentables - 1) {
      translateY = -100;
    }
  }

  if (offsetFromMiddle === 0 && down) {
    translateY += delta[1] / (offsetRadius + 1);
    if (translateY > -40) {
      moveSlide(-1);
    }
    if (translateY < -100) {
      moveSlide(1);
    }
  }

  if (offsetFromMiddle > 0) {
    translateY += translateYoffset;
  } else if (offsetFromMiddle < 0) {
    translateY -= translateYoffset;
  }

  const bind = useDrag(({ down, movement: [mx, my] }) => {
    moveSlide(down ? my : 0);
  });

  const style = useSpring({
    transform: `translateX(0%) translateY(${translateY}%) scale(${distanceFactor})`,
    top: `${
      offsetRadius === 0 ? 50 : 50 + (offsetFromMiddle * 50) / offsetRadius
    }%`,
    opacity: distanceFactor * distanceFactor,
    config: animationConfig,
  });

  return (
    <SlideContainer
      {...bind()}
      style={{
        ...style,
        zIndex: Math.abs(Math.abs(offsetFromMiddle) - 10),
      }}
    >
      <SlideCard>{content}</SlideCard>
    </SlideContainer>
  );
}

Slide.propTypes = {
  content: PropTypes.any.isRequired,
  offsetRadius: PropTypes.any.isRequired,
  index: PropTypes.any.isRequired,
  animationConfig: PropTypes.any.isRequired,
  moveSlide: PropTypes.any.isRequired,
  delta: PropTypes.any.isRequired,
  down: PropTypes.any.isRequired,
  up: PropTypes.any.isRequired,
};

export default Slide;