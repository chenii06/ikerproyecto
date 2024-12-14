import 'bootstrap/dist/css/bootstrap.min.css';
import 'animate.css/animate.min.css';
import 'animate.css';

import React, { useEffect, useState, useRef } from 'react';
import ReactDOM from 'react-dom';
import { useRoulette } from './useRoulette';
import Modal from 'react-modal';
import Example from './example';
import './index.css'


function Main() {
    const { getLevels, getInfo, newLevel, sendGg } = useRoulette();
    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [listRoulette, setListRoulette] = useState([]);
    const [listData, setListData] = useState([]);
    const [listInput, setListInput] = useState('');
    const [render, setRender] = useState(false);
    const [ggActive, setGgActive] = useState(false);
    const [fadeOutClass, setFadeOutClass] = useState('');
    const [levelAnimation, setlevelAnimation] = useState(false);
    const [maxIntervalDuration, setmaxIntervalDuration] = useState(Math.floor(Math.random() * (4) + 4) * 1000);

   const urlRoulette = window.location.pathname.split('/');
   const roulette = urlRoulette[urlRoulette.length-1];

useEffect(() => {
    const fetchData = async () => {
        const result = await getInfo(roulette);
        const ruleta = await getLevels(roulette);
        setListRoulette(ruleta);
        setListData(result);
        setListInput('');
        setRender(false);

        if (result.demons.length > 3){
            setTimeout(() => {
                window.scrollTo(0, document.body.scrollHeight);
            }, 300);
        }
    };
    fetchData();
    }, [render]);
   
useEffect(() => {
    if (modalIsOpen) {
        const timeoutId = setTimeout(() => {
        setFadeOutClass('animate__fadeOut');
        }, maxIntervalDuration + 2000);

        return () => clearTimeout(timeoutId);
    } else {
        setFadeOutClass('');
    }
    }, [modalIsOpen]);

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
}

    if (listData.length ===  0 || listRoulette.length === 0) {

        return (

        <div>
            Loading...
        </div>

       );
    }

    

    return (
        <>
            <div className={`roulette-levels card-${listData.aspect_mode}mode`}>
                {listData.demons.map((item, index) => (
                    <div key={index} className={`new-demon-level-card content-${listData.aspect_mode}mode ${index == listData.demons.length -1 && listData.complete == false && levelAnimation == true ? 'animate__animated animate__backInUp' : ''}`}>
                        
                    <img src={!item.demon__photo || item.demon__photo === "" ? 
                        (item.demon__type ? 
                            `/static/img/niveles_sin_miniatura/demon-${item.demon__demon_difficulty.split(' ')[0].toLowerCase()}-${item.demon__type}.png` : 
                            `/static/img/niveles_sin_miniatura/demon-${item.demon__demon_difficulty.split(' ')[0].toLowerCase()}.png`) :
                        `${listData.media_url}${item.demon__photo}`} alt="" />
                    <div className={`level-info-container text-${listData.aspect_mode}mode`}>
                    <div className={`level-main-data-container text-${listData.aspect_mode}mode`}>
                        <p className="level-title">{item.demon__level}</p>
                        <p className="level-creator">{listData.list_words.creator}: <b>{item.demon__creator}</b></p>
                        <p className="level-id">{listData.list_words.level_id}: <b onClick={() => copyToClipboard(item.demon__level_id)}>{item.demon__level_id}</b></p>
                    </div>
                    <div className="level-progress-data-container">
                       {  
                            listData.mode == "platformer" || listData.mode == "platformer_best_time" ? (
                            <p className="level-stage">{listData.list_words.stage} <b>{item.stage}</b> - {item.num_level}</p>
                            )
                            : (
                                <p></p>
                            )
                        }
                        <form className="new-demon-level-input-container" onKeyPress={handleKeyPress}>
                            {
                                index == listData.demons.length -1 && listData.complete == false ? (
                                    <div className='new-container'>
                                        {  
                                            listData.mode == "classic" ? (
                                            <input type="number" className={`done-button percentaje-input card-${listData.aspect_mode}mode text-${listData.aspect_mode}mode`} placeholder={`${listData.list_words.percentage}`} name="percentage" id="percentage" value={listInput} onChange={(e) => {setListInput(e.target.value)}} required/>
                                        )
                                        : listData.mode === "platformer_best_time" ? (
                                            <label class={`new-label text-${listData.aspect_mode}mode`}>{item.best_time ? item.best_time : "No Best Time"}</label>
                                        )
                                        : (
                                            <></>
                                        )
                                        }
                                            <button 
                                            type="button"
                                            className={`done-button main-button-${listData.aspect_mode}mode`}
                                            data-bs-toggle="modal" 
                                            data-bs-target="#staticBackdrop"
                                             onClick={(e) => { 
                                                var last_demon = false;
                                                var enabled_button = false;
                                                if ((listData.mode == "classic" && parseInt(listInput) == 100) || ((listData.mode == "platformer" || listData.mode == "platformer_best_time") && listData.last_demon == true) || (Object.keys(listRoulette).length == 0)) {
                                                    last_demon = true;
                                                }

                                                if ((listInput >= (listData.highest_percent + 1) && listInput <= 100) || listData.mode == "platformer" || listData.mode == "platformer_best_time"){
                                                    enabled_button = true;
                                                }

                                                if (listData.fast_animation){
                                                    setmaxIntervalDuration(Math.floor(Math.random() * (2) + 2) * 1000)
                                                }

                                                if (last_demon && enabled_button) {
                                                    setGgActive(true);
                                                    sendGg(roulette, listInput);
                                                    setlevelAnimation(true);
                                                    setRender(true);
                                                }
                                                else if (Object.keys(listRoulette).length == 1 && enabled_button) {
                                                    newLevel(listRoulette[0].level_id, roulette, listInput)
                                                    setlevelAnimation(true);
                                                    setRender(true);
                                                }
                                                else if(enabled_button) {
                                                    e.preventDefault(); 
                                                    setModalIsOpen(true);
                                                    var body = document.querySelector('body');
                                                    body.classList.add("refused-scroll");
                                                }
                                            }}>{listData.list_words.complete}</button>
                                    </div>

                                )
                                 : (
                                    <div className={`labels-container text-${listData.aspect_mode}mode`}>
                                        <label className="done-label">{listData.list_words.done}</label>
                                        {  
                                            listData.mode == "classic" ? (
                                            <label className="number-label">({item.percentage}%)</label>
                                        )
                                        : listData.mode === "platformer_best_time" ? (
                                            <label className="number-label">({item.best_time ? item.best_time : "No Best Time"})</label>
                                        )
                                        : (
                                            <></>
                                        )
                                        }
                                    </div>
                                 )
                            }
                        </form>
                    </div>
                    </div>
                </div>
                ))}

                {
                    listRoulette.length != 0 && listData.demons.length === 0 ?(
                        <button 
                        type="button"
                        className={`done-button main-button-${listData.aspect_mode}mode`}
                        data-bs-toggle="modal" 
                        data-bs-target="#staticBackdrop"
                        onClick={(e) => { 
                            if (listData.fast_animation){
                                setmaxIntervalDuration(Math.floor(Math.random() * (2) + 2) * 1000)
                            }
                            e.preventDefault(); 
                            setModalIsOpen(true);
                            var body = document.querySelector('body');
                            body.classList.add("refused-scroll");
                        }}>Start</button>
                    )
                    : (
                    <></>
                    )
                }
                {
                    ggActive == true || listData.complete == true ?(
                        <div key="gg" className={`new-demon-level-card ${levelAnimation == true ? 'animate__animated animate__backInUp' : ''}`}>
                            <p className="gg-label">GG</p>
                        </div>
                    )
                    : (
                    <></>
                    )
                }
                  <div className="App" >
                  <Modal
                        isOpen={modalIsOpen}
                        onRequestClose={() => setModalIsOpen(false)}
                        overlayClassName={`modal-overlay animate__animated animate__fadeIn ${fadeOutClass}`}
                        style={{
                            content: {
                                position:"fixed",
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                color: 'lightsteelblue',
                                width: '80%',
                                margin: '0 auto',
                                background: listData.background,
                                border: 'solid 1px #282834',
                            }
                        }}
                        contentLabel="Example Modal"
                    >
                        <Example
                        setModalIsOpen={setModalIsOpen}
                        listRoulette={listRoulette}
                        maxIntervalDuration={maxIntervalDuration}
                        newLevel={newLevel}
                        roulette={roulette}
                        setRender={setRender}
                        listInput={listInput}
                        setlevelAnimation={setlevelAnimation}
                        listData={listData}
                        />
                    </Modal>
                    </div>
            </div>
        </>
    );
}

ReactDOM.render(<Main/>, document.getElementById('component-root'));