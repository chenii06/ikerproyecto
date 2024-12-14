
import React from "react";
import { keyframes } from "@emotion/react";
import styled from "@emotion/styled";
import Slide from "./Slide";
import PropTypes from "prop-types";

const Wrapper = styled.div`
  position: relative;
  display: flex;
  justify-content: center;
  width: 100%;
  height: 500px;

  @media (max-width: 970px) {
    height: 325px;
  }
`;

const blink = keyframes`
  0% {background-color: #282834;}
  50% {background-color: #5A7BAE;}
  100% {background-color: #282834;}
`;

const AnimatedDiv = styled.div`
  animation: ${blink} 0.5s infinite;
`;
  
function mod(a, b) {
  return ((a % b) + b) % b;
}

export default class VerticalCarousel extends React.Component {
  state = {
    index: Math.floor(Math.random() * this.props.listLevels.length),
    goToSlide: null,
    prevPropsGoToSlide: 0,
    newSlide: false,
    centralIndex: 0,
  };
 
  componentDidMount = () => {
    let intervalDuration = 0;
    
    const gradualInterval = () => {
      this.moveSlide(-1);
      intervalDuration = Math.min(intervalDuration + 10, this.props.maxIntervalDuration);
      this.intervalId = setTimeout(gradualInterval, intervalDuration);
    };

    this.intervalId = setTimeout(gradualInterval, intervalDuration);

    this.timeoutId = setTimeout(async() => {
      clearInterval(this.intervalId);
       const middleElement = this.props.listLevels[this.state.index];

         await this.props.newLevel(middleElement.level_id, this.props.roulette, this.props.listInput)
      
    }, this.props.maxIntervalDuration);

    this.timeoutId = setTimeout(async() => {
      this.setState({
        centralIndex: Number(this.props.listLevels[this.state.index].level_id),
      });
    }, this.props.maxIntervalDuration + 200);

    this.timeoutId = setTimeout(async() => {
      await this.props.setRender(true);
      this.props.setModalIsOpen(false);
      this.props.setlevelAnimation(true);
      var body = document.querySelector('body');
      body.classList.remove("refused-scroll");
    }, this.props.maxIntervalDuration + 2400);
  };

  renderSlide = (slide, isCentral) => {
    // Aplica el estilo solo si el slide es el elemento central
    const Div = isCentral ? AnimatedDiv : "div";
    return (
      <div
        className="level-card-container"
        style={{
          width: "800px",
          height: "200px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
        alt="card"
      >
        <Div
          className={`level-card card-${this.props.listData.aspect_mode}mode`}
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            justifyItems: "start",
            alignItems: "center",
            gap: "25px",
            borderRadius: "10px",
            padding: "10px",
          }}
        >
          <img
            src={slide.photo__url ? slide.photo__url : (slide.type ? `/static/img/niveles_sin_miniatura/demon-${slide.demon_difficulty.split(' ')[0].toLowerCase()}-${slide.type}.png` : `/static/img/niveles_sin_miniatura/demon-${slide.demon_difficulty.split(' ')[0].toLowerCase()}.png`)}
            alt=""
            className="level-img"
            style={{
              width: "320px",
              height: "180px",
              borderRadius: "10px",
            }}
          />
          <div
            className="level-data-container"
            style={{
              height: "180px",
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              justifyContent: "space-between",
              padding: "25px 0px",
            }}
          >
            <h5
              className={`level-title text-${this.props.listData.aspect_mode}mode`}
              style={{
                fontSize: "25px",
                fontWeight: "800",
                fontFamily: "Akira Expanded",
              }}
            >
              {slide.level}
            </h5>
            <p
              className={`level-data text-${this.props.listData.aspect_mode}mode`}
              style={{
                fontSize: "18px",
                fontWeight: "400",
                fontFamily: "Poppins",
              }}
            >
              {this.props.listData.list_words.creator}: <b
                className={`level-data-b text-${this.props.listData.aspect_mode}mode`}
                style={{
                  fontSize: "18px",
                  fontWeight: "700",
                  fontFamily: "Poppins",
                }}
              >
                {slide.creator}
              </b>
            </p>
            <p
              className={`level-data text-${this.props.listData.aspect_mode}mode`}
              style={{
                fontSize: "18px",
                fontWeight: "400",
                fontFamily: "Poppins",
              }}
            >
              {this.props.listData.list_words.level_id}: <b
                className={`level-data-b text-${this.props.listData.aspect_mode}mode`}
                style={{
                  fontSize: "18px",
                  fontWeight: "700",
                  fontFamily: "Poppins",
                }}
              >
                {slide.level_id}
              </b>
            </p>
          </div>
        </Div>
      </div>
    );
  };

  componentWillUnmount = () => {
    clearInterval(this.intervalId);
    clearTimeout(this.timeoutId);
  };

  static propTypes = {
    listLevels: PropTypes.arrayOf(
      PropTypes.shape({
        key: PropTypes.any,
        content: PropTypes.object,
      })
    ).isRequired,
    goToSlide: PropTypes.number,
    showNavigation: PropTypes.bool,
    offsetRadius: PropTypes.number,
    animationConfig: PropTypes.object,
    setModalIsOpen: PropTypes.func,
    roulette: PropTypes.any.isRequired,
    newLevel: PropTypes.any.isRequired,
    setRender: PropTypes.any.isRequired,
    maxIntervalDuration: PropTypes.any.isRequired,
    listInput: PropTypes.any,
    listData: PropTypes.any,
  };

  static defaultProps = {
    offsetRadius: 2,
    animationConfig: { tension: 120, friction: 14 },
  };

  modBySlidesLength = (index) => {
    const { listLevels } = this.props;
    return (index + listLevels.length) % listLevels.length;
  };

  moveSlide = (direction) => {
    this.setState({
      index: this.modBySlidesLength(this.state.index + direction),
      goToSlide: null,
    });
  };

  clampOffsetRadius(offsetRadius) {
    const { listLevels } = this.props;
    const upperBound = Math.floor((listLevels.length - 1) / 2);
   
    if (offsetRadius < 0) {
      return 0;
    }
    if (offsetRadius > upperBound) {
      return upperBound;
    }

    return offsetRadius;
  }

  getPresentableSlides() {
    const { listLevels } = this.props;
    const { index } = this.state;
    let { offsetRadius } = this.props;
    offsetRadius = this.clampOffsetRadius(offsetRadius);
    const presentableSlides = new Array();
    for (let i = -offsetRadius; i < 1 + offsetRadius; i++) {
      presentableSlides.push(listLevels[this.modBySlidesLength(index + i)]);
    }

    return presentableSlides;
  }

  render() {
    const { animationConfig, offsetRadius } = this.props;

    return (
      <React.Fragment>
        <Wrapper>
          {this.getPresentableSlides().map((slide, index) => {
            
            const isCentral = this.state.centralIndex === Number(slide.level_id);
            
            return (
              <Slide
                key={slide.level_id}
                content={this.renderSlide(slide, isCentral)}
                moveSlide={this.moveSlide}
                offsetRadius={this.clampOffsetRadius(offsetRadius)}
                index={index}
                animationConfig={animationConfig}
              />
            );
          })}
        </Wrapper>
      </React.Fragment>
    );
  }
}